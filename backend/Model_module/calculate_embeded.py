import os
import sys
import torch
from torchvision import transforms, models
from torch.utils.data import DataLoader
import torch.nn as nn
from PIL import Image
from tqdm import tqdm
# 添加项目根路径，便于导入 config 和模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from config import config


class calaculate_embeded(object):
    def __init__(self):
        """
        外部接口：初始化，直接使用 config.py 中的配置变量
        """
        self.device = config.device
        self.pretrain = config.pretrain
        self.model_type = config.model_type
        self.input_size = config.input_size
        self.normalize_mean = config.normalize_mean
        self.normalize_std = config.normalize_std
        self.batchsize = config.batchsize

        # 动态加载模型
        self.model = self._load_model(self.model_type, self.pretrain)
        self.model.fc = nn.Identity()

        # 图像预处理
        self.data_transforms = transforms.Compose([
            transforms.Resize((self.input_size, self.input_size)),
            transforms.ToTensor(),
            transforms.Normalize(self.normalize_mean, self.normalize_std)
        ])
        self.dimension = self.get_output_dim()

    def _load_model(self, model_type, pretrain):
        """
        内部函数：根据模型类型和预训练参数动态加载模型
        """
        if not hasattr(models, model_type):
            raise ValueError(f"model_type '{model_type}' not found in torchvision.models")
        model_fn = getattr(models, model_type)
        model = model_fn(pretrained=pretrain)
        return model

    def get_dimension(self):
        """
        外部接口：获取模型输出特征维度
        """
        return self.dimension

    def calculate(self, image):
        """
        外部接口：计算单张图片的特征向量
        """
        model = self.model.to(self.device)
        model.eval()
        image = image.convert('RGB')
        image = self.data_transforms(image)
        image_tensor = image.unsqueeze(0).to(self.device)
        with torch.no_grad():
            output = model(image_tensor)
        return output.squeeze(0).cpu().numpy().astype('float32')

    def calculate_batch(self, image_list):
        """
        外部接口：批量计算图片特征向量
        """
        model = self.model.to(self.device)
        model.eval()
        batchsize = self.batchsize

        all_outputs = []

        for i in tqdm(range(0, len(image_list), batchsize), desc="Processing batches"):
            batch_img = image_list[i:i + batchsize]
            processed_images = []
            for img in batch_img:
                img = img.convert('RGB')
                img = self.data_transforms(img)
                processed_images.append(img)

            image_tensor = torch.stack(processed_images).to(self.device)

            with torch.no_grad():
                output = model(image_tensor)
                all_outputs.append(output.cpu())

        return torch.cat(all_outputs, dim=0).cpu().numpy().astype('float32')

    def get_output_dim(self):
        """
        内部函数：获取模型输出特征维度（供初始化时调用）
        """
        dummy_input = torch.randn(1, 3, self.input_size, self.input_size).to(self.device)
        model = self.model.to(self.device)
        model.eval()
        with torch.no_grad():
            output = model(dummy_input)
            output = output.view(output.size(0), -1)
        return output.shape[1]
