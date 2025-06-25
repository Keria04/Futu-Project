"""
计算端工作者 - 策略模式 + 单例模式
负责处理计算任务
"""
import os
import sys
import time
import base64
import threading
from io import BytesIO
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
import logging
import json

from PIL import Image
import numpy as np

# 添加路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared import redis_client, TaskMessage, TaskResult, TaskType, TaskStatus, MessageProtocol
from compute_service.model_module.feature_extractor import feature_extractor


class TaskProcessor(ABC):
    """任务处理器接口"""
    
    @abstractmethod
    def can_handle(self, task_type: TaskType) -> bool:
        """判断是否能处理该类型任务"""
        pass
    
    @abstractmethod
    def process(self, task: TaskMessage) -> TaskResult:
        """处理任务"""
        pass


class FeatureExtractionProcessor(TaskProcessor):
    """特征提取处理器"""
    
    def __init__(self):
        self.extractor = None
        self._lock = threading.Lock()
    
    def _get_extractor(self):
        """获取特征提取器实例（懒加载）"""
        if self.extractor is None:
            with self._lock:
                if self.extractor is None:
                    self.extractor = feature_extractor()
        return self.extractor
    
    def can_handle(self, task_type: TaskType) -> bool:
        """判断是否能处理该类型任务"""
        return task_type in [TaskType.FEATURE_EXTRACTION, TaskType.BATCH_FEATURE_EXTRACTION]
    
    def process(self, task: TaskMessage) -> TaskResult:
        """处理特征提取任务"""
        try:
            if task.task_type == TaskType.FEATURE_EXTRACTION:
                return self._process_single_image(task)
            elif task.task_type == TaskType.BATCH_FEATURE_EXTRACTION:
                return self._process_batch_images(task)
            else:
                raise ValueError(f"不支持的任务类型: {task.task_type}")
        
        except Exception as e:
            return MessageProtocol.create_error_result(
                task.task_id, 
                f"特征提取失败: {str(e)}"
            )
    def _process_single_image(self, task: TaskMessage) -> TaskResult:
        """处理单张图片特征提取"""
        logger = logging.getLogger(f"{__name__}.FeatureExtractionProcessor")
        
        payload = task.payload
        image_data = payload.get('image_data')
        
        if not image_data:
            logger.error("❌ 缺少图片数据")
            raise ValueError("缺少图片数据")
        
        logger.debug(f"🖼️ 开始处理单张图片特征提取")
        
        # 解码图片
        try:
            img_bytes = base64.b64decode(image_data)
            img = Image.open(BytesIO(img_bytes))
            logger.debug(f"📏 图片尺寸: {img.size}")
            logger.debug(f"🎨 图片模式: {img.mode}")
        except Exception as e:
            logger.error(f"❌ 图片解码失败: {e}")
            raise ValueError(f"图片解码失败: {e}")
        
        # 提取特征
        extractor = self._get_extractor()
        logger.debug(f"🔍 使用特征提取器: {extractor.__class__.__name__}")
        
        start_time = time.time()
        features = extractor.calculate(img)
        extract_time = time.time() - start_time
        
        logger.debug(f"✅ 特征提取完成，耗时: {extract_time:.3f}s")
        logger.debug(f"📊 特征维度: {features.shape if hasattr(features, 'shape') else len(features)}")
        
        return MessageProtocol.create_success_result(
            task.task_id,
            features.tolist()
        )
    
    def _process_batch_images(self, task: TaskMessage) -> TaskResult:
        """处理批量图片特征提取"""
        payload = task.payload
        image_list = payload.get('image_list', [])
        
        if not image_list:
            raise ValueError("缺少图片数据列表")
        
        # 解码所有图片
        images = []
        for img_data in image_list:
            img_bytes = base64.b64decode(img_data)
            img = Image.open(BytesIO(img_bytes))
            images.append(img)
        
        # 批量提取特征
        extractor = self._get_extractor()
        features = extractor.calculate_batch(images)
        
        return MessageProtocol.create_success_result(
            task.task_id,
            features.tolist()
        )


class ComputeWorker:
    """计算端工作者"""
    def __init__(self, worker_name: str = "compute_worker", debug: bool = False):
        self.worker_name = worker_name
        self.debug = debug
        self.redis = redis_client.get_client()
        self.processors: List[TaskProcessor] = []
        self.running = False
        self.worker_thread = None
        self.logger = logging.getLogger(f"{__name__}.{worker_name}")
        
        if self.debug:
            self.logger.debug(f"🔧 初始化计算工作者: {worker_name}")
        
        # 注册处理器
        self._register_processors()
    
    def _register_processors(self):
        """注册任务处理器"""
        self.processors.append(FeatureExtractionProcessor())
    
    def start(self):
        """启动工作者"""
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._work_loop)
            self.worker_thread.daemon = True
            self.worker_thread.start()
            logging.info(f"计算工作者 {self.worker_name} 已启动")
    
    def stop(self):
        """停止工作者"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logging.info(f"计算工作者 {self.worker_name} 已停止")
    
    def _work_loop(self):
        """工作循环"""
        task_queue = "task_queue"
        result_queue = "result_queue"
        while self.running:
            try:
                if self.debug:
                    self.logger.debug(f"🔍 等待任务...")
                
                # 从优先级队列获取任务
                task_data = self.redis.bzpopmin(task_queue, timeout=1)
                if not task_data:
                    if self.debug:
                        self.logger.debug("⏰ 超时，继续等待...")
                    continue
                
                _, task_json, _ = task_data
                task = TaskMessage.from_json(task_json)
                
                if self.debug:
                    self.logger.debug(f"📥 收到任务: {task.task_id}")
                    self.logger.debug(f"🏷️ 任务类型: {task.task_type.value}")
                    self.logger.debug(f"📊 任务数据大小: {len(task_json)} bytes")
                
                self.logger.info(f"处理任务: {task.task_id}, 类型: {task.task_type.value}")
                
                # 更新任务状态为处理中
                self._update_task_status(task.task_id, TaskStatus.PROCESSING)
                
                # 查找合适的处理器
                processor = self._find_processor(task.task_type)
                if processor is None:
                    if self.debug:
                        self.logger.debug(f"❌ 没有找到处理器: {task.task_type.value}")
                    result = MessageProtocol.create_error_result(
                        task.task_id,
                        f"没有找到处理器: {task.task_type.value}"
                    )
                else:
                    if self.debug:
                        self.logger.debug(f"✅ 找到处理器: {processor.__class__.__name__}")
                    # 处理任务
                    start_time = time.time()
                    result = processor.process(task)
                    process_time = time.time() - start_time
                    
                    if self.debug:
                        self.logger.debug(f"⏱️ 处理耗时: {process_time:.3f}s")
                
                # 发送结果
                self.redis.lpush(result_queue, result.to_json())
                
                if self.debug:
                    self.logger.debug(f"📤 结果已发送到队列")
                
                self.logger.info(f"任务完成: {task.task_id}, 状态: {result.status.value}")
                
            except Exception as e:
                self.logger.error(f"工作循环出错: {e}")
                if self.debug:
                    import traceback
                    self.logger.debug(f"错误详情:\n{traceback.format_exc()}")
                time.sleep(1)
    
    def _find_processor(self, task_type: TaskType) -> Optional[TaskProcessor]:
        """查找任务处理器"""
        for processor in self.processors:
            if processor.can_handle(task_type):
                return processor
        return None
    
    def _update_task_status(self, task_id: str, status: TaskStatus):
        """更新任务状态"""
        task_key = f"task:{task_id}"
        task_data = redis_client.get_json(task_key)
        if task_data:
            task_data['status'] = status.value
            redis_client.set_json(task_key, task_data, ex=3600)


def run_compute_worker():
    """运行计算工作者"""
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='计算端工作者')
    parser.add_argument('--debug', action='store_true', help='启用详细debug输出')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    args, unknown = parser.parse_known_args()
    
    # 设置日志级别
    log_level = getattr(logging, args.log_level.upper())
    if args.debug:
        log_level = logging.DEBUG
    
    # 设置日志
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),  # 确保输出到标准输出
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    if args.debug:
        logger.info("🐛 DEBUG模式已启用")
        logger.debug(f"当前工作目录: {os.getcwd()}")
        logger.debug(f"Python路径: {sys.path}")
    
    # 设置工作目录
    current_dir = os.getcwd()
    target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if current_dir != target_dir:
        logger.debug(f"切换工作目录: {current_dir} -> {target_dir}")
        os.chdir(target_dir)
    
    # 创建工作者
    worker = ComputeWorker(debug=args.debug)
    
    try:
        worker.start()
        
        # 保持运行
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("收到停止信号...")
    finally:
        worker.stop()
        logger.info("计算工作者已退出")


if __name__ == '__main__':
    run_compute_worker()
