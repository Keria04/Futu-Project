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
        echo Port %%P for !NAME! is already in use, PID: !PID!
        set /p KILL=Do you want to terminate this process? [y/N] 
        if /i "!KILL!"=="y" (
            taskkill /F /PID !PID!
            echo Process !PID! has been terminated.
        ) else (
            echo Please free the port manually before starting.
            exit /b 1
        )
    )
)

REM 启动前端
start cmd /k "cd /d %~dp0..\frontend && npm install && npm run dev"

REM 启动后端
start cmd /k "cd /d %~dp0.. && set KMP_DUPLICATE_LIB_OK=TRUE && python backend/app.py"

REM 延时5秒
timeout /t 5 /nobreak >nul

echo Opening the web page, please wait...

REM 打开默认浏览器访问前端地址
start http://localhost:19197