# 提供给外部的统一 API
from .factory import build_index

def build_dataset_index(dataset_dir, dataset_name, distributed=False):
    """
    构建指定数据集的索引
    :param dataset_dir: 数据集图片路径
    :param dataset_name: 数据集名称
    :param distributed: 是否分布式
    :return: True/False
    """
    return build_index(dataset_dir, dataset_name, distributed)
