"""
索引服务 - 建造者模式 + 观察者模式
负责索引构建的业务逻辑
"""
import os
import sys
import threading
import time
from typing import List, Dict, Any, Optional, Callable
from abc import ABC, abstractmethod
from PIL import Image
import base64
from io import BytesIO
import numpy as np

# 添加路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from shared import task_manager, TaskObserver, TaskResult, MessageProtocol
from .database_service import database_service
from control_service.faiss_module.indexer import FaissIndexer


class IndexBuildObserver(ABC):
    """索引构建观察者接口"""
    
    @abstractmethod
    def on_progress_update(self, dataset_name: str, progress: float, message: str):
        """进度更新回调"""
        pass
    
    @abstractmethod
    def on_build_completed(self, dataset_name: str, success: bool, message: str):
        """构建完成回调"""
        pass


class ProgressFileObserver(IndexBuildObserver):
    """文件进度观察者"""
    
    def __init__(self, progress_file: str):
        self.progress_file = progress_file
    
    def on_progress_update(self, dataset_name: str, progress: float, message: str):
        """更新进度文件"""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                f.write(f"{progress:.2f}% - {message}\n")
        except Exception as e:
            print(f"更新进度文件失败: {e}")
    
    def on_build_completed(self, dataset_name: str, success: bool, message: str):
        """写入完成状态"""
        try:
            with open(self.progress_file, 'a', encoding='utf-8') as f:
                if success:
                    f.write("100.00% - 索引构建完成\n")
                else:
                    f.write(f"ERROR - {message}\n")
        except Exception as e:
            print(f"写入完成状态失败: {e}")


class IndexBuilder:
    """索引构建器"""
    
    def __init__(self, dataset_dir: str, dataset_name: str, distributed: bool = False):
        self.dataset_dir = dataset_dir
        self.dataset_name = dataset_name
        self.distributed = distributed
        self.observers: List[IndexBuildObserver] = []
        self.vector_dim = 2048  # 默认特征维度
    
    def add_observer(self, observer: IndexBuildObserver):
        """添加观察者"""
        if observer not in self.observers:
            self.observers.append(observer)
    
    def remove_observer(self, observer: IndexBuildObserver):
        """移除观察者"""
        if observer in self.observers:
            self.observers.remove(observer)
    
    def _notify_progress(self, progress: float, message: str):
        """通知进度更新"""
        for observer in self.observers:
            try:
                observer.on_progress_update(self.dataset_name, progress, message)
            except Exception as e:
                print(f"通知观察者失败: {e}")
    
    def _notify_completed(self, success: bool, message: str):
        """通知构建完成"""
        for observer in self.observers:
            try:
                observer.on_build_completed(self.dataset_name, success, message)
            except Exception as e:
                print(f"通知观察者失败: {e}")
    
    def build(self, progress_file: Optional[str] = None):
        """构建索引"""
        if progress_file:
            file_observer = ProgressFileObserver(progress_file)
            self.add_observer(file_observer)
        
        try:
            self._notify_progress(0, "开始构建索引...")
            
            # 检查数据集目录
            if not os.path.exists(self.dataset_dir):
                raise Exception(f"数据集目录不存在: {self.dataset_dir}")
            
            # 获取图片列表
            image_files = self._get_image_files()
            if not image_files:
                raise Exception("数据集中没有找到图片文件")
            
            self._notify_progress(10, f"找到 {len(image_files)} 张图片")
            
            # 确保数据集存在于数据库中
            dataset_id = database_service.get_or_create_dataset(self.dataset_name)
            
            # 提取特征
            features, ids = self._extract_features(image_files, dataset_id)
            self._notify_progress(70, "特征提取完成")
            
            # 构建索引
            self._build_faiss_index(features, ids)
            self._notify_progress(100, "索引构建完成")
            
            self._notify_completed(True, "索引构建成功")
            
        except Exception as e:
            error_msg = f"索引构建失败: {str(e)}"
            print(error_msg)
            self._notify_completed(False, error_msg)
            raise
    
    def _get_image_files(self) -> List[str]:
        """获取图片文件列表"""
        supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif')
        image_files = []
        
        for filename in os.listdir(self.dataset_dir):
            if filename.lower().endswith(supported_formats):
                image_files.append(filename)
        
        return sorted(image_files)
    
    def _extract_features(self, image_files: List[str], dataset_id: int):
        """提取特征向量"""
        features_list = []
        ids_list = []
        
        if self.distributed:
            # 分布式特征提取
            features_list, ids_list = self._extract_features_distributed(image_files, dataset_id)
        else:
            # 本地特征提取
            features_list, ids_list = self._extract_features_local(image_files, dataset_id)
        
        return np.array(features_list, dtype=np.float32), np.array(ids_list, dtype=np.int64)
    
    def _extract_features_local(self, image_files: List[str], dataset_id: int):
        """本地特征提取"""
        features_list = []
        ids_list = []
        total_files = len(image_files)
        
        for i, filename in enumerate(image_files):
            try:
                # 加载图片
                image_path = os.path.join(self.dataset_dir, filename)
                with Image.open(image_path) as img:
                    # 转换为base64
                    buffer = BytesIO()
                    img.convert('RGB').save(buffer, format='JPEG')
                    img_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                # 提交特征提取任务
                task_id = task_manager.submit_feature_extraction_task(img_data)
                result = task_manager.wait_for_task(task_id, timeout=30)
                
                if result and result.status.value == 'completed':
                    features = result.result
                    
                    # 添加图片到数据库
                    image_id = database_service.add_image(
                        dataset_id=dataset_id,
                        filename=filename,
                        file_path=image_path,
                        file_size=os.path.getsize(image_path)
                    )
                    
                    features_list.append(features)
                    ids_list.append(image_id)
                else:
                    print(f"特征提取失败: {filename}")
                
                # 更新进度
                progress = 10 + (i + 1) / total_files * 60
                self._notify_progress(progress, f"已处理 {i + 1}/{total_files} 张图片")
                
            except Exception as e:
                print(f"处理图片 {filename} 时出错: {e}")
                continue
        
        return features_list, ids_list
    
    def _extract_features_distributed(self, image_files: List[str], dataset_id: int):
        """分布式特征提取"""
        # TODO: 实现真正的分布式特征提取
        # 当前版本回退到本地处理
        return self._extract_features_local(image_files, dataset_id)
    
    def _build_faiss_index(self, features: np.ndarray, ids: np.ndarray):
        """构建Faiss索引"""
        index_path = os.path.join("data/indexes", f"{self.dataset_name}.index")
        
        # 创建索引器
        indexer = FaissIndexer(
            dim=features.shape[1],
            index_path=index_path,
            use_IVF=True
        )
        
        # 构建索引
        indexer.build_index(features, ids)
        
        # 保存索引
        indexer.save_index()


class IndexService:
    """索引服务"""
    
    def __init__(self):
        self.builders: Dict[str, IndexBuilder] = {}
        self.build_threads: Dict[str, threading.Thread] = {}
    
    def build_dataset_index(self, dataset_name: str, dataset_dir: str, 
                          distributed: bool = False, progress_file: Optional[str] = None) -> bool:
        """构建数据集索引"""
        if dataset_name in self.builders:
            return False  # 已在构建中
        
        builder = IndexBuilder(dataset_dir, dataset_name, distributed)
        self.builders[dataset_name] = builder
        
        def build_task():
            try:
                builder.build(progress_file)
            finally:
                # 清理
                if dataset_name in self.builders:
                    del self.builders[dataset_name]
                if dataset_name in self.build_threads:
                    del self.build_threads[dataset_name]
        
        thread = threading.Thread(target=build_task)
        self.build_threads[dataset_name] = thread
        thread.start()
        
        return True
    
    def get_build_status(self, dataset_name: str) -> str:
        """获取构建状态"""
        if dataset_name in self.builders:
            return "building"
        elif dataset_name in self.build_threads and self.build_threads[dataset_name].is_alive():
            return "building"
        else:
            # 检查索引文件是否存在
            index_path = os.path.join("data/indexes", f"{dataset_name}.index")
            if os.path.exists(index_path):
                return "completed"
            else:
                return "not_started"


# 全局索引服务实例
index_service = IndexService()
