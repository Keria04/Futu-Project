"""
数据库服务 - 单例模式
负责数据库操作的业务逻辑
"""
import os
import sys
from typing import List, Dict, Any, Optional
import sqlite3

# 添加路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from control_service.database import Database


class DatabaseService:
    """数据库服务 - 单例模式"""
    
    _instance = None
    _database = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._database = Database()
            self._initialized = True
    
    @property
    def database(self):
        """获取数据库实例"""
        return self._database
    
    def get_datasets(self) -> List[Dict[str, Any]]:
        """获取所有数据集"""
        try:
            query = "SELECT id, name, description FROM datasets"
            results = self._database.execute_query(query)
            return [
                {
                    "id": str(row[0]),
                    "name": row[1],
                    "description": row[2] or f"数据集 {row[1]}"
                }
                for row in results
            ]
        except Exception as e:
            print(f"获取数据集失败: {e}")
            return []
    
    def get_dataset_id(self, dataset_name: str) -> Optional[int]:
        """根据数据集名称获取ID"""
        try:
            query = "SELECT id FROM datasets WHERE name = ?"
            results = self._database.execute_query(query, (dataset_name,))
            return results[0][0] if results else None
        except Exception as e:
            print(f"获取数据集ID失败: {e}")
            return None
    
    def get_dataset_name_by_id(self, dataset_id: int) -> Optional[str]:
        """根据数据集ID获取名称"""
        try:
            query = "SELECT name FROM datasets WHERE id = ?"
            results = self._database.execute_query(query, (dataset_id,))
            return results[0][0] if results else None
        except Exception as e:
            print(f"获取数据集名称失败: {e}")
            return None
    
    def get_images_by_dataset(self, dataset_name: str) -> List[Dict[str, Any]]:
        """获取指定数据集的所有图片"""
        try:
            query = """
                SELECT i.id, i.filename, i.file_path, i.description 
                FROM images i 
                JOIN datasets d ON i.dataset_id = d.id 
                WHERE d.name = ?
            """
            results = self._database.execute_query(query, (dataset_name,))
            return [
                {
                    "id": row[0],
                    "filename": row[1],
                    "file_path": row[2],
                    "description": row[3],
                    "dataset": dataset_name
                }
                for row in results
            ]
        except Exception as e:
            print(f"获取数据集图片失败: {e}")
            return []
    
    def get_image_by_id(self, image_id: int) -> Optional[Dict[str, Any]]:
        """根据图片ID获取图片信息"""
        try:
            query = """
                SELECT i.id, i.filename, i.file_path, i.description, d.name as dataset
                FROM images i 
                JOIN datasets d ON i.dataset_id = d.id 
                WHERE i.id = ?
            """
            results = self._database.execute_query(query, (image_id,))
            if results:
                row = results[0]
                return {
                    "id": row[0],
                    "filename": row[1],
                    "file_path": row[2],
                    "description": row[3] or {},
                    "dataset": row[4]
                }
            return None
        except Exception as e:
            print(f"获取图片信息失败: {e}")
            return None
    
    def add_dataset(self, name: str, description: str = None) -> int:
        """添加数据集"""
        try:
            query = "INSERT INTO datasets (name, description) VALUES (?, ?)"
            return self._database.execute_update(query, (name, description))
        except Exception as e:
            print(f"添加数据集失败: {e}")
            return None
    
    def add_image(self, filename: str, file_path: str, dataset_id: int, 
                  description: str = None) -> int:
        """添加图片"""
        try:
            query = "INSERT INTO images (filename, file_path, dataset_id, description) VALUES (?, ?, ?, ?)"
            return self._database.execute_update(query, (filename, file_path, dataset_id, description))
        except Exception as e:
            print(f"添加图片失败: {e}")
            return None
    
    def update_image_description(self, image_id: int, description: str) -> bool:
        """更新图片描述"""
        try:
            query = "UPDATE images SET description = ? WHERE id = ?"
            result = self._database.execute_update(query, (description, image_id))
            return result is not None
        except Exception as e:
            print(f"更新图片描述失败: {e}")
            return False
    
    def delete_image(self, image_id: int) -> bool:
        """删除图片"""
        try:
            query = "DELETE FROM images WHERE id = ?"
            result = self._database.execute_update(query, (image_id,))
            return result is not None
        except Exception as e:
            print(f"删除图片失败: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self._database:
            self._database.close()
    
    def get_or_create_dataset(self, dataset_name: str) -> int:
        """获取或创建数据集，返回数据集ID"""
        try:
            # 首先尝试获取现有数据集
            dataset_id = self.get_dataset_id(dataset_name)
            if dataset_id is not None:
                return dataset_id
            
            # 如果不存在，创建新数据集
            description = f"数据集 {dataset_name}"
            dataset_id = self.add_dataset(dataset_name, description)
            return dataset_id
            
        except Exception as e:
            print(f"获取或创建数据集失败: {e}")
            raise


# 全局数据库服务实例
database_service = DatabaseService()
