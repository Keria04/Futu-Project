#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型接口 - 使用GOF设计模式重构的特征提取模块接口

采用的设计模式：
1. 工厂模式(Factory Pattern) - 创建不同类型的特征提取器
2. 策略模式(Strategy Pattern) - 不同的模型策略
3. 外观模式(Facade Pattern) - 简化复杂调用
4. 建造者模式(Builder Pattern) - 构建配置对象
5. 适配器模式(Adapter Pattern) - 适配不同配置方式
"""

from abc import ABC, abstractmethod
from typing import Union, List, Optional, Dict, Any
import numpy as np
from PIL import Image


# ==================== 策略模式 - 模型策略接口 ====================
class ModelStrategy(ABC):
    """模型策略抽象接口"""
    
    @abstractmethod
    def create_extractor(self, config: 'ModelConfig') -> 'FeatureExtractor':
        """创建特征提取器"""
        pass
    
    @abstractmethod
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        pass


# ==================== 具体策略实现 ====================
class ResNetStrategy(ModelStrategy):
    """ResNet模型策略"""
    
    def create_extractor(self, config: 'ModelConfig') -> 'FeatureExtractor':
        from model_module import feature_extractor
        return ResNetExtractorAdapter(feature_extractor(config._internal_config))
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            'model_type': 'resnet50',
            'input_size': 224,
            'pretrain': True
        }


class EfficientNetStrategy(ModelStrategy):
    """EfficientNet模型策略（预留扩展）"""
    
    def create_extractor(self, config: 'ModelConfig') -> 'FeatureExtractor':
        # 未来可以扩展其他模型
        from model_module import feature_extractor
        return EfficientNetExtractorAdapter(feature_extractor(config._internal_config))
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            'model_type': 'efficientnet_b0',  # 假设支持
            'input_size': 224,
            'pretrain': True
        }


# ==================== 工厂模式 - 模型工厂 ====================
class ModelStrategyFactory:
    """模型策略工厂"""
    
    _strategies = {
        'resnet': ResNetStrategy,
        'resnet18': ResNetStrategy,
        'resnet34': ResNetStrategy,
        'resnet50': ResNetStrategy,
        'resnet101': ResNetStrategy,
        'resnet152': ResNetStrategy,
        'efficientnet': EfficientNetStrategy,
        'efficientnet_b0': EfficientNetStrategy,
    }
    
    @classmethod
    def create_strategy(cls, model_type: str) -> ModelStrategy:
        """创建模型策略"""
        # 根据模型类型选择策略
        for key, strategy_class in cls._strategies.items():
            if model_type.lower().startswith(key.lower()):
                return strategy_class()
        
        # 默认使用ResNet策略
        return ResNetStrategy()
    
    @classmethod
    def register_strategy(cls, model_type: str, strategy_class: type):
        """注册新的模型策略"""
        cls._strategies[model_type] = strategy_class


# ==================== 建造者模式 - 配置建造者 ====================
class ModelConfigBuilder:
    """模型配置建造者"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """重置建造者"""
        self._config = ModelConfig()
        return self
    
    def set_device(self, device: str):
        """设置设备"""
        self._config.device = device
        return self
    
    def set_model_type(self, model_type: str):
        """设置模型类型"""
        self._config.model_type = model_type
        return self
    
    def set_input_size(self, input_size: int):
        """设置输入尺寸"""
        self._config.input_size = input_size
        return self
    
    def set_batch_size(self, batch_size: int):
        """设置批处理大小"""
        self._config.batch_size = batch_size
        return self
    
    def set_pretrain(self, pretrain: bool):
        """设置是否使用预训练模型"""
        self._config.pretrain = pretrain
        return self
    
    def set_normalize_params(self, mean: List[float], std: List[float]):
        """设置归一化参数"""
        self._config.normalize_mean = mean
        self._config.normalize_std = std
        return self
    
    def build(self) -> 'ModelConfig':
        """构建配置对象"""
        config = self._config
        self.reset()
        return config


# ==================== 适配器模式 - 配置适配器 ====================
class ModelConfig:
    """模型配置类 - 使用适配器模式适配内部配置"""
    
    def __init__(self):
        # 公共接口属性
        self.device: str = "cpu"
        self.model_type: str = "resnet50"
        self.input_size: int = 224
        self.batch_size: int = 128
        self.pretrain: bool = True
        self.normalize_mean: List[float] = [0.485, 0.456, 0.406]
        self.normalize_std: List[float] = [0.229, 0.224, 0.225]
        
        # 内部配置对象（适配器）
        self._internal_config = None
    
    @property
    def internal_config(self):
        """获取内部配置对象"""
        if self._internal_config is None:
            self._create_internal_config()
        return self._internal_config
    
    def _create_internal_config(self):
        """创建内部配置对象"""
        from model_module import ModelConfig as InternalConfig
        
        self._internal_config = InternalConfig()
        self._internal_config.device = self.device
        self._internal_config.model_type = self.model_type
        self._internal_config.input_size = self.input_size
        self._internal_config.batchsize = self.batch_size  # 注意内部使用batchsize
        self._internal_config.pretrain = self.pretrain
        self._internal_config.normalize_mean = self.normalize_mean
        self._internal_config.normalize_std = self.normalize_std
    
    def update_from_dict(self, config_dict: Dict[str, Any]):
        """从字典更新配置"""
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self._internal_config = None  # 重置内部配置


# ==================== 特征提取器接口 ====================
class FeatureExtractor(ABC):
    """特征提取器抽象接口"""
    
    @abstractmethod
    def extract_single(self, image: Image.Image) -> np.ndarray:
        """提取单张图像特征"""
        pass
    
    @abstractmethod
    def extract_batch(self, images: List[Image.Image]) -> np.ndarray:
        """批量提取图像特征"""
        pass
    
    @abstractmethod
    def get_feature_dimension(self) -> int:
        """获取特征维度"""
        pass
    
    @abstractmethod
    def get_config(self) -> ModelConfig:
        """获取配置信息"""
        pass


# ==================== 适配器模式 - 特征提取器适配器 ====================
class BaseExtractorAdapter(FeatureExtractor):
    """基础特征提取器适配器"""
    
    def __init__(self, internal_extractor):
        self._extractor = internal_extractor
        self._config = None
    
    def extract_single(self, image: Image.Image) -> np.ndarray:
        """提取单张图像特征"""
        return self._extractor.calculate(image)
    
    def extract_batch(self, images: List[Image.Image]) -> np.ndarray:
        """批量提取图像特征"""
        return self._extractor.calculate_batch(images)
    
    def get_feature_dimension(self) -> int:
        """获取特征维度"""
        return self._extractor.get_dimension()
    
    def get_config(self) -> ModelConfig:
        """获取配置信息"""
        if self._config is None:
            self._config = ModelConfig()
            # 从内部提取器适配配置
            self._config.device = self._extractor.device
            self._config.model_type = self._extractor.model_type
            self._config.input_size = self._extractor.input_size
            self._config.batch_size = self._extractor.batchsize
            self._config.normalize_mean = self._extractor.normalize_mean
            self._config.normalize_std = self._extractor.normalize_std
        return self._config


class ResNetExtractorAdapter(BaseExtractorAdapter):
    """ResNet特征提取器适配器"""
    pass


class EfficientNetExtractorAdapter(BaseExtractorAdapter):
    """EfficientNet特征提取器适配器"""
    pass


# ==================== 外观模式 - 模型外观 ====================
class ModelFacade:
    """模型外观类 - 简化复杂的模型操作"""
    
    def __init__(self):
        self._strategy_factory = ModelStrategyFactory()
        self._config_builder = ModelConfigBuilder()
    
    def create_extractor(
        self,
        model_type: str = "resnet50",
        device: str = "cpu",
        input_size: int = 224,
        batch_size: int = 128,
        pretrain: bool = True,
        **kwargs
    ) -> FeatureExtractor:
        """创建特征提取器 - 简化接口"""
        
        # 使用建造者模式构建配置
        config = (self._config_builder
                 .set_model_type(model_type)
                 .set_device(device)
                 .set_input_size(input_size)
                 .set_batch_size(batch_size)
                 .set_pretrain(pretrain)
                 .build())
        
        # 处理其他参数
        if kwargs:
            config.update_from_dict(kwargs)
        
        # 使用工厂模式创建策略
        strategy = self._strategy_factory.create_strategy(model_type)
        
        # 创建提取器
        return strategy.create_extractor(config)
    
    def create_extractor_from_config(self, config: Union[ModelConfig, Dict[str, Any]]) -> FeatureExtractor:
        """从配置创建特征提取器"""
        if isinstance(config, dict):
            model_config = ModelConfig()
            model_config.update_from_dict(config)
        else:
            model_config = config
        
        strategy = self._strategy_factory.create_strategy(model_config.model_type)
        return strategy.create_extractor(model_config)
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型类型"""
        return list(self._strategy_factory._strategies.keys())
    
    def register_model_strategy(self, model_type: str, strategy_class: type):
        """注册新的模型策略"""
        self._strategy_factory.register_strategy(model_type, strategy_class)


# ==================== 单例模式 - 全局模型管理器 ====================
class ModelManager:
    """模型管理器单例"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._facade = ModelFacade()
            self._extractors = {}  # 缓存提取器
            self._initialized = True
    
    def get_extractor(
        self,
        model_type: str = "resnet50",
        device: str = "cpu",
        cache_key: Optional[str] = None,
        **kwargs
    ) -> FeatureExtractor:
        """获取特征提取器（支持缓存）"""
        
        if cache_key is None:
            cache_key = f"{model_type}_{device}_{kwargs.get('input_size', 224)}"
        
        if cache_key not in self._extractors:
            self._extractors[cache_key] = self._facade.create_extractor(
                model_type=model_type,
                device=device,
                **kwargs
            )
        
        return self._extractors[cache_key]
    
    def clear_cache(self):
        """清空缓存"""
        self._extractors.clear()
    
    def get_facade(self) -> ModelFacade:
        """获取外观对象"""
        return self._facade


# ==================== 便利函数 - 向后兼容 ====================
def create_feature_extractor(**kwargs) -> FeatureExtractor:
    """创建特征提取器的便利函数"""
    manager = ModelManager()
    return manager.get_extractor(**kwargs)


def create_model_config(**kwargs) -> ModelConfig:
    """创建模型配置的便利函数"""
    config = ModelConfig()
    if kwargs:
        config.update_from_dict(kwargs)
    return config


def get_model_manager() -> ModelManager:
    """获取模型管理器实例"""
    return ModelManager()


# ==================== 导出接口 ====================
__all__ = [
    # 主要接口
    'FeatureExtractor',
    'ModelConfig',
    'ModelFacade',
    'ModelManager',
    
    # 设计模式类
    'ModelStrategy',
    'ModelStrategyFactory',
    'ModelConfigBuilder',
    
    # 具体实现
    'ResNetStrategy',
    'EfficientNetStrategy',
    'BaseExtractorAdapter',
    'ResNetExtractorAdapter',
    'EfficientNetExtractorAdapter',
    
    # 便利函数
    'create_feature_extractor',
    'create_model_config',
    'get_model_manager',
]
