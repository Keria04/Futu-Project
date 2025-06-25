#!/usr/bin/env python3
"""
测试搜索功能修复的脚本
验证特征提取任务是否能正常工作
"""

import requests
import os
import time
import json

def test_search_with_real_image():
    """测试使用真实图片的搜索功能"""
    print("=== 测试搜索功能修复 ===")
    
    # 寻找测试图片
    test_image_paths = [
        "datasets/1",
        "datasets/2",
        "datasets/3"
    ]
    
    test_image = None
    for dataset_path in test_image_paths:
        if os.path.exists(dataset_path):
            for root, dirs, files in os.walk(dataset_path):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
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
      # 准备搜索请求
    with open(test_image, 'rb') as f:
        files = {'query_img': f}
        data = {
            'dataset_names[]': ['1'],  # 搜索数据集1
            'top_k': 5,
            'similarity_threshold': 30.0  # 降低阈值以获得更多结果
        }
        
        print("🚀 发送搜索请求...")
        start_time = time.time()
        
        try:
            response = requests.post(
                'http://localhost:19198/api/search',
                files=files,
                data=data,
                timeout=60  # 增加超时时间
            )
            
            end_time = time.time()
            print(f"⏱️  请求耗时: {end_time - start_time:.2f} 秒")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 搜索请求成功")
                
                if result.get('success'):
                    results = result.get('results', [])
                    print(f"🎯 找到 {len(results)} 个相似图片")
                    
                    for i, res in enumerate(results):
                        similarity = res.get('similarity', 0)
                        filename = res.get('fname', 'Unknown')
                        print(f"  {i+1}. {filename} - 相似度: {similarity:.2f}%")
                    
                    # 显示搜索参数
                    search_params = result.get('search_params', {})
                    print(f"📋 搜索参数: {json.dumps(search_params, indent=2, ensure_ascii=False)}")
                    
                    return True
                else:
                    print(f"❌ 搜索失败: {result}")
                    return False
                
            else:
                print(f"❌ 搜索请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ 请求超时，可能计算端服务未正常响应")
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

def check_compute_server_status():
    """检查计算端服务状态"""
    print("\n=== 检查计算端服务状态 ===")
    
    # 通过Redis检查计算端是否在线
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # 发送健康检查任务
        import uuid
        task_id = str(uuid.uuid4())
        task_data = {
            'task_id': task_id,
            'task_type': 'health_check'
        }
        
        # 发布任务
        r.publish('compute:health_check', json.dumps(task_data))
        print("✅ 已发送健康检查任务")
        
        # 等待结果
        for i in range(10):
            result = r.get(f"result:{task_id}")
            if result:
                result_data = json.loads(result)
                print(f"✅ 计算端服务正常: {result_data}")
                return True
            time.sleep(0.5)
        
        print("⚠️  计算端服务未响应健康检查")
        return False
        
    except Exception as e:
        print(f"❌ 检查计算端服务状态失败: {e}")
        return False

def test_feature_extraction_directly():
    """直接测试特征提取功能"""
    print("\n=== 直接测试特征提取 ===")
    
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
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # 发送特征提取任务
        import uuid
        task_id = str(uuid.uuid4())
        task_data = {
            'task_id': task_id,
            'task_type': 'single_feature_extraction',
            'image_path': os.path.abspath(test_image)
        }
        
        print(f"📸 测试图片: {test_image}")
        print("🚀 发送特征提取任务...")
        
        # 发布任务
        r.publish('compute:single_feature_extraction', json.dumps(task_data))
        
        # 等待结果
        for i in range(30):  # 等待30秒
            result = r.get(f"result:{task_id}")
            if result:
                result_data = json.loads(result)
                if result_data.get('success'):
                    features = result_data.get('features', [])
                    print(f"✅ 特征提取成功，特征维度: {len(features)}")
                    return True
                else:
                    print(f"❌ 特征提取失败: {result_data.get('error', '未知错误')}")
                    return False
            time.sleep(1)
            if i % 5 == 0:
                print(f"⏳ 等待中... {i+1}/30 秒")
        
        print("❌ 特征提取超时")
        return False
        
    except Exception as e:
        print(f"❌ 特征提取测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🔧 搜索功能修复验证")
    print("=" * 50)
    
    # 1. 检查计算端服务状态
    compute_ok = check_compute_server_status()
    
    # 2. 直接测试特征提取
    extraction_ok = test_feature_extraction_directly()
    
    # 3. 测试完整搜索流程
    search_ok = False
    if extraction_ok:
        search_ok = test_search_with_real_image()
    
    print("\n" + "=" * 50)
    print("📋 测试结果总结:")
    print(f"  计算端服务状态: {'✅ 正常' if compute_ok else '❌ 异常'}")
    print(f"  特征提取功能: {'✅ 正常' if extraction_ok else '❌ 异常'}")
    print(f"  搜索功能: {'✅ 正常' if search_ok else '❌ 异常'}")
    
    if search_ok:
        print("\n🎉 修复成功！搜索功能已正常工作。")
    else:
        print("\n⚠️  仍有问题需要解决:")
        if not compute_ok:
            print("  - 计算端服务未正常响应")
        if not extraction_ok:
            print("  - 特征提取功能异常")
        print("  请检查日志获取更多信息")
    
    return search_ok

if __name__ == '__main__':
    # 改变工作目录到项目根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    success = main()
    exit(0 if success else 1)
