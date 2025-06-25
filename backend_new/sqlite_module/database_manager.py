"""
数据库管理器实现
组合各个仓储接口，提供统一的数据库访问入口
"""

import sys
import os
from typing import Optional

# 添加上一层路径便于模块导入
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from _database_interface import DatabaseManagerInterface, DatasetRepositoryInterface, ImageRepositoryInterface
from sqlite_module.database import SQLiteDatabase
from sqlite_module.dataset_repository import SQLiteDatasetRepository
from sqlite_module.image_repository import SQLiteImageRepository


class SQLiteDatabaseManager(DatabaseManagerInterface):
    """SQLite数据库管理器"""
    
    def __init__(self, db_path: Optional[str] = None):
        self._db = SQLiteDatabase(db_path)
        self._dataset_repository = None
        self._image_repository = None
    
    def get_dataset_repository(self) -> DatasetRepositoryInterface:
        """获取数据集仓储"""
        if self._dataset_repository is None:
            self._dataset_repository = SQLiteDatasetRepository(self._db)
        return self._dataset_repository
    
    def get_image_repository(self) -> ImageRepositoryInterface:
        """获取图片仓储"""
        if self._image_repository is None:
            self._image_repository = SQLiteImageRepository(self._db)
        return self._image_repository
    
    def initialize(self) -> None:
        """初始化数据库"""
        self._db.create_tables()
    
    def close(self) -> None:
        """关闭数据库连接"""
        self._db.disconnect()
    
    def get_database(self) -> SQLiteDatabase:
        """获取底层数据库实例（用于高级操作）"""
        return self._db


# 全局数据库管理器实例
_db_manager = None


def get_database_manager(db_path: Optional[str] = None) -> SQLiteDatabaseManager:
    """获取数据库管理器单例"""
    global _db_manager
    if _db_manager is None:
        _db_manager = SQLiteDatabaseManager(db_path)
        _db_manager.initialize()
    return _db_manager


def close_database_manager():
    """关闭数据库管理器"""
    global _db_manager
    if _db_manager:
        _db_manager.close()
        _db_manager = None
