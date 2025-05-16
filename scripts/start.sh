#!/bin/bash

# 切换到项目根目录
cd "$(dirname "$0")/.."

# 检查 environment.yml 是否存在
if [ ! -f environment.yml ]; then
    echo "Error: environment.yml not found in project root." >&2
    exit 1
fi

# 自动检测 conda 路径并加载初始化脚本
if [ -n "$CONDA_EXE" ]; then
    CONDA_BASE=$(dirname "$(dirname "$CONDA_EXE")")
    # shellcheck source=/dev/null
    source "$CONDA_BASE/etc/profile.d/conda.sh"
else
    echo "Error: Conda is not installed or not found in PATH." >&2
    exit 1
fi

# 检查 .conda 环境是否已存在
if [ ! -d ".conda" ]; then
    echo "Creating conda environment at ./.conda ..."
    conda env create -f environment.yml -p .conda --python=3.12.0
else
    echo "Conda environment ./.conda already exists."
fi

# 激活当前目录下的 .conda 环境
conda activate "$(pwd)/.conda"
if [ $? -ne 0 ]; then
    echo "Failed to activate conda environment." >&2
    exit 1
fi

echo "Conda environment activated at ./.conda"

# 启动后端
cd backend
if [ -f "app.py" ]; then
    echo "Starting Flask application in background..."
    python app.py &
    BACKEND_PID=$!
else
    echo "Error: app.py not found in backend directory." >&2
    exit 1
fi

# 启动前端
cd ../frontend
if [ -f "package.json" ]; then
    # 检查 Node.js 和 npm 是否已安装
    npm install
    if [ $? -ne 0 ]; then
        echo "Failed to install npm packages." >&2
        exit 1
    fi
    echo "Starting Vite frontend in background..."
    npm run dev &
    FRONTEND_PID=$!
else
    echo "Error: package.json not found in frontend directory." >&2
    exit 1
fi

# 等待前后端进程
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
wait $BACKEND_PID
wait $FRONTEND_PID
