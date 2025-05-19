import os
import sys
import numpy as np
# 添加项目根路径，便于导入 config 和模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from config import faiss_config
from indexer import FaissIndexer
def search_index(query_feature: np.ndarray, top_k=5):
    """
    使用 FAISS 对给定特征向量进行搜索，返回 top_k 个最相似图像的编号（ID）。
    参数:
        query_feature (np.ndarray): 查询图像的特征向量，形状应为 (dim,) 或 (1, dim)
        top_k (int): 返回最相似的结果数量，默认 5
    返回:
        List[int]: 最相似图像的编号（ID）
    """
    # 确保 query_feature 是二维形状 (1, dim)
    if query_feature.ndim == 1:
        query_feature = query_feature.reshape(1, -1)
    elif query_feature.ndim != 2:
        raise ValueError("query_feature 必须是 1 维或 2 维 numpy 数组")
    dim = faiss_config.VECTOR_DIM
    # 初始化索引器并加载索引
    indexer = FaissIndexer(
        dim=dim,
        index_path=faiss_config.INDEX_PATH,
        nlist=faiss_config.N_LIST
    )
    indexer.load_index()
    distances, indices = indexer.search(query_feature.astype('float32'), top_k)
    return indices[0].tolist()
# 示例用法
if __name__ == "__main__":
    # 从文件加载示例特征，调用函数测试
    example_feature = np.load(os.path.join(faiss_config.FEATURE_DIR, "query.npy"))
    result_ids = search_by_feature(example_feature, top_k=5)
    print("最相似图像编号列表：", result_ids)