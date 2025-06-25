"""
数据修改操作封装
基于新的数据库接口实现的增删改功能
"""

import sys
import os
from typing import Dict, List, Optional, Any

# 添加上层路径便于模块导入
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlite_module.database_manager import get_database_manager


def insert_one(table: str, data: Dict[str, Any]) -> int:
    """
    插入单条记录
    :param table: 表名
    :param data: 要插入的字段字典，如 {'name': 'John', 'age': 30}
    :return: 插入的记录 ID（如 SQLite 的 lastrowid）
    """
    db_manager = get_database_manager()
    db = db_manager.get_database()
    return db.insert_one(table, data)


def insert_multi(table: str, data_list: List[Dict[str, Any]]) -> int:
    """
    批量插入多条记录
    :param table: 表名
    :param data_list: 字典列表，如 [{'name': 'A', 'age': 20}, {'name': 'B', 'age': 25}]
    :return: 插入的记录总数
    """
    db_manager = get_database_manager()
    db = db_manager.get_database()
    return db.insert_multi(table, data_list)


def update(table: str, data: Dict[str, Any], where: Optional[Dict] = None) -> int:
    """
    更新符合条件的记录
    :param table: 表名
    :param data: 要更新的字段字典，如 {'age': 31}
    :param where: 查询条件字典，如 {'name': 'John'}
    :return: 受影响的行数
    """
    db_manager = get_database_manager()
    db = db_manager.get_database()
    return db.update(table, data, where)


def delete(table: str, where: Dict[str, Any]) -> int:
    """
    删除符合条件的记录
    :param table: 表名
    :param where: 查询条件字典，如 {'age': 30}
    :return: 被删除的行数
    """
    db_manager = get_database_manager()
    db = db_manager.get_database()
    return db.delete(table, where)


# 高级数据操作函数

def create_dataset(name: str, description: str = "") -> int:
    """
    创建新数据集
    :param name: 数据集名称
    :param description: 数据集描述
    :return: 数据集ID
    """
    db_manager = get_database_manager()
    dataset_repo = db_manager.get_dataset_repository()
    return dataset_repo.create_dataset(name, description)


def add_image_to_dataset(dataset_id: int, filename: str, file_path: str, 
                        file_size: int = 0, checksum: str = "") -> int:
    """
    添加图片到数据集
    :param dataset_id: 数据集ID
    :param filename: 文件名
    :param file_path: 文件路径
    :param file_size: 文件大小
    :param checksum: 文件校验和
    :return: 图片ID
    """
    db_manager = get_database_manager()
    image_repo = db_manager.get_image_repository()
    return image_repo.add_image(dataset_id, filename, file_path, file_size, checksum)


def batch_add_images(dataset_id: int, image_list: List[Dict]) -> int:
    """
    批量添加图片到数据集
    :param dataset_id: 数据集ID
    :param image_list: 图片信息列表
    :return: 成功添加的图片数量
    """
    db_manager = get_database_manager()
    image_repo = db_manager.get_image_repository()
    return image_repo.batch_add_images(dataset_id, image_list)


def update_dataset(dataset_id: int, data: Dict[str, Any]) -> bool:
    """
    更新数据集信息
    :param dataset_id: 数据集ID
    :param data: 更新数据
    :return: 是否成功
    """
    db_manager = get_database_manager()
    dataset_repo = db_manager.get_dataset_repository()
    return dataset_repo.update_dataset(dataset_id, data)


def delete_dataset(dataset_id: int) -> bool:
    """
    删除数据集（会级联删除所有图片）
    :param dataset_id: 数据集ID
    :return: 是否成功
    """
    db_manager = get_database_manager()
    dataset_repo = db_manager.get_dataset_repository()
    return dataset_repo.delete_dataset(dataset_id)


def delete_image(image_id: int) -> bool:
    """
    删除图片
    :param image_id: 图片ID
    :return: 是否成功
    """
    db_manager = get_database_manager()
    image_repo = db_manager.get_image_repository()
    return image_repo.delete_image(image_id)


def update_dataset_stats(dataset_id: int) -> bool:
    """
    更新数据集统计信息
    :param dataset_id: 数据集ID
    :return: 是否成功
    """
    db_manager = get_database_manager()
    dataset_repo = db_manager.get_dataset_repository()
    return dataset_repo.update_dataset_stats(dataset_id)


if __name__ == "__main__":
    # 测试数据修改功能
    print("测试数据集创建:")
    dataset_id = create_dataset("测试数据集", "这是一个测试数据集")
    print(f"创建数据集ID: {dataset_id}")
    
    print("\n测试图片添加:")
    image_id = add_image_to_dataset(dataset_id, "test.jpg", "/path/to/test.jpg", 1024)
    print(f"添加图片ID: {image_id}")
    
    print("\n测试批量图片添加:")
    images = [
        {"filename": "img1.jpg", "file_path": "/path/img1.jpg", "file_size": 2048},
        {"filename": "img2.jpg", "file_path": "/path/img2.jpg", "file_size": 3072}
    ]
    count = batch_add_images(dataset_id, images)
    print(f"批量添加图片数量: {count}")
    
    print("\n测试统计信息更新:")
    success = update_dataset_stats(dataset_id)
    print(f"更新统计信息成功: {success}")
