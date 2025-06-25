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

def start_compute_service(debug=False):
    """启动计算端服务"""
    print("启动计算端服务...")
    python_path = sys.executable
    compute_script = os.path.join("compute_service", "worker.py")
      # 确保从backend目录启动
    cwd = os.path.dirname(os.path.abspath(__file__))
    
    # 根据debug模式决定是否显示输出
    if debug:
        # Debug模式：显示输出到控制台，传递debug参数
        process = subprocess.Popen([
            python_path, compute_script, "--debug"
        ], cwd=cwd, stdout=None, stderr=None)
    else:
        # 正常模式：隐藏输出
        process = subprocess.Popen([
            python_path, compute_script
        ], cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    return process

def main():
    """主函数"""
    import argparse
    
    # 添加命令行参数解析
    parser = argparse.ArgumentParser(description='浮图图像搜索系统启动脚本')
    parser.add_argument('--debug', action='store_true', help='启用计算端debug模式')
    parser.add_argument('--compute-only', action='store_true', help='只启动计算端')
    parser.add_argument('--control-only', action='store_true', help='只启动控制端')
    args = parser.parse_args()
    
    processes = []
    
    try:
        # 检查Redis
        if not args.compute_only:
            start_redis()
        
        # 启动控制端
        if not args.compute_only:
            control_process = start_control_service()
            if control_process:
                processes.append(("控制端", control_process))
            
            # 等待控制端启动
            time.sleep(2)
        
        # 启动计算端
        if not args.control_only:
            compute_process = start_compute_service(debug=args.debug)
            if compute_process:
                processes.append(("计算端", compute_process))
        
        print("\n" + "="*50)
        print("🎉 浮图图像搜索系统启动完成!")
        if not args.compute_only:
            print("📊 控制端: http://localhost:19198")
        if not args.control_only:
            if args.debug:
                print("🔧 计算端: Debug模式运行，输出显示在控制台")
            else:
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
