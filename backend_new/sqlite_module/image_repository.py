"""
图片仓储实现类
负责图片相关的数据库操作
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

# 添加上一层路径便于模块导入
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from _database_interface import ImageRepositoryInterface
from sqlite_module.database import SQLiteDatabase


class SQLiteImageRepository(ImageRepositoryInterface):
    """SQLite图片仓储实现"""
    
    def __init__(self, db: SQLiteDatabase):
        self.db = db
    
    def add_image(self, dataset_id: int, filename: str, file_path: str, 
                 file_size: int = 0, checksum: str = "") -> int:
        """添加图片到数据集"""
        data = {
            "dataset_id": dataset_id,
            "filename": filename,
            "file_path": file_path,
            "file_size": file_size,
            "checksum": checksum,
            "created_at": datetime.now().isoformat()
        }
        return self.db.insert_one("images", data)
    
    def get_image_by_id(self, image_id: int) -> Optional[Dict]:
        """根据ID获取图片信息"""
        result = self.db.query_one("images", "*", where={"id": image_id})
        if result:
            return self._tuple_to_image_dict(result)
        return None
    
    def get_images_by_dataset(self, dataset_id: int) -> List[Dict]:
        """获取数据集中的所有图片"""
        results = self.db.query_multi("images", "*", where={"dataset_id": dataset_id}, 
                                     order_by="created_at DESC")
        images = []
        for row in results:
            images.append(self._tuple_to_image_dict(row))
        return images
    
    def get_images_by_dataset_name(self, dataset_name: str) -> List[Dict]:
        """根据数据集名称获取图片"""        # 首先获取数据集ID
        dataset_result = self.db.query_one("datasets", "id", where={"name": dataset_name})
        if not dataset_result:
            return []
        
        dataset_id = dataset_result[0]
        return self.get_images_by_dataset(dataset_id)
    
    def update_image(self, image_id: int, data: Dict[str, Any]) -> bool:
        """更新图片信息"""
        try:
            # 添加调试信息
            print(f"正在更新图片 {image_id}，数据: {list(data.keys())}")
            
            rows_affected = self.db.update("images", data, where={"id": image_id})
            
            print(f"更新图片 {image_id}，影响行数: {rows_affected}")
            return rows_affected > 0
        except Exception as e:
            print(f"更新图片失败 - ID: {image_id}, 错误: {str(e)}")
            import traceback
            print(f"错误详情: {traceback.format_exc()}")
            return False
    
    def delete_image(self, image_id: int) -> bool:
        """删除图片"""
        try:
            rows_affected = self.db.delete("images", where={"id": image_id})
            return rows_affected > 0
        except Exception as e:
            print(f"删除图片失败: {str(e)}")
            return False
    
    def delete_images_by_dataset(self, dataset_id: int) -> int:
        """删除数据集中的所有图片"""
        try:
            return self.db.delete("images", where={"dataset_id": dataset_id})
        except Exception as e:
            print(f"删除数据集图片失败: {str(e)}")
            return 0
    
    def batch_add_images(self, dataset_id: int, image_list: List[Dict]) -> int:
        """批量添加图片"""
        try:
            current_time = datetime.now().isoformat()
            data_list = []
            
            for image_info in image_list:
                data = {
                    "dataset_id": dataset_id,
                    "filename": image_info.get("filename", ""),
                    "file_path": image_info.get("file_path", ""),
                    "file_size": image_info.get("file_size", 0),
                    "checksum": image_info.get("checksum", ""),
                    "created_at": current_time,
                    "metadata_json": image_info.get("metadata_json", None)
                }
                data_list.append(data)
            
            return self.db.insert_multi("images", data_list)
        except Exception as e:
            print(f"批量添加图片失败: {str(e)}")
            return 0
    
    def get_image_count_by_dataset(self, dataset_id: int) -> int:
        """获取数据集图片数量"""
        result = self.db.query_one("images", "COUNT(*) as count", where={"dataset_id": dataset_id})
        return result[0] if result else 0
    
    def search_images(self, dataset_id: Optional[int] = None, filename_pattern: Optional[str] = None,
                     limit: Optional[int] = None) -> List[Dict]:
        """搜索图片"""
        where_conditions = {}
        if dataset_id:
            where_conditions["dataset_id"] = dataset_id
        
        # 注意：这里的filename_pattern搜索需要使用LIKE，但当前接口不支持
        # 可以考虑扩展接口或在这里直接使用原始SQL
        results = self.db.query_multi("images", "*", where=where_conditions, 
                                     order_by="created_at DESC", limit=limit)
        images = []
        for row in results:
            image_dict = self._tuple_to_image_dict(row)
            # 如果有文件名模式匹配，在这里过滤
            if filename_pattern and filename_pattern.lower() not in image_dict["filename"].lower():
                continue
            images.append(image_dict)
        return images
    
    def _tuple_to_image_dict(self, row: tuple) -> Dict:
        """将元组转换为图片字典"""
        return {
            "id": row[0],
            "dataset_id": row[1],
            "filename": row[2],
            "file_path": row[3],
            "file_size": row[4] if len(row) > 4 else 0,
            "checksum": row[5] if len(row) > 5 else "",
            "created_at": row[6] if len(row) > 6 else "",
            "metadata_json": row[7] if len(row) > 7 else None,
            "feature_vector": row[8] if len(row) > 8 else None
        }

# 为了向后兼容，提供别名
ImageRepository = SQLiteImageRepository
