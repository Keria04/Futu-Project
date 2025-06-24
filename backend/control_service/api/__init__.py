"""
API路由初始化
"""
from .search_api import search_bp
from .index_api import index_bp
from .dataset_api import dataset_bp
from .image_api import image_bp

__all__ = ['search_bp', 'index_bp', 'dataset_bp', 'image_bp']
