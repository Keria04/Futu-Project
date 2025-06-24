"""
启动计算端服务
"""
import os
import sys

def main():
    # 设置工作目录到项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    os.chdir(project_root)
    
    print(f"工作目录: {os.getcwd()}")
    print("启动计算端服务...")
    
    # 导入并运行
    sys.path.insert(0, current_dir)
    from compute_service.worker import run_compute_worker
    
    run_compute_worker()

if __name__ == "__main__":
    main()
