@echo off

REM 获取脚本所在目录并切换到 backend 目录
cd /d %~dp0..\backend

REM 启动 celery worker
celery -A worker worker --loglevel=info --pool=solo
