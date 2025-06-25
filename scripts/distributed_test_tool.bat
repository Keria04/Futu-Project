@echo off
title 浮图项目 - 分布式计算测试工具
color 0A

echo ========================================
echo 浮图项目 - 分布式计算测试工具
echo ========================================
echo.

:menu
echo 请选择操作:
echo 1. 启动Flask应用
echo 2. 启动Celery Worker
echo 3. 测试分布式功能
echo 4. 查看功能说明
echo 5. 退出
echo.
set /p choice=请输入选择 (1-5): 

if "%choice%"=="1" goto start_flask
if "%choice%"=="2" goto start_worker
if "%choice%"=="3" goto test_function
if "%choice%"=="4" goto show_readme
if "%choice%"=="5" goto exit

echo 无效选择，请重新输入
goto menu

:start_flask
echo.
echo 正在启动Flask应用...
echo 应用将运行在 http://localhost:19198
echo 按 Ctrl+C 停止应用
echo.
cd /d "%~dp0"
python backend/app.py
pause
goto menu

:start_worker
echo.
echo 正在启动Celery Worker...
echo 这将启动分布式计算后台进程
echo 按 Ctrl+C 停止Worker
echo.
cd /d "%~dp0"
python backend/start_worker.py
pause
goto menu

:test_function
echo.
echo 正在测试分布式功能...
echo.
cd /d "%~dp0"
python test_distributed_fix.py
echo.
pause
goto menu

:show_readme
echo.
echo 正在打开功能说明文档...
start DISTRIBUTED_FIX_README.md
goto menu

:exit
echo.
echo 感谢使用！
timeout /t 2 >nul
exit
