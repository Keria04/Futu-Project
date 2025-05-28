import sys
import os
# 添加上一层路径便于模块内导入
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database_module.database import Database

def create_tables():
    """
    创建数据库表结构
    """
    # 初始化数据库连接
    db = Database()
    db.initialize_db()  # 确保数据库文件存在
    
    # 数据集表
    datasets_sql = '''
        CREATE TABLE IF NOT EXISTS datasets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        created_at DATETIME NOT NULL,
        last_rebuild DATETIME,
        image_count INTEGER NOT NULL DEFAULT 0,
        size TEXT NOT NULL DEFAULT '0'
        )
    '''
    
    # 图片表
    images_sql = '''
        CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_id INTEGER NOT NULL,
        image_path TEXT NOT NULL,
        resource_type TEXT CHECK(resource_type IN ('control', 'compute')) NOT NULL,
        metadata_json TEXT,
        feature_vector BLOB,
        external_ids INTEGER,
        FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE
        )
    '''
    
    try:
        # 执行建表语句
        db.execute(datasets_sql)
        db.execute(images_sql)
        db.commit()
        print("数据库表已创建或已存在。")
    except Exception as e:
        db.rollback()
        print(f"创建表失败: {str(e)}")
        

# 调试入口
if __name__ == "__main__":
    create_tables()