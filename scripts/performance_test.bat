@echo off
echo ========================================
echo 浮图项目性能测试工具
echo ========================================
echo.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

:menu
echo 请选择测试模式:
echo [1] 快速性能测试 (推荐)
echo [2] 完整性能基准测试
echo [3] 自定义配置测试
echo [4] 分布式计算可用性检查
echo [5] 启动Worker (如需要分布式测试)
echo [0] 退出
echo.
set /p choice=请输入选择 (0-5): 

if "%choice%"=="1" goto quick_test
if "%choice%"=="2" goto full_test
if "%choice%"=="3" goto custom_test
if "%choice%"=="4" goto check_distributed
if "%choice%"=="5" goto start_worker
if "%choice%"=="0" goto exit
echo 无效选择，请重试
goto menu

:quick_test
echo.
echo 开始快速性能测试...
echo ========================================
python scripts\quick_performance_test.py
echo.
echo 快速测试完成！
pause
goto menu

:full_test
echo.
echo 开始完整性能基准测试...
echo 警告: 这可能需要几分钟时间
echo ========================================
python scripts\performance_testbench.py --mode full
echo.
echo 完整测试完成！
pause
goto menu

:custom_test
echo.
echo 自定义配置测试...
echo ========================================
python scripts\performance_testbench.py --mode custom --images 15
echo.
echo 自定义测试完成！
pause
goto menu

:check_distributed
echo.
echo 检查分布式计算可用性...
echo ========================================
python -c "
import sys, os
sys.path.append('.')
sys.path.append('backend')
from config import config
print('配置信息:')
print(f'  Redis主机: {config.REDIS_HOST}:{config.REDIS_PORT}')
print(f'  分布式可用: {config.DISTRIBUTED_AVAILABLE}')

try:
    import redis
    r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_BROKER_DB)
    r.ping()
    print('✅ Redis连接正常')
    
    from backend.worker import celery_app
    i = celery_app.control.inspect()
    active_workers = i.active()
    
    if active_workers:
        print(f'✅ 发现 {len(active_workers)} 个活跃Worker')
        for worker_name in active_workers.keys():
            print(f'  - {worker_name}')
    else:
        print('❌ 没有发现活跃Worker')
        print('提示: 运行选项5启动Worker')
        
except Exception as e:
    print(f'❌ 检查失败: {e}')
"
echo.
pause
goto menu

:start_worker
echo.
echo 启动Celery Worker...
echo 注意: 保持此窗口打开，Worker将在后台运行
echo 按 Ctrl+C 停止Worker
echo ========================================
cd backend
python -m celery -A worker worker --loglevel=info --pool=solo
cd ..
pause
goto menu

:exit
echo 再见！
exit /b 0
