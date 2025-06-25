#!/usr/bin/env python3
"""
Celery Worker启动脚本
用于启动分布式特征提取的后台工作进程
"""

import os
import sys

# 设置工作目录
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(backend_dir)
os.chdir(project_dir)

# 添加后端路径到Python路径
sys.path.insert(0, backend_dir)

if __name__ == '__main__':
    # 使用命令行方式启动，避免直接调用celery_app.start()
    import subprocess
    
    # 切换到backend目录
    os.chdir(backend_dir)
    
    # 使用subprocess启动celery worker
    cmd = [
        sys.executable, '-m', 'celery',
        '-A', 'worker',
        'worker',
        '--loglevel=info',
        '--concurrency=2',
        '--pool=threads',  # 使用线程池而不是进程池
        '--without-gossip',  # 禁用gossip协议
        '--without-mingle',  # 禁用mingle
        '--without-heartbeat',  # 禁用心跳
    ]
    
    print("启动Celery Worker...")
    print(f"命令: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n正在停止Worker...")
    except subprocess.CalledProcessError as e:
        print(f"Worker启动失败: {e}")
        sys.exit(1)
