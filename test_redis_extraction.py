#!/usr/bin/env python3
"""
测试Redis特征提取流程
"""

import os
import sys
import json
import time
import uuid

# 添加后端路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend_new')
sys.path.insert(0, backend_path)

import redis

def test_redis_feature_extraction():
    """测试通过Redis的特征提取流程"""
    print("=== 测试Redis特征提取流程 ===")
    
    # 寻找测试图片
    test_image = None
    for dataset_path in ["datasets/1", "datasets/2", "datasets/3"]:
        if os.path.exists(dataset_path):
            for root, dirs, files in os.walk(dataset_path):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        test_image = os.path.join(root, file)
                        break
                if test_image:
                    break
            if test_image:
                break
    
    if not test_image:
        print("❌ 未找到测试图片")
        return False
    
    print(f"📸 测试图片: {test_image}")
    print(f"📸 绝对路径: {os.path.abspath(test_image)}")
    
    try:
        # 连接Redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # 测试Redis连接
        r.ping()
        print("✅ Redis连接成功")
        
        # 发送特征提取任务
        task_id = str(uuid.uuid4())
        task_data = {
            'task_id': task_id,
            'task_type': 'single_feature_extraction',
            'image_path': os.path.abspath(test_image)
        }
        
        print(f"🚀 发送任务: {task_id}")
        print(f"📋 任务数据: {json.dumps(task_data, indent=2, ensure_ascii=False)}")
        
        # 发布任务
        r.publish('compute:single_feature_extraction', json.dumps(task_data))
        print("✅ 任务已发布")
        
        # 等待结果
        print("⏳ 等待结果...")
        for i in range(30):
            result_key = f"result:{task_id}"
            result = r.get(result_key)
            if result:
                result_data = json.loads(result)
                print(f"✅ 收到结果: {json.dumps(result_data, indent=2, ensure_ascii=False)}")
                
                if result_data.get('success'):
                    features = result_data.get('result', [])
                    print(f"🎯 特征维度: {len(features) if isinstance(features, list) else 'Unknown'}")
                    if isinstance(features, list) and len(features) > 0:
                        print(f"   前5个值: {features[:5]}")
                        return True
                    else:
                        print("❌ 特征为空或无效")
                        return False
                else:
                    print(f"❌ 特征提取失败: {result_data.get('error', '未知错误')}")
                    return False
            
            time.sleep(1)
            if i % 5 == 0:
                print(f"   等待 {i+1}/30 秒...")
        
        print("❌ 等待超时")
        return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_redis_feature_extraction()
    print(f"\n{'✅ 测试通过' if success else '❌ 测试失败'}")
