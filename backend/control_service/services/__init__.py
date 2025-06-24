"""
控制端服务层初始化
"""
# 延迟导入避免循环导入问题
try:
    from .database_service import database_service
except ImportError:
    database_service = None

try:
    from .search_service import search_service, SearchService
except ImportError:
    search_service = None
    SearchService = None

try:
    from .index_service import index_service, IndexService
except ImportError:
    index_service = None
    IndexService = None

__all__ = [
    'database_service',
    'search_service',
    'SearchService',
    'index_service',
    'IndexService'
]
