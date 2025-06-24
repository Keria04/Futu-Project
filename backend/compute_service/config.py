"""
计算端配置文件
"""
import os
import sys

# 添加项目根路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 从根配置导入需要的变量
try:
    import config.config as root_config
    # 继承原有配置
    device = getattr(root_config, 'device', 'cpu')
    pretrain = getattr(root_config, 'pretrain', True)
    model_type = getattr(root_config, 'model_type', 'resnet50')
    input_size = getattr(root_config, 'input_size', 224)
    batchsize = getattr(root_config, 'batchsize', 128)
    normalize_mean = getattr(root_config, 'normalize_mean', [0.485, 0.456, 0.406])
    normalize_std = getattr(root_config, 'normalize_std', [0.229, 0.224, 0.225])
except ImportError:
    # 如果导入失败，使用默认配置
    device = 'cpu'
    pretrain = True
    model_type = 'resnet50'
    input_size = 224
    batchsize = 128
    normalize_mean = [0.485, 0.456, 0.406]
    normalize_std = [0.229, 0.224, 0.225]

# 计算端特有配置
COMPUTE_SERVICE_NAME = 'compute_worker'

# Redis配置
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_TASK_QUEUE = 'task_queue'
REDIS_RESULT_QUEUE = 'result_queue'

# 工作者配置
WORKER_CONCURRENCY = 1
WORKER_LOGLEVEL = 'info'
MAX_TASK_TIMEOUT = 300  # 5分钟

# 模型配置
MODEL_CACHE_SIZE = 1  # 缓存的模型数量
