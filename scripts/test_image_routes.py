#!/usr/bin/env python3
"""
快速启动脚本 - 用于测试图片静态服务
"""
import subprocess
import time
import requests
import os
import sys

def check_backend():
    """检查后端是否可用"""
    try:
        response = requests.get('http://localhost:19198/api/datasets', timeout=5)
        return response.status_code == 200
    except:
        return False

def test_image_route():
    """测试图片路由"""
    test_images = [
        '/show_image/datasets/1/circles_10.jpg',
        '/show_image/datasets/1/circles_11.jpg',
        '/show_image/datasets/1/circles_12.jpg'
    ]
    
    for img_path in test_images:
        try:
            response = requests.get(f'http://localhost:19198{img_path}', timeout=10)
            print(f"测试 {img_path}: 状态码 {response.status_code}")
            if response.status_code == 200:
                print(f"  ✓ 图片访问成功 - Content-Type: {response.headers.get('Content-Type', 'unknown')}")
            else:
                print(f"  ✗ 图片访问失败 - {response.text[:100]}")
        except Exception as e:
            print(f"  ✗ 图片访问异常: {e}")

def test_search_api():
    """测试搜索API"""
    try:
        data = {
            "dataset_names": ["dataset1", "dataset2"],
            "distributed": False
        }
        response = requests.post('http://localhost:19198/api/build_index', json=data, timeout=10)
        print(f"测试索引构建: 状态码 {response.status_code}")
        if response.status_code == 200:
            print(f"  ✓ 索引构建API正常")
        else:
            print(f"  ✗ 索引构建API异常 - {response.text[:100]}")
    except Exception as e:
        print(f"  ✗ 索引构建API异常: {e}")

def main():
    print("=" * 50)
    print("浮图项目后端测试脚本")
    print("=" * 50)
    
    # 切换到正确的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 检查后端是否已经运行
    if check_backend():
        print("✓ 后端服务已在运行")
    else:
        print("✗ 后端服务未运行")
        print("\n请先启动后端服务:")
        print("  方法1: python run.py")
        print("  方法2: python app.py")
        print("  方法3: start_server.bat")
        return
    
    print("\n开始测试...")
    print("-" * 30)
    
    # 测试数据集API
    print("1. 测试数据集API")
    try:
        response = requests.get('http://localhost:19198/api/datasets', timeout=10)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 获取到 {len(data.get('datasets', []))} 个数据集")
        else:
            print(f"   ✗ API异常 - {response.text[:100]}")
    except Exception as e:
        print(f"   ✗ API异常: {e}")
    
    print("\n2. 测试图片静态路由")
    test_image_route()
    
    print("\n3. 测试搜索相关API")
    test_search_api()
    
    print("\n" + "=" * 50)
    print("测试完成!")
    print("\n如果图片访问正常，说明show_image路由工作正常")
    print("前端应该能够正常显示图片")

if __name__ == '__main__':
    main()
