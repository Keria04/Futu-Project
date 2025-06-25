import base64
from io import BytesIO
from PIL import Image
from celery import Celery
from model_module.feature_extractor import feature_extractor
import redis
import logging
import sys
import os

# 添加配置路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 从配置文件读取Redis设置
REDIS_HOST = getattr(config, 'REDIS_HOST', 'localhost')
REDIS_PORT = getattr(config, 'REDIS_PORT', 6379)
REDIS_BROKER_DB = getattr(config, 'REDIS_BROKER_DB', 0)
REDIS_BACKEND_DB = getattr(config, 'REDIS_BACKEND_DB', 1)

# 创建Celery应用
celery_app = Celery(
    'tasks',
    broker=f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BROKER_DB}',
    backend=f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BACKEND_DB}'
)

# 配置Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    task_time_limit=getattr(config, 'CELERY_TASK_TIME_LIMIT', 300),
    task_soft_time_limit=getattr(config, 'CELERY_TASK_SOFT_TIME_LIMIT', 240),    # 修复任务注册问题
    include=['worker'],  # 确保任务被正确注册
    # 统一使用celery队列，避免队列混乱
    task_default_queue='celery',
    task_routes={
        'worker.generate_embeddings_task': {'queue': 'celery'},
    },
    # 简化worker配置
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
)

def check_redis_connection():
    """检查Redis连接是否可用"""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)
        r.ping()
        return True
    except Exception as e:
        logger.error(f"Redis连接失败: {e}")
        return False

def check_celery_worker():
    """检查Celery工作节点是否可用"""
    try:
        # 检查活跃的工作节点
        i = celery_app.control.inspect()
        active_workers = i.active()
        if active_workers:
            return True
        return False
    except Exception as e:
        logger.error(f"Celery工作节点检查失败: {e}")
        return False

def is_distributed_available():
    """检查分布式计算是否可用"""
    return check_redis_connection() and check_celery_worker()

@celery_app.task(bind=True, max_retries=getattr(config, 'CELERY_MAX_RETRIES', 3))
def generate_embeddings_task(self, img_data_b64):
    """生成图像特征向量的Celery任务"""
    try:
        logger.info(f"开始处理特征提取任务: {self.request.id}")
        
        # 解码图像数据
        img_bytes = base64.b64decode(img_data_b64)
        img = Image.open(BytesIO(img_bytes))
        
        # 创建特征提取器并计算特征
        embedder = feature_extractor()
        feat = embedder.calculate(img)
        
        logger.info(f"特征提取任务完成: {self.request.id}")
        return feat.tolist()
        
    except Exception as exc:
        logger.error(f"特征提取任务失败: {exc}")
        # 重试机制
        if self.request.retries < self.max_retries:
            logger.info(f"重试任务 {self.request.id}, 重试次数: {self.request.retries + 1}")
            raise self.retry(countdown=60, exc=exc)
        else:
            logger.error(f"任务 {self.request.id} 达到最大重试次数，放弃执行")
            raise exc
