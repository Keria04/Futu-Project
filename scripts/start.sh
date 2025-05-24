#!/bin/bash

check_and_kill_port() {
  local port=$1
  local pname=$2
  pid=$(lsof -ti tcp:$port)
  if [ -n "$pid" ]; then
    echo "$pname 端口 $port 已被占用，进程号: $pid"
    read -p "是否结束该进程？[y/N] " yn
    if [[ "$yn" == "y" || "$yn" == "Y" ]]; then
      kill -9 $pid
      echo "已结束进程 $pid"
    else
      echo "请手动释放端口后再启动。"
      exit 1
    fi
  fi
}

check_and_kill_port 19197 "前端"
check_and_kill_port 19198 "后端"

# 启动前端和后端服务，分别在两个后台线程

# 启动前端
(
  cd "$(dirname "$0")/.."
  cd frontend
  npm install
  npm run dev
) &

# 启动后端
(
  cd "$(dirname "$0")/.."
  export KMP_DUPLICATE_LIB_OK=TRUE
  python3 backend/app.py
) &

# 打开默认浏览器访问前端地址
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open http://localhost:19197
elif command -v open >/dev/null 2>&1; then
  open http://localhost:19197
else
  echo "请手动打开浏览器访问 http://localhost:19197"
fi

wait
