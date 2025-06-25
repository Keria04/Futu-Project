# 浮图项目后端 API 服务

基于 Flask 的图片相似度搜索后端服务，支持索引构建、图片搜索、重复检测等功能。

## 项目结构

```
backend_new/
├── app.py                 # Flask 应用主文件
├── run.py                 # 启动脚本
├── config.py              # 配置文件
├── requirements.txt       # 依赖包列表
├── test_api.py           # API 测试脚本
├── route/                # 路由模块
│   ├── __init__.py
│   ├── index_routes.py   # 索引构建相关路由
│   ├── search_routes.py  # 图片搜索相关路由
│   ├── dataset_routes.py # 数据集管理相关路由
│   ├── duplicate_routes.py # 重复检测相关路由
│   └── static_routes.py  # 静态资源相关路由
└── data/                 # 数据存储目录
    ├── indexes/          # 索引文件存储
    ├── progress/         # 进度文件存储
    └── main.db          # SQLite 数据库
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动服务

### 方法1: 使用启动脚本（推荐）
```bash
python run.py
```

### 方法2: 直接运行
```bash
python app.py
```

### 方法3: 使用环境变量
```bash
# Windows
set FLASK_CONFIG=development
set FLASK_HOST=0.0.0.0
set FLASK_PORT=19198
set FLASK_DEBUG=True
python run.py

# Linux/Mac
export FLASK_CONFIG=development
export FLASK_HOST=0.0.0.0
export FLASK_PORT=19198
export FLASK_DEBUG=True
python run.py
```

## API 接口

### 基础信息
- **基础URL**: `http://localhost:19198/api`
- **端口**: 19198
- **支持CORS**: 允许来自 `http://localhost:19197` 的请求

### 1. 索引构建
- **POST** `/api/build_index` - 构建搜索索引
- **GET** `/api/progress/{progress_path}` - 获取构建进度

### 2. 图片搜索
- **POST** `/api/search` - 图片相似度搜索

### 3. 数据集管理
- **GET** `/api/datasets` - 获取所有数据集列表
- **POST** `/api/get_dataset_id` - 根据名称获取数据集ID
- **POST** `/api/upload_images` - 上传图片到数据集

### 4. 重复检测
- **POST** `/api/repeated_search` - 查找重复图片

### 5. 静态资源
- **GET** `/show_image/{image_path}` - 访问图片资源

## 测试 API

运行测试脚本来验证 API 接口：

```bash
python test_api.py
```

测试脚本会测试以下功能：
- 获取数据集列表
- 构建索引
- 获取数据集ID
- 重复检测
- 图片搜索（需要测试图片）
- 静态图片访问

## 配置说明

### 环境配置
- `development`: 开发环境（默认）
- `production`: 生产环境
- `testing`: 测试环境

### 主要配置项
- `MAX_CONTENT_LENGTH`: 最大文件上传大小（100MB）
- `ALLOWED_EXTENSIONS`: 支持的图片格式
- `DATABASE_PATH`: SQLite 数据库路径
- `CORS_ORIGINS`: 允许的跨域来源
- `DATASETS_FOLDER`: 数据集存储路径

## 开发说明

### 当前状态
- ✅ Flask 应用框架搭建完成
- ✅ 路由结构设计完成
- ✅ API 接口定义完成
- ✅ 配置管理系统完成
- ⏸️ 业务逻辑实现（待开发）
- ⏸️ 数据库集成（待开发）
- ⏸️ 图片处理模块集成（待开发）

### 待实现的功能

1. **索引构建模块**
   - 集成 FAISS 索引构建
   - 图片特征提取
   - 进度跟踪和持久化

2. **图片搜索模块**
   - 图片预处理和裁剪
   - 特征提取和相似度计算
   - 搜索结果排序和过滤

3. **数据集管理模块**
   - 数据库操作封装
   - 文件系统管理
   - 图片元数据处理

4. **重复检测模块**
   - 相似度阈值处理
   - 重复分组算法
   - 去重操作实现

### 集成现有模块

现有的模块可以按以下方式集成：

```python
# 在相应的路由文件中导入现有模块
from faiss_module.indexer import Indexer
from model_module.feature_extractor import FeatureExtractor
from sqlite_module.database_manager import DatabaseManager

# 在路由处理函数中调用相应的服务
def build_index():
    indexer = Indexer()
    result = indexer.build(dataset_names, distributed)
    return jsonify(result)
```

## 错误处理

所有 API 接口都实现了统一的错误处理格式：

```json
{
  "error": "错误类型",
  "message": "详细错误信息"
}
```

## 日志记录

建议在生产环境中配置适当的日志记录：

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 性能优化建议

1. **缓存机制**: 对频繁查询的数据集信息进行缓存
2. **异步处理**: 对耗时操作（索引构建）使用异步任务队列
3. **连接池**: 配置数据库连接池以提高并发性能
4. **静态文件**: 使用 Nginx 等反向代理服务静态文件

## 部署建议

### 开发环境
```bash
python run.py
```

### 生产环境
```bash
# 使用 Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:19198 "app:create_app('production')"

# 或使用 uWSGI
pip install uwsgi
uwsgi --http 0.0.0.0:19198 --module app:application --callable create_app
```

## 许可证

此项目为浮图项目的一部分，请遵循项目整体的许可证条款。
