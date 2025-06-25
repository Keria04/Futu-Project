#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索引接口 - 使用GOF设计模式重构的Faiss索引模块接口

采用的设计模式：
1. 工厂模式(Factory Pattern) - 创建不同类型的索引器
2. 策略模式(Strategy Pattern) - 不同的索引策略
3. 外观模式(Facade Pattern) - 简化复杂调用
4. 建造者模式(Builder Pattern) - 构建配置对象
5. 适配器模式(Adapter Pattern) - 适配不同配置方式
6. 命令模式(Command Pattern) - 封装索引操作
7. 观察者模式(Observer Pattern) - 监听索引操作状态
"""

from abc import ABC, abstractmethod
from typing import Union, List, Optional, Dict, Any, Tuple, Callable
import numpy as np
import os
from enum import Enum


# ==================== 策略模式 - 索引策略接口 ====================
class IndexStrategy(ABC):
    """索引策略抽象接口"""
    
    @abstractmethod
    def create_indexer(self, config: 'IndexConfig') -> 'VectorIndexer':
        """创建索引器"""
        pass
    
    @abstractmethod
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """获取策略名称"""
        pass


# ==================== 具体策略实现 ====================
class FlatIndexStrategy(IndexStrategy):
    """平坦索引策略 - 精确搜索"""
    
    def create_indexer(self, config: 'IndexConfig') -> 'VectorIndexer':
        return FlatIndexerAdapter(config)
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            'use_ivf': False,
            'metric_type': 'L2',
            'description': 'Flat exact search'
        }
    
    def get_strategy_name(self) -> str:
        return "FlatIndex"


class IVFIndexStrategy(IndexStrategy):
    """IVF索引策略 - 近似搜索"""
    
    def create_indexer(self, config: 'IndexConfig') -> 'VectorIndexer':
        return IVFIndexerAdapter(config)
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            'use_ivf': True,
            'metric_type': 'L2',
            'nlist': None,  # 自动计算
            'nprobe': None,  # 自动计算
            'description': 'IVF approximate search'
        }
    
    def get_strategy_name(self) -> str:
        return "IVFIndex"


class HNSWIndexStrategy(IndexStrategy):
    """HNSW索引策略 - 高性能近似搜索"""
    
    def create_indexer(self, config: 'IndexConfig') -> 'VectorIndexer':
        return HNSWIndexerAdapter(config)
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            'use_ivf': False,
            'metric_type': 'L2',
            'M': 16,
            'efConstruction': 200,
            'efSearch': 100,
            'description': 'HNSW high-performance search'
        }
    
    def get_strategy_name(self) -> str:
        return "HNSWIndex"


# ==================== 工厂模式 - 索引策略工厂 ====================
class IndexStrategyFactory:
    """索引策略工厂"""
    
    _strategies = {
        'flat': FlatIndexStrategy,
        'ivf': IVFIndexStrategy,
        'hnsw': HNSWIndexStrategy,
    }
    
    @classmethod
    def create_strategy(cls, strategy_type: str) -> IndexStrategy:
        """创建索引策略"""
        strategy_type = strategy_type.lower()
        if strategy_type in cls._strategies:
            return cls._strategies[strategy_type]()
        else:
            # 默认使用IVF策略
            return IVFIndexStrategy()
    
    @classmethod
    def register_strategy(cls, strategy_type: str, strategy_class: type):
        """注册新的索引策略"""
        cls._strategies[strategy_type.lower()] = strategy_class
    
    @classmethod
    def get_available_strategies(cls) -> List[str]:
        """获取可用的策略类型"""
        return list(cls._strategies.keys())


# ==================== 建造者模式 - 配置建造者 ====================
class IndexConfigBuilder:
    """索引配置建造者"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """重置建造者"""
        self._config = IndexConfig()
        return self
    
    def set_base_dir(self, base_dir: str):
        """设置基础目录"""
        self._config.base_dir = base_dir
        return self
    
    def set_vector_dim(self, vector_dim: int):
        """设置向量维度"""
        self._config.vector_dim = vector_dim
        return self
    
    def set_strategy_type(self, strategy_type: str):
        """设置策略类型"""
        self._config.strategy_type = strategy_type
        return self
    
    def set_similarity_threshold(self, threshold: float):
        """设置相似度阈值"""
        self._config.similarity_threshold = threshold
        return self
    
    def set_index_folder(self, folder: str):
        """设置索引文件夹"""
        self._config.index_folder = folder
        return self
    
    def set_metric_type(self, metric_type: str):
        """设置距离度量类型"""
        self._config.metric_type = metric_type
        return self
    
    def enable_ivf(self, nlist: Optional[int] = None, nprobe: Optional[int] = None):
        """启用IVF"""
        self._config.use_ivf = True
        if nlist is not None:
            self._config.nlist = nlist
        if nprobe is not None:
            self._config.nprobe = nprobe
        return self
    
    def build(self) -> 'IndexConfig':
        """构建配置对象"""
        config = self._config
        self.reset()
        return config


# ==================== 适配器模式 - 配置适配器 ====================
class IndexConfig:
    """索引配置类 - 使用适配器模式适配内部配置"""
    
    def __init__(self):
        # 公共接口属性
        self.base_dir: str = os.getcwd()
        self.vector_dim: int = 2048
        self.strategy_type: str = "ivf"
        self.similarity_threshold: float = 10.0
        self.index_folder: Optional[str] = None
        self.metric_type: str = "L2"
        
        # IVF相关配置
        self.use_ivf: bool = True
        self.nlist: Optional[int] = None
        self.nprobe: Optional[int] = None
        
        # HNSW相关配置
        self.M: int = 16
        self.efConstruction: int = 200
        self.efSearch: int = 100
        
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
        from faiss_module import FaissConfig
        
        self._internal_config = FaissConfig()
        
        # 适配公共属性
        if self.base_dir:
            self._internal_config.BASE_DIR = self.base_dir
            # 重新计算相关路径
            self._internal_config.FEATURE_PATH = os.path.join(self.base_dir, "data", "features.npy")
            self._internal_config.ID_PATH = os.path.join(self.base_dir, "data", "ids.npy")
            self._internal_config.INDEX_FOLDER = self.index_folder or os.path.join(self.base_dir, "data", "indexes")
            self._internal_config.NEW_FEATURE_PATH = os.path.join(self.base_dir, "data", "new_features.npy")
            self._internal_config.NEW_ID_PATH = os.path.join(self.base_dir, "data", "new_ids.npy")
            self._internal_config.UPLOAD_FOLDER = os.path.join(self.base_dir, 'data', 'uploads')
            self._internal_config.DATASET_DIR = os.path.join(self.base_dir, 'datasets')
        
        self._internal_config.VECTOR_DIM = self.vector_dim
        self._internal_config.SIMILARITY_SIGMA = self.similarity_threshold
    
    def update_from_dict(self, config_dict: Dict[str, Any]):
        """从字典更新配置"""
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self._internal_config = None  # 重置内部配置


# ==================== 观察者模式 - 索引操作观察者 ====================
class IndexObserver(ABC):
    """索引操作观察者接口"""
    
    @abstractmethod
    def on_build_start(self, num_vectors: int):
        """构建开始"""
        pass
    
    @abstractmethod
    def on_build_progress(self, current: int, total: int):
        """构建进度"""
        pass
    
    @abstractmethod
    def on_build_complete(self, index_path: str):
        """构建完成"""
        pass
    
    @abstractmethod
    def on_search_start(self, query_count: int):
        """搜索开始"""
        pass
    
    @abstractmethod
    def on_search_complete(self, results_count: int):
        """搜索完成"""
        pass


class DefaultIndexObserver(IndexObserver):
    """默认索引观察者"""
    
    def on_build_start(self, num_vectors: int):
        print(f"开始构建索引，向量数量: {num_vectors}")
    
    def on_build_progress(self, current: int, total: int):
        if total > 0:
            progress = (current / total) * 100
            print(f"构建进度: {progress:.1f}% ({current}/{total})")
    
    def on_build_complete(self, index_path: str):
        print(f"索引构建完成: {index_path}")
    
    def on_search_start(self, query_count: int):
        print(f"开始搜索，查询数量: {query_count}")
    
    def on_search_complete(self, results_count: int):
        print(f"搜索完成，结果数量: {results_count}")


# ==================== 命令模式 - 索引操作命令 ====================
class IndexCommand(ABC):
    """索引操作命令接口"""
    
    @abstractmethod
    def execute(self) -> Any:
        """执行命令"""
        pass
    
    @abstractmethod
    def undo(self) -> Any:
        """撤销命令"""
        pass


class BuildIndexCommand(IndexCommand):
    """构建索引命令"""
    
    def __init__(self, indexer: 'VectorIndexer', features: np.ndarray, 
                 ids: np.ndarray, index_name: str):
        self.indexer = indexer
        self.features = features
        self.ids = ids
        self.index_name = index_name
        self.backup_path = None
    
    def execute(self) -> str:
        """执行构建"""
        return self.indexer.build_index(self.features, self.ids, self.index_name)
    
    def undo(self) -> bool:
        """撤销构建（删除索引文件）"""
        index_path = os.path.join(self.indexer.get_config().index_folder, self.index_name)
        if os.path.exists(index_path):
            os.remove(index_path)
            return True
        return False


class SearchIndexCommand(IndexCommand):
    """搜索索引命令"""
    
    def __init__(self, indexer: 'VectorIndexer', query_features: np.ndarray,
                 index_names: List[str], top_k: int = 5):
        self.indexer = indexer
        self.query_features = query_features
        self.index_names = index_names
        self.top_k = top_k
        self.last_results = None
    
    def execute(self) -> Tuple[List[int], List[float]]:
        """执行搜索"""
        self.last_results = self.indexer.search_index(
            self.query_features, self.index_names, self.top_k
        )
        return self.last_results
    
    def undo(self) -> Any:
        """搜索命令无法撤销"""
        return self.last_results


# ==================== 向量索引器接口 ====================
class VectorIndexer(ABC):
    """向量索引器抽象接口"""
    
    @abstractmethod
    def build_index(self, features: np.ndarray, ids: np.ndarray, index_name: str) -> str:
        """构建索引"""
        pass
    
    @abstractmethod
    def search_index(self, query_features: np.ndarray, index_names: List[str], 
                    top_k: int = 5) -> Tuple[List[int], List[float]]:
        """搜索索引"""
        pass
    
    @abstractmethod
    def update_index(self, new_features: np.ndarray, new_ids: np.ndarray, 
                    index_name: str) -> bool:
        """更新索引"""
        pass
    
    @abstractmethod
    def delete_from_index(self, ids_to_delete: np.ndarray, index_name: str) -> bool:
        """从索引中删除"""
        pass
    
    @abstractmethod
    def get_index_info(self, index_name: str) -> Dict[str, Any]:
        """获取索引信息"""
        pass
    
    @abstractmethod
    def get_config(self) -> IndexConfig:
        """获取配置"""
        pass
    
    @abstractmethod
    def add_observer(self, observer: IndexObserver):
        """添加观察者"""
        pass
    
    @abstractmethod
    def remove_observer(self, observer: IndexObserver):
        """移除观察者"""
        pass


# ==================== 适配器模式 - 索引器适配器 ====================
class BaseIndexerAdapter(VectorIndexer):
    """基础索引器适配器"""
    
    def __init__(self, config: IndexConfig):
        self._config = config
        self._observers: List[IndexObserver] = []
    
    def _notify_observers(self, method: str, *args, **kwargs):
        """通知观察者"""
        for observer in self._observers:
            if hasattr(observer, method):
                getattr(observer, method)(*args, **kwargs)
    
    def add_observer(self, observer: IndexObserver):
        """添加观察者"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: IndexObserver):
        """移除观察者"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def get_config(self) -> IndexConfig:
        """获取配置"""
        return self._config
    
    def build_index(self, features: np.ndarray, ids: np.ndarray, index_name: str) -> str:
        """构建索引"""
        from faiss_module import build_index
        
        self._notify_observers('on_build_start', len(features))
        
        # 确保索引目录存在
        os.makedirs(self._config.internal_config.index_folder, exist_ok=True)
        
        # 构建索引
        build_index(features, ids, index_name, self._config.internal_config)
        
        index_path = os.path.join(self._config.internal_config.index_folder, index_name)
        self._notify_observers('on_build_complete', index_path)
        
        return index_path
    
    def search_index(self, query_features: np.ndarray, index_names: List[str], 
                    top_k: int = 5) -> Tuple[List[int], List[float]]:
        """搜索索引"""
        from faiss_module import search_index
        
        self._notify_observers('on_search_start', query_features.shape[0])
        
        results, similarities = search_index(
            query_features, index_names, top_k, self._config.internal_config
        )
        
        self._notify_observers('on_search_complete', len(results))
        
        return results, similarities
    
    def update_index(self, new_features: np.ndarray, new_ids: np.ndarray, 
                    index_name: str) -> bool:
        """更新索引"""
        from faiss_module import update_index
        
        try:
            update_index(new_features, new_ids, index_name, self._config.internal_config)
            return True
        except Exception as e:
            print(f"更新索引失败: {e}")
            return False
    
    def delete_from_index(self, ids_to_delete: np.ndarray, index_name: str) -> bool:
        """从索引中删除"""
        # 这里需要实现删除功能，可能需要在faiss_module中添加
        # 暂时返回False表示未实现
        print("删除功能暂未实现")
        return False
    
    def get_index_info(self, index_name: str) -> Dict[str, Any]:
        """获取索引信息"""
        index_path = os.path.join(self._config.internal_config.index_folder, index_name)
        
        info = {
            'index_name': index_name,
            'index_path': index_path,
            'exists': os.path.exists(index_path),
            'config': self._config.__dict__        }
        
        if info['exists']:
            stat = os.stat(index_path)
            info['file_size'] = stat.st_size
            info['modified_time'] = stat.st_mtime
        
        return info


class FlatIndexerAdapter(BaseIndexerAdapter):
    """平坦索引适配器"""
    
    def __init__(self, config: IndexConfig):
        super().__init__(config)
        # 强制设置为非IVF模式
        self._config.use_ivf = False


class IVFIndexerAdapter(BaseIndexerAdapter):
    """IVF索引适配器"""
    
    def __init__(self, config: IndexConfig):
        super().__init__(config)
        # 强制设置为IVF模式
        self._config.use_ivf = True


class HNSWIndexerAdapter(BaseIndexerAdapter):
    """HNSW索引适配器"""
    
    def __init__(self, config: IndexConfig):
        super().__init__(config)
        # HNSW配置
        self._config.use_ivf = False
        # 注意：当前faiss_module可能不支持HNSW，这里只是预留接口


# ==================== 外观模式 - 索引外观 ====================
class IndexFacade:
    """索引外观类 - 简化复杂的索引操作"""
    
    def __init__(self):
        self._strategy_factory = IndexStrategyFactory()
        self._config_builder = IndexConfigBuilder()
        self._command_history: List[IndexCommand] = []
    
    def create_indexer(
        self,
        vector_dim: int,
        strategy_type: str = "ivf",
        base_dir: Optional[str] = None,
        similarity_threshold: float = 10.0,
        **kwargs
    ) -> VectorIndexer:
        """创建索引器 - 简化接口"""
        
        # 使用建造者模式构建配置
        builder = self._config_builder.set_vector_dim(vector_dim).set_strategy_type(strategy_type)
        
        if base_dir:
            builder.set_base_dir(base_dir)
        
        builder.set_similarity_threshold(similarity_threshold)
        
        # 处理IVF相关参数
        if strategy_type.lower() == "ivf" and 'use_ivf' not in kwargs:
            builder.enable_ivf()
        
        config = builder.build()
        
        # 处理其他参数
        if kwargs:
            config.update_from_dict(kwargs)
        
        # 使用工厂模式创建策略
        strategy = self._strategy_factory.create_strategy(strategy_type)
        
        # 创建索引器
        indexer = strategy.create_indexer(config)
        
        # 添加默认观察者
        indexer.add_observer(DefaultIndexObserver())
        
        return indexer
    
    def create_indexer_from_config(self, config: Union[IndexConfig, Dict[str, Any]]) -> VectorIndexer:
        """从配置创建索引器"""
        if isinstance(config, dict):
            index_config = IndexConfig()
            index_config.update_from_dict(config)
        else:
            index_config = config
        
        strategy = self._strategy_factory.create_strategy(index_config.strategy_type)
        indexer = strategy.create_indexer(index_config)
        indexer.add_observer(DefaultIndexObserver())
        
        return indexer
    
    def execute_command(self, command: IndexCommand) -> Any:
        """执行命令"""
        result = command.execute()
        self._command_history.append(command)
        return result
    
    def undo_last_command(self) -> Any:
        """撤销最后一个命令"""
        if self._command_history:
            command = self._command_history.pop()
            return command.undo()
        return None
    
    def get_available_strategies(self) -> List[str]:
        """获取可用的策略类型"""
        return self._strategy_factory.get_available_strategies()
    
    def register_strategy(self, strategy_type: str, strategy_class: type):
        """注册新的策略"""
        self._strategy_factory.register_strategy(strategy_type, strategy_class)


# ==================== 单例模式 - 全局索引管理器 ====================
class IndexManager:
    """索引管理器单例"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._facade = IndexFacade()
            self._indexers = {}  # 缓存索引器
            self._initialized = True
    
    def get_indexer(
        self,
        vector_dim: int,
        strategy_type: str = "ivf",
        base_dir: Optional[str] = None,
        cache_key: Optional[str] = None,
        **kwargs
    ) -> VectorIndexer:
        """获取索引器（支持缓存）"""
        
        if cache_key is None:
            cache_key = f"{strategy_type}_{vector_dim}_{base_dir or 'default'}"
        
        if cache_key not in self._indexers:
            self._indexers[cache_key] = self._facade.create_indexer(
                vector_dim=vector_dim,
                strategy_type=strategy_type,
                base_dir=base_dir,
                **kwargs
            )
        
        return self._indexers[cache_key]
    
    def clear_cache(self):
        """清空缓存"""
        self._indexers.clear()
    
    def get_facade(self) -> IndexFacade:
        """获取外观对象"""
        return self._facade


# ==================== 便利函数 - 向后兼容 ====================
def create_vector_indexer(**kwargs) -> VectorIndexer:
    """创建向量索引器的便利函数"""
    manager = IndexManager()
    return manager.get_indexer(**kwargs)


def create_index_config(**kwargs) -> IndexConfig:
    """创建索引配置的便利函数"""
    config = IndexConfig()
    if kwargs:
        config.update_from_dict(kwargs)
    return config


def get_index_manager() -> IndexManager:
    """获取索引管理器实例"""
    return IndexManager()


# 向后兼容的便利函数
def build_index(features: np.ndarray, ids: np.ndarray, index_name: str, 
               vector_dim: int, base_dir: Optional[str] = None, **kwargs) -> str:
    """构建索引的便利函数"""
    indexer = create_vector_indexer(
        vector_dim=vector_dim, 
        base_dir=base_dir,
        **kwargs
    )
    return indexer.build_index(features, ids, index_name)


def search_index(query_features: np.ndarray, index_names: List[str], 
                vector_dim: int, top_k: int = 5, base_dir: Optional[str] = None,
                **kwargs) -> Tuple[List[int], List[float]]:
    """搜索索引的便利函数"""
    indexer = create_vector_indexer(
        vector_dim=vector_dim,
        base_dir=base_dir,
        **kwargs
    )
    return indexer.search_index(query_features, index_names, top_k)


# ==================== 导出接口 ====================
__all__ = [
    # 主要接口
    'VectorIndexer',
    'IndexConfig',
    'IndexFacade',
    'IndexManager',
    
    # 设计模式类
    'IndexStrategy',
    'IndexStrategyFactory',
    'IndexConfigBuilder',
    'IndexObserver',
    'IndexCommand',
    
    # 具体实现
    'FlatIndexStrategy',
    'IVFIndexStrategy',
    'HNSWIndexStrategy',
    'BaseIndexerAdapter',
    'FlatIndexerAdapter',
    'IVFIndexerAdapter',
    'HNSWIndexerAdapter',
    'DefaultIndexObserver',
    'BuildIndexCommand',
    'SearchIndexCommand',
    
    # 便利函数
    'create_vector_indexer',
    'create_index_config',
    'get_index_manager',
    'build_index',
    'search_index',
]
