"""
任务管理器 - 观察者模式 + 策略模式
负责任务的分发、监控和结果收集
"""
import asyncio
import time
import threading
from typing import Dict, List, Optional, Callable, Any
from abc import ABC, abstractmethod
import json
import logging

from .redis_client import redis_client
from .message_protocol import TaskMessage, TaskResult, TaskStatus, MessageProtocol


class TaskObserver(ABC):
    """任务观察者接口"""
    
    @abstractmethod
    def on_task_completed(self, task_result: TaskResult):
        """任务完成回调"""
        pass
    
    @abstractmethod
    def on_task_failed(self, task_result: TaskResult):
        """任务失败回调"""
        pass


class TaskDispatchStrategy(ABC):
    """任务分发策略接口"""
    
    @abstractmethod
    def dispatch(self, task: TaskMessage) -> bool:
        """分发任务"""
        pass


class RedisTaskDispatchStrategy(TaskDispatchStrategy):
    """基于Redis的任务分发策略"""
    
    def __init__(self, queue_name: str = "task_queue"):
        self.queue_name = queue_name
        self.redis = redis_client.get_client()
    
    def dispatch(self, task: TaskMessage) -> bool:
        """将任务推送到Redis队列"""
        try:
            # 使用优先级队列，优先级越小越先执行
            priority_score = task.priority
            self.redis.zadd(self.queue_name, {task.to_json(): priority_score})
            
            # 同时存储任务状态
            task_key = f"task:{task.task_id}"
            task_data = task.to_dict()
            task_data['status'] = TaskStatus.PENDING.value
            redis_client.set_json(task_key, task_data, ex=3600)  # 1小时过期
            
            return True
        except Exception as e:
            logging.error(f"Failed to dispatch task {task.task_id}: {e}")
            return False


class TaskManager:
    """任务管理器 - 单例模式"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(TaskManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.dispatch_strategy: TaskDispatchStrategy = RedisTaskDispatchStrategy()
        self.observers: List[TaskObserver] = []
        self.pending_tasks: Dict[str, TaskMessage] = {}
        self.task_callbacks: Dict[str, Callable] = {}
        self.result_queue = "result_queue"
        self.redis = redis_client.get_client()
        self.monitoring = False
        self.monitor_thread = None
        
        self._initialized = True
    
    def set_dispatch_strategy(self, strategy: TaskDispatchStrategy):
        """设置任务分发策略"""
        self.dispatch_strategy = strategy
    
    def add_observer(self, observer: TaskObserver):
        """添加任务观察者"""
        if observer not in self.observers:
            self.observers.append(observer)
    
    def remove_observer(self, observer: TaskObserver):
        """移除任务观察者"""
        if observer in self.observers:
            self.observers.remove(observer)
    
    def submit_task(self, task: TaskMessage, callback: Optional[Callable] = None) -> str:
        """提交任务"""
        if self.dispatch_strategy.dispatch(task):
            self.pending_tasks[task.task_id] = task
            if callback:
                self.task_callbacks[task.task_id] = callback
            return task.task_id
        else:
            raise Exception(f"Failed to submit task {task.task_id}")
    
    def submit_feature_extraction_task(self, image_data: str, callback: Optional[Callable] = None) -> str:
        """提交特征提取任务的便捷方法"""
        task = MessageProtocol.create_feature_extraction_task(image_data)
        return self.submit_task(task, callback)
    
    def submit_batch_feature_extraction_task(self, image_list: List[str], callback: Optional[Callable] = None) -> str:
        """提交批量特征提取任务的便捷方法"""
        task = MessageProtocol.create_batch_feature_extraction_task(image_list)
        return self.submit_task(task, callback)
    
    def get_task_status(self, task_id: str) -> Optional[str]:
        """获取任务状态"""
        task_key = f"task:{task_id}"
        task_data = redis_client.get_json(task_key)
        if task_data:
            return task_data.get('status')
        return None
    
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """获取任务结果"""
        result_key = f"result:{task_id}"
        result_data = redis_client.get_json(result_key)
        if result_data:
            return TaskResult.from_dict(result_data)
        return None
    
    def wait_for_task(self, task_id: str, timeout: int = 60) -> Optional[TaskResult]:
        """等待任务完成"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = self.get_task_result(task_id)
            if result:
                return result
            time.sleep(0.1)
        return None
    
    def start_monitoring(self):
        """开始监控任务结果"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_results)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控任务结果"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
    
    def _monitor_results(self):
        """监控任务结果的后台线程"""
        while self.monitoring:
            try:
                # 从结果队列中获取结果
                result_data = self.redis.blpop(self.result_queue, timeout=1)
                if result_data:
                    _, result_json = result_data
                    result = TaskResult.from_json(result_json)
                    self._handle_task_result(result)
            except Exception as e:
                logging.error(f"Error monitoring results: {e}")
                time.sleep(1)
    
    def _handle_task_result(self, result: TaskResult):
        """处理任务结果"""
        task_id = result.task_id
        
        # 更新任务状态
        task_key = f"task:{task_id}"
        task_data = redis_client.get_json(task_key)
        if task_data:
            task_data['status'] = result.status.value
            redis_client.set_json(task_key, task_data, ex=3600)
        
        # 存储结果
        result_key = f"result:{task_id}"
        redis_client.set_json(result_key, result.to_dict(), ex=3600)
        
        # 清理待处理任务
        if task_id in self.pending_tasks:
            del self.pending_tasks[task_id]
        
        # 执行回调
        if task_id in self.task_callbacks:
            callback = self.task_callbacks.pop(task_id)
            try:
                callback(result)
            except Exception as e:
                logging.error(f"Error executing callback for task {task_id}: {e}")
        
        # 通知观察者
        if result.status == TaskStatus.COMPLETED:
            for observer in self.observers:
                try:
                    observer.on_task_completed(result)
                except Exception as e:
                    logging.error(f"Error notifying observer: {e}")
        elif result.status == TaskStatus.FAILED:
            for observer in self.observers:
                try:
                    observer.on_task_failed(result)
                except Exception as e:
                    logging.error(f"Error notifying observer: {e}")


# 全局任务管理器实例
task_manager = TaskManager()
