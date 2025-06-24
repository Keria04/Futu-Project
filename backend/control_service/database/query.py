import sys
import os

# 添加上层路径便于模块导入
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from .database import Database

def _build_where_clause(where):
    """
    构建 WHERE 子句和参数列表
    :param where: 字典形式的查询条件，如 {'id': 1, 'name': 'John'}
    :return: (where_clause, params) 元组
    """
    if not where:
        return "", []

    clauses = []
    params = []
    for key, value in where.items():
        clauses.append(f"{key} = ?")
        params.append(value)
    where_clause = "WHERE " + " AND ".join(clauses)
    return where_clause, params

def query_one(table, columns='*', where=None):
    """
    查询单条记录
    :param table: 表名
    :param columns: 查询字段（默认为 '*'）
    :param where: 查询条件（字典形式）
    :return: 单条记录（tuple）或 None
    """
    db = Database()
    try:
        where_clause, params = _build_where_clause(where)
        query = f"SELECT {columns} FROM {table} {where_clause}"
        cursor = db.execute(query, params)
        return cursor.fetchone()
    except Exception as e:
        print(f"查询失败: {str(e)}")
        return None

def query_multi(table, columns='*', where=None, order_by=None, limit=None):
    """
    查询多条记录
    :param table: 表名
    :param columns: 查询字段（默认为 '*'）
    :param where: 查询条件（字典形式）
    :param order_by: 排序字段（如 'id DESC'）
    :param limit: 限制返回记录数
    :return: 查询结果列表（list of tuples）
    """
    db = Database()
    try:
        where_clause, params = _build_where_clause(where)
        order_by_clause = f"ORDER BY {order_by}" if order_by else ""
        limit_clause = f"LIMIT {limit}" if limit else ""
        query = f"SELECT {columns} FROM {table} {where_clause} {order_by_clause} {limit_clause}"
        cursor = db.execute(query, params)
        return cursor.fetchall()
    except Exception as e:
        print(f"查询失败: {str(e)}")
        return []
        
def get_dataset_id(dataset_name):
    """
    根据数据集名称获取数据集ID
    :param dataset_name: 数据集名称
    :return: 数据集ID或None
    """
    result = query_one("datasets", "id", where={"name": dataset_name})
    return result[0] if result else None

def get_datasets():
    """
    获取所有数据集
    :return: 数据集列表
    """
    # 先尝试包含description列，如果失败则使用基本列
    try:
        results = query_multi("datasets", "id, name, description, created_at")
        datasets = []
        for row in results:
            datasets.append({
                "id": row[0],
                "name": row[1], 
                "description": row[2] if len(row) > 2 else "",
                "created_at": row[3] if len(row) > 3 else ""
            })
        return datasets
    except:
        # 如果description列不存在，使用基本列
        results = query_multi("datasets", "id, name")
        datasets = []
        for row in results:
            datasets.append({
                "id": row[0],
                "name": row[1], 
                "description": "",
                "created_at": ""
            })
        return datasets

def get_image_by_id(image_id):
    """
    根据图片ID获取图片信息
    :param image_id: 图片ID
    :return: 图片信息字典或None
    """
    result = query_one("images", "*", where={"id": image_id})
    if result:
        return {
            "id": result[0],
            "dataset_id": result[1],
            "filename": result[2],
            "file_path": result[3],
            "file_size": result[4] if len(result) > 4 else 0,
            "checksum": result[5] if len(result) > 5 else "",
            "created_at": result[6] if len(result) > 6 else ""
        }
    return None

def get_images_by_dataset(dataset_name):
    """
    获取数据集中的所有图片
    :param dataset_name: 数据集名称
    :return: 图片列表
    """
    # 首先获取数据集ID
    dataset_id = get_dataset_id(dataset_name)
    if dataset_id is None:
        return []
    
    results = query_multi("images", "*", where={"dataset_id": dataset_id})
    images = []
    for row in results:
        images.append({
            "id": row[0],
            "dataset_id": row[1],
            "filename": row[2],
            "file_path": row[3],
            "file_size": row[4] if len(row) > 4 else 0,
            "checksum": row[5] if len(row) > 5 else "",
            "created_at": row[6] if len(row) > 6 else ""
        })
    return images