#!/usr/bin/env python3
"""
调试进度文件保存和加载的脚本
"""

import os
import sys
import json
from datetime import datetime

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_root, 'backend_new'))

def test_progress_file_operations():
    """测试进度文件的保存和加载"""
    print("=== 测试进度文件操作 ===")
    
    # 模拟进度数据
    test_filename = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    test_data = {
        "task_id": "test-task-123",
        "progress": 50.0,
        "status": "processing",
        "message": "测试进度数据",
        "start_time": datetime.now().isoformat()
    }
    
    print(f"测试文件名: {test_filename}")
    print(f"测试数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    # 计算进度文件目录
    progress_dir = os.path.join(project_root, 'data', 'progress')
    file_path = os.path.join(progress_dir, test_filename)
    
    print(f"进度目录: {progress_dir}")
    print(f"文件路径: {file_path}")
    
    try:
        # 确保目录存在
        os.makedirs(progress_dir, exist_ok=True)
        print(f"✅ 进度目录已创建/存在")
        
        # 保存测试文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 测试文件已保存")
        
        # 验证文件存在
        if os.path.exists(file_path):
            print(f"✅ 文件确实存在")
            
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            print(f"✅ 文件读取成功")
            print(f"读取的数据: {json.dumps(loaded_data, indent=2, ensure_ascii=False)}")
            
            # 验证数据一致性
            if loaded_data == test_data:
                print(f"✅ 数据一致性验证通过")
            else:
                print(f"❌ 数据不一致")
                print(f"原始: {test_data}")
                print(f"读取: {loaded_data}")
        else:
            print(f"❌ 文件不存在")
            
        # 清理测试文件
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🧹 测试文件已清理")
            
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        return False
    
    return True

def check_existing_progress_files():
    """检查现有的进度文件"""
    print(f"\n=== 检查现有进度文件 ===")
    
    progress_dir = os.path.join(project_root, 'data', 'progress')
    print(f"进度目录: {progress_dir}")
    
    if not os.path.exists(progress_dir):
        print(f"⚠️  进度目录不存在")
        return
    
    try:
        files = os.listdir(progress_dir)
        if not files:
            print(f"📂 进度目录为空")
        else:
            print(f"📂 找到 {len(files)} 个文件:")
            for file in sorted(files):
                file_path = os.path.join(progress_dir, file)
                size = os.path.getsize(file_path)
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                print(f"  📄 {file} ({size} bytes, {mtime})")
                
                # 尝试读取文件内容
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"    ✅ JSON格式正确, 状态: {data.get('status', 'N/A')}, 进度: {data.get('progress', 'N/A')}%")
                except Exception as e:
                    print(f"    ❌ 读取失败: {e}")
                    
    except Exception as e:
        print(f"❌ 检查失败: {e}")

def simulate_api_request(filename):
    """模拟API请求"""
    print(f"\n=== 模拟API请求 ===")
    print(f"请求文件: {filename}")
    
    # 模拟后端的 _load_progress_data 函数
    progress_dir = os.path.join(project_root, 'data', 'progress')
    file_path = os.path.join(progress_dir, filename)
    
    print(f"查找路径: {file_path}")
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ 找到文件，数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            return False
    else:
        print(f"❌ 文件不存在")
        return False

def main():
    """主函数"""
    print("🔍 进度文件调试工具")
    
    # 测试基本操作
    if test_progress_file_operations():
        print(f"\n✅ 基本文件操作测试通过")
    else:
        print(f"\n❌ 基本文件操作测试失败")
    
    # 检查现有文件
    check_existing_progress_files()
    
    # 如果有参数，模拟API请求
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        simulate_api_request(filename)
    else:
        print(f"\n💡 提示: 可以传入文件名参数来模拟API请求")
        print(f"例如: python debug_progress_files.py 20250625_154436_xxx.json")

if __name__ == '__main__':
    main()
