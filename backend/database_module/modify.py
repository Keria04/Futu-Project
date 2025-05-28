import sys
import os

# 添加上层路径便于模块导入
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database_module.database import Database

def _build_where_clause(where):
    """
    构建 WHERE 子句和参数列表
    :param where: 字典形式的查询条件，如 {'id': 1}
    :return: (where_clause, params)
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

def insert_one(table, data):
    """
    插入单条记录
    :param table: 表名
    :param data: 要插入的字段字典，如 {'name': 'John', 'age': 30}
    :return: 插入的记录 ID（如 SQLite 的 lastrowid）
    """
    db = Database()
    try:
        keys = list(data.keys())
        values = list(data.values())
        columns = ', '.join(keys)
        placeholders = ', '.join('?' * len(keys))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        cursor = db.execute(query, values)
        db.commit()
        return cursor.lastrowid
    except Exception as e:
        db.rollback()
        raise e

def insert_multi(table, data_list):
    """
    批量插入多条记录
    :param table: 表名
    :param data_list: 字典列表，如 [{'name': 'A', 'age': 20}, {'name': 'B', 'age': 25}]
    :return: 插入的记录总数
    """
    if not data_list:
        return 0

    db = Database()
    try:
        keys = list(data_list[0].keys())
        columns = ', '.join(keys)
        placeholders = ', '.join('?' * len(keys))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        values = [tuple(item[key] for key in keys) for item in data_list]
        cursor = db.execute_many(query, values)
        db.commit()
        return cursor.rowcount
    except Exception as e:
        db.rollback()
        raise e

def update(table, data, where=None):
    """
    更新符合条件的记录
    :param table: 表名
    :param data: 要更新的字段字典，如 {'age': 31}
    :param where: 查询条件字典，如 {'name': 'John'}
    :return: 受影响的行数
    """
    db = Database()
    try:
        where_clause, params = _build_where_clause(where)
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        values = list(data.values()) + params
        query = f"UPDATE {table} SET {set_clause} {where_clause}"
        cursor = db.execute(query, values)
        db.commit()
        return cursor.rowcount
    except Exception as e:
        db.rollback()
        raise e

def delete(table, where):
    """
    删除符合条件的记录
    :param table: 表名
    :param where: 查询条件字典，如 {'age': 30}
    :return: 被删除的行数
    """
    db = Database()
    try:
        where_clause, params = _build_where_clause(where)
        query = f"DELETE FROM {table} {where_clause}"
        cursor = db.execute(query, params)
        db.commit()
        return cursor.rowcount
    except Exception as e:
        db.rollback()
        raise e

if __name__ == "__main__":
    # 插入单条记录
    user_id = insert_one("users", {"name": "Alice", "age": 25})
    print(f"插入单条记录，ID: {user_id}")

    # 插入多条记录
    users = [
        {"name": "Bob", "age": 30},
        {"name": "Charlie", "age": 35}
    ]
    count = insert_many("users", users)
    print(f"插入 {count} 条记录")

    # 更新记录
    rows = update("users", {"age": 31}, {"name": "Bob"})
    print(f"更新 {rows} 条记录")

    # 删除记录
    rows = delete("users", {"age": 25})
    print(f"删除 {rows} 条记录")