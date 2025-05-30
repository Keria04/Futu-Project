from .index_builder import IndexBuilder

def build_index(dataset_dir, dataset_name, distributed=False):
    """
    构建索引的工厂接口
    :param dataset_dir: 数据集图片路径
    :param dataset_name: 数据集名称
    :param distributed: 是否分布式
    :return: True/False
    """
    builder = IndexBuilder(dataset_dir, dataset_name, distributed=distributed)
    return builder.build()
