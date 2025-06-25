"""
查询操作封装
基于新的数据库接口实现的查询功能
"""

import sys
import os
from typing import Dict, List, Optional, Any

# 添加上层路径便于模块导入
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlite_module.database_manager import get_database_manager


def query_one(table: str, columns: str = '*', where: Optional[Dict] = None) -> Optional[tuple]:
    """
    查询单条记录
    :param table: 表名
    :param columns: 查询字段（默认为 '*'）
    :param where: 查询条件（字典形式）
    :return: 单条记录（tuple）或 None
    """
    db_manager = get_database_manager()
    db = db_manager.get_database()
    return db.query_one(table, columns, where)


def query_multi(table: str, columns: str = '*', where: Optional[Dict] = None, 
               order_by: Optional[str] = None, limit: Optional[int] = None) -> List[tuple]:
    """
    查询多条记录
    :param table: 表名
    :param columns: 查询字段（默认为 '*'）
    :param where: 查询条件（字典形式）
    :param order_by: 排序字段（如 'id DESC'）
    :param limit: 限制返回记录数
    :return: 查询结果列表（list of tuples）
    """
    db_manager = get_database_manager()
    db = db_manager.get_database()
    return db.query_multi(table, columns, where, order_by, limit)


def get_dataset_id(dataset_name: str) -> Optional[int]:
    """
    根据数据集名称获取数据集ID
    :param dataset_name: 数据集名称
    :return: 数据集ID或None
    """
    db_manager = get_database_manager()
    dataset_repo = db_manager.get_dataset_repository()
    dataset = dataset_repo.get_dataset_by_name(dataset_name)
    return dataset["id"] if dataset else None


def get_datasets() -> List[Dict]:
    """
    获取所有数据集
    :return: 数据集列表
    """
    db_manager = get_database_manager()
    dataset_repo = db_manager.get_dataset_repository()
    return dataset_repo.get_all_datasets()


def get_image_by_id(image_id: int) -> Optional[Dict]:
    """
    根据图片ID获取图片信息
    :param image_id: 图片ID
    :return: 图片信息字典或None
    """
    db_manager = get_database_manager()
    image_repo = db_manager.get_image_repository()
    return image_repo.get_image_by_id(image_id)


def get_images_by_dataset(dataset_name: str) -> List[Dict]:
    """
    获取数据集中的所有图片
    :param dataset_name: 数据集名称
    :return: 图片列表
    """
    db_manager = get_database_manager()
    image_repo = db_manager.get_image_repository()
    return image_repo.get_images_by_dataset_name(dataset_name)


def get_images_by_dataset_id(dataset_id: int) -> List[Dict]:
    """
    根据数据集ID获取图片
    :param dataset_id: 数据集ID
    :return: 图片列表
    """
    db_manager = get_database_manager()
    image_repo = db_manager.get_image_repository()
    return image_repo.get_images_by_dataset(dataset_id)


# 向后兼容函数
def get_dataset_by_name(name: str) -> Optional[Dict]:
    """根据名称获取数据集"""
    db_manager = get_database_manager()
    dataset_repo = db_manager.get_dataset_repository()
    return dataset_repo.get_dataset_by_name(name)


def get_dataset_by_id(dataset_id: int) -> Optional[Dict]:
    """根据ID获取数据集"""
    db_manager = get_database_manager()
    dataset_repo = db_manager.get_dataset_repository()
    return dataset_repo.get_dataset_by_id(dataset_id)


if __name__ == "__main__":
    # 测试查询功能
    print("测试数据集查询:")
    datasets = get_datasets()
    for dataset in datasets:
        print(f"数据集: {dataset}")
    
    print("\n测试图片查询:")
    if datasets:
        dataset_name = datasets[0]["name"]
        images = get_images_by_dataset(dataset_name)
        print(f"数据集 '{dataset_name}' 中的图片数量: {len(images)}")
        if images:
            print(f"第一张图片: {images[0]}")