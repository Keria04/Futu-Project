# config/faiss_config.py
import os
# 特征文件路径
FEATURE_PATH = os.path.join("backend","features.npy")
# 图像 ID 文件路径（可选）
ID_PATH = os.path.join("backend", "ids.npy")
# FAISS 索引文件保存路径
INDEX_PATH = os.path.join("backend", "faiss_module", "image.index")
# 特征维度（如 ResNet 输出为 512）
VECTOR_DIM = 2048
# IVF 索引中的聚类数量（影响召回速度与精度）
N_LIST = 50