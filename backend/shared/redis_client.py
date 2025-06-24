"""
Redis客户端 - 单例模式
提供统一的Redis连接管理
"""
import redis
import json
from typing import Any, Optional
import threading


class RedisClient:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, host='localhost', port=6379, db=0, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(RedisClient, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, host='localhost', port=6379, db=0, **kwargs):
        if self._initialized:
            return
        
        self.host = host
        self.port = port
        self.db = db
        self._client = redis.Redis(
            host=host, 
            port=port, 
            db=db, 
            decode_responses=True,
            **kwargs
        )
        self._initialized = True
    
    def get_client(self) -> redis.Redis:
        """获取Redis客户端实例"""
        return self._client
    
    def ping(self) -> bool:
        """检查Redis连接"""
        try:
            return self._client.ping()
        except Exception:
            return False
    
    def set_json(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """存储JSON数据"""
        try:
            json_str = json.dumps(value, ensure_ascii=False)
            return self._client.set(key, json_str, ex=ex)
        except Exception:
            return False
    
    def get_json(self, key: str) -> Optional[Any]:
        """获取JSON数据"""
        try:
            json_str = self._client.get(key)
            if json_str is None:
                return None
            return json.loads(json_str)
        except Exception:
            return None
    
    def delete(self, key: str) -> bool:
        """删除键"""
        try:
            return bool(self._client.delete(key))
        except Exception:
            return False
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return bool(self._client.exists(key))
        except Exception:
            return False


# 全局Redis客户端实例
redis_client = RedisClient()
