@echo off
echo 启动浮图图片检索系统...
echo.

echo 启动后端服务器...
cd /d "%~dp0"
start "后端服务器" cmd /k "python backend/app.py"

echo 等待后端服务器启动...
timeout /t 5 /nobreak >nul

echo 启动前端开发服务器...
cd frontend
start "前端开发服务器" cmd /k "npm run dev"

echo.
echo 系统启动完成！
echo 后端地址: http://localhost:19198
echo 前端地址: http://localhost:19197
echo.
echo 按任意键退出...
pause >nul
