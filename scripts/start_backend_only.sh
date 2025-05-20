#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# 切换到上一级目录（即项目根目录）
cd "$SCRIPT_DIR/.."

# 判断操作系统，选择合适的 python 命令
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    PYTHON_CMD=python
else
    PYTHON_CMD=python3
fi

# 启动 backend/app.py
$PYTHON_CMD backend/app.py
