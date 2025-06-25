"""
数据库接口定义 - 符合设计模式的抽象接口
定义了所有数据库操作的抽象方法，确保实现类遵循统一的接口规范
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union


class DatabaseInterface(ABC):
    """数据库操作抽象接口"""
    
    @abstractmethod
    def connect(self) -> None:
        """建立数据库连接"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """关闭数据库连接"""
        pass
    
    @abstractmethod
    def execute(self, query: str, params: Tuple = ()) -> Any:
        """执行SQL语句"""
        pass
    
    @abstractmethod
    def execute_many(self, query: str, seq_of_params: List[Tuple]) -> Any:
        """批量执行SQL语句"""
        pass
    
    @abstractmethod
    def commit(self) -> None:
        """提交事务"""
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """回滚事务"""
        pass
    
    @abstractmethod
    def query_one(self, table: str, columns: str = '*', where: Optional[Dict] = None) -> Optional[Tuple]:
        """查询单条记录"""
        pass
    
    @abstractmethod
    def query_multi(self, table: str, columns: str = '*', where: Optional[Dict] = None, 
                   order_by: Optional[str] = None, limit: Optional[int] = None) -> List[Tuple]:
        """查询多条记录"""
        pass
    
    @abstractmethod
    def insert_one(self, table: str, data: Dict[str, Any]) -> int:
        """插入单条记录"""
        pass
    
    @abstractmethod
    def insert_multi(self, table: str, data_list: List[Dict[str, Any]]) -> int:
        """批量插入多条记录"""
        pass
    
    @abstractmethod
    def update(self, table: str, data: Dict[str, Any], where: Optional[Dict] = None) -> int:
        """更新记录"""
        pass
    
    @abstractmethod
    def delete(self, table: str, where: Dict[str, Any]) -> int:
        """删除记录"""
        pass
    
    @abstractmethod
    def create_tables(self) -> None:
        """创建数据库表结构"""
        pass


class DatasetRepositoryInterface(ABC):
    """数据集仓储接口"""
    
    @abstractmethod
    def create_dataset(self, name: str, description: str = "") -> int:
        """创建新数据集"""
        pass
    
    @abstractmethod
    def get_dataset_by_id(self, dataset_id: int) -> Optional[Dict]:
        """根据ID获取数据集"""
        pass
    
    @abstractmethod
    def get_dataset_by_name(self, name: str) -> Optional[Dict]:
        """根据名称获取数据集"""
        pass
    
    @abstractmethod
    def get_all_datasets(self) -> List[Dict]:
        """获取所有数据集"""
        pass
    
    @abstractmethod
    def update_dataset(self, dataset_id: int, data: Dict[str, Any]) -> bool:
        """更新数据集信息"""
        pass
    
    @abstractmethod
    def delete_dataset(self, dataset_id: int) -> bool:
        """删除数据集"""
        pass
    
    @abstractmethod
    def get_dataset_stats(self, dataset_id: int) -> Dict:
        """获取数据集统计信息"""
        pass


class ImageRepositoryInterface(ABC):
    """图片仓储接口"""
    
    @abstractmethod
    def add_image(self, dataset_id: int, filename: str, file_path: str, 
                 file_size: int = 0, checksum: str = "") -> int:
        """添加图片到数据集"""
        pass
    
    @abstractmethod
    def get_image_by_id(self, image_id: int) -> Optional[Dict]:
        """根据ID获取图片信息"""
        pass
    
    @abstractmethod
    def get_images_by_dataset(self, dataset_id: int) -> List[Dict]:
        """获取数据集中的所有图片"""
        pass
    
    @abstractmethod
    def get_images_by_dataset_name(self, dataset_name: str) -> List[Dict]:
        """根据数据集名称获取图片"""
        pass
    
    @abstractmethod
    def update_image(self, image_id: int, data: Dict[str, Any]) -> bool:
        """更新图片信息"""
        pass
    
    @abstractmethod
    def delete_image(self, image_id: int) -> bool:
        """删除图片"""
        pass
    
    @abstractmethod
    def delete_images_by_dataset(self, dataset_id: int) -> int:
        """删除数据集中的所有图片"""
        pass


class DatabaseManagerInterface(ABC):
    """数据库管理器接口 - 组合多个仓储接口"""
    
    @abstractmethod
    def get_dataset_repository(self) -> DatasetRepositoryInterface:
        """获取数据集仓储"""
        pass
    
    @abstractmethod
    def get_image_repository(self) -> ImageRepositoryInterface:
        """获取图片仓储"""
        pass
    
    @abstractmethod
    def initialize(self) -> None:
        """初始化数据库"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """关闭数据库连接"""
        pass
