"""
向后兼容适配器
提供与旧版本数据库接口兼容的API，让现有代码无需修改即可使用新的数据库系统
"""

import sys
import os
from typing import Dict, List, Optional, Any, Tuple

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlite_module.database_manager import get_database_manager


class LegacyDatabaseAdapter:
    """兼容旧版本数据库接口的适配器"""
    
    def __init__(self):
        self._db_manager = get_database_manager()
        self._db = self._db_manager.get_database()
    
    def query_one(self, table: str, columns: str = '*', where: Optional[Dict] = None) -> Optional[Tuple]:
        """查询单条记录 - 兼容旧接口"""
        return self._db.query_one(table, columns, where)
    
    def query_multi(self, table: str, columns: str = '*', where: Optional[Dict] = None, 
                   order_by: Optional[str] = None, limit: Optional[int] = None) -> List[Tuple]:
        """查询多条记录 - 兼容旧接口"""
        return self._db.query_multi(table, columns, where, order_by, limit)
    
    def get_dataset_id(self, dataset_name: str) -> Optional[int]:
        """根据数据集名称获取ID - 兼容旧接口"""
        dataset_repo = self._db_manager.get_dataset_repository()
        dataset = dataset_repo.get_dataset_by_name(dataset_name)
        return dataset["id"] if dataset else None
    
    def get_datasets(self) -> List[Dict]:
        """获取所有数据集 - 兼容旧接口"""
        dataset_repo = self._db_manager.get_dataset_repository()
        datasets = dataset_repo.get_all_datasets()
        
        # 转换为旧格式
        legacy_datasets = []
        for dataset in datasets:
            legacy_datasets.append({
                "id": dataset["id"],
                "name": dataset["name"],
                "description": dataset.get("description", ""),
                "created_at": dataset.get("created_at", "")
            })
        return legacy_datasets
    
    def get_image_by_id(self, image_id: int) -> Optional[Dict]:
        """根据图片ID获取图片信息 - 兼容旧接口"""
        image_repo = self._db_manager.get_image_repository()
        image = image_repo.get_image_by_id(image_id)
        if image:
            # 转换为旧格式
            return {
                "id": image["id"],
                "dataset_id": image["dataset_id"],
                "filename": image["filename"],
                "file_path": image["file_path"],
                "file_size": image.get("file_size", 0),
                "checksum": image.get("checksum", ""),
                "created_at": image.get("created_at", "")
            }
        return None
    
    def get_images_by_dataset(self, dataset_name: str) -> List[Dict]:
        """获取数据集中的所有图片 - 兼容旧接口"""
        # 首先获取数据集ID
        dataset_id = self.get_dataset_id(dataset_name)
        if dataset_id is None:
            return []
        
        image_repo = self._db_manager.get_image_repository()
        images = image_repo.get_images_by_dataset(dataset_id)
        
        # 转换为旧格式
        legacy_images = []
        for image in images:
            legacy_images.append({
                "id": image["id"],
                "dataset_id": image["dataset_id"],
                "filename": image["filename"],
                "file_path": image["file_path"],
                "file_size": image.get("file_size", 0),
                "checksum": image.get("checksum", ""),
                "created_at": image.get("created_at", "")
            })
        return legacy_images


# 创建全局适配器实例
_legacy_adapter = None


def get_legacy_adapter() -> LegacyDatabaseAdapter:
    """获取兼容适配器单例"""
    global _legacy_adapter
    if _legacy_adapter is None:
        _legacy_adapter = LegacyDatabaseAdapter()
    return _legacy_adapter


# 提供与旧版本完全兼容的函数接口
def query_one(table: str, columns: str = '*', where: Optional[Dict] = None) -> Optional[Tuple]:
    """查询单条记录 - 兼容函数"""
    adapter = get_legacy_adapter()
    return adapter.query_one(table, columns, where)


def query_multi(table: str, columns: str = '*', where: Optional[Dict] = None, 
               order_by: Optional[str] = None, limit: Optional[int] = None) -> List[Tuple]:
    """查询多条记录 - 兼容函数"""
    adapter = get_legacy_adapter()
    return adapter.query_multi(table, columns, where, order_by, limit)


def get_dataset_id(dataset_name: str) -> Optional[int]:
    """根据数据集名称获取ID - 兼容函数"""
    adapter = get_legacy_adapter()
    return adapter.get_dataset_id(dataset_name)


def get_datasets() -> List[Dict]:
    """获取所有数据集 - 兼容函数"""
    adapter = get_legacy_adapter()
    return adapter.get_datasets()


def get_image_by_id(image_id: int) -> Optional[Dict]:
    """根据图片ID获取图片信息 - 兼容函数"""
    adapter = get_legacy_adapter()
    return adapter.get_image_by_id(image_id)


def get_images_by_dataset(dataset_name: str) -> List[Dict]:
    """获取数据集中的所有图片 - 兼容函数"""
    adapter = get_legacy_adapter()
    return adapter.get_images_by_dataset(dataset_name)
