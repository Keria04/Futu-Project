@echo off

REM 获取脚本所在目录并切换到上一级目录
cd /d %~dp0..
REM 判断 python 命令
where python >nul 2>nul
if %errorlevel%==0 (
    set PYTHON_CMD=python
) else (
    set PYTHON_CMD=python3
)

REM 启动 backend/app.py
%PYTHON_CMD% backend\app.py
