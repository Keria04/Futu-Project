#!/usr/bin/env python3
"""
清理Redis队列并重新测试任务分派
"""

import sys
import os
import redis
import time

# 添加路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def clear_redis_queues():
    """清理Redis中的积压任务"""
    try:
        from config import config
        
        redis_host = getattr(config, 'REDIS_HOST', 'localhost')
        redis_port = getattr(config, 'REDIS_PORT', 6379)
        redis_db = getattr(config, 'REDIS_BROKER_DB', 0)
        
        r = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=False)
        
        print("清理Redis队列...")
        
        # 检查积压任务
        default_count = r.llen('default')
        celery_count = r.llen('celery')
        
        print(f"清理前 - default队列: {default_count} 个任务")
        print(f"清理前 - celery队列: {celery_count} 个任务")
        
        # 清理积压任务
        if default_count > 0:
            r.delete('default')
            print(f"✅ 已清理default队列的 {default_count} 个积压任务")
        
        if celery_count > 0:
            r.delete('celery')
            print(f"✅ 已清理celery队列的 {celery_count} 个积压任务")
        
        # 清理结果后端
        result_keys = r.keys('celery-task-meta-*')
        if result_keys:
            r.delete(*result_keys)
            print(f"✅ 已清理 {len(result_keys)} 个任务结果缓存")
        
        print("队列清理完成!")
        return True
        
    except Exception as e:
        print(f"❌ 清理队列失败: {e}")
        return False

def restart_worker_suggestion():
    """提示重启Worker"""
    print("\n" + "=" * 60)
    print("重启Worker建议")
    print("=" * 60)
    print("由于修改了队列配置，建议重启Worker以应用新配置:")
    print("1. 停止当前Worker进程 (Ctrl+C)")
    print("2. 重新启动Worker:")
    print("   python -m celery -A worker worker --loglevel=info --pool=solo")
    print("3. 重新运行测试:")
    print("   python backend/test_celery_dispatch.py")

def quick_test():
    """快速测试任务分派"""
    print("\n" + "=" * 60)
    print("快速测试任务分派")
    print("=" * 60)
    
    try:
        from worker import generate_embeddings_task
        import base64
        from PIL import Image
        from io import BytesIO
        
        # 创建简单测试图像
        test_img = Image.new('RGB', (100, 100), color='green')
        img_buffer = BytesIO()
        test_img.save(img_buffer, format='JPEG')
        img_data = img_buffer.getvalue()
        img_data_b64 = base64.b64encode(img_data).decode('utf-8')
        
        print(f"分派测试任务...")
        future = generate_embeddings_task.delay(img_data_b64)
        print(f"任务ID: {future.id}")
        
        # 检查队列状态
        from config import config
        redis_host = getattr(config, 'REDIS_HOST', 'localhost')
        redis_port = getattr(config, 'REDIS_PORT', 6379)
        redis_db = getattr(config, 'REDIS_BROKER_DB', 0)
        
        r = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=False)
        
        print(f"celery队列长度: {r.llen('celery')}")
        print(f"default队列长度: {r.llen('default')}")
        
        # 等待结果
        print("等待任务执行 (10秒)...")
        try:
            result = future.get(timeout=10)
            print("✅ 任务执行成功!")
            print(f"特征向量维度: {len(result)}")
            return True
        except Exception as e:
            print(f"❌ 任务执行失败或超时: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    print("Redis队列清理和任务测试工具")
    print("=" * 60)
    
    # 1. 清理队列
    if not clear_redis_queues():
        print("队列清理失败，无法继续")
        return
    
    # 2. 提示重启Worker
    restart_worker_suggestion()
    
    # 3. 询问是否进行快速测试
    print("\n是否现在进行快速测试? (y/N):")
    response = input().strip().lower()
    
    if response in ['y', 'yes']:
        if quick_test():
            print("\n✅ 快速测试通过！队列配置正确")
        else:
            print("\n❌ 快速测试失败，请检查Worker是否重启")
    else:
        print("\n请重启Worker后运行完整测试:")
        print("python backend/test_celery_dispatch.py")

if __name__ == "__main__":
    main()
