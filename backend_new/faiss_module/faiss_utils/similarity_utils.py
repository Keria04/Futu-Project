import math
import numpy as np
from ..faiss_config import default_config

def distance_to_similarity_percent(distance_squared, config=None) -> float:
    """
    将 faiss 的平方距离转换为百分比相似度（0 ~ 100]），采用指数衰减模型。
    sigma 值从配置中读取。
    
    :param distance_squared: 平方距离值
    :param config: 可选的配置对象，如果不提供则使用默认配置
    """
    if config is None:
        config = default_config
        
    sigma = config.similarity_sigma

    distance_squared = np.asarray(distance_squared, dtype=np.float32)
    if np.any(distance_squared < 0):
        raise ValueError("欧氏平方距离不能为负")
    similarity = np.exp(-distance_squared / (2 * sigma ** 2))
    return similarity * 100