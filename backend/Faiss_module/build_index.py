"""
build_index.py
构建 Faiss 图像索引。接收特征数组和ID，保存索引文件至 config.INDEX_FOLDER 指定目录。
"""
import numpy as np
import os
import sys
import faiss

# 添加项目根路径，便于导入 config 和模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from config import config
from faiss_module.indexer import FaissIndexer

def build_index(features: np.ndarray, ids: np.ndarray, name: str):
    # 1. 参数检查
    if features is None or ids is None:
        raise ValueError("features 和 ids 不能为 None。")
    if len(features) != len(ids):
        raise ValueError("features 和 ids 的长度必须一致。")

    print(f"接收的特征 shape = {features.shape}, ID 数量 = {len(ids)}")

    # 2. 构建 index 路径
    os.makedirs(config.INDEX_FOLDER, exist_ok=True)
    index_path = os.path.join(config.INDEX_FOLDER, name)

    # 3. 构建索引器并生成索引
    indexer = FaissIndexer(dim=config.VECTOR_DIM, index_path=index_path, use_IVF=True)
    indexer.build_index(features.astype("float32"), ids.astype("int64"))

    # 4. 保存索引
    indexer.save_index()
    print(f"索引已保存至 {index_path}")