"""
控制端配置文件
"""
import os
import sys

# 添加项目根路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 从根配置导入需要的变量
try:
    import config.config as root_config
    # 继承根配置
    BASE_DIR = getattr(root_config, 'BASE_DIR', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    DATABASE_PATH = getattr(root_config, 'DATABASE_PATH', os.path.join(BASE_DIR, 'data', 'main.db'))
    UPLOAD_FOLDER = getattr(root_config, 'UPLOAD_FOLDER', os.path.join(BASE_DIR, 'data', 'uploads'))
    DATASET_DIR = getattr(root_config, 'DATASET_DIR', os.path.join(BASE_DIR, 'datasets'))
    INDEX_FOLDER = getattr(root_config, 'INDEX_FOLDER', os.path.join(BASE_DIR, 'data', 'indexes'))
    VECTOR_DIM = getattr(root_config, 'VECTOR_DIM', 2048)
    SIMILARITY_SIGMA = getattr(root_config, 'SIMILARITY_SIGMA', 0.1)
    DISTRIBUTED_AVAILABLE = getattr(root_config, 'DISTRIBUTED_AVAILABLE', True)
except ImportError:
    # 如果导入失败，使用默认配置
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'main.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data', 'uploads')
    DATASET_DIR = os.path.join(BASE_DIR, 'datasets')
    INDEX_FOLDER = os.path.join(BASE_DIR, 'data', 'indexes')
    VECTOR_DIM = 2048
    SIMILARITY_SIGMA = 0.1
    DISTRIBUTED_AVAILABLE = True

# 控制端特有配置
CONTROL_PORT = 19198
CONTROL_SERVICE_HOST = '0.0.0.0'
CONTROL_SERVICE_DEBUG = True

# Redis配置
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_TASK_QUEUE = 'task_queue'
REDIS_RESULT_QUEUE = 'result_queue'

# 任务超时配置
TASK_TIMEOUT = 300  # 5分钟
TASK_RESULT_TTL = 3600  # 1小时

# 分布式计算配置
MAX_CONCURRENT_TASKS = 10
