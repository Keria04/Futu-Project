#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# 切换到 backend 目录
cd "$SCRIPT_DIR/../backend"

# 启动 celery worker
celery -A worker worker --loglevel=info --pool=solo
