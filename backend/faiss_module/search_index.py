import os
import sys
import numpy as np
import heapq

# 添加项目根路径，便于导入 config 和模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from config import config
from faiss_module.indexer import FaissIndexer
from faiss_module.faiss_utils.similarity_utils import distance_to_similarity_percent

def search_index(query_feature: np.ndarray, names, top_k=5):
    """
    支持多索引库的查询。
    参数:
        query_feature (np.ndarray): 查询向量
        names (str or List[str]): 单个或多个索引文件名（如 'index1.index' 或 ['a.index', 'b.index']）
        top_k (int): 返回最相似的 top_k 个图像 ID
    返回:
        List[int], List[float]: 匹配的 ID 列表 和 相似度百分比列表
    """
    if isinstance(names, str):
        names = [names]
    if top_k < 1:
        raise ValueError("top_k 必须大于等于 1")
    # 标准化查询向量形状
    if query_feature.ndim == 1:
        query_feature = query_feature.reshape(1, -1)
    elif query_feature.ndim != 2:
        raise ValueError("query_feature 必须是 1 维或 2 维 numpy 数组")

    dim = config.VECTOR_DIM
    results = []  # 用于收集所有库的搜索结果
    query_feature = query_feature.astype('float32')
    for name in names:
        index_path = os.path.join(config.INDEX_FOLDER, name)
        if not os.path.exists(index_path):
            print(f"索引文件 {index_path} 不存在，跳过。")
            continue

        indexer = FaissIndexer(dim=dim, index_path=index_path, use_IVF=True)
        indexer.load_index()
        distances, indices = indexer.search(query_feature.astype('float32'), top_k)

        for d, i in zip(distances[0], indices[0]):
            results.append((d, i))

    # 保留最小的 top_k 项（按距离排序）
    top_k_results = heapq.nsmallest(top_k, results, key=lambda x: x[0])
    final_distances, final_indices = zip(*top_k_results) if top_k_results else ([], [])

    similarities = distance_to_similarity_percent(np.array(final_distances))
    return list(final_indices), similarities.tolist()