"""
faiss_config.py - Faiss模块内部配置
"""
import os


class FaissConfig:
    """Faiss模块配置类，内部配置不依赖外部"""
    def __init__(self):
        # 获取项目根目录（向上3级目录）
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 特征文件路径
        self.FEATURE_PATH = os.path.join(self.BASE_DIR, "data", "features.npy")
        # 图像 ID 文件路径（可选）
        self.ID_PATH = os.path.join(self.BASE_DIR, "data", "ids.npy")
        # FAISS 索引文件夹路径
        self.INDEX_FOLDER = os.path.join(self.BASE_DIR, "data", "indexes")
        # 特征维度（如 ResNet 输出为 2048）
        self.VECTOR_DIM = 2048
        # IVF 索引中的聚类数量（影响召回速度与精度）
        self.N_LIST = 5
        
        # 用于增加新图片的特征文件路径
        self.NEW_FEATURE_PATH = os.path.join(self.BASE_DIR, "data", "new_features.npy")
        self.NEW_ID_PATH = os.path.join(self.BASE_DIR, "data", "new_ids.npy")
        
        # 上传图片的位置
        self.UPLOAD_FOLDER = os.path.join(self.BASE_DIR, 'data', 'uploads')
        
        # 数据集目录
        self.DATASET_DIR = os.path.join(self.BASE_DIR, 'datasets')
        
        # 相似度转换SIGMA超参数，越大缓冲性越强
        self.SIMILARITY_SIGMA = 10.0
    
    @property
    def index_folder(self):
        return self.INDEX_FOLDER
    
    @property
    def vector_dim(self):
        return self.VECTOR_DIM
    
    @property
    def feature_path(self):
        return self.FEATURE_PATH
    
    @property
    def id_path(self):
        return self.ID_PATH
    
    @property
    def new_feature_path(self):
        return self.NEW_FEATURE_PATH
    
    @property
    def new_id_path(self):
        return self.NEW_ID_PATH
    
    @property
    def similarity_sigma(self):
        return self.SIMILARITY_SIGMA


# 创建默认配置实例
default_config = FaissConfig()
