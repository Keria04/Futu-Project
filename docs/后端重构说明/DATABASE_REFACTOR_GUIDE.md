# 数据库重构使用指南

## 概述

本次重构采用了设计模式中的接口模式和仓储模式，将数据库操作重新组织为更加清晰、可维护的结构。

## 架构设计

### 1. 接口层 (`_database_interface.py`)
- `DatabaseInterface`: 数据库基础操作接口
- `DatasetRepositoryInterface`: 数据集仓储接口  
- `ImageRepositoryInterface`: 图片仓储接口
- `DatabaseManagerInterface`: 数据库管理器接口

### 2. 实现层 (`sqlite_module/`)
- `SQLiteDatabase`: SQLite数据库实现
- `SQLiteDatasetRepository`: 数据集仓储实现
- `SQLiteImageRepository`: 图片仓储实现  
- `SQLiteDatabaseManager`: 数据库管理器实现

### 3. 业务层
- `query.py`: 查询操作封装
- `modify.py`: 增删改操作封装
- `schema.py`: 表结构定义

### 4. 兼容层
- `legacy_adapter.py`: 向后兼容适配器

## 使用方式

### 方式1: 使用新的仓储模式（推荐）

```python
from sqlite_module.database_manager import get_database_manager

# 获取数据库管理器
db_manager = get_database_manager()

# 操作数据集
dataset_repo = db_manager.get_dataset_repository()
dataset_id = dataset_repo.create_dataset("新数据集", "描述")
datasets = dataset_repo.get_all_datasets()

# 操作图片
image_repo = db_manager.get_image_repository()
image_id = image_repo.add_image(dataset_id, "test.jpg", "/path/test.jpg")
images = image_repo.get_images_by_dataset(dataset_id)
```

### 方式2: 使用封装函数（简化版）

```python
from sqlite_module import (
    create_dataset, 
    get_datasets,
    add_image_to_dataset,
    get_images_by_dataset_id
)

# 创建数据集
dataset_id = create_dataset("新数据集", "描述")

# 获取所有数据集
datasets = get_datasets()

# 添加图片
image_id = add_image_to_dataset(dataset_id, "test.jpg", "/path/test.jpg")

# 获取图片
images = get_images_by_dataset_id(dataset_id)
```

### 方式3: 兼容旧代码（无需修改现有代码）

```python
from sqlite_module.legacy_adapter import (
    query_one,
    query_multi,
    get_dataset_id,
    get_datasets,
    get_image_by_id,
    get_images_by_dataset
)

# 现有代码无需任何修改，直接使用
datasets = get_datasets()
dataset_id = get_dataset_id("数据集名称")
images = get_images_by_dataset("数据集名称")
```

## 主要改进

### 1. 设计模式应用
- **接口模式**: 定义清晰的抽象接口，便于扩展和测试
- **仓储模式**: 封装数据访问逻辑，提供面向对象的数据操作
- **单例模式**: 数据库管理器使用单例，确保资源合理使用

### 2. 类型安全
- 使用 Python 类型提示，提高代码可读性和IDE支持
- 明确的参数和返回值类型定义

### 3. 错误处理
- 统一的异常处理机制
- 更好的错误信息提示

### 4. 数据模型优化
- 标准化的数据字典格式
- 更完整的字段定义（如 created_at, file_size 等）

### 5. 向后兼容
- 提供完整的兼容层，现有代码无需修改
- 渐进式迁移，可以逐步升级到新接口

## 数据库表结构

### datasets 表
```sql
CREATE TABLE datasets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_rebuild DATETIME,
    image_count INTEGER NOT NULL DEFAULT 0,
    size_bytes INTEGER NOT NULL DEFAULT 0
);
```

### images 表
```sql
CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER DEFAULT 0,
    checksum TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata_json TEXT,
    feature_vector BLOB,
    FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE
);
```

## 测试和验证

运行测试文件验证重构结果：

```bash
cd backend_new
python test_database_refactor.py
```

## 迁移建议

1. **立即可用**: 使用 `legacy_adapter` 确保现有代码正常工作
2. **逐步迁移**: 新功能使用新的仓储接口
3. **最终目标**: 全面迁移到新的架构模式

## 扩展性

新架构支持：
- 轻松添加新的数据库类型（如 PostgreSQL, MySQL）
- 添加新的仓储接口（如 用户管理、日志记录）
- 支持缓存层、连接池等高级功能
- 便于单元测试和集成测试
