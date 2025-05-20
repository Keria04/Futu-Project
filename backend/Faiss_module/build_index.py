"""
build_index.py
构建 Faiss 图像索引。加载特征文件，生成索引文件和ID映射文件。
"""
import numpy as np
import os
import sys
# 添加项目根路径，便于导入 config 和模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from config import config
from faiss_module.indexer import FaissIndexer

def build_index():
    # 1. 加载特征向量
    if not os.path.exists(config.FEATURE_PATH):
        raise FileNotFoundError(f"特征文件 {config.FEATURE_PATH} 不存在。")
    features = np.load(config.FEATURE_PATH).astype('float32')
    print(f"已加载特征向量，shape={features.shape}")
    # 2. 加载或生成 ID
    if os.path.exists(config.ID_PATH):
        ids = np.load(config.ID_PATH).astype('int64')
        print(f"已加载 ID，数量 = {len(ids)}")
    else:
        ids = np.arange(len(features)).astype('int64')
        np.save(config.ID_PATH, ids)
        print(f"自动生成 ID 并保存至 {config.ID_PATH}")
    # 3. 构建索引
    indexer = FaissIndexer(dim=config.VECTOR_DIM, index_path=config.INDEX_PATH, nlist=config.N_LIST)
    indexer.build_index(features, ids)
    # 4. 保存索引
    indexer.save_index()
    print(f"索引已保存至 {config.INDEX_PATH}")
if __name__ == "__main__":
    main()