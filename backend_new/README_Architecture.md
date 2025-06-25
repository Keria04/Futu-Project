# 浮图项目后端重构说明

## 架构概述

项目已重构为分离式架构，支持控制端和计算端独立部署：

- **控制端 (Controller)**: 负责Flask API、数据库操作、FAISS索引管理
- **计算端 (Compute Server)**: 负责图片特征提取计算
- **Redis**: 作为控制端和计算端之间的通信中间件

## 最新修复（2025-06-25）

### 问题诊断
根据日志分析，发现以下问题导致系统卡顿：

1. **任务重复处理**：同一个任务被多个计算工作者重复处理
2. **资源竞争**：多个worker同时处理相同任务造成冲突
3. **清理机制缺失**：任务完成后没有正确清理Redis中的数据

### 修复措施

#### 1. 添加分布式锁机制
在 `redis_client.py` 中添加了分布式锁功能：
- `acquire_lock()`: 获取任务锁，防止重复处理
- `release_lock()`: 释放任务锁
- `is_locked()`: 检查锁状态

#### 2. 优化任务处理流程
在 `compute_server.py` 中改进了任务处理：
- 处理前检查任务是否已被处理
- 使用分布式锁确保同一任务只被一个worker处理
- 添加异常处理和资源清理

#### 3. 使用方法
如果遇到卡顿问题，请按以下步骤修复：

```bash
# 1. 备份原文件
cp backend_new/compute_server/compute_server.py backend_new/compute_server/compute_server_backup.py

# 2. 使用修复版本
cp backend_new/compute_server/compute_server_fixed.py backend_new/compute_server/compute_server.py

# 3. 重启服务
python run.py both
```

## 目录结构

```
backend_new/
├── controller/                # 控制端
│   ├── controller_app.py     # Flask应用
│   └── route/                # API路由
├── compute_server/           # 计算端
│   ├── compute_server.py     # 计算服务器
│   └── compute_server_fixed.py # 修复版本
├── redis_client/             # Redis客户端
│   └── redis_client.py       # Redis封装（已修复）
├── model_module/             # 模型模块
├── faiss_module/             # FAISS模块
├── sqlite_module/            # 数据库模块
├── run.py                    # 主启动脚本
├── service_manager.py        # 服务管理脚本
├── start.sh                  # Linux启动脚本
└── start.bat                 # Windows启动脚本
```

## 启动方式

### 1. 使用主启动脚本

```bash
# 同时启动控制端和计算端（默认）
python run.py both

# 只启动控制端
python run.py controller --host 0.0.0.0 --port 19198

# 只启动计算端
python run.py compute --workers 4

# 查看帮助
python run.py --help
```

### 2. 使用服务管理脚本

```bash
# 启动所有服务
python service_manager.py start all

# 启动特定服务
python service_manager.py start controller
python service_manager.py start compute
python service_manager.py start redis

# 查看服务状态
python service_manager.py status

# 停止服务
python service_manager.py stop all
```

### 3. 使用便捷脚本

```bash
# Linux/Mac
./start.sh both --host 0.0.0.0 --port 19198

# Windows
start.bat both --host 0.0.0.0 --port 19198
```

## 启动参数

### 通用参数
- `--config`: 配置环境 (development/production)
- `--log-level`: 日志级别 (DEBUG/INFO/WARNING/ERROR)

### 控制端参数
- `--host`: 主机地址 (默认: 0.0.0.0)
- `--port`: 端口号 (默认: 19198)
- `--debug`: 启用调试模式

### 计算端参数
- `--workers`: 工作线程数 (默认: 2)

## 配置说明

### Redis配置
通过环境变量配置Redis连接：

```bash
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_DB=0
export REDIS_PASSWORD=your_password
```

### 计算端配置
```bash
export COMPUTE_WORKERS=4
export FEATURE_TIMEOUT=30
export BATCH_FEATURE_TIMEOUT=60
```

## API接口

### 新增计算端通信接口

1. **单个特征提取**
   ```
   POST /api/compute/feature_extraction
   {
     "image_path": "/path/to/image.jpg"
   }
   ```

2. **批量特征提取**
   ```
   POST /api/compute/batch_feature_extraction
   {
     "image_paths": ["/path/to/image1.jpg", "/path/to/image2.jpg"],
     "timeout": 60
   }
   ```

3. **健康检查**
   ```
   GET /health
   ```

## 部署方案

### 方案一：单机部署
适合开发和小规模使用：
```bash
python run.py both
```

### 方案二：分离部署
适合生产环境和大规模使用：

1. **服务器A (控制端)**:
   ```bash
   python run.py controller --host 0.0.0.0 --port 19198
   ```

2. **服务器B (计算端)**:
   ```bash
   python run.py compute --workers 8
   ```

3. **Redis服务器**:
   ```bash
   redis-server
   ```

### 方案三：多计算端
支持多个计算端实例：

```bash
# 计算端1
python run.py compute --workers 4

# 计算端2  
python run.py compute --workers 4

# 计算端3
python run.py compute --workers 4
```

## 优势

1. **可扩展性**: 可以根据负载独立扩展控制端或计算端
2. **容错性**: 单个组件故障不会影响整个系统
3. **资源优化**: 可以将计算密集型任务分配到专门的GPU服务器
4. **维护便利**: 可以独立更新和维护各个组件
5. **负载均衡**: 支持多个计算端实例，自动负载均衡
6. **任务幂等性**: 通过分布式锁防止任务重复处理

## 监控和调试

### 查看日志
```bash
tail -f futu_backend.log
```

### 检查Redis连接
```bash
redis-cli ping
```

### 健康检查
```bash
curl http://localhost:19198/health
```

### 调试卡顿问题
如果遇到任务卡顿：

1. **检查Redis中的锁**:
   ```bash
   redis-cli KEYS "lock:*"
   ```

2. **清理过期锁**:
   ```bash
   redis-cli FLUSHDB  # 注意：这会清空整个数据库
   ```

3. **检查任务结果**:
   ```bash
   redis-cli KEYS "result:*"
   ```

## 注意事项

1. 确保Redis服务器正常运行
2. 控制端和计算端需要能够访问相同的Redis实例
3. 图片文件路径需要在计算端可访问
4. 建议在生产环境中使用Redis密码认证
5. 可以通过配置文件或环境变量调整各项参数
6. **如果遇到任务重复处理导致的卡顿，请使用修复版本的compute_server.py**

## 故障排除

### 常见问题

#### 1. 索引构建卡顿
**症状**: 索引构建进度到100%后系统无响应
**原因**: 任务重复处理导致资源竞争
**解决**: 使用修复版本的compute_server.py

#### 2. 计算任务重复执行
**症状**: 日志显示同一任务被多个worker处理
**原因**: 缺少任务锁机制
**解决**: 更新redis_client.py和compute_server.py

#### 3. Redis连接异常
**症状**: Redis连接超时或失败
**解决**: 检查Redis服务状态，确认连接配置
