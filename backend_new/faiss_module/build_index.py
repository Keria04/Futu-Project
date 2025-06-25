"""
build_index.py
构建 Faiss 图像索引。接收特征数组和ID，保存索引文件至指定目录。
"""
import numpy as np
import os
import faiss
from .faiss_config import default_config
from .indexer import FaissIndexer

def build_index(features: np.ndarray, ids: np.ndarray, name: str, config=None):
    """
    构建Faiss索引
    
    :param features: 特征数组
    :param ids: ID数组
    :param name: 索引名称
    :param config: 可选的配置对象，如果不提供则使用默认配置
    """
    if config is None:
        config = default_config
    
    # 1. 参数检查
    if features is None or ids is None:
        raise ValueError("features 和 ids 不能为 None。")
    if len(features) != len(ids):
        raise ValueError("features 和 ids 的长度必须一致。")

    print(f"接收的特征 shape = {features.shape}, ID 数量 = {len(ids)}")

    # 2. 构建 index 路径
    os.makedirs(config.index_folder, exist_ok=True)
    index_path = os.path.join(config.index_folder, name)

    # 3. 构建索引器并生成索引
    indexer = FaissIndexer(dim=config.vector_dim, index_path=index_path, use_IVF=True)
    indexer.build_index(features.astype("float32"), ids.astype("int64"))

    # 4. 保存索引test
    indexer.save_index()
    print(f"索引已保存至 {index_path}")