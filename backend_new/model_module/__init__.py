"""
model_module - 独立的特征提取模块

这个模块提供了图像特征提取功能，不依赖外部配置文件。
包含：
- ModelConfig: 内部配置类
- feature_extractor: 特征提取器类
"""

try:
    from .feature_extractor import feature_extractor, ModelConfig
    
    __all__ = [
        'feature_extractor',
        'ModelConfig'
    ]
except ImportError as e:
    print(f"模型模块导入失败: {e}")
    __all__ = []


def create_feature_extractor(device="cpu", model_type="resnet50", input_size=224, pretrain=True, 
                           batchsize=128, normalize_mean=None, normalize_std=None):
    """
    便利函数：创建特征提取器实例
    
    :param device: 设备类型 "cpu" 或 "cuda"
    :param model_type: 模型类型，如 "resnet50"
    :param input_size: 输入图像大小
    :param pretrain: 是否使用预训练模型
    :param batchsize: 批处理大小
    :param normalize_mean: 图像归一化均值
    :param normalize_std: 图像归一化标准差
    :return: feature_extractor 实例
    """
    if normalize_mean is None:
        normalize_mean = [0.485, 0.456, 0.406]
    if normalize_std is None:
        normalize_std = [0.229, 0.224, 0.225]
    
    config = ModelConfig()
    config.device = device
    config.model_type = model_type
    config.input_size = input_size
    config.pretrain = pretrain
    config.batchsize = batchsize
    config.normalize_mean = normalize_mean
    config.normalize_std = normalize_std
    
    return feature_extractor(config)
