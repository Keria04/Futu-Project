from .indexer import FaissIndexer
from .faiss_config import default_config
import numpy as np

def update_index(index_path=None, config=None):
    """
    更新Faiss索引
    
    :param index_path: 索引文件路径，如果不提供则从config获取
    :param config: 可选的配置对象，如果不提供则使用默认配置
    """
    if config is None:
        config = default_config
    
    # 加载新数据特征和 ID
    new_features = np.load(config.new_feature_path).astype('float32')  # shape=(M, dim)
    new_ids = np.load(config.new_id_path).astype('int64')              # shape=(M,)

    # 如果没有指定index_path，使用配置中的路径
    if index_path is None:
        index_path = config.index_folder  # 这里可能需要具体的索引文件名

    # 加载已有索引
    indexer = FaissIndexer(dim=config.vector_dim, index_path=index_path, use_IVF=True)
    indexer.load_index()

    # 更新索引
    indexer.update_index(new_features, new_ids)

    # 保存新索引
    indexer.save_index()
    print("索引已更新并保存。")