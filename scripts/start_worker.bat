@echo off
echo 启动Celery Worker进程...
echo 如果启动卡住，请按 Ctrl+C 停止，然后手动运行：
echo cd backend && python -m celery -A worker worker --loglevel=info --pool=solo
echo.
cd /d "%~dp0.."
cd backend
python -m celery -A worker worker --loglevel=info --pool=solo
pause
