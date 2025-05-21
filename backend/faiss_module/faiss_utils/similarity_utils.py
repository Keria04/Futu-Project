import math
def distance_to_similarity_percent(distance_squared: float) -> float:
    """
    将 faiss 的平方距离转换为百分比相似度（0 ~ 100]）。
    """
    if distance_squared < 0:
        raise ValueError("欧氏平方距离不能为负")
    euclidean_distance = math.sqrt(distance_squared)
    similarity = 1 / (1 + euclidean_distance)
    return similarity * 100