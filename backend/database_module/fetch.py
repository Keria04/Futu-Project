import sys
import os

# 添加上层路径便于模块导入
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database_module.database import Database

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

def fetch_one(table, columns='*', where=None):
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

def fetch_all(table, columns='*', where=None, order_by=None, limit=None):
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
        
if __name__ == "__main__":
    # 查询单条记录
    user = fetch_one("users", where={"id": 1})
    print("单条记录:", user)

    # 查询多条记录
    users = fetch_all("users", where={"status": "active"}, order_by="id DESC", limit=10)
    print("多条记录:", users)