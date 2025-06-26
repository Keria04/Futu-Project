#!/usr/bin/env python3
"""
简化版Celery Worker启动脚本
"""

import os
import sys

# 设置环境
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(backend_dir)

# 切换到项目根目录
os.chdir(project_dir)

# 设置Python路径
sys.path.insert(0, backend_dir)
sys.path.insert(0, project_dir)

if __name__ == '__main__':
    print("启动简化版Celery Worker...")
    print(f"工作目录: {os.getcwd()}")
    
    # 直接运行celery命令
    os.system(f'cd backend && python -m celery -A worker worker --loglevel=info --pool=solo')
