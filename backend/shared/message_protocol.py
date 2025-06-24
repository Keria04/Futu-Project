"""
消息协议定义
定义控制端和计算端之间的通信格式
"""
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
from enum import Enum
import uuid
import json
from datetime import datetime


class TaskType(Enum):
    """任务类型枚举"""
    FEATURE_EXTRACTION = "feature_extraction"
    BATCH_FEATURE_EXTRACTION = "batch_feature_extraction"
    INDEX_BUILD = "index_build"


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskMessage:
    """任务消息基类"""
    task_id: str
    task_type: TaskType
    payload: Dict[str, Any]
    priority: int = 5  # 1-10, 数字越小优先级越高
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        result = asdict(self)
        result['task_type'] = self.task_type.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TaskMessage':
        """从字典创建实例"""
        data['task_type'] = TaskType(data['task_type'])
        return cls(**data)
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'TaskMessage':
        """从JSON字符串创建实例"""
        return cls.from_dict(json.loads(json_str))


@dataclass
class TaskResult:
    """任务结果消息"""
    task_id: str
    status: TaskStatus
    result: Optional[Any] = None
    error_message: Optional[str] = None
    completed_at: str = None
    
    def __post_init__(self):
        if self.completed_at is None:
            self.completed_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        result = asdict(self)
        result['status'] = self.status.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TaskResult':
        """从字典创建实例"""
        data['status'] = TaskStatus(data['status'])
        return cls(**data)
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'TaskResult':
        """从JSON字符串创建实例"""
        return cls.from_dict(json.loads(json_str))


class MessageProtocol:
    """消息协议工具类"""
    
    @staticmethod
    def generate_task_id() -> str:
        """生成唯一的任务ID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def create_feature_extraction_task(image_data: str, **kwargs) -> TaskMessage:
        """创建特征提取任务"""
        task_id = MessageProtocol.generate_task_id()
        payload = {
            'image_data': image_data,  # base64编码的图片数据
            **kwargs
        }
        return TaskMessage(
            task_id=task_id,
            task_type=TaskType.FEATURE_EXTRACTION,
            payload=payload
        )
    
    @staticmethod
    def create_batch_feature_extraction_task(image_list: List[str], **kwargs) -> TaskMessage:
        """创建批量特征提取任务"""
        task_id = MessageProtocol.generate_task_id()
        payload = {
            'image_list': image_list,  # base64编码的图片数据列表
            **kwargs
        }
        return TaskMessage(
            task_id=task_id,
            task_type=TaskType.BATCH_FEATURE_EXTRACTION,
            payload=payload
        )
    
    @staticmethod
    def create_index_build_task(dataset_name: str, features_data: List[List[float]], ids: List[int], **kwargs) -> TaskMessage:
        """创建索引构建任务"""
        task_id = MessageProtocol.generate_task_id()
        payload = {
            'dataset_name': dataset_name,
            'features_data': features_data,
            'ids': ids,
            **kwargs
        }
        return TaskMessage(
            task_id=task_id,
            task_type=TaskType.INDEX_BUILD,
            payload=payload
        )
    
    @staticmethod
    def create_success_result(task_id: str, result: Any) -> TaskResult:
        """创建成功结果"""
        return TaskResult(
            task_id=task_id,
            status=TaskStatus.COMPLETED,
            result=result
        )
    
    @staticmethod
    def create_error_result(task_id: str, error_message: str) -> TaskResult:
        """创建错误结果"""
        return TaskResult(
            task_id=task_id,
            status=TaskStatus.FAILED,
            error_message=error_message
        )
