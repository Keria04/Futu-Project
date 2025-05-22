import math
import numpy as np

def distance_to_similarity_percent(distance_squared) -> float:
    """
    将 faiss 的平方距离转换为百分比相似度（0 ~ 100]）。
    支持 float 或 numpy.ndarray 输入。
    """
    distance_squared = np.asarray(distance_squared)
    if np.any(distance_squared < 0):
        raise ValueError("欧氏平方距离不能为负")
    euclidean_distance = np.sqrt(distance_squared)
    similarity = 1 / (1 + euclidean_distance)
    return similarity * 100