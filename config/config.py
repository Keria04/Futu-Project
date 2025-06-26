# 配置参数，直接以变量形式暴露

device = "cpu"  # 使用 "cuda" 或 "cpu"
pretrain = True  # 是否加载预训练模型
model_type = "resnet50"  # torchvision.models 里的模型名
input_size = 224  # 输入图像的大小
batchsize = 128
normalize_mean = [0.485, 0.456, 0.406]  # 图像预处理的均值
normalize_std = [0.229, 0.224, 0.225]   # 图像预处理的标准差

# config/faiss_config.py
import os
BASE_DIR = os.path.abspath(os.getcwd())
# print("当前工作目录:", BASE_DIR)

# 特征文件路径
FEATURE_PATH = os.path.join(BASE_DIR, "data", "features.npy")
# 图像 ID 文件路径（可选）
ID_PATH = os.path.join(BASE_DIR, "data", "ids.npy")
# FAISS 索引文件夹路径
INDEX_FOLDER = os.path.join(BASE_DIR, "data", "indexes")
# 特征维度（如 ResNet 输出为 512）
VECTOR_DIM = 2048
# IVF 索引中的聚类数量（影响召回速度与精度）
N_LIST = 5

#用于增加新图片的特征文件路径
NEW_FEATURE_PATH = os.path.join(BASE_DIR, "data", "new_features.npy")
NEW_ID_PATH = os.path.join(BASE_DIR, "data", "new_ids.npy")

# 上传图片的位置
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data', 'uploads')

# 数据集目录
DATASET_DIR = os.path.join(BASE_DIR, 'datasets')

# 是否允许远程计算（默认启用，但会进行实时检测）
# 如果Worker启动有问题，可以临时设置为 False
DISTRIBUTED_AVAILABLE = True  # 改为 False 可禁用分布式计算

# Redis配置
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_BROKER_DB = 0
REDIS_BACKEND_DB = 1

# Celery配置
CELERY_TASK_TIME_LIMIT = 300  # 5分钟超时
CELERY_TASK_SOFT_TIME_LIMIT = 240  # 4分钟软超时
CELERY_MAX_RETRIES = 3  # 最大重试次数
# 相似度转换SIGMA超参数，越大缓冲性越强
SIMILARITY_SIGMA=10.0

# -----------数据库相关-----------
DATABASE_PATH = os.path.join(BASE_DIR, "data", "main.db")  # 数据库文件名