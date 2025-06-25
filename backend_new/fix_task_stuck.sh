#!/bin/bash

# 浮图项目任务卡顿修复脚本
# 作用：修复计算服务器任务重复处理导致的卡顿问题

echo "=== 浮图项目任务卡顿修复脚本 ==="
echo "正在备份和替换相关文件..."

# 检查是否在正确的目录
if [ ! -f "run.py" ]; then
    echo "错误：请在 backend_new 目录下运行此脚本"
    exit 1
fi

# 1. 备份原文件
echo "1. 备份原始文件..."
if [ -f "compute_server/compute_server.py" ]; then
    cp compute_server/compute_server.py compute_server/compute_server_backup_$(date +%Y%m%d_%H%M%S).py
    echo "   ✓ 已备份 compute_server.py"
fi

# 2. 使用修复版本
echo "2. 应用修复版本..."
if [ -f "compute_server/compute_server_fixed.py" ]; then
    cp compute_server/compute_server_fixed.py compute_server/compute_server.py
    echo "   ✓ 已应用修复版本的 compute_server.py"
else
    echo "   ✗ 未找到修复版本文件"
fi

# 3. 更新README
echo "3. 更新架构文档..."
if [ -f "README_Architecture_Fixed.md" ]; then
    cp README_Architecture_Fixed.md README_Architecture.md
    echo "   ✓ 已更新架构文档"
fi

# 4. 清理Redis缓存（可选）
echo "4. 清理Redis缓存..."
read -p "是否清理Redis缓存以移除可能存在的锁？(y/N): " choice
case "$choice" in 
    y|Y ) 
        if command -v redis-cli &> /dev/null; then
            redis-cli FLUSHDB
            echo "   ✓ 已清理Redis缓存"
        else
            echo "   ! 未找到redis-cli命令，请手动清理"
        fi
        ;;
    * ) 
        echo "   - 跳过Redis缓存清理"
        ;;
esac

echo ""
echo "=== 修复完成 ==="
echo "修复内容："
echo "  - 添加了分布式锁机制防止任务重复处理"
echo "  - 优化了任务处理流程"
echo "  - 改进了异常处理和资源清理"
echo ""
echo "请重启服务以应用修复："
echo "  python run.py both"
echo ""
echo "如果问题仍然存在，请检查日志文件：futu_backend.log"
