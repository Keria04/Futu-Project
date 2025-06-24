import sys
import os
# 添加项目根路径，便于导入 config 和模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
import sqlite3

# 默认配置
try:
    from config.config import BASE_DIR, DATABASE_PATH
except ImportError:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'main.db')


class Database:
    """数据库操作类"""
    
    def __init__(self):
        try:
            # 确保数据库目录存在
            db_dir = os.path.dirname(DATABASE_PATH)
            os.makedirs(db_dir, exist_ok=True)
            
            self.conn = sqlite3.connect(DATABASE_PATH)
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(f"数据库连接失败: {e}")
            raise e  # 不使用fallback，直接抛出异常
    
    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
    
    def commit(self):
        self.conn.commit()
    
    def rollback(self):
        self.conn.rollback()
    
    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor

    def execute_many(self, query, seq_of_params):
        self.cursor.executemany(query, seq_of_params)
        return self.cursor
    
    @classmethod
    def initialize_db(cls):
        if not os.path.exists(DATABASE_PATH):
            print(f"Creating database {DATABASE_PATH}")


# 创建数据库实例
database = Database()
