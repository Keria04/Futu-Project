#!/usr/bin/env python3
"""
性能测试启动器
从项目根目录启动各种性能测试工具
"""

import os
import sys
import subprocess
import argparse

def run_script(script_name, args=None):
    """运行指定的脚本"""
    script_path = os.path.join(script_name)
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 脚本运行失败: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ 找不到脚本: {script_path}")
        return False

def main():
    parser = argparse.ArgumentParser(description='性能测试启动器')
    parser.add_argument('command', choices=['quick', 'full', 'optimize', 'verify', 'examples'],
                      help='要运行的测试类型')
    parser.add_argument('--images', type=int, default=20,
                      help='测试图像数量')
    parser.add_argument('--mode', choices=['full', 'grid', 'adaptive'], default='full',
                      help='优化模式')
    
    args = parser.parse_args()
    
    print("🚀 浮图项目性能测试启动器")
    print("="*50)
    
    if args.command == 'quick':
        print("开始快速性能测试...")
        success = run_script("quick_performance_test.py")
        
    elif args.command == 'full':
        print("开始完整性能基准测试...")
        success = run_script("performance_testbench.py", ["--mode", "full", "--images", str(args.images)])
        
    elif args.command == 'optimize':
        print("开始配置优化...")
        success = run_script("config_optimizer.py", ["--mode", args.mode])
        
    elif args.command == 'verify':
        print("开始验证测试工具...")
        success = run_script("verify_testbench.py")
        
    elif args.command == 'examples':
        print("开始运行示例...")
        success = run_script("performance_examples.py")
    
    if success:
        print("\n✅ 测试完成!")
    else:
        print("\n❌ 测试失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()
