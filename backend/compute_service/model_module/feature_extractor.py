import os
import sys
# 添加项目根路径，便于导入 config 和模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    import torch
    from torchvision import transforms, models
    import torch.nn as nn
    from PIL import Image
    from compute_service.config import device, pretrain, model_type, input_size, batchsize, normalize_mean, normalize_std
    TORCH_AVAILABLE = True
except ImportError as e:
    print(f"PyTorch not available: {e}")
    TORCH_AVAILABLE = False


class FeatureExtractor(object):
    def __init__(self):
        """
        外部接口：初始化
        """
        if not TORCH_AVAILABLE:
            print("警告：PyTorch不可用，特征提取器将无法工作")
            return
            
        self.device = device
        self.pretrain = pretrain
        self.model_type = model_type
        self.input_size = input_size
        self.normalize_mean = normalize_mean
        self.normalize_std = normalize_std
        self.batchsize = batchsize
        
        # 延迟加载模型（避免初始化时的错误）
        self.model = None
        self.data_transforms = None

    def _lazy_init(self):
        """延迟初始化模型和变换"""
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch不可用")
            
        if self.model is None:
            # 动态加载模型
            self.model = self._load_model(self.model_type, self.pretrain)
            if hasattr(self.model, 'fc'):
                self.model.fc = nn.Identity()

            # 设置数据变换
            self.data_transforms = transforms.Compose([
                transforms.Resize((self.input_size, self.input_size)),
                transforms.ToTensor(),
                transforms.Normalize(self.normalize_mean, self.normalize_std)
            ])

    def _load_model(self, model_type, pretrain):
        """
        加载模型
        """
        try:
            model = getattr(models, model_type)(pretrained=pretrain)
            model.to(self.device)
            model.eval()
            return model
        except AttributeError:
            raise ValueError(f"Model type '{model_type}' is not supported")

    def get_dimension(self):
        """
        获取特征向量维度
        """
        if not TORCH_AVAILABLE:
            return 2048  # 默认维度
            
        self._lazy_init()
        # 使用一个假的输入来获取特征维度
        dummy_input = torch.randn(1, 3, self.input_size, self.input_size).to(self.device)
        with torch.no_grad():
            features = self.model(dummy_input)
        return features.shape[1]

    def calculate(self, image):
        """
        计算单个图像的特征向量
        """
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch不可用")
            
        self._lazy_init()
        
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        elif isinstance(image, Image.Image):
            image = image.convert('RGB')
        
        # 应用数据变换
        image_tensor = self.data_transforms(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            features = self.model(image_tensor)
        
        return features.cpu().numpy().flatten()

    def calculate_batch(self, image_list):
        """
        批量计算图像特征向量
        """
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch不可用")
            
        self._lazy_init()
        
        processed_images = []
        
        for image in image_list:
            if isinstance(image, str):
                img = Image.open(image).convert('RGB')
            elif isinstance(image, Image.Image):
                img = image.convert('RGB')
            else:
                continue
            
            img_tensor = self.data_transforms(img)
            processed_images.append(img_tensor)
        
        if not processed_images:
            return []
        
        # 批量处理
        batch_tensor = torch.stack(processed_images).to(self.device)
        
        with torch.no_grad():
            features = self.model(batch_tensor)
        
        return features.cpu().numpy()

    def get_output_dim(self):
        """
        获取输出特征维度
        """
        return self.get_dimension()


# 创建单例实例
feature_extractor = FeatureExtractor()
