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
print("当前工作目录:", BASE_DIR)

# 特征文件路径
FEATURE_PATH = os.path.join(BASE_DIR, "data", "features.npy")
# 图像 ID 文件路径（可选）
ID_PATH = os.path.join(BASE_DIR, "data", "ids.npy")
# FAISS 索引文件保存路径
INDEX_PATH = os.path.join(BASE_DIR, "data", "image.index")
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

# 是否允许远程计算
DISTRIBUTED_AVAILABLE = True
# 相似度转换SIGMA超参数，越大缓冲性越强
SIMILARITY_SIGMA=10.0