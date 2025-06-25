#!/usr/bin/env python3
"""
测试索引构建修复
"""
import requests
import json
import time

# 后端API地址
BASE_URL = "http://localhost:19198/api"

def test_build_index():
    """测试索引构建功能"""
    print("开始测试索引构建...")
      # 1. 先获取可用的数据集
    print("\n1. 获取数据集列表...")
    try:
        response = requests.get(f"{BASE_URL}/datasets")
        if response.status_code == 200:
            data = response.json()
            datasets = data.get('datasets', [])
            print(f"找到 {len(datasets)} 个数据集:")
            for dataset in datasets:
                print(f"  - {dataset['name']}: {dataset['image_count']} 张图片")
        else:
            print(f"获取数据集失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"请求失败: {e}")
        return False
    
    if not datasets:
        print("没有可用的数据集")
        return False
    
    # 2. 选择第一个有图片的数据集进行索引构建
    target_dataset = None
    for dataset in datasets:
        if dataset['image_count'] > 0:
            target_dataset = dataset
            break
    
    if not target_dataset:
        print("没有包含图片的数据集")
        return False
    
    print(f"\n2. 开始为数据集 '{target_dataset['name']}' 构建索引...")
    
    # 3. 发送索引构建请求
    build_data = {
        "dataset_names": [target_dataset['name']],
        "distributed": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/build_index", json=build_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                task_id = result.get('task_id')
                print(f"索引构建任务已启动，任务ID: {task_id}")
                
                # 4. 监控构建进度
                print("\n3. 监控构建进度...")
                return monitor_build_progress(task_id)
            else:
                print(f"索引构建启动失败: {result.get('msg', '未知错误')}")
                return False
        else:
            print(f"请求失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"请求异常: {e}")
        return False

def monitor_build_progress(task_id):
    """监控构建进度"""
    max_attempts = 30  # 最多监控30次
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{BASE_URL}/build_status/{task_id}")
            if response.status_code == 200:
                result = response.json()
                status = result.get('status')
                progress = result.get('progress', {})
                
                if isinstance(progress, list) and progress:
                    latest_progress = progress[-1]
                    percentage = latest_progress.get('percentage', 0)
                    message = latest_progress.get('message', '')
                    print(f"进度: {percentage:.1f}% - {message}")
                    
                    if status == 'completed':
                        print("\n✅ 索引构建成功完成！")
                        print(f"处理结果: {result.get('message', '')}")
                        return True
                    elif status == 'failed':
                        print(f"\n❌ 索引构建失败: {result.get('message', '')}")
                        if 'error' in result:
                            print(f"错误详情: {result['error']}")
                        return False
                else:
                    print(f"状态: {status}")
                
            else:
                print(f"获取状态失败: {response.status_code}")
            
            time.sleep(2)  # 等待2秒后再检查
            attempt += 1
            
        except Exception as e:
            print(f"监控异常: {e}")
            break
    
    print("\n⚠️ 监控超时")
    return False

if __name__ == "__main__":
    print("=" * 50)
    print("浮图项目 - 索引构建修复测试")
    print("=" * 50)
    
    success = test_build_index()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ 测试通过！索引构建修复成功")
    else:
        print("❌ 测试失败！请检查错误信息")
    print("=" * 50)
