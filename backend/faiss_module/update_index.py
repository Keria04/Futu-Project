from faiss_module.indexer import FaissIndexer
from config import config
import numpy as np

def update_index():
    # 加载新数据特征和 ID
    new_features = np.load(config.NEW_FEATURE_PATH).astype('float32')  # shape=(M, dim)
    new_ids = np.load(config.NEW_ID_PATH).astype('int64')              # shape=(M,)

    # 加载已有索引
    indexer = FaissIndexer(dim=config.VECTOR_DIM, index_path=config.INDEX_PATH)
    indexer.load_index()

    # 更新索引
    indexer.update_index(new_features, new_ids)

    # 保存新索引
    indexer.save_index()
    print("索引已更新并保存。")