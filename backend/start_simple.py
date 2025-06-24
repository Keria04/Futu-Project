"""
简化启动脚本 - 不依赖Redis
"""
import os
import sys
import subprocess
import time

def start_control_service_simple():
    """启动简化的控制端服务"""
    print("启动控制端服务（简化模式）...")
    
    # 设置工作目录
    current_dir = os.getcwd()
    target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if current_dir != target_dir:
        os.chdir(target_dir)
    
    python_path = sys.executable
    control_script = os.path.join("backend", "control_service", "app.py")
    
    # 添加环境变量，指示简化模式
    env = os.environ.copy()
    env['FUTU_SIMPLE_MODE'] = '1'
    
    process = subprocess.Popen([
        python_path, control_script
    ], cwd=os.getcwd(), env=env)
    
    return process

def main():
    """主函数"""
    print("=" * 50)
    print("🚀 浮图图像搜索系统启动（简化模式）")
    print("⚠️  此模式不需要Redis，但功能受限")
    print("=" * 50)
    
    try:
        # 启动控制端
        control_process = start_control_service_simple()
        
        print("\n✅ 控制端启动成功!")
        print("📊 访问地址: http://localhost:19198")
        print("💡 按 Ctrl+C 停止服务")
        
        # 等待进程
        while True:
            time.sleep(1)
            if control_process.poll() is not None:
                print("⚠️  控制端服务意外退出")
                break
    
    except KeyboardInterrupt:
        print("\n正在停止服务...")
        try:
            control_process.terminate()
            control_process.wait(timeout=5)
        except:
            control_process.kill()
        print("服务已停止")
    
    except Exception as e:
        print(f"启动失败: {e}")

if __name__ == "__main__":
    main()
