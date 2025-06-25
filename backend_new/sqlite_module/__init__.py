"""
SQLite模块初始化文件
提供统一的数据库访问接口
"""

# 导入主要接口
from .database_manager import get_database_manager, close_database_manager
from .database import SQLiteDatabase
from .dataset_repository import SQLiteDatasetRepository
from .image_repository import SQLiteImageRepository
from .query import (
    query_one, query_multi, 
    get_dataset_id, get_datasets, get_image_by_id, 
    get_images_by_dataset, get_images_by_dataset_id,
    get_dataset_by_name, get_dataset_by_id
)
from .modify import (
    insert_one, insert_multi, update, delete,
    create_dataset, add_image_to_dataset, batch_add_images,
    update_dataset, delete_dataset, delete_image, update_dataset_stats
)
from .schema import create_tables, initialize_database

# 为了向后兼容，提供简化的接口
def get_db():
    """获取数据库管理器（简化接口）"""
    return get_database_manager()

def init_db():
    """初始化数据库（简化接口）"""
    initialize_database()

# 公开的API接口
__all__ = [
    # 核心管理器
    'get_database_manager',
    'close_database_manager',
    'get_db',
    'init_db',
    
    # 数据库类
    'SQLiteDatabase',
    'SQLiteDatasetRepository', 
    'SQLiteImageRepository',
    
    # 查询函数
    'query_one',
    'query_multi',
    'get_dataset_id',
    'get_datasets',
    'get_image_by_id',
    'get_images_by_dataset',
    'get_images_by_dataset_id',
    'get_dataset_by_name',
    'get_dataset_by_id',
    
    # 修改函数
    'insert_one',
    'insert_multi',
    'update',
    'delete',
    'create_dataset',
    'add_image_to_dataset',
    'batch_add_images',
    'update_dataset',
    'delete_dataset',
    'delete_image',
    'update_dataset_stats',
    
    # 初始化函数
    'create_tables',
    'initialize_database'
]
