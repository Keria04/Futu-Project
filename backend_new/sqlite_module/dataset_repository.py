"""
数据集仓储实现类
负责数据集相关的数据库操作
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

# 添加上一层路径便于模块导入
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from _database_interface import DatasetRepositoryInterface
from sqlite_module.database import SQLiteDatabase


class SQLiteDatasetRepository(DatasetRepositoryInterface):
    """SQLite数据集仓储实现"""
    
    def __init__(self, db: SQLiteDatabase):
        self.db = db
    
    def create_dataset(self, name: str, description: str = "") -> int:
        """创建新数据集"""
        data = {
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        return self.db.insert_one("datasets", data)
    
    def get_dataset_by_id(self, dataset_id: int) -> Optional[Dict]:
        """根据ID获取数据集"""
        result = self.db.query_one("datasets", "*", where={"id": dataset_id})
        if result:
            return self._tuple_to_dataset_dict(result)
        return None
    
    def get_dataset_by_name(self, name: str) -> Optional[Dict]:
        """根据名称获取数据集"""
        result = self.db.query_one("datasets", "*", where={"name": name})
        if result:
            return self._tuple_to_dataset_dict(result)
        return None
    
    def get_all_datasets(self) -> List[Dict]:
        """获取所有数据集"""
        results = self.db.query_multi("datasets", "*", order_by="created_at DESC")
        datasets = []
        for row in results:
            datasets.append(self._tuple_to_dataset_dict(row))
        return datasets
    
    def update_dataset(self, dataset_id: int, data: Dict[str, Any]) -> bool:
        """更新数据集信息"""
        try:
            rows_affected = self.db.update("datasets", data, where={"id": dataset_id})
            return rows_affected > 0
        except Exception as e:
            print(f"更新数据集失败: {str(e)}")
            return False
    
    def delete_dataset(self, dataset_id: int) -> bool:
        """删除数据集"""
        try:
            rows_affected = self.db.delete("datasets", where={"id": dataset_id})
            return rows_affected > 0
        except Exception as e:
            print(f"删除数据集失败: {str(e)}")
            return False
    
    def get_dataset_stats(self, dataset_id: int) -> Dict:
        """获取数据集统计信息"""
        # 获取图片数量
        image_count_result = self.db.query_one(
            "images", 
            "COUNT(*) as count", 
            where={"dataset_id": dataset_id}
        )
        image_count = image_count_result[0] if image_count_result else 0
        
        # 获取总大小
        size_result = self.db.query_one(
            "images", 
            "SUM(file_size) as total_size", 
            where={"dataset_id": dataset_id}
        )
        total_size = size_result[0] if size_result and size_result[0] else 0
        
        return {
            "image_count": image_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2) if total_size else 0
        }
    
    def update_dataset_stats(self, dataset_id: int) -> bool:
        """更新数据集统计信息"""
        try:
            stats = self.get_dataset_stats(dataset_id)
            update_data = {
                "image_count": stats["image_count"],
                "size_bytes": stats["total_size_bytes"]
            }
            return self.update_dataset(dataset_id, update_data)
        except Exception as e:
            print(f"更新数据集统计信息失败: {str(e)}")
            return False
    
    def _tuple_to_dataset_dict(self, row: tuple) -> Dict:
        """将元组转换为数据集字典"""
        return {
            "id": row[0],
            "name": row[1],
            "description": row[2] if len(row) > 2 else "",
            "created_at": row[3] if len(row) > 3 else "",
            "last_rebuild": row[4] if len(row) > 4 else None,
            "image_count": row[5] if len(row) > 5 else 0,
            "size_bytes": row[6] if len(row) > 6 else 0
        }

# 为了向后兼容，提供别名
DatasetRepository = SQLiteDatasetRepository
