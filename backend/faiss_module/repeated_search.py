import numpy as np
import os
import sys
import faiss
from typing import List
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from faiss_module.indexer import FaissIndexer
from faiss_module.faiss_utils.similarity_utils import distance_to_similarity_percent
from index_manage_module.api import get_dataset_image_features
from config import config
# from indexer import FaissIndexer
# from faiss_utils.similarity_utils import distance_to_similarity_percent
# from ..index_manage_module.api import get_dataset_image_features

def repeated_search(index_id, threshold: float = 95.0, deduplicate: bool = False) -> List[List[int]]:
    """
    寻找指定索引文件中的重复图片集合（基于相似度阈值）。
    参数:
        index_id: 数据集ID（int）或数据集名称（str）
        threshold (float): 相似度阈值（百分制），大于等于此值即认为是重复
        deduplicate (bool): 是否执行去重（仅保留每组中索引最小的项）
    返回:
        List[List[int]]: 每组为一组重复图像的ID集合（包括自己）
    """
    # 如果传入的是字符串（数据集名称），需要转换为数据集ID
    if isinstance(index_id, str):
        from database_module.query import query_one
        dataset = query_one("datasets", where={"name": index_id})
        if dataset is None:
            raise ValueError(f"数据集 {index_id} 不存在")
        dataset_id = dataset[0]  # ID在第一个字段
    else:
        dataset_id = index_id
    
    # 初始化 indexer
    dim = config.VECTOR_DIM
    index_path = os.path.join(config.INDEX_FOLDER, f"{dataset_id}.index")
    print("index_path:", index_path)
    indexer = FaissIndexer(dim=dim, index_path=index_path, use_IVF=True)
    indexer.load_index()


    # 获取原始图片特征（id, vector）
    id_vector_pairs = get_dataset_image_features(dataset_id)

    if not id_vector_pairs:
        raise ValueError(f"未找到数据集 {index_path} 的图像特征")

    id_list = [id for id, _ in id_vector_pairs]
    xb = np.stack([vec for _, vec in id_vector_pairs])

    total_ids = len(id_list)
    visited = set()
    duplicates = []

    # GPU 模式下的最大 k 值
    MAX_K_GPU = 2048

    for i in range(total_ids):
        current_id = id_list[i]
        if current_id in visited:
            continue

        query_vec = xb[i].reshape(1, -1)

        if indexer.use_gpu:
            # GPU 模式：限制 k 值
            k = min(MAX_K_GPU, total_ids)
            distances, neighbors = indexer.index.search(query_vec, k)
        else:
            # CPU 模式：直接搜索全部
            distances, neighbors = indexer.index.search(query_vec, total_ids)

        group = []
        for d, neighbor_id in zip(distances[0], neighbors[0]):
            if neighbor_id < 0 or neighbor_id == current_id:
                continue
            sim = distance_to_similarity_percent(d)
            if sim >= threshold:
                group.append(neighbor_id)
                visited.add(neighbor_id)

        if group:
            group.append(current_id)
            group = sorted(group)
            visited.add(current_id)
            duplicates.append(group)
    # 去重：保留每组中最小ID
    if deduplicate and duplicates:
        to_keep = set(min(group) for group in duplicates)
        to_remove = [id for group in duplicates for id in group if id not in to_keep]
        id_selector = faiss.IDSelectorBatch(len(to_remove), faiss.swig_ptr(np.array(to_remove, dtype='int64')))
        indexer.index.remove_ids(id_selector)
        indexer.save_index()
    return duplicates

if __name__ == "__main__":
    name = "1.index"         # 索引文件名
    threshold = 95.0         # 相似度阈值
    delete_flag = False      # 是否启用去重删除
    result = repeated_search(name, threshold, delete_flag)

    print("重复组如下：")
    for group in result:
        print(group)