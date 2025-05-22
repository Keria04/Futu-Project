import math
import numpy as np
from config.config import SIMILARITY_SIGMA
def distance_to_similarity_percent(distance_squared) -> float:
    """
    将 faiss 的平方距离转换为百分比相似度（0 ~ 100]），采用指数衰减模型。
    sigma 值从 config 配置中读取。
    """
    sigma = SIMILARITY_SIGMA

    distance_squared = np.asarray(distance_squared, dtype=np.float32)
    if np.any(distance_squared < 0):
        raise ValueError("欧氏平方距离不能为负")
    similarity = np.exp(-distance_squared / (2 * sigma ** 2))
    return similarity * 100