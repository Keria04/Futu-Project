"""
共享组件包初始化
"""
from .redis_client import redis_client
from .message_protocol import TaskMessage, TaskResult, TaskType, TaskStatus, MessageProtocol
from .task_manager import task_manager, TaskObserver, TaskDispatchStrategy

__all__ = [
    'redis_client',
    'task_manager',
    'TaskMessage',
    'TaskResult', 
    'TaskType',
    'TaskStatus',
    'MessageProtocol',
    'TaskObserver',
    'TaskDispatchStrategy'
]
