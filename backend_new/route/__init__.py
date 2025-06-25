"""
路由模块初始化文件
"""

# 导入所有蓝图
from .index_routes import index_bp
from .search_routes import search_bp
from .dataset_routes import dataset_bp
from .duplicate_routes import duplicate_bp
from .static_routes import static_bp

__all__ = [
    'index_bp',
    'search_bp', 
    'dataset_bp',
    'duplicate_bp',
    'static_bp'
]
