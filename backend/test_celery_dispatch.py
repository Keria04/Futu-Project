#!/usr/bin/env python3
"""
Celery任务分派诊断脚本
用于测试Worker是否能正常接收和处理任务
"""

import sys
import os
import base64
import time
from PIL import Image
from io import BytesIO

# 添加路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_simple_task():
    """测试简单任务分派"""
    print("=" * 60)
    print("1. 测试简单任务分派")
    print("=" * 60)
    
    try:
        from worker import celery_app, generate_embeddings_task
        
        # 检查Worker连接
        print("检查Celery应用配置...")
        print(f"Broker URL: {celery_app.conf.broker_url}")
        print(f"Backend URL: {celery_app.conf.result_backend}")
        
        # 检查活跃Worker
        print("\n检查活跃Worker...")
        i = celery_app.control.inspect()
        active_workers = i.active()
        
        if not active_workers:
            print("❌ 没有发现活跃的Worker节点！")
            print("请确保Worker已启动：python -m celery -A worker worker --loglevel=info --pool=solo")
            return False
        
        print(f"✅ 发现 {len(active_workers)} 个活跃Worker节点:")
        for worker_name, tasks in active_workers.items():
            print(f"  - {worker_name}: {len(tasks)} 个活跃任务")
        
        # 检查注册的任务
        print("\n检查注册的任务...")
        registered_tasks = i.registered()
        if registered_tasks:
            for worker_name, tasks in registered_tasks.items():
                print(f"Worker {worker_name} 注册的任务:")
                for task in tasks:
                    print(f"  - {task}")
                if 'worker.generate_embeddings_task' in tasks:
                    print("✅ generate_embeddings_task 已正确注册")
                else:
                    print("❌ generate_embeddings_task 未注册")
        else:
            print("❌ 没有发现注册的任务")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

def test_task_dispatch():
    """测试任务分派和执行"""
    print("\n" + "=" * 60)
    print("2. 测试任务分派和执行")
    print("=" * 60)
    
    try:
        from worker import generate_embeddings_task
        
        # 创建测试图像
        print("创建测试图像...")
        test_img = Image.new('RGB', (224, 224), color='red')
        img_buffer = BytesIO()
        test_img.save(img_buffer, format='JPEG')
        img_data = img_buffer.getvalue()
        img_data_b64 = base64.b64encode(img_data).decode('utf-8')
        
        print(f"测试图像大小: {len(img_data)} bytes")
        print(f"Base64编码后大小: {len(img_data_b64)} chars")
        
        # 分派任务
        print("\n分派任务...")
        future = generate_embeddings_task.delay(img_data_b64)
        print(f"✅ 任务已分派，ID: {future.id}")
        
        # 等待结果
        print("等待任务执行...")
        start_time = time.time()
        timeout = 30  # 30秒超时
        
        while not future.ready():
            elapsed = time.time() - start_time
            if elapsed > timeout:
                print(f"❌ 任务执行超时 ({timeout}秒)")
                return False
            print(f"  等待中... ({elapsed:.1f}s)")
            time.sleep(1)
        
        # 获取结果
        try:
            result = future.get(timeout=5)
            print(f"✅ 任务执行成功！")
            print(f"特征向量维度: {len(result) if result else 'None'}")
            print(f"执行时间: {time.time() - start_time:.2f}秒")
            return True
        except Exception as e:
            print(f"❌ 获取任务结果失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 任务分派失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_redis_queue():
    """测试Redis队列状态"""
    print("\n" + "=" * 60)
    print("3. 测试Redis队列状态")
    print("=" * 60)
    
    try:
        import redis
        from config import config
        
        redis_host = getattr(config, 'REDIS_HOST', 'localhost')
        redis_port = getattr(config, 'REDIS_PORT', 6379)
        redis_db = getattr(config, 'REDIS_BROKER_DB', 0)
        
        r = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=False)
        
        # 检查连接
        print("检查Redis连接...")
        r.ping()
        print("✅ Redis连接正常")
        
        # 检查队列状态
        print("\n检查Celery队列...")
        
        # 默认队列
        queue_length = r.llen('celery')
        print(f"默认队列 'celery' 长度: {queue_length}")
        
        # 其他可能的队列
        for queue_name in ['default', 'tasks']:
            length = r.llen(queue_name)
            if length > 0:
                print(f"队列 '{queue_name}' 长度: {length}")
        
        # 检查所有队列
        all_keys = r.keys('*')
        celery_keys = [key for key in all_keys if b'celery' in key.lower()]
        
        if celery_keys:
            print("\n发现的Celery相关键:")
            for key in celery_keys[:10]:  # 只显示前10个
                key_str = key.decode('utf-8', errors='ignore')
                key_type = r.type(key).decode('utf-8')
                print(f"  {key_str} ({key_type})")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis检查失败: {e}")
        return False

def test_feature_extractor():
    """测试特征提取器本身"""
    print("\n" + "=" * 60)
    print("4. 测试特征提取器")
    print("=" * 60)
    
    try:
        from model_module.feature_extractor import feature_extractor
        
        print("初始化特征提取器...")
        embedder = feature_extractor()
        print("✅ 特征提取器初始化成功")
        
        # 创建测试图像
        print("创建测试图像...")
        test_img = Image.new('RGB', (224, 224), color='blue')
        
        print("计算特征向量...")
        start_time = time.time()
        feat = embedder.calculate(test_img)
        end_time = time.time()
        
        print(f"✅ 特征计算成功")
        print(f"特征向量形状: {feat.shape}")
        print(f"计算时间: {end_time - start_time:.2f}秒")
        
        return True
        
    except Exception as e:
        print(f"❌ 特征提取器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("Celery分布式任务诊断工具")
    print("=" * 60)
    
    all_passed = True
    
    # 1. 测试简单任务分派
    if not test_simple_task():
        all_passed = False
        print("\n⚠️  简单任务分派测试失败，请检查Worker是否启动")
        return
    
    # 2. 测试Redis队列
    if not test_redis_queue():
        all_passed = False
        print("\n⚠️  Redis队列测试失败")
    
    # 3. 测试特征提取器
    if not test_feature_extractor():
        all_passed = False
        print("\n⚠️  特征提取器测试失败")
    
    # 4. 测试任务分派和执行
    if not test_task_dispatch():
        all_passed = False
        print("\n⚠️  任务分派和执行测试失败")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过！分布式任务系统正常工作")
    else:
        print("❌ 部分测试失败，请根据上述信息排查问题")
        
    print("\n诊断建议:")
    print("1. 确保Redis服务正在运行")
    print("2. 确保Worker已启动: python -m celery -A worker worker --loglevel=info --pool=solo")
    print("3. 检查网络连接和防火墙设置")
    print("4. 查看Worker日志中的错误信息")

if __name__ == "__main__":
    main()
