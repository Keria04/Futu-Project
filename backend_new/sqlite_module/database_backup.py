import sys
import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

# 添加项目根路径，便于导入 config 和模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    from config.config import DATABASE_PATH
except ImportError:
    # 默认配置
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'main.db')

from _database_interface import DatabaseInterface


class SQLiteDatabase(DatabaseInterface):
    """SQLite数据库实现类"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        self.conn = None
        self.cursor = None
        self._tables_checked = False  # 标记是否已检查表结构
        self.connect()
    
    def connect(self) -> None:
        """建立数据库连接"""
        try:
            # 确保数据库目录存在
            db_dir = os.path.dirname(self.db_path)
            os.makedirs(db_dir, exist_ok=True)
            
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # 启用外键约束            self.cursor.execute("PRAGMA foreign_keys = ON")
        except Exception as e:
            print(f"数据库连接失败: {e}")
            raise e
    
    def disconnect(self) -> None:
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
    
    def __del__(self):
        self.disconnect()
    
    def _ensure_tables_exist(self) -> None:
        """确保数据库表存在，如不存在则自动创建"""
        if self._tables_checked:
            return
        
        try:
            # 检查表是否存在
            cursor = self.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('datasets', 'images')")
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            # 如果表不存在或不完整，则创建表
            if 'datasets' not in existing_tables or 'images' not in existing_tables:
                print("检测到数据库表缺失，正在自动创建...")
                self.create_tables()
            
            self._tables_checked = True
        except Exception as e:
            print(f"检查表结构失败: {e}")
            # 即使检查失败，也尝试创建表
            try:
                self.create_tables()
                self._tables_checked = True
            except Exception as create_error:
                print(f"自动创建表失败: {create_error}")
                raise create_error
    
    def commit(self) -> None:
        """提交事务"""
        if self.conn:
            self.conn.commit()
    
    def rollback(self) -> None:
        """回滚事务"""
        if self.conn:
            self.conn.rollback()
    
    def execute(self, query: str, params: Tuple = ()) -> Any:
        """执行SQL语句"""
        if not self.cursor:
            raise RuntimeError("数据库连接未建立")
        self.cursor.execute(query, params)
        return self.cursor

    def execute_many(self, query: str, seq_of_params: List[Tuple]) -> Any:
        """批量执行SQL语句"""
        if not self.cursor:
            raise RuntimeError("数据库连接未建立")
        self.cursor.executemany(query, seq_of_params)
        return self.cursor
    
    def _build_where_clause(self, where: Optional[Dict]) -> Tuple[str, List]:
        """构建WHERE子句"""
        if not where:
            return "", []
        
        clauses = []
        params = []
        for key, value in where.items():
            clauses.append(f"{key} = ?")
            params.append(value)
        where_clause = "WHERE " + " AND ".join(clauses)
        return where_clause, params
    
    def query_one(self, table: str, columns: str = '*', where: Optional[Dict] = None) -> Optional[Tuple]:
        """查询单条记录"""
        self._ensure_tables_exist()  # 确保表存在
        try:
            where_clause, params = self._build_where_clause(where)
            query = f"SELECT {columns} FROM {table} {where_clause}"
            cursor = self.execute(query, params)
            return cursor.fetchone()
        except Exception as e:
            print(f"查询失败: {str(e)}")
            return None
      def query_multi(self, table: str, columns: str = '*', where: Optional[Dict] = None, 
                   order_by: Optional[str] = None, limit: Optional[int] = None) -> List[Tuple]:
        """查询多条记录"""
        self._ensure_tables_exist()  # 确保表存在
        try:
            where_clause, params = self._build_where_clause(where)
            order_by_clause = f"ORDER BY {order_by}" if order_by else ""
            limit_clause = f"LIMIT {limit}" if limit else ""
            query = f"SELECT {columns} FROM {table} {where_clause} {order_by_clause} {limit_clause}"
            cursor = self.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            print(f"查询失败: {str(e)}")
            return []
    
    def insert_one(self, table: str, data: Dict[str, Any]) -> int:
        """插入单条记录"""
        try:
            keys = list(data.keys())
            values = list(data.values())
            columns = ', '.join(keys)
            placeholders = ', '.join('?' * len(keys))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            cursor = self.execute(query, values)
            self.commit()
            return cursor.lastrowid
        except Exception as e:
            self.rollback()
            raise e
    
    def insert_multi(self, table: str, data_list: List[Dict[str, Any]]) -> int:
        """批量插入多条记录"""
        if not data_list:
            return 0
        
        try:
            keys = list(data_list[0].keys())
            columns = ', '.join(keys)
            placeholders = ', '.join('?' * len(keys))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            values = [tuple(item[key] for key in keys) for item in data_list]
            cursor = self.execute_many(query, values)
            self.commit()
            return cursor.rowcount
        except Exception as e:
            self.rollback()
            raise e
    
    def update(self, table: str, data: Dict[str, Any], where: Optional[Dict] = None) -> int:
        """更新记录"""
        try:
            where_clause, params = self._build_where_clause(where)
            set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
            values = list(data.values()) + params
            query = f"UPDATE {table} SET {set_clause} {where_clause}"
            cursor = self.execute(query, values)
            self.commit()
            return cursor.rowcount
        except Exception as e:
            self.rollback()
            raise e
    
    def delete(self, table: str, where: Dict[str, Any]) -> int:
        """删除记录"""
        try:
            where_clause, params = self._build_where_clause(where)
            query = f"DELETE FROM {table} {where_clause}"
            cursor = self.execute(query, params)
            self.commit()
            return cursor.rowcount
        except Exception as e:
            self.rollback()
            raise e
    
    def create_tables(self) -> None:
        """创建数据库表结构"""
        # 数据集表
        datasets_sql = '''
            CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_rebuild DATETIME,
            image_count INTEGER NOT NULL DEFAULT 0,
            size_bytes INTEGER NOT NULL DEFAULT 0
            )
        '''
        
        # 图片表  
        images_sql = '''
            CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER DEFAULT 0,
            checksum TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            metadata_json TEXT,
            feature_vector BLOB,
            FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE
            )
        '''
        
        try:
            self.execute(datasets_sql)
            self.execute(images_sql)
            self.commit()
            print("数据库表已创建或已存在")
        except Exception as e:
            self.rollback()
            print(f"创建表失败: {str(e)}")
            raise e


# 为了向后兼容，保留原始类名
Database = SQLiteDatabase