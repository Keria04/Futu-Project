"""
faiss_module - 独立的Faiss索引模块

这个模块提供了Faiss索引的构建、搜索、更新等功能，不依赖外部配置文件。
包含：
- FaissConfig: 内部配置类
- FaissIndexer: 索引器类
- build_index: 构建索引函数
- search_index: 搜索索引函数
- update_index: 更新索引函数
- repeated_search: 重复搜索函数
"""

import os

try:
    from .faiss_config import FaissConfig, default_config
    from .indexer import FaissIndexer
    from .build_index import build_index
    from .search_index import search_index
    from .update_index import update_index
    from .repeated_search import repeated_search
    from .faiss_utils.similarity_utils import distance_to_similarity_percent
    
    __all__ = [
        'FaissConfig',
        'default_config',
        'FaissIndexer',
        'build_index',
        'search_index',
        'update_index',
        'repeated_search',
        'distance_to_similarity_percent'
    ]
except ImportError as e:
    print(f"Faiss模块导入失败: {e}")
    __all__ = []


def create_faiss_config(base_dir=None, vector_dim=2048, similarity_sigma=10.0):
    """
    便利函数：创建Faiss配置实例
    
    :param base_dir: 项目根目录，如果不提供则自动推导
    :param vector_dim: 特征向量维度
    :param similarity_sigma: 相似度转换参数
    :return: FaissConfig 实例
    """
    config = FaissConfig()
    if base_dir:
        config.BASE_DIR = base_dir
        # 重新计算相关路径
        config.FEATURE_PATH = os.path.join(base_dir, "data", "features.npy")
        config.ID_PATH = os.path.join(base_dir, "data", "ids.npy")
        config.INDEX_FOLDER = os.path.join(base_dir, "data", "indexes")
        config.NEW_FEATURE_PATH = os.path.join(base_dir, "data", "new_features.npy")
        config.NEW_ID_PATH = os.path.join(base_dir, "data", "new_ids.npy")
        config.UPLOAD_FOLDER = os.path.join(base_dir, 'data', 'uploads')
        config.DATASET_DIR = os.path.join(base_dir, 'datasets')
    
    config.VECTOR_DIM = vector_dim
    config.SIMILARITY_SIGMA = similarity_sigma
    
    return config


def create_indexer(dim, index_path, use_IVF=True):
    """
    便利函数：创建Faiss索引器实例
    
    :param dim: 特征维度
    :param index_path: 索引文件路径
    :param use_IVF: 是否使用IVF
    :return: FaissIndexer 实例
    """
    return FaissIndexer(dim=dim, index_path=index_path, use_IVF=use_IVF)
