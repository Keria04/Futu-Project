# 浮图图像搜索系统 - 重构版

## 🏗️ 架构设计

### 系统架构概览

```
前端 → 控制端(Flask) → Redis任务队列 → 计算端(Worker)
  ↑                    ↓
  └──── Faiss索引 ←─────┘
```

### 设计模式应用

- **单例模式**: Redis客户端、任务管理器、数据库服务
- **工厂模式**: 搜索策略工厂、应用工厂
- **策略模式**: 搜索策略、任务分发策略、任务处理器
- **观察者模式**: 任务监控、索引构建进度通知
- **建造者模式**: 索引构建器
- **代理模式**: 数据库服务代理

## 📁 新目录结构

```
backend/
├── control_service/          # 控制端
│   ├── app.py               # Flask主应用
│   ├── config.py            # 控制端配置
│   ├── api/                 # API路由层
│   │   ├── __init__.py
│   │   ├── search_api.py    # 搜索API
│   │   ├── index_api.py     # 索引API
│   │   ├── dataset_api.py   # 数据集API
│   │   └── image_api.py     # 图片API
│   ├── services/            # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── search_service.py    # 搜索服务
│   │   ├── index_service.py     # 索引服务
│   │   └── database_service.py  # 数据库服务
│   └── faiss_module/        # Faiss模块（不可修改）
├── compute_service/         # 计算端
│   ├── worker.py            # 计算工作节点
│   ├── config.py            # 计算端配置
│   └── model_module/        # Model模块（不可修改）
├── shared/                  # 共享组件
│   ├── __init__.py
│   ├── redis_client.py      # Redis客户端
│   ├── task_manager.py      # 任务管理器
│   └── message_protocol.py  # 消息协议
├── start.py                 # 统一启动脚本
├── database_module/         # 原数据库模块（保留）
├── index_manage_module/     # 原索引管理模块（保留）
└── search_module/           # 原搜索模块（保留）
```

## 🚀 快速启动

### 1. 安装依赖

```bash
pip install -r requirement.txt
```

### 2. 启动Redis服务

Windows:
```bash
# 下载并启动Redis for Windows
redis-server
```

Linux/Mac:
```bash
redis-server
```

### 3. 启动系统

```bash
cd backend
python start.py
```

或者分别启动：

```bash
# 启动控制端
cd backend/control_service
python app.py

# 启动计算端（新终端）
cd backend/compute_service  
python worker.py
```

## 📊 系统特性

### 控制端特性
- **异步任务管理**: 基于Redis的任务队列
- **RESTful API**: 完整的REST API接口
- **索引管理**: 分布式索引构建和管理
- **搜索服务**: 支持单图搜索和重复图搜索
- **进度监控**: 实时任务进度追踪

### 计算端特性
- **可扩展性**: 支持多个计算工作节点
- **任务处理**: 图像特征提取和批处理
- **容错机制**: 任务失败重试和错误处理
- **资源管理**: 模型懒加载和内存管理

### 共享组件特性
- **消息协议**: 标准化的任务和结果格式
- **Redis集成**: 高性能的任务队列和缓存
- **观察者模式**: 灵活的事件通知机制

## 🔧 API接口

### 搜索相关
- `POST /api/search` - 图像搜索
- `POST /api/repeated_search` - 重复图像搜索

### 索引相关
- `POST /api/build_index` - 构建索引
- `GET /api/build_index/progress/<dataset_name>` - 获取构建进度
- `GET /api/build_index/status/<dataset_name>` - 获取构建状态

### 数据集相关
- `GET /api/datasets` - 获取所有数据集
- `GET /api/dataset/<dataset_name>/id` - 获取数据集ID
- `GET /api/dataset/<dataset_name>/images` - 获取数据集图片

### 图片相关
- `GET /api/image/<filename>` - 获取图片文件
- `POST /api/upload` - 上传图片

## 🧪 开发指南

### 添加新的任务类型

1. 在 `shared/message_protocol.py` 中添加新的 `TaskType`
2. 在 `compute_service/worker.py` 中创建对应的 `TaskProcessor`
3. 在控制端服务中添加提交任务的方法

### 扩展搜索策略

1. 在 `control_service/services/search_service.py` 中实现新的 `SearchStrategy`
2. 在 `SearchServiceFactory` 中注册新策略

### 添加新的API接口

1. 在 `control_service/api/` 中创建新的API模块
2. 在对应的服务层中实现业务逻辑
3. 在 `control_service/app.py` 中注册新的蓝图

## 🔄 迁移说明

原有的 `faiss_module` 和 `model_module` 已按要求移动到对应位置：
- `faiss_module` → `control_service/faiss_module`
- `model_module` → `compute_service/model_module`

原有的其他模块（`database_module`、`route`、`search_module` 等）已重构为新的服务层架构。

## 📈 性能优化

- **连接池**: Redis连接池管理
- **批处理**: 支持批量特征提取
- **缓存**: 任务结果缓存
- **并发**: 多线程任务处理
- **索引优化**: Faiss IVF索引优化

## 🛠️ 故障排除

### Redis连接问题
确保Redis服务正在运行：
```bash
redis-cli ping
```

### 计算端无法启动
检查模型依赖是否正确安装：
```bash
python -c "import torch; print(torch.__version__)"
```

### 内存不足
调整批处理大小：
```python
# 在 config/config.py 中
batchsize = 32  # 减小批处理大小
```
