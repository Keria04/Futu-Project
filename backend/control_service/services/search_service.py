"""
搜索服务 - 策略模式 + 工厂模式
负责图像搜索的业务逻辑
"""
import os
import base64
from io import BytesIO
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
import numpy as np
from abc import ABC, abstractmethod

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from shared import task_manager, MessageProtocol
from .database_service import database_service

# 导入搜索模块
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
try:
    from control_service.faiss_module.search_index import search_similar_images
except ImportError:
    # 如果模块不存在，创建一个模拟函数
    def search_similar_images(dataset_name, query_features, top_k=10):
        return []


class SearchStrategy(ABC):
    """搜索策略接口"""
    
    @abstractmethod
    def search(self, query_image: Image.Image, dataset_names: List[str], 
               crop_info: Optional[Tuple[int, int, int, int]] = None) -> List[Dict[str, Any]]:
        """执行搜索"""
        pass


class LocalSearchStrategy(SearchStrategy):
    """本地搜索策略"""
    
    def search(self, query_image: Image.Image, dataset_names: List[str], 
               crop_info: Optional[Tuple[int, int, int, int]] = None) -> List[Dict[str, Any]]:
        """在本地执行搜索"""
        # 图片预处理
        if crop_info and all(crop_info):
            x, y, w, h = crop_info
            query_image = query_image.crop((x, y, x + w, y + h))
        
        # 转换为base64用于特征提取
        buffer = BytesIO()
        query_image.save(buffer, format='JPEG')
        img_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # 提交特征提取任务
        task_id = task_manager.submit_feature_extraction_task(img_data)
        
        # 等待结果
        result = task_manager.wait_for_task(task_id, timeout=30)
        if not result or result.status.value != 'completed':
            raise Exception("特征提取失败")
        
        query_features = np.array(result.result, dtype=np.float32)
        
        # 在指定数据集中搜索
        search_results = []
        for dataset_name in dataset_names:
            try:
                results = search_similar_images(dataset_name, query_features, top_k=10)
                for img_id, similarity in results:                    # 从数据库获取图片信息
                    img_info = database_service.get_image_by_id(img_id)
                    if img_info:
                        search_results.append({
                            'idx': img_id,
                            'fname': img_info.get('filename', ''),
                            'img_url': f"/api/image/{dataset_name}/{img_id}",
                            'dataset': dataset_name,
                            'similarity': float(similarity * 100),  # 转换为百分比
                            'description': img_info.get('description', {})
                        })
            except Exception as e:
                print(f"搜索数据集 {dataset_name} 时出错: {e}")
                continue
        
        # 按相似度排序
        search_results.sort(key=lambda x: x['similarity'], reverse=True)
        return search_results[:20]  # 返回top 20


class DistributedSearchStrategy(SearchStrategy):
    """分布式搜索策略"""
    
    def search(self, query_image: Image.Image, dataset_names: List[str], 
               crop_info: Optional[Tuple[int, int, int, int]] = None) -> List[Dict[str, Any]]:
        """分布式搜索 - 当前版本回退到本地搜索"""
        # TODO: 实现真正的分布式搜索
        local_strategy = LocalSearchStrategy()
        return local_strategy.search(query_image, dataset_names, crop_info)


class SearchServiceFactory:
    """搜索服务工厂"""
    
    @staticmethod
    def create_search_strategy(distributed: bool = False) -> SearchStrategy:
        """创建搜索策略"""
        if distributed:
            return DistributedSearchStrategy()
        else:
            return LocalSearchStrategy()


class SearchService:
    """搜索服务"""
    
    def __init__(self, distributed: bool = False):
        self.search_strategy = SearchServiceFactory.create_search_strategy(distributed)
    
    def search_image(self, query_image: Image.Image, dataset_names: List[str], 
                    crop_info: Optional[Tuple[int, int, int, int]] = None) -> List[Dict[str, Any]]:
        """搜索相似图像"""
        if not dataset_names:
            raise ValueError("数据集名称不能为空")
        
        return self.search_strategy.search(query_image, dataset_names, crop_info)
    
    def search_repeated_images(self, index_id: int, threshold: int = 95, 
                              deduplicate: bool = False) -> Dict[str, Any]:
        """搜索重复图像"""
        # 根据index_id获取数据集名称
        dataset_name = database_service.get_dataset_name_by_id(index_id)
        if not dataset_name:
            raise ValueError("数据集不存在")
        
        # 导入重复搜索模块
        try:
            from control_service.faiss_module.repeated_search import find_repeated_images
        except ImportError:
            # 如果模块不存在，创建一个模拟函数
            def find_repeated_images(dataset_name, threshold=0.95):
                return []
        
        try:
            repeated_groups = find_repeated_images(dataset_name, threshold=threshold/100.0)
            
            # 转换格式以匹配API文档
            groups = []
            total_duplicates = 0
            
            for group in repeated_groups:
                if len(group) > 1:  # 只有超过1张图片才算重复组
                    groups.append(group)
                    total_duplicates += len(group)
            
            result = {
                "groups": groups,
                "total_groups": len(groups),
                "total_duplicates": total_duplicates
            }
            
            # 如果需要去重，执行去重操作
            if deduplicate:
                # TODO: 实现去重逻辑
                result["deduplicated"] = False
                result["message"] = "去重功能尚未实现"
            
            return result
            
        except Exception as e:
            print(f"搜索数据集 {dataset_name} 的重复图像时出错: {e}")
            return {
                "groups": [],
                "total_groups": 0,
                "total_duplicates": 0
            }


# 全局搜索服务实例
search_service = SearchService()
