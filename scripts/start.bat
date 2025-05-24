@echo off
setlocal enabledelayedexpansion

REM 检查端口是否被占用并询问是否结束进程
set PORTS=19197 19198
set NAMES=前端 后端
set IDX=0

for %%P in (%PORTS%) do (
    set /a IDX+=1
    for /f "tokens=%IDX%" %%N in ("%NAMES%") do set NAME=%%N
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%%P ^| findstr LISTENING') do (
        set PID=%%a
        echo !NAME! 端口 %%P 已被占用，进程号: !PID!
        set /p KILL=是否结束该进程？[y/N] 
        if /i "!KILL!"=="y" (
            taskkill /F /PID !PID!
            echo 已结束进程 !PID!
        ) else (
            echo 请手动释放端口后再启动。
            exit /b 1
        )
    )
)

REM 启动前端
start cmd /k "cd /d %~dp0..\frontend && npm install && npm run dev"

REM 启动后端
start cmd /k "cd /d %~dp0.. && set KMP_DUPLICATE_LIB_OK=TRUE && python backend/app.py"

REM 打开默认浏览器访问前端地址
start http://localhost:19197