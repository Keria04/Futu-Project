#!/usr/bin/env python3
"""
测试图片搜索功能的脚本
"""

import requests
import os
import json
import sys

def test_image_search():
    """测试图片搜索接口"""
    print("=== 测试图片搜索接口 ===")
    
    # 准备测试图片
    test_image_path = "datasets/1"  # 假设有测试图片
    if not os.path.exists(test_image_path):
        print("❌ 测试图片目录不存在，请确保有测试数据")
        return False
    
    # 找一张测试图片
    image_files = []
    for root, dirs, files in os.walk(test_image_path):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                image_files.append(os.path.join(root, file))
                break
        if image_files:
            break
    
    if not image_files:
        print("❌ 未找到测试图片")
        return False
    
    test_image = image_files[0]
    print(f"📸 使用测试图片: {test_image}")
    
    # 准备请求数据
    with open(test_image, 'rb') as f:
        files = {'query_img': f}
        data = {
            'dataset_names[]': ['1', '2'],  # 测试数据集
            'top_k': 5,
            'similarity_threshold': 50.0,
            'crop_x': 0,
            'crop_y': 0,
            'crop_w': 0,
            'crop_h': 0
        }
        
        try:
            print("🚀 发送搜索请求...")
            response = requests.post(
                'http://localhost:5000/api/search',
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 搜索请求成功")
                print(f"📊 搜索结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                # 验证响应格式
                required_fields = ['success', 'results', 'total_found', 'search_params']
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    print(f"❌ 响应缺少必要字段: {missing_fields}")
                    return False
                
                results = result.get('results', [])
                print(f"🎯 找到 {len(results)} 个相似图片")
                
                for i, res in enumerate(results):
                    print(f"  {i+1}. {res.get('fname', 'Unknown')} - 相似度: {res.get('similarity', 0):.2f}%")
                
                return True
                
            else:
                print(f"❌ 搜索请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

def test_search_with_crop():
    """测试带裁剪的图片搜索"""
    print("\n=== 测试带裁剪的图片搜索 ===")
    
    # 这里可以添加裁剪功能的测试
    print("⚠️  裁剪功能测试待实现")
    return True

def test_search_parameters():
    """测试搜索参数验证"""
    print("\n=== 测试搜索参数验证 ===")
    
    # 测试没有图片的情况
    try:
        response = requests.post(
            'http://localhost:5000/api/search',
            data={'dataset_names[]': ['1']},
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ 无图片参数验证正确")
        else:
            print(f"❌ 无图片参数验证失败，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 参数验证测试异常: {e}")
        return False
    
    return True

def check_backend_status():
    """检查后端服务状态"""
    print("=== 检查后端服务状态 ===")
    
    try:
        response = requests.get('http://localhost:5000/api/datasets', timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
            return True
        else:
            print(f"⚠️  后端服务状态异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接后端服务: {e}")
        print("请确保后端服务正在运行 (python run.py)")
        return False

def main():
    """主测试函数"""
    print("🔍 图片搜索功能测试")
    print("请确保后端服务正在运行 (http://localhost:5000)")
    
    # 检查后端服务
    if not check_backend_status():
        return False
    
    # 测试搜索参数验证
    if not test_search_parameters():
        return False
    
    # 测试图片搜索
    if not test_image_search():
        return False
    
    # 测试裁剪功能
    if not test_search_with_crop():
        return False
    
    print("\n🎉 所有测试完成")
    return True

if __name__ == '__main__':
    # 改变工作目录到项目根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    success = main()
    sys.exit(0 if success else 1)
