"""
indexer.py
使用 Faiss 实现图像特征索引构建和查询的模块。
它支持压缩、PCA降维、倒排索引（IVF）和ID映射（IDMap）等多级结构，适合中大型图像搜索场景。
主要功能：
- 建立带ID的Faiss索引（支持训练与压缩）
- 加载与保存索引
- 执行向量查询并返回相似项ID
"""
import faiss
import numpy as np
import os
class FaissIndexer:
    """
        FaissIndexer 类用于构建、保存、加载和查询 FAISS 索引。
        属性:
            dim (int): 特征维度，例如2048。
            index_path (str): 索引文件保存路径。
            nlist (int): 倒排列表数量（用于聚类中心数量）。
            index: FAISS 索引对象。
    """
    def __init__(self, dim, index_path, nlist=50):
        self.dim = dim
        self.index_path = index_path
        self.nlist = nlist
        self.index = None
    def build_index(self, features: np.ndarray, ids: np.ndarray):
        """
            构建压缩索引，并绑定自定义图像ID。
            参数:
                features (np.ndarray): shape=(N, dim) 的图像特征向量。
                ids (np.ndarray): shape=(N,) 的图像编号。
        """
        quantizer = "IDMap,IVF{},SQ8".format(self.nlist)  # 移除PCAR16
        self.index = faiss.index_factory(self.dim, quantizer, faiss.METRIC_L2)
        if not self.index.is_trained:
            self.index.train(features)
        self.index.add_with_ids(features, ids)
    def save_index(self):
        if self.index:
            faiss.write_index(self.index, self.index_path)
    def load_index(self):
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            raise FileNotFoundError(f"No FAISS index at {self.index_path}")
    def search(self, query: np.ndarray, k: int = 5):
        """
            对查询向量执行近邻搜索。
               参数:
                   query (np.ndarray): shape=(1, dim) 的查询向量。
                   k (int): 返回最近的 k 个相似项。
               返回:
                   distances (np.ndarray): 距离值。
                   ids (np.ndarray): 匹配的图像编号。
        """
        if self.index is None:
            raise ValueError("Index not loaded")
        return self.index.search(query, k)

    def update_index(self, new_features: np.ndarray, new_ids: np.ndarray):
        """
        更新索引：对已有 ID 执行删除再添加新向量；对新 ID 执行添加操作。
        参数:
            new_features (np.ndarray): shape=(M, dim) 的新特征向量。
            new_ids (np.ndarray): shape=(M,) 的图像 ID。
        """
        if self.index is None:
            raise ValueError("Index not loaded")

        # 先移除旧的 ID（如果存在）
        id_selector = faiss.IDSelectorBatch(new_ids.size, faiss.swig_ptr(new_ids))
        self.index.remove_ids(id_selector)

        # 添加新向量
        self.index.add_with_ids(new_features, new_ids)