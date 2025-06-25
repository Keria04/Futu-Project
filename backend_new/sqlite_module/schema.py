"""
数据库表结构定义和初始化
"""

import sys
import os

# 添加上一层路径便于模块内导入
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlite_module.database_manager import get_database_manager


def create_tables():
    """
    创建数据库表结构
    """
    db_manager = get_database_manager()
    db_manager.initialize()
    print("数据库表结构初始化完成")


def initialize_database():
    """
    初始化数据库（创建表和默认数据）
    """
    # 创建表结构
    create_tables()
    
    # 可以在这里添加默认数据的插入逻辑
    print("数据库初始化完成")


# 调试入口
if __name__ == "__main__":
    initialize_database()