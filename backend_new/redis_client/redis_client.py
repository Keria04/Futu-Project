"""
Redis客户端配置和封装
"""
import redis
import json
import uuid
import time
import logging
from typing import Any, Optional, Dict, List


class RedisConfig:
    """Redis配置类"""
    def __init__(self):
        self.host = 'localhost'
        self.port = 6379
        self.db = 0
        self.password = None
        self.decode_responses = True
        self.socket_connect_timeout = 5
        self.socket_timeout = 5
        self.retry_on_timeout = True
        self.health_check_interval = 30


class RedisClient:
    """Redis客户端封装类"""
    
    def __init__(self, config: RedisConfig = None):
        if config is None:
            config = RedisConfig()
        
        self.config = config
        self.client = None
        self.logger = logging.getLogger(__name__)
        self._connect()
    
    def _connect(self):
        """连接Redis"""
        try:
            self.client = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                decode_responses=self.config.decode_responses,
                socket_connect_timeout=self.config.socket_connect_timeout,
                socket_timeout=self.config.socket_timeout,
                retry_on_timeout=self.config.retry_on_timeout,
                health_check_interval=self.config.health_check_interval
            )
            # 测试连接
            self.client.ping()
            self.logger.info(f"Redis连接成功: {self.config.host}:{self.config.port}")
        except Exception as e:
            self.logger.error(f"Redis连接失败: {e}")
            raise
    
    def is_connected(self) -> bool:
        """检查Redis连接状态"""
        try:
            return self.client.ping()
        except:
            return False
    
    def publish_task(self, channel: str, task_data: Dict[str, Any]) -> str:
        """发布任务到Redis频道"""
        task_id = str(uuid.uuid4())
        task_data['task_id'] = task_id
        task_data['timestamp'] = time.time()
        
        try:
            self.client.publish(channel, json.dumps(task_data))
            self.logger.info(f"任务发布成功: {task_id} -> {channel}")
            return task_id
        except Exception as e:
            self.logger.error(f"任务发布失败: {e}")
            raise
    
    def send_task(self, channel: str, task_data: Dict[str, Any]) -> str:
        """发送任务到指定频道（publish_task的别名）"""
        return self.publish_task(channel, task_data)
    
    def subscribe_tasks(self, channels: List[str]):
        """订阅Redis频道"""
        try:
            pubsub = self.client.pubsub()
            pubsub.subscribe(*channels)
            self.logger.info(f"订阅频道成功: {channels}")
            return pubsub
        except Exception as e:
            self.logger.error(f"订阅频道失败: {e}")
            raise
    
    def get_task(self, channels: List[str], timeout: int = 1) -> Optional[Dict[str, Any]]:
        """从指定频道获取任务"""
        try:
            pubsub = self.client.pubsub()
            pubsub.subscribe(*channels)
            
            # 等待消息
            message = pubsub.get_message(timeout=timeout)
            if message and message['type'] == 'message':
                return {
                    'channel': message['channel'].decode() if isinstance(message['channel'], bytes) else message['channel'],
                    'data': message['data']
                }
            
            pubsub.close()
            return None
            
        except Exception as e:
            self.logger.error(f"获取任务失败: {e}")
            return None
    
    def set_result(self, task_id: str, result: Any, expire: int = 3600):
        """设置任务结果"""
        key = f"result:{task_id}"
        try:
            self.client.setex(key, expire, json.dumps(result))
            self.logger.debug(f"结果存储成功: {task_id}")
        except Exception as e:
            self.logger.error(f"结果存储失败: {e}")
            raise
    
    def get_result(self, task_id: str, timeout: int = 30) -> Optional[Any]:
        """获取任务结果"""
        key = f"result:{task_id}"
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                result = self.client.get(key)
                if result:
                    return json.loads(result)
                time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"获取结果失败: {e}")
                break
        
        return None
    
    def delete_result(self, task_id: str):
        """删除任务结果"""
        key = f"result:{task_id}"
        try:
            self.client.delete(key)
        except Exception as e:
            self.logger.error(f"删除结果失败: {e}")
    
    def close(self):
        """关闭Redis连接"""
        if self.client:
            self.client.close()
            self.logger.info("Redis连接已关闭")
    
    def acquire_lock(self, lock_key: str, owner: str, expire: int = 300) -> bool:
        """获取分布式锁"""
        try:
            # 使用 SET NX EX 命令获取锁
            result = self.client.set(lock_key, owner, nx=True, ex=expire)
            if result:
                self.logger.debug(f"获取锁成功: {lock_key} by {owner}")
                return True
            else:
                self.logger.debug(f"获取锁失败: {lock_key} by {owner}")
                return False
        except Exception as e:
            self.logger.error(f"获取锁失败: {e}")
            return False
    
    def release_lock(self, lock_key: str, owner: str) -> bool:
        """释放分布式锁"""
        try:
            # Lua脚本确保只有锁的拥有者才能释放锁
            lua_script = """
            if redis.call("GET", KEYS[1]) == ARGV[1] then
                return redis.call("DEL", KEYS[1])
            else
                return 0
            end
            """
            result = self.client.eval(lua_script, 1, lock_key, owner)
            if result:
                self.logger.debug(f"释放锁成功: {lock_key} by {owner}")
                return True
            else:
                self.logger.debug(f"释放锁失败或锁不属于此owner: {lock_key} by {owner}")
                return False
        except Exception as e:
            self.logger.error(f"释放锁失败: {e}")
            return False
    
    def is_locked(self, lock_key: str) -> bool:
        """检查锁是否存在"""
        try:
            return self.client.exists(lock_key) > 0
        except Exception as e:
            self.logger.error(f"检查锁状态失败: {e}")
            return False


# 全局Redis客户端实例
redis_client = None


def init_redis_client(config: RedisConfig = None) -> RedisClient:
    """初始化全局Redis客户端"""
    global redis_client
    redis_client = RedisClient(config)
    return redis_client


def get_redis_client() -> RedisClient:
    """获取全局Redis客户端"""
    global redis_client
    if redis_client is None:
        redis_client = RedisClient()
    return redis_client
