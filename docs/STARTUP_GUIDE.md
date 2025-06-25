# 浮图图像搜索系统 - 启动说明

## 启动模式

### 1. 正常启动
```bash
python start.py
```
启动完整系统（控制端 + 计算端），计算端在后台运行。

### 2. Debug模式启动
```bash
python start.py --debug
```
启动完整系统，计算端以debug模式运行，显示详细的调试信息。

### 3. 只启动控制端
```bash
python start.py --control-only
```
只启动控制端服务，用于API测试。

### 4. 只启动计算端
```bash
python start.py --compute-only
```
只启动计算端服务。

### 5. 只启动计算端（Debug模式）
```bash
python start.py --compute-only --debug
```
只启动计算端服务，显示详细的调试信息。

## Debug信息说明

当使用 `--debug` 参数启动时，计算端会显示以下调试信息：

- 🐛 **DEBUG模式标识**: 确认debug模式已启用
- 🔧 **初始化信息**: 工作者初始化过程
- 🔍 **任务等待**: 显示正在等待任务
- 📥 **任务接收**: 收到新任务的详细信息
- 🏷️ **任务类型**: 显示任务类型
- 📊 **数据大小**: 显示任务数据的大小
- ✅ **处理器匹配**: 找到合适的任务处理器
- 🖼️ **图片处理**: 图片解码和尺寸信息
- ⏱️ **性能监控**: 显示特征提取耗时
- 📤 **结果发送**: 确认结果已发送到队列
- ❌ **错误详情**: 显示完整的错误堆栈信息

## 示例输出

### 正常模式
```
2025-06-24 10:30:15 - compute_worker - INFO - 计算工作者 compute_worker 已启动
2025-06-24 10:30:16 - compute_worker - INFO - 处理任务: task_123, 类型: FEATURE_EXTRACTION
2025-06-24 10:30:17 - compute_worker - INFO - 任务完成: task_123, 状态: SUCCESS
```

### Debug模式
```
2025-06-24 10:30:15 - compute_worker - INFO - 🐛 DEBUG模式已启用
2025-06-24 10:30:15 - compute_worker - DEBUG - 🔧 初始化计算工作者: compute_worker
2025-06-24 10:30:15 - compute_worker - INFO - 计算工作者 compute_worker 已启动
2025-06-24 10:30:16 - compute_worker - DEBUG - 🔍 等待任务...
2025-06-24 10:30:16 - compute_worker - DEBUG - 📥 收到任务: task_123
2025-06-24 10:30:16 - compute_worker - DEBUG - 🏷️ 任务类型: FEATURE_EXTRACTION
2025-06-24 10:30:16 - compute_worker - DEBUG - 📊 任务数据大小: 50240 bytes
2025-06-24 10:30:16 - compute_worker - INFO - 处理任务: task_123, 类型: FEATURE_EXTRACTION
2025-06-24 10:30:16 - compute_worker - DEBUG - ✅ 找到处理器: FeatureExtractionProcessor
2025-06-24 10:30:16 - compute_worker - DEBUG - 🖼️ 开始处理单张图片特征提取
2025-06-24 10:30:16 - compute_worker - DEBUG - 📏 图片尺寸: (224, 224)
2025-06-24 10:30:16 - compute_worker - DEBUG - 🎨 图片模式: RGB
2025-06-24 10:30:16 - compute_worker - DEBUG - 🔍 使用特征提取器: FeatureExtractor
2025-06-24 10:30:17 - compute_worker - DEBUG - ✅ 特征提取完成，耗时: 0.245s
2025-06-24 10:30:17 - compute_worker - DEBUG - 📊 特征维度: (2048,)
2025-06-24 10:30:17 - compute_worker - DEBUG - 📤 结果已发送到队列
2025-06-24 10:30:17 - compute_worker - INFO - 任务完成: task_123, 状态: SUCCESS
```

## 性能监控

Debug模式会显示以下性能指标：
- **图片解码时间**
- **特征提取时间**
- **总处理时间**
- **特征向量维度**
- **任务数据大小**

## 错误诊断

在Debug模式下，所有错误都会显示完整的堆栈信息，便于问题诊断：
- **Redis连接问题**
- **图片解码错误**
- **特征提取失败**
- **模型加载问题**

## 注意事项

1. Debug模式会产生大量日志输出，建议只在开发和调试时使用
2. Debug模式可能会影响性能，生产环境建议使用正常模式
3. 如果计算端频繁出错，建议使用Debug模式查看详细错误信息
4. 按 `Ctrl+C` 可以优雅地停止所有服务

## 服务地址

- **控制端API**: http://localhost:19198
- **健康检查**: http://localhost:19198/health
- **前端地址**: http://localhost:19197 (如果启动了前端)
