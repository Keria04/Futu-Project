import os
import numpy as np
import heapq
from .faiss_config import default_config
from .indexer import FaissIndexer
from .faiss_utils.similarity_utils import distance_to_similarity_percent

def search_index(query_feature: np.ndarray, names, top_k=5, config=None):
    """
    支持多索引库的查询。
    参数:
        query_feature (np.ndarray): 查询向量
        names (str or List[str]): 单个或多个索引文件名（如 'index1.index' 或 ['a.index', 'b.index']）
        top_k (int): 返回最相似的 top_k 个图像 ID
        config: 可选的配置对象，如果不提供则使用默认配置
    返回:
        List[int], List[float]: 匹配的 ID 列表 和 相似度百分比列表
    """
    if config is None:
        config = default_config
        
    if isinstance(names, str):
        names = [names]
    if top_k < 1:
        raise ValueError("top_k 必须大于等于 1")
    # 标准化查询向量形状
    if query_feature.ndim == 1:
        query_feature = query_feature.reshape(1, -1)
    elif query_feature.ndim != 2:
        raise ValueError("query_feature 必须是 1 维或 2 维 numpy 数组")

    dim = config.vector_dim
    results = []  # 用于收集所有库的搜索结果
    query_feature = query_feature.astype('float32')
    for name in names:
        index_path = os.path.join(config.index_folder, name)
        if not os.path.exists(index_path):
            print(f"索引文件 {index_path} 不存在，跳过。")
            continue

        indexer = FaissIndexer(dim=dim, index_path=index_path, use_IVF=True)
        indexer.load_index()
        distances, indices = indexer.search(query_feature.astype('float32'), top_k)

        for d, i in zip(distances[0], indices[0]):
            results.append((d, i))    # 保留最小的 top_k 项（按距离排序）
    top_k_results = heapq.nsmallest(top_k, results, key=lambda x: x[0])
    final_distances, final_indices = zip(*top_k_results) if top_k_results else ([], [])
    
    similarities = distance_to_similarity_percent(np.array(final_distances), config)
    return list(final_indices), similarities.tolist()