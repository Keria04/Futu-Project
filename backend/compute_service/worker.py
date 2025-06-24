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
        payload = task.payload
        image_data = payload.get('image_data')
        
        if not image_data:
            raise ValueError("缺少图片数据")
        
        # 解码图片
        img_bytes = base64.b64decode(image_data)
        img = Image.open(BytesIO(img_bytes))
        
        # 提取特征
        extractor = self._get_extractor()
        features = extractor.calculate(img)
        
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
    
    def __init__(self, worker_name: str = "compute_worker"):
        self.worker_name = worker_name
        self.redis = redis_client.get_client()
        self.processors: List[TaskProcessor] = []
        self.running = False
        self.worker_thread = None
        
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
                # 从优先级队列获取任务
                task_data = self.redis.bzpopmin(task_queue, timeout=1)
                if not task_data:
                    continue
                
                _, task_json, _ = task_data
                task = TaskMessage.from_json(task_json)
                
                logging.info(f"处理任务: {task.task_id}, 类型: {task.task_type.value}")
                
                # 更新任务状态为处理中
                self._update_task_status(task.task_id, TaskStatus.PROCESSING)
                
                # 查找合适的处理器
                processor = self._find_processor(task.task_type)
                if processor is None:
                    result = MessageProtocol.create_error_result(
                        task.task_id,
                        f"没有找到处理器: {task.task_type.value}"
                    )
                else:
                    # 处理任务
                    result = processor.process(task)
                
                # 发送结果
                self.redis.lpush(result_queue, result.to_json())
                
                logging.info(f"任务完成: {task.task_id}, 状态: {result.status.value}")
                
            except Exception as e:
                logging.error(f"工作循环出错: {e}")
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
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 设置工作目录
    current_dir = os.getcwd()
    target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if current_dir != target_dir:
        os.chdir(target_dir)
    
    # 创建工作者
    worker = ComputeWorker()
    
    try:
        worker.start()
        
        # 保持运行
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logging.info("收到停止信号...")
    finally:
        worker.stop()
        logging.info("计算工作者已退出")


if __name__ == '__main__':
    run_compute_worker()
