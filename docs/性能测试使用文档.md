# 性能测试基准工具文档

本项目提供了全面的性能测试和优化工具，用于评估和优化浮图项目的性能表现。

## 🎯 测试目标

1. **远程 vs 本地计算性能对比** - 评估Celery分布式计算与本地计算的性能差异
2. **簇大小影响分析** - 分析FAISS索引的`N_LIST`参数对检索性能的影响
3. **批处理大小优化** - 找到最优的`batchsize`配置
4. **设备性能对比** - 比较CPU和GPU的性能表现
5. **并发处理能力** - 测试系统的并发处理性能
6. **配置参数优化** - 自动寻找最佳配置组合

## 📁 工具文件

| 文件名 | 功能描述 | 适用场景 |
|--------|----------|----------|
| `quick_performance_test.py` | 快速性能测试 | 日常性能检查，配置验证 |
| `performance_testbench.py` | 完整性能基准测试 | 全面性能评估，发布前测试 |
| `config_optimizer.py` | 配置参数优化器 | 寻找最佳配置，性能调优 |
| `testbench_configs.json` | 测试配置文件 | 预定义测试场景 |
| `scripts/performance_test.bat` | Windows批处理脚本 | 便捷启动测试 |

## 🚀 快速开始

### 1. 快速性能测试（推荐）

```bash
# 运行快速测试
python scripts/quick_performance_test.py

# 或使用批处理脚本
scripts\performance_test.bat
```

快速测试包括：
- 当前配置性能评估
- 分布式计算可用性检查
- 本地 vs 分布式性能对比
- 不同批处理大小性能测试

### 2. 完整性能基准测试

```bash
# 完整测试（需要较长时间）
python scripts/performance_testbench.py --mode full

# 快速版本
python scripts/performance_testbench.py --mode quick --images 10

# 自定义测试
python scripts/performance_testbench.py --mode custom --images 15
```

### 3. 配置参数优化

```bash
# 完整优化流程
python scripts/config_optimizer.py --mode full

# 仅网格搜索
python scripts/config_optimizer.py --mode grid
```

## 📊 测试结果

所有测试结果将保存在 `performance_reports/` 目录下，包括：

- **JSON数据文件** - 原始测试数据
- **Markdown报告** - 人类可读的测试报告
- **PNG图表** - 性能趋势图表

### 报告内容

1. **配置信息** - 测试时的配置参数
2. **性能指标** - 处理时间、吞吐量、加速比等
3. **对比分析** - 不同配置的性能对比
4. **优化建议** - 基于测试结果的优化建议

## 🔧 测试配置

### 可调节的配置参数

在 `config/config.py` 中可以调节以下参数：

| 参数 | 描述 | 影响 |
|------|------|------|
| `device` | 计算设备 ("cpu"/"cuda") | 特征提取速度 |
| `batchsize` | 批处理大小 | 内存使用和吞吐量 |
| `N_LIST` | FAISS簇数量 | 检索速度和精度 |
| `DISTRIBUTED_AVAILABLE` | 分布式计算开关 | 是否使用Celery |
| `CELERY_TASK_TIME_LIMIT` | 任务超时时间 | 分布式任务稳定性 |

### 测试场景配置

`testbench_configs.json` 包含预定义的测试场景：

- **baseline** - 基准配置
- **high_performance** - 高性能配置
- **low_latency** - 低延迟配置
- **accuracy_focused** - 准确率优先配置

## 📈 性能指标

### 主要指标

1. **处理时间 (Processing Time)** - 完成任务所需时间
2. **吞吐量 (Throughput)** - 每秒处理的图像数量
3. **加速比 (Speedup)** - 相对于基准配置的性能提升
4. **内存使用 (Memory Usage)** - 峰值内存消耗
5. **准确率 (Accuracy)** - 检索结果的准确性

### 评估维度

1. **可扩展性** - 处理大量数据的能力
2. **稳定性** - 长时间运行的稳定性
3. **资源效率** - CPU/内存使用效率
4. **响应延迟** - 单次请求的响应时间

## 🛠️ 使用指南

### 日常性能检查

```bash
# 每日快速检查
python scripts/quick_performance_test.py
```

适用于：
- 验证新部署的性能
- 检查配置更改的影响
- 监控系统性能退化

### 发布前性能测试

```bash
# 完整基准测试
python scripts/performance_testbench.py --mode full
```

适用于：
- 新版本发布前的性能验证
- 重大配置更改后的全面测试
- 性能回归测试

### 性能优化

```bash
# 自动寻找最佳配置
python scripts/config_optimizer.py --mode full
```

适用于：
- 新环境的性能调优
- 硬件升级后的重新优化
- 定期性能优化

## 🔍 分布式测试准备

### 启动Worker

测试分布式计算前，需要启动Celery Worker：

```bash
# 方法1：使用批处理脚本
scripts\performance_test.bat
# 选择选项5启动Worker

# 方法2：手动启动
cd backend
python -m celery -A worker worker --loglevel=info --pool=solo
```

### 检查分布式环境

```bash
python -c "
from config import config
from backend.worker import celery_app
print('Redis:', config.REDIS_HOST, config.REDIS_PORT)
print('Workers:', celery_app.control.inspect().active())
"
```

## 📋 最佳实践

### 1. 测试环境准备

- 确保系统资源充足（CPU、内存）
- 关闭不必要的后台程序
- 使用一致的测试数据

### 2. 测试执行

- 先运行快速测试验证环境
- 分批进行完整测试避免系统过载
- 多次运行取平均值提高可靠性

### 3. 结果分析

- 关注吞吐量和延迟的平衡
- 考虑实际使用场景的需求
- 验证优化后的配置在生产环境的表现

### 4. 配置优化

- 逐步调整参数，避免大幅度改动
- 记录每次优化的结果
- 在生产环境谨慎应用优化配置

## 🚨 注意事项

1. **资源消耗** - 完整测试可能消耗大量CPU和内存
2. **测试时间** - 完整基准测试可能需要几分钟到几十分钟
3. **环境一致性** - 确保测试环境与生产环境一致
4. **数据准备** - 某些测试需要预先准备数据集
5. **Worker状态** - 分布式测试需要确保Worker正常运行

## 📞 故障排除

### 常见问题

1. **分布式测试失败**
   - 检查Redis服务是否运行
   - 确认Worker已启动
   - 验证网络连接

2. **GPU测试失败**
   - 检查CUDA环境
   - 确认PyTorch GPU支持
   - 验证显存是否足够

3. **内存不足**
   - 降低批处理大小
   - 减少测试图像数量
   - 释放系统内存

4. **测试结果异常**
   - 检查配置参数合理性
   - 验证测试数据完整性
   - 重新运行测试确认

### 获取帮助

如果遇到问题，可以：
1. 查看详细的错误信息
2. 检查测试日志
3. 运行单项测试定位问题
4. 参考项目文档和代码注释

---

*最后更新: 2025年6月25日*
