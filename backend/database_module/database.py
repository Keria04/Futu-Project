import sys
import os
# 添加项目根路径，便于导入 config 和模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import sqlite3
from config import config

# 数据库定义
class Database:
    # 初始化使用sqlite3
    def __init__(self):
        self.conn = sqlite3.connect(config.DATABASE_PATH)
        self.cursor = self.conn.cursor()
    
    def __del__(self):
        self.conn.close()
    
    def commit(self):
        self.conn.commit()
    
    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor
    
    @classmethod
    def initialize_db(cls):
        if not os.path.exists(config.DATABASE_PATH):
            print(f"Creating database {config.DATABASE_PATH}")