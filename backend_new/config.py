"""
Flask 应用配置
"""
import os
from datetime import timedelta

class Config:
    """基础配置类"""
    
    # 基本配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    
    # 数据库配置
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'main.db')
    
    # CORS配置
    CORS_ORIGINS = ["http://localhost:19197"]
    
    # 索引配置
    INDEX_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data', 'indexes')
    PROGRESS_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data', 'progress')
    
    # 数据集配置
    DATASETS_FOLDER = os.path.join(os.path.dirname(__file__), '..', '..', 'datasets')
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 确保必要的文件夹存在
        folders = [
            Config.UPLOAD_FOLDER,
            Config.INDEX_FOLDER,
            Config.PROGRESS_FOLDER,
            os.path.dirname(Config.DATABASE_PATH)
        ]
        
        for folder in folders:
            os.makedirs(folder, exist_ok=True)

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    
class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    
class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
