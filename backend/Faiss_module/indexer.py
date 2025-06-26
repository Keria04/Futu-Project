"""
indexer.py
使用 Faiss 实现图像特征索引构建和查询的模块。
它支持压缩、PCA降维、倒排索引（IVF）和ID映射（IDMap）等多级结构，适合中大型图像搜索场景。
主要功能：
- 建立带ID的Faiss索引（支持训练与压缩）
- 加载与保存索引
- 执行向量查询并返回相似项ID
- 支持GPU加速（如果可用）
"""
import faiss
import numpy as np
import os
import math

class FaissIndexer:
    """
       FaissIndexer 类用于构建、保存、加载和查询 FAISS 索引。
       属性:
           dim (int): 特征维度，例如2048。
           index_path (str): 索引文件保存路径。
           use_IVF (bool): 是否启用 IVF 聚类（默认启用）。
           index: FAISS 索引对象。
           use_gpu (bool): 是否使用 GPU
           gpu_resources: GPU 资源对象
    """
    def __init__(self, dim, index_path, use_IVF):
        self.dim = dim
        self.index_path = index_path
        self.use_IVF = use_IVF
        self.index = None
        self.use_gpu = False
        self.gpu_resources = None

        # 检测是否可以使用 GPU
        self.init_gpu()

    def init_gpu(self):
        """初始化 GPU 资源"""
        try:
            ngpus = faiss.get_num_gpus()
            if ngpus > 0:
                self.use_gpu = True
                # 使用第一个可用的 GPU
                res = faiss.StandardGpuResources()
                self.gpu_resources = res
                print(f"成功初始化 GPU 资源，可用 GPU 数量: {ngpus}")
            else:
                print("未检测到可用的 GPU，将使用 CPU 模式")
        except Exception as e:
            print(f"GPU 初始化失败，将使用 CPU 模式: {str(e)}")
            self.use_gpu = False

    def to_gpu(self, index):
        """将索引转移到 GPU"""
        if self.use_gpu and self.gpu_resources is not None:
            return faiss.index_cpu_to_gpu(self.gpu_resources, 0, index)
        return index

    def to_cpu(self, index):
        """将索引转移回 CPU"""
        if self.use_gpu:
            return faiss.index_gpu_to_cpu(index)
        return index

    def build_index(self, features: np.ndarray, ids: np.ndarray):
        """
        构建压缩索引，并绑定自定义图像ID。
        参数:
            features (np.ndarray): shape=(N, dim) 的图像特征向量。
            ids (np.ndarray): shape=(N,) 的图像编号。
        """
        num_data = features.shape[0]

        if self.use_IVF:
            # 自动设置 nlist（√N）和 nprobe（5%）
            nlist = max(1, int(math.sqrt(num_data)))
            nprobe = max(1, math.ceil(nlist * 0.1))

            if num_data < nlist:
                nlist = num_data  # 避免 nx < k 错误

            quantizer = f"IDMap,IVF{nlist},SQ8"
            self.index = faiss.index_factory(self.dim, quantizer, faiss.METRIC_L2)

            if not self.index.is_trained:
                self.index.train(features)

            self.index.add_with_ids(features, ids)
            self.index.probe= nprobe
            print(f"[√] 使用 IVF 索引构建完成: nlist={nlist}, nprobe={nprobe}")
        else:
            # 不使用 IVF，使用简单的 Flat 索引
            self.index = faiss.IndexFlatL2(self.dim)
            id_index = faiss.IndexIDMap(self.index)
            id_index.add_with_ids(features, ids)
            self.index = id_index
            print("[√] 使用 Flat 索引构建完成（测试用途）")

        # 如果可用，将索引转移到 GPU
        self.index = self.to_gpu(self.index)

    def save_index(self):
        if self.index:
            faiss.write_index(self.index, self.index_path)
    def load_index(self):
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            # 加载后转移到 GPU（如果可用）
            self.index = self.to_gpu(self.index)
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