"""
API接口测试脚本
"""
import requests
import json
import os

# 配置
BASE_URL = "http://localhost:19198/api"
TEST_IMAGE_PATH = "test_image.jpg"  # 测试图片路径

def test_get_datasets():
    """测试获取数据集列表"""
    print("测试: 获取数据集列表")
    try:
        response = requests.get(f"{BASE_URL}/datasets")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {e}")
    print("-" * 50)

def test_build_index():
    """测试构建索引"""
    print("测试: 构建索引")
    try:
        data = {
            "dataset_names": ["dataset1", "dataset2"],
            "distributed": False
        }
        response = requests.post(f"{BASE_URL}/build_index", json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {e}")
    print("-" * 50)

def test_get_dataset_id():
    """测试获取数据集ID"""
    print("测试: 获取数据集ID")
    try:
        data = {"name": "dataset1"}
        response = requests.post(f"{BASE_URL}/get_dataset_id", json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {e}")
    print("-" * 50)

def test_repeated_search():
    """测试重复检测"""
    print("测试: 重复检测")
    try:
        data = {
            "index_id": "dataset1",
            "threshold": 0.85,
            "deduplicate": False
        }
        response = requests.post(f"{BASE_URL}/repeated_search", json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {e}")
    print("-" * 50)

def test_search_image():
    """测试图片搜索（需要测试图片）"""
    print("测试: 图片搜索")
    
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"跳过图片搜索测试 - 未找到测试图片: {TEST_IMAGE_PATH}")
        print("-" * 50)
        return
    
    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'query_img': f}
            data = {
                'crop_x': 0,
                'crop_y': 0,
                'crop_w': 100,
                'crop_h': 100,
                'dataset_names[]': ['dataset1', 'dataset2']
            }
            response = requests.post(f"{BASE_URL}/search", files=files, data=data)
            print(f"状态码: {response.status_code}")
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {e}")
    print("-" * 50)

def test_static_image():
    """测试静态图片访问"""
    print("测试: 静态图片访问")
    try:
        # 测试访问一个模拟的图片路径
        response = requests.get("http://localhost:19198/show_image/datasets/1/circles_10.jpg")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("图片访问成功")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")
    print("-" * 50)

def main():
    """运行所有测试"""
    print("=" * 60)
    print("浮图项目 API 接口测试")
    print("=" * 60)
    
    # 检查服务是否可用
    try:
        response = requests.get(f"{BASE_URL}/datasets", timeout=5)
        print("✓ 后端服务可用")
    except Exception as e:
        print(f"✗ 后端服务不可用: {e}")
        print("请先启动后端服务: python run.py")
        return
    
    print("\n开始测试...")
    print("-" * 50)
    
    # 运行测试
    test_get_datasets()
    test_build_index()
    test_get_dataset_id()
    test_repeated_search()
    test_search_image()
    test_static_image()
    
    print("测试完成!")

if __name__ == '__main__':
    main()
