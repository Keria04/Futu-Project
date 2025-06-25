#!/usr/bin/env python3
"""
测试修复后的Celery+Redis分布式计算功能
"""

import os
import sys
import time
import requests
import json

# 添加后端路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

def test_redis_connection():
    """测试Redis连接"""
    print("=== 测试Redis连接 ===")
    try:
        from worker import check_redis_connection
        is_available = check_redis_connection()
        if is_available:
            print("✅ Redis连接成功")
            return True
        else:
            print("❌ Redis连接失败")
            return False
    except Exception as e:
        print(f"❌ Redis连接测试出错: {e}")
        return False

def test_celery_worker():
    """测试Celery Worker"""
    print("\n=== 测试Celery Worker ===")
    try:
        from worker import check_celery_worker
        is_available = check_celery_worker()
        if is_available:
            print("✅ Celery Worker可用")
            return True
        else:
            print("⚠️  Celery Worker不可用（可能需要启动worker进程）")
            return False
    except Exception as e:
        print(f"❌ Celery Worker测试出错: {e}")
        return False

def test_distributed_availability():
    """测试分布式计算可用性"""
    print("\n=== 测试分布式计算可用性 ===")
    try:
        from worker import is_distributed_available
        is_available = is_distributed_available()
        if is_available:
            print("✅ 分布式计算完全可用")
            return True
        else:
            print("⚠️  分布式计算不可用，将使用本地计算")
            return False
    except Exception as e:
        print(f"❌ 分布式计算测试出错: {e}")
        return False

def test_feature_extraction():
    """测试特征提取任务"""
    print("\n=== 测试特征提取任务 ===")
    
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
    
    print(f"📸 使用测试图片: {test_image}")
    
    try:
        # 测试直接任务提交
        import base64
        from worker import generate_embeddings_task
        
        with open(test_image, 'rb') as f:
            img_data = f.read()
        img_data_b64 = base64.b64encode(img_data).decode('utf-8')
        
        print("📤 提交特征提取任务...")
        task = generate_embeddings_task.delay(img_data_b64)
        
        print(f"📋 任务ID: {task.id}")
        print("⏳ 等待任务完成...")
        
        # 等待任务完成，最多等待30秒
        try:
            result = task.get(timeout=30)
            print(f"✅ 特征提取成功，特征维度: {len(result)}")
            return True
        except Exception as e:
            print(f"❌ 任务执行失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 特征提取测试失败: {e}")
        return False

def test_index_building():
    """测试索引构建（通过API）"""
    print("\n=== 测试索引构建API ===")
    
    # 检查是否有可用的数据集
    available_datasets = []
    for dataset_name in ["1", "2", "3"]:
        dataset_path = f"datasets/{dataset_name}"
        if os.path.exists(dataset_path):
            files = [f for f in os.listdir(dataset_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if files:
                available_datasets.append(dataset_name)
    
    if not available_datasets:
        print("❌ 没有可用的数据集进行测试")
        return False
    
    test_dataset = available_datasets[0]
    print(f"📁 使用测试数据集: {test_dataset}")
    
    try:
        # 调用构建索引API
        url = "http://localhost:19198/api/build_index"
        data = {
            "dataset_names": [test_dataset],
            "distributed": True
        }
        
        print("📤 发送索引构建请求...")
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 索引构建请求成功提交")
            print(f"📋 返回结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return True
        else:
            print(f"❌ API调用失败，状态码: {response.status_code}")
            print(f"📋 错误信息: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Flask应用，请确保应用正在运行")
        return False
    except Exception as e:
        print(f"❌ 索引构建测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试修复后的Celery+Redis分布式计算功能")
    print("=" * 60)
    
    # 测试各个组件
    redis_ok = test_redis_connection()
    worker_ok = test_celery_worker()
    distributed_ok = test_distributed_availability()
    
    if redis_ok and worker_ok:
        feature_ok = test_feature_extraction()
    else:
        print("\n⚠️  Redis或Celery Worker不可用，跳过特征提取测试")
        feature_ok = False
    
    # 测试API（无论分布式是否可用）
    api_ok = test_index_building()
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    print(f"   Redis连接: {'✅' if redis_ok else '❌'}")
    print(f"   Celery Worker: {'✅' if worker_ok else '❌'}")
    print(f"   分布式计算: {'✅' if distributed_ok else '❌'}")
    print(f"   特征提取任务: {'✅' if feature_ok else '❌'}")
    print(f"   索引构建API: {'✅' if api_ok else '❌'}")
    
    if distributed_ok:
        print("\n🎉 分布式计算功能完全正常！")
    elif api_ok:
        print("\n✅ 虽然分布式计算不可用，但会自动回退到本地计算")
    else:
        print("\n⚠️  存在一些问题，请检查配置")
    
    print("\n💡 提示:")
    if not redis_ok:
        print("   - 请确保Redis服务正在运行")
    if not worker_ok:
        print("   - 请启动Celery Worker进程: python backend/start_worker.py")
    if not api_ok:
        print("   - 请确保Flask应用正在运行: python backend/app.py")

if __name__ == "__main__":
    main()
