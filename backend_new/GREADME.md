# Backend_new 模块封装文档

## 概述

已将 `backend_new` 目录下的两个模块进行了封装，使其不依赖外部配置文件：

1. **model_module** - 特征提取模块
2. **faiss_module** - Faiss索引模块

## 模块特性

- **独立性**: 不依赖外部 `config` 配置文件
- **可配置**: 提供内部配置类，支持自定义配置
- **接口友好**: 提供便利函数快速创建实例
- **向后兼容**: 保持原有API的兼容性

## 1. Model Module (特征提取模块)

### 核心类

#### ModelConfig
```python
class ModelConfig:
    def __init__(self):
        self.device = "cpu"
        self.pretrain = True
        self.model_type = "resnet50"
        self.input_size = 224
        self.batchsize = 128
        self.normalize_mean = [0.485, 0.456, 0.406]
        self.normalize_std = [0.229, 0.224, 0.225]
```

#### feature_extractor
- 支持传入自定义配置或使用默认配置
- 提供图像特征提取功能

#### feature_extractor 方法说明
- `calculate(image)` - 计算单张图片的特征向量
- `calculate_batch(image_list)` - 批量计算图片特征向量
- `get_dimension()` - 获取模型输出特征维度

### 使用示例

```python
from backend_new.model_module import feature_extractor, ModelConfig, create_feature_extractor

# 方法1: 使用默认配置
extractor = feature_extractor()

# 方法2: 使用自定义配置
config = ModelConfig()
config.device = "cuda"
config.model_type = "resnet101"
extractor = feature_extractor(config)

# 方法3: 使用便利函数
extractor = create_feature_extractor(
    device="cuda",
    model_type="resnet101",
    input_size=224
)

# 创建特征提取器
extractor = feature_extractor()

# 加载图片
image = Image.open("test.jpg")

# 提取单张图片特征
feature = extractor.calculate(image)  # 返回 numpy array，形状为 (特征维度,)

# 批量提取特征
images = [Image.open(f"image_{i}.jpg") for i in range(10)]
features = extractor.calculate_batch(images)  # 返回 numpy array，形状为 (图片数量, 特征维度)

# 获取特征维度
dim = extractor.get_dimension()
print(f"特征维度: {dim}")
```

## 2. Faiss Module (索引模块)

### 核心类

#### FaissConfig
```python
class FaissConfig:
    def __init__(self):
        self.BASE_DIR = "..."  # 自动推导项目根目录
        self.VECTOR_DIM = 2048
        self.INDEX_FOLDER = os.path.join(self.BASE_DIR, "data", "indexes")
        self.SIMILARITY_SIGMA = 10.0
        # ... 其他配置
```

#### FaissIndexer
- 提供索引构建、搜索、更新功能

### 主要函数

- `build_index()` - 构建索引
- `search_index()` - 搜索索引
- `update_index()` - 更新索引
- `repeated_search()` - 重复搜索

### 使用示例

```python
from backend_new.faiss_module import (
    build_index, search_index, 
    FaissConfig, create_faiss_config,
    create_indexer
)

# 方法1: 使用默认配置
build_index(features, ids, "my_index.index")

# 方法2: 使用自定义配置
config = create_faiss_config(
    base_dir="/path/to/project",
    vector_dim=2048,
    similarity_sigma=10.0
)
build_index(features, ids, "my_index.index", config)

# 搜索
results, similarities = search_index(
    query_feature, 
    ["index1.index", "index2.index"], 
    top_k=5,
    config=config
)
```

## 3. 重要变更

### model_module
- `feature_extractor.__init__()` 现在接受可选的 `config` 参数
- 移除了对外部 `config` 模块的依赖
- 添加了便利函数 `create_feature_extractor()`

### faiss_module
- 所有函数现在接受可选的 `config` 参数
- `distance_to_similarity_percent()` 函数增加了 `config` 参数
- `repeated_search()` 函数增加了 `get_features_func` 参数来获取数据集特征
- 移除了对外部 `config` 模块的依赖
- 添加了便利函数 `create_faiss_config()` 和 `create_indexer()`

## 4. 迁移指南

### 从旧版本迁移

**原来的代码：**
```python
from config import config
from model_module.feature_extractor import feature_extractor
from faiss_module.build_index import build_index

extractor = feature_extractor()
build_index(features, ids, "index.index")
```

**新版本代码：**
```python
from backend_new.model_module import feature_extractor
from backend_new.faiss_module import build_index

extractor = feature_extractor()  # 使用默认配置
build_index(features, ids, "index.index")  # 使用默认配置
```

### 自定义配置

**新版本自定义配置：**
```python
from backend_new.model_module import ModelConfig, feature_extractor
from backend_new.faiss_module import FaissConfig, build_index

# 自定义模型配置
model_config = ModelConfig()
model_config.device = "cuda"
model_config.model_type = "resnet101"

# 自定义Faiss配置
faiss_config = FaissConfig()
faiss_config.VECTOR_DIM = 1024
faiss_config.SIMILARITY_SIGMA = 5.0

extractor = feature_extractor(model_config)
build_index(features, ids, "index.index", faiss_config)
```

## 5. 注意事项

1. **repeated_search 函数**: 现在需要传入 `get_features_func` 参数来获取数据集特征，因为移除了对外部模块的依赖。

2. **路径配置**: FaissConfig 会自动推导项目根目录，如果需要自定义路径，请使用 `create_faiss_config()` 函数。

3. **向后兼容**: 所有函数都保持了向后兼容性，如果不传入config参数，会使用默认配置。
