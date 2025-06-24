"""
统一启动脚本
"""
import os
import sys
import subprocess
import time
import signal
import threading
from typing import List

def start_redis():
    """启动Redis服务"""
    print("正在检查Redis服务...")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✓ Redis服务已运行")
        return None
    except Exception:
        print("⚠ Redis服务未运行，请手动启动Redis")
        return None

def start_control_service():
    """启动控制端服务"""
    print("启动控制端服务...")
    python_path = sys.executable
    control_script = os.path.join("control_service", "app.py")
    
    # 确保从backend目录启动
    cwd = os.path.dirname(os.path.abspath(__file__))
    
    process = subprocess.Popen([
        python_path, control_script
    ], cwd=cwd)
    
    return process

def start_compute_service():
    """启动计算端服务"""
    print("启动计算端服务...")
    python_path = sys.executable
    compute_script = os.path.join("compute_service", "worker.py")
    
    # 确保从backend目录启动
    cwd = os.path.dirname(os.path.abspath(__file__))
    
    process = subprocess.Popen([
        python_path, compute_script
    ], cwd=cwd)
    
    return process

def main():
    """主函数"""
    processes = []
    
    try:
        # 检查Redis
        start_redis()
        
        # 启动控制端
        control_process = start_control_service()
        if control_process:
            processes.append(("控制端", control_process))
        
        # 等待控制端启动
        time.sleep(2)
        
        # 启动计算端
        compute_process = start_compute_service()
        if compute_process:
            processes.append(("计算端", compute_process))
        
        print("\n" + "="*50)
        print("🎉 浮图图像搜索系统启动完成!")
        print("📊 控制端: http://localhost:19198")
        print("🔧 计算端: 后台运行")
        print("="*50)
        print("按 Ctrl+C 停止所有服务")
        
        # 等待所有进程
        while True:
            time.sleep(1)
            # 检查进程状态
            for name, process in processes:
                if process.poll() is not None:
                    print(f"⚠ {name}服务意外退出")
    
    except KeyboardInterrupt:
        print("\n正在停止所有服务...")
        
        # 停止所有进程
        for name, process in processes:
            try:
                print(f"停止{name}服务...")
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"强制终止{name}服务...")
                process.kill()
            except Exception as e:
                print(f"停止{name}服务时出错: {e}")
        
        print("所有服务已停止")

if __name__ == "__main__":
    main()
