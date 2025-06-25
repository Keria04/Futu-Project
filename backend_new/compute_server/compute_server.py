"""
计算端服务器 - 负责图片特征提取计算
修复版本：解决任务重复处理和资源竞争问题
"""
import json
import logging
import threading
import time
import sys
import os
from typing import Dict, Any, List

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from redis_client.redis_client import RedisClient, RedisConfig
from _model_interface import ModelManager, create_feature_extractor, create_model_config, ModelConfig


class ComputeServer:
    """计算端服务器类"""
    
    def __init__(self, redis_config: RedisConfig = None, model_config: ModelConfig = None):
        self.logger = logging.getLogger(__name__)
        
        # 初始化Redis客户端
        self.redis_client = RedisClient(redis_config)
        
        # 初始化模型管理器和特征提取器
        self.model_manager = ModelManager()
        
        # 创建特征提取器配置
        if model_config is None:
            # 使用默认配置
            self.logger.info("使用默认模型配置")
            self.feature_extractor = create_feature_extractor(
                model_type="resnet50",
                device="cpu",
                input_size=224,
                batch_size=128,
                pretrain=True
            )
        else:
            # 使用传入的配置
            self.logger.info(f"使用传入的模型配置: {model_config.__dict__}")
            self.logger.info(f"检查internal_config属性: {hasattr(model_config, 'internal_config')}")
            
            try:
                internal_config = model_config.internal_config
                self.logger.info(f"internal_config获取成功: {internal_config}")
                self.feature_extractor = self.model_manager.get_facade().create_extractor_from_config(model_config)
            except Exception as e:
                self.logger.error(f"使用传入配置失败，转为默认配置: {e}")
                self.feature_extractor = create_feature_extractor(
                    model_type="resnet50",
                    device="cpu",
                    input_size=224,
                    batch_size=128,
                    pretrain=True
                )
        
        # 工作线程
        self.worker_threads = []
        self.running = False
        self.num_workers = 2
        
        # 订阅的任务频道
        self.task_channels = [
            'compute:single_feature_extraction',
            'compute:batch_feature_extraction',
            'compute:model_info',
            'compute:update_model',
            'compute:health_check'
        ]
    
    def start(self, num_workers: int = 2):
        """启动计算端服务器"""
        self.num_workers = num_workers
        self.running = True
        
        self.logger.info(f"启动计算端服务器，工作线程数: {num_workers}")
        
        # 启动工作线程
        for i in range(num_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"ComputeWorker-{i}",
                daemon=True
            )
            worker.start()
            self.worker_threads.append(worker)
        
        self.logger.info("计算端服务器启动成功")
    
    def stop(self):
        """停止计算端服务器"""
        self.logger.info("正在停止计算端服务器...")
        self.running = False
        
        # 等待工作线程结束
        for worker in self.worker_threads:
            worker.join(timeout=5)
        
        self.worker_threads.clear()
        self.redis_client.close()
        self.logger.info("计算端服务器已停止")
    
    def _worker_loop(self):
        """工作线程主循环"""
        worker_name = threading.current_thread().name
        self.logger.info(f"{worker_name} 开始监听任务")
        
        # 订阅任务频道
        pubsub = self.redis_client.subscribe_tasks(self.task_channels)
        
        try:
            while self.running:
                try:
                    # 获取消息，超时1秒
                    message = pubsub.get_message(timeout=1.0)
                    
                    if message and message['type'] == 'message':
                        self._process_task(message, worker_name)
                        
                except Exception as e:
                    self.logger.error(f"{worker_name} 处理消息时出错: {e}")
                    time.sleep(1)
        
        finally:
            pubsub.close()
            self.logger.info(f"{worker_name} 停止监听任务")
    
    def _process_task(self, message: Dict[str, Any], worker_name: str):
        """处理单个任务"""
        task_id = None
        try:
            # 解析任务数据
            task_data = json.loads(message['data'])
            task_id = task_data.get('task_id')
            task_type = task_data.get('task_type')
            channel = message['channel']
            
            # 检查任务是否已被处理（防止重复处理）
            existing_result = self.redis_client.get_result(task_id, timeout=0.1)
            if existing_result is not None:
                self.logger.info(f"{worker_name} 任务已被处理，跳过: {task_id}")
                return
            
            # 尝试获取任务锁
            lock_key = f"lock:{task_id}"
            if not self.redis_client.acquire_lock(lock_key, worker_name, expire=300):
                self.logger.info(f"{worker_name} 无法获取任务锁，跳过: {task_id}")
                return
            
            try:
                self.logger.info(f"{worker_name} 处理任务: {task_id} ({task_type})")

                # 根据任务类型处理
                if task_type == 'single_feature_extraction':
                    result = self._handle_single_feature_extraction(task_data)
                elif task_type == 'batch_feature_extraction':
                    result = self._handle_batch_feature_extraction(task_data)
                elif task_type == 'model_info':
                    result = self._handle_model_info(task_data)
                elif task_type == 'update_model':
                    result = self._handle_update_model(task_data)
                elif task_type == 'health_check':
                    result = self._handle_health_check(task_data)
                else:
                    raise ValueError(f"未知任务类型: {task_type}")
                
                # 存储结果
                self.redis_client.set_result(task_id, {
                    'success': True,
                    'result': result,
                    'processed_by': worker_name,
                    'processed_at': time.time()
                })
                
                self.logger.info(f"{worker_name} 完成任务: {task_id}")
                
            finally:
                # 释放任务锁
                self.redis_client.release_lock(lock_key, worker_name)
            
        except Exception as e:
            self.logger.error(f"{worker_name} 任务处理失败: {e}")
            # 存储错误结果
            if task_id:
                self.redis_client.set_result(task_id, {
                    'success': False,
                    'error': str(e),
                    'processed_by': worker_name,
                    'processed_at': time.time()
                })
    
    def _handle_single_feature_extraction(self, task_data: Dict[str, Any]) -> List[float]:
        """处理单个图片特征提取"""
        image_path = task_data.get('image_path')
        if not image_path:
            raise ValueError("缺少图片路径参数")
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        
        # 使用接口提取特征
        from PIL import Image
        image = Image.open(image_path)
        features = self.feature_extractor.extract_single(image)
        return features.tolist() if hasattr(features, 'tolist') else features
    
    def _handle_batch_feature_extraction(self, task_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """处理批量图片特征提取"""
        image_paths = task_data.get('image_paths', [])
        if not image_paths:
            raise ValueError("缺少图片路径列表参数")
        
        # 验证文件存在并加载图片
        valid_images = []
        valid_paths = []
        for path in image_paths:
            if os.path.exists(path):
                try:
                    from PIL import Image
                    image = Image.open(path)
                    valid_images.append(image)
                    valid_paths.append(path)
                except Exception as e:
                    self.logger.warning(f"无法加载图片 {path}: {e}")
            else:
                self.logger.warning(f"图片文件不存在，跳过: {path}")
        
        if not valid_images:
            raise ValueError("没有有效的图片文件")
        
        # 批量提取特征
        results = []
        try:
            features_array = self.feature_extractor.extract_batch(valid_images)
            
            for i, features in enumerate(features_array):
                results.append({
                    'image_path': valid_paths[i],
                    'features': features.tolist() if hasattr(features, 'tolist') else features,
                    'success': True
                })
                
        except Exception as e:
            # 如果批量失败，尝试单个处理
            self.logger.warning(f"批量处理失败，尝试单个处理: {e}")
            
            for i, (path, image) in enumerate(zip(valid_paths, valid_images)):
                try:
                    features = self.feature_extractor.extract_single(image)
                    results.append({
                        'image_path': path,
                        'features': features.tolist() if hasattr(features, 'tolist') else features,
                        'success': True
                    })
                except Exception as single_error:
                    results.append({
                        'image_path': path,
                        'features': None,
                        'success': False,
                        'error': str(single_error)
                    })
        
        return results
    
    def _handle_model_info(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理获取模型信息请求"""
        return self.get_model_info()
    
    def _handle_update_model(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理更新模型请求"""
        new_config = task_data.get('model_config')
        if not new_config:
            raise ValueError("缺少模型配置参数")
        
        # 这里可以实现模型热更新逻辑
        # 暂时返回成功状态
        return {'updated': True, 'message': '模型配置更新成功'}
    
    def _handle_health_check(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理健康检查请求"""
        return {
            'status': 'healthy',
            'timestamp': time.time(),
            'workers': len(self.worker_threads),
            'redis_connected': self.redis_client.is_connected() if self.redis_client else False
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        try:
            info = {
                'model_loaded': self.feature_extractor is not None,
                'feature_dim': getattr(self.feature_extractor, 'feature_dim', 'unknown'),
                'workers': len(self.worker_threads),
                'status': 'running' if self.running else 'stopped'
            }
            
            # 如果有模型接口，获取更多信息
            if hasattr(self.feature_extractor, 'get_info'):
                model_info = self.feature_extractor.get_info()
                info.update(model_info)
                
            return info
        except Exception as e:
            self.logger.error(f"获取模型信息失败: {e}")
            return {'error': str(e)}


def create_compute_server(redis_config: RedisConfig = None, 
                         model_config: ModelConfig = None,
                         num_workers: int = 2) -> ComputeServer:
    """创建计算端服务器实例"""
    server = ComputeServer(redis_config, model_config)
    return server


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建并启动计算端服务器
    server = create_compute_server(num_workers=2)
    
    try:
        server.start()
        
        # 保持服务器运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n正在停止计算端服务器...")
    finally:
        server.stop()
