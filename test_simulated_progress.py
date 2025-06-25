#!/usr/bin/env python3
"""
模拟构建索引请求，测试进度文件保存
"""

import os
import sys
import json
import uuid
from datetime import datetime

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_root, 'backend_new'))

def simulate_build_index_progress():
    """模拟构建索引的进度保存流程"""
    print("=== 模拟构建索引进度保存 ===")
    
    # 模拟生成任务ID和文件名（与后端代码相同）
    task_id = str(uuid.uuid4())
    progress_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task_id}.json"
    progress_file = progress_filename  # 直接使用文件名
    
    print(f"任务ID: {task_id}")
    print(f"进度文件名: {progress_filename}")
    print(f"progress_file变量: {progress_file}")
    
    # 模拟初始进度数据（与后端代码相同）
    progress_data = {
        "task_id": task_id,
        "progress": 5.0,
        "status": "processing",
        "message": f"任务已启动，准备处理 100 张图片",
        "start_time": datetime.now().isoformat(),
        "dataset_names": ["test_dataset"],
        "dataset_info": {"test_dataset": {"id": 1, "image_count": 100}},
        "total_images": 100,
        "distributed": False
    }
    
    print(f"初始进度数据: {json.dumps(progress_data, indent=2, ensure_ascii=False)}")
    
    # 模拟 _save_progress_data 函数
    try:
        # 构建完整的文件路径
        progress_dir = os.path.join(project_root, 'data', 'progress')
        os.makedirs(progress_dir, exist_ok=True)
        
        # 直接使用文件名，不进行路径替换
        file_path = os.path.join(progress_dir, progress_filename)
        
        print(f"保存路径: {file_path}")
        
        # 保存数据
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 进度文件保存成功")
        
        # 验证文件存在
        if os.path.exists(file_path):
            print(f"✅ 文件确实存在")
            file_size = os.path.getsize(file_path)
            print(f"文件大小: {file_size} bytes")
        else:
            print(f"❌ 文件不存在")
            return None
            
        # 模拟前端的API请求URL
        api_url = f"/api/progress/{progress_filename}"
        print(f"前端应该请求的URL: {api_url}")
        
        # 模拟 _load_progress_data 函数
        print(f"\n--- 模拟加载进度数据 ---")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            print(f"✅ 进度数据加载成功")
            print(f"加载的状态: {loaded_data.get('status')}")
            print(f"加载的进度: {loaded_data.get('progress')}%")
        except Exception as e:
            print(f"❌ 加载失败: {e}")
            return None
        
        return progress_filename
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return None

def test_api_endpoint(filename):
    """测试API端点是否能找到文件"""
    print(f"\n=== 测试API端点 ===")
    print(f"文件名: {filename}")
    
    # 模拟 get_progress 路由中的 _load_progress_data 调用
    progress_dir = os.path.join(project_root, 'data', 'progress')
    file_path = os.path.join(progress_dir, filename)
    
    print(f"API查找路径: {file_path}")
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ API能够找到并读取文件")
            print(f"返回状态: {data.get('status')}")
            print(f"返回进度: {data.get('progress')}%")
            print(f"返回消息: {data.get('message')}")
            return True
        except Exception as e:
            print(f"❌ API读取文件失败: {e}")
            return False
    else:
        print(f"❌ API找不到文件")
        return False

def main():
    """主函数"""
    print("🧪 模拟构建索引进度测试")
    
    # 模拟保存进度
    filename = simulate_build_index_progress()
    
    if filename:
        # 测试API端点
        if test_api_endpoint(filename):
            print(f"\n🎉 测试成功！进度文件保存和加载都正常工作")
            print(f"\n🔧 现在你可以用真实的API测试:")
            print(f"1. 启动后端服务")
            print(f"2. 发送构建索引请求") 
            print(f"3. 检查返回的progress_file URL")
            print(f"4. 用浏览器或curl测试该URL")
        else:
            print(f"\n❌ API端点测试失败")
        
        # 清理测试文件
        file_path = os.path.join(project_root, 'data', 'progress', filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🧹 测试文件已清理")
    else:
        print(f"\n❌ 进度保存测试失败")

if __name__ == '__main__':
    main()
