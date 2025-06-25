@echo off
chcp 65001 >nul

REM 浮图项目任务卡顿修复脚本
REM 作用：修复计算服务器任务重复处理导致的卡顿问题

echo === 浮图项目任务卡顿修复脚本 ===
echo 正在备份和替换相关文件...

REM 检查是否在正确的目录
if not exist "run.py" (
    echo 错误：请在 backend_new 目录下运行此脚本
    pause
    exit /b 1
)

REM 1. 备份原文件
echo 1. 备份原始文件...
if exist "compute_server\compute_server.py" (
    for /f "tokens=1-4 delims=/ " %%a in ('date /t') do (
        for /f "tokens=1-2 delims=: " %%e in ('time /t') do (
            copy "compute_server\compute_server.py" "compute_server\compute_server_backup_%%c%%a%%b_%%e%%f.py" >nul
        )
    )
    echo    ✓ 已备份 compute_server.py
)

REM 2. 使用修复版本
echo 2. 应用修复版本...
if exist "compute_server\compute_server_fixed.py" (
    copy "compute_server\compute_server_fixed.py" "compute_server\compute_server.py" >nul
    echo    ✓ 已应用修复版本的 compute_server.py
) else (
    echo    ✗ 未找到修复版本文件
)

REM 3. 更新README
echo 3. 更新架构文档...
if exist "README_Architecture_Fixed.md" (
    copy "README_Architecture_Fixed.md" "README_Architecture.md" >nul
    echo    ✓ 已更新架构文档
)

REM 4. 清理Redis缓存（可选）
echo 4. 清理Redis缓存...
set /p choice="是否清理Redis缓存以移除可能存在的锁？(y/N): "
if /i "%choice%"=="y" (
    where redis-cli >nul 2>&1
    if !errorlevel! == 0 (
        redis-cli FLUSHDB
        echo    ✓ 已清理Redis缓存
    ) else (
        echo    ! 未找到redis-cli命令，请手动清理
    )
) else (
    echo    - 跳过Redis缓存清理
)

echo.
echo === 修复完成 ===
echo 修复内容：
echo   - 添加了分布式锁机制防止任务重复处理
echo   - 优化了任务处理流程
echo   - 改进了异常处理和资源清理
echo.
echo 请重启服务以应用修复：
echo   python run.py both
echo.
echo 如果问题仍然存在，请检查日志文件：futu_backend.log
pause
