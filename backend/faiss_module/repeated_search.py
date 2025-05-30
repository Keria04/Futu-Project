import numpy as np
import os
import faiss
from typing import List
# from faiss_module.indexer import FaissIndexer
# from faiss_module.faiss_utils.similarity_utils import distance_to_similarity_percent
from config import config
from indexer import FaissIndexer
from faiss_utils.similarity_utils import distance_to_similarity_percent

def repeated_search(index_name: str, threshold: float=95.0, deduplicate: bool = False) -> List[List[int]]:
    """
    寻找指定索引文件中的重复图片集合（基于相似度阈值）。
    参数:
        index_name (str): 索引文件名
        threshold (float): 相似度阈值（百分制），大于等于此值即认为是重复
        deduplicate (bool): 是否执行去重（仅保留每组中索引最小的项）

    返回:
        List[List[int]]: 每组为一组重复图像的ID集合（包括自己）
    """
    # index_path = os.path.join(config.INDEX_FOLDER, index_name)
    # if not os.path.exists(index_path):
    #     raise FileNotFoundError(f"索引文件 {index_path} 不存在")

    dim = config.VECTOR_DIM
    # indexer = FaissIndexer(dim=dim, index_path=index_path, nlist=config.N_LIST)
    indexer = FaissIndexer(dim=dim, index_path="/Users/caiyile/Desktop/Futu-Project/data/indexes/1.index", nlist=config.N_LIST)
    indexer.load_index()

    total_ids = indexer.index.ntotal
    #获取所有id
    id_list = faiss.vector_to_array(indexer.index.id_map)

    # 获取全部向量
    xb = indexer.index.reconstruct_n(0, total_ids)

    # 避免重复对比
    visited = set()
    duplicates = []

    for i in range(total_ids):
        if id_list[i] in visited:
            continue

        # 查询其余所有点，返回可能重复的项
        query_vec = xb[i].reshape(1, -1)
        distances, neighbors = indexer.index.search(query_vec, total_ids)

        group = []
        for d, idx in zip(distances[0], neighbors[0]):
            if idx < 0 or idx == id_list[i]:
                continue
            sim = distance_to_similarity_percent(d)
            if sim >= threshold:
                group.append(id_list[idx])
                visited.add(id_list[idx])

        if group:
            group.append(id_list[i])
            group = list(sorted(group))
            visited.add(id_list[i])
            duplicates.append(group)

    # 可选：去重保留每组中最小 ID 的那个
    if deduplicate:
        to_keep = set(min(group) for group in duplicates)
        to_remove = [id for group in duplicates for id in group if id not in to_keep]
        id_selector = faiss.IDSelectorBatch(len(to_remove), faiss.swig_ptr(np.array(to_remove, dtype='int64')))
        indexer.index.remove_ids(id_selector)
        indexer.save_index()

    return duplicates
if __name__ == "__main__":
    name = "1.index"  # 请替换为你实际的 index 文件名
    threshold = 95.0     # 设置相似度阈值百分比（如 95%）
    delete_flag = False
    result = repeated_search(name, threshold, delete_flag)
    print("重复组如下：")
    for group in result:
        print(group)