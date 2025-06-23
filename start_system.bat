@echo off
echo 浮图图片检索系统 - 启动脚本
echo ===============================

echo 正在启动后端服务器...
start "后端服务器" cmd /k "cd /d %~dp0 && python backend/app.py"

echo 等待后端服务器启动...
timeout /t 5 /nobreak > nul

echo 正在启动前端开发服务器...
start "前端服务器" cmd /k "cd /d %~dp0frontend && npm run dev"

echo 等待前端服务器启动...
timeout /t 10 /nobreak > nul

echo.
echo 启动完成！
echo 后端服务地址: http://localhost:19198
echo 前端服务地址: http://localhost:19197
echo.
echo 按任意键打开浏览器...
pause > nul

start http://localhost:19197

echo 系统已启动完成！
echo 关闭此窗口不会停止服务器。
echo 要停止服务器，请关闭对应的服务器窗口。
pause
