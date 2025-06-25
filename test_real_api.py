#!/usr/bin/env python3
"""
测试实际的API请求
"""

import requests
import json
import time

def test_build_index_api():
    """测试构建索引API"""
    print("=== 测试构建索引API ===")
    
    url = "http://localhost:5000/api/build_index"
    data = {
        "dataset_names": ["1"],  # 假设数据集1存在
        "distributed": False
    }
    
    print(f"请求URL: {url}")
    print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 提取进度文件URL
            progress_info = result.get('progress', [])
            if progress_info:
                progress_url = progress_info[0].get('progress_file')
                print(f"进度文件URL: {progress_url}")
                return progress_url
            else:
                print("❌ 响应中没有progress信息")
                return None
        else:
            print(f"❌ 请求失败")
            print(f"响应内容: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        print("请确保后端服务正在运行 (python backend_new/run.py)")
        return None
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def test_progress_api(progress_url):
    """测试进度查询API"""
    print(f"\n=== 测试进度查询API ===")
    
    if not progress_url:
        print("❌ 没有进度URL")
        return
    
    # 构建完整URL
    if progress_url.startswith('/'):
        full_url = f"http://localhost:5000{progress_url}"
    else:
        full_url = progress_url
    
    print(f"进度查询URL: {full_url}")
    
    # 轮询进度
    for i in range(5):
        try:
            print(f"\n--- 第 {i+1} 次查询 ---")
            response = requests.get(full_url, timeout=5)
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"进度: {data.get('progress', 'N/A')}%")
                print(f"状态: {data.get('status', 'N/A')}")
                print(f"消息: {data.get('message', 'N/A')}")
                
                # 如果完成，停止轮询
                if data.get('status') in ['done', 'error']:
                    print(f"任务完成，状态: {data.get('status')}")
                    break
                    
            elif response.status_code == 404:
                print("❌ 进度文件不存在 (404)")
                print(f"响应: {response.text}")
                break
            else:
                print(f"❌ 查询失败，状态码: {response.status_code}")
                print(f"响应: {response.text}")
                
        except Exception as e:
            print(f"❌ 查询异常: {e}")
        
        # 等待2秒
        if i < 4:
            time.sleep(2)

def check_backend_status():
    """检查后端服务状态"""
    print("=== 检查后端服务状态 ===")
    
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        print(f"✅ 后端服务正在运行，状态码: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ 后端服务未运行")
        return False
    except Exception as e:
        print(f"⚠️  检查异常: {e}")
        return False

def main():
    """主函数"""
    print("🧪 实际API测试")
    
    # 检查后端服务
    if not check_backend_status():
        print("\n🔧 启动后端服务:")
        print("cd backend_new")
        print("python run.py")
        return
    
    # 测试构建索引API
    progress_url = test_build_index_api()
    
    # 测试进度查询API
    if progress_url:
        test_progress_api(progress_url)
    else:
        print("\n❌ 无法获取进度URL，跳过进度查询测试")

if __name__ == '__main__':
    main()
