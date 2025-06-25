# GOF设计模式接口文档

## 概述

本文档介绍了使用GOF（Gang of Four）设计模式重构的Backend_new模块接口。新接口提供了更加灵活、可扩展和易用的API，同时保持了与原有实现的兼容性。

## 文件说明

- `_model_interface.py` - 模型特征提取接口，采用GOF设计模式
- `_index_interface.py` - 索引管理接口，采用GOF设计模式  
- `test_gof_interfaces.py` - 接口测试文件，演示各种使用方法

## 设计模式应用

### 1. 工厂模式 (Factory Pattern)
用于创建不同类型的特征提取器和索引器。

```python
# 模型工厂
from _model_interface import ModelStrategyFactory
strategy = ModelStrategyFactory.create_strategy("resnet50")

# 索引工厂  
from _index_interface import IndexStrategyFactory
strategy = IndexStrategyFactory.create_strategy("ivf")
```

### 2. 策略模式 (Strategy Pattern)
支持不同的模型和索引策略，便于扩展。

```python
# 模型策略
from _model_interface import ResNetStrategy, EfficientNetStrategy

# 索引策略
from _index_interface import IVFIndexStrategy, FlatIndexStrategy, HNSWIndexStrategy
```

### 3. 外观模式 (Facade Pattern)
简化复杂的模块调用，提供统一接口。

```python
# 模型外观
from _model_interface import ModelFacade
facade = ModelFacade()
extractor = facade.create_extractor(model_type="resnet50", device="cpu")

# 索引外观
from _index_interface import IndexFacade  
facade = IndexFacade()
indexer = facade.create_indexer(vector_dim=2048, strategy_type="ivf")
```

### 4. 建造者模式 (Builder Pattern)
灵活构建复杂的配置对象。

```python
# 模型配置建造者
from _model_interface import ModelConfigBuilder
config = (ModelConfigBuilder()
         .set_model_type("resnet50")
         .set_device("cuda")
         .set_input_size(224)
         .set_batch_size(64)
         .build())

# 索引配置建造者
from _index_interface import IndexConfigBuilder
config = (IndexConfigBuilder()
         .set_vector_dim(2048)
         .set_strategy_type("ivf")
         .enable_ivf(nlist=100, nprobe=10)
         .build())
```

### 5. 适配器模式 (Adapter Pattern)
适配现有的内部实现，无需修改底层代码。

```python
# 模型适配器
from _model_interface import BaseExtractorAdapter, ModelConfig

# 索引适配器
from _index_interface import BaseIndexerAdapter, IndexConfig
```

### 6. 单例模式 (Singleton Pattern)
全局管理器实例，避免重复创建。

```python
# 模型管理器
from _model_interface import ModelManager
manager = ModelManager()  # 全局单例

# 索引管理器
from _index_interface import IndexManager
manager = IndexManager()  # 全局单例
```

### 7. 命令模式 (Command Pattern)
封装索引操作，支持撤销功能。

```python
from _index_interface import BuildIndexCommand, SearchIndexCommand

# 构建命令
build_cmd = BuildIndexCommand(indexer, features, ids, "test.index")
facade.execute_command(build_cmd)

# 搜索命令
search_cmd = SearchIndexCommand(indexer, query, ["test.index"], top_k=5)
results = facade.execute_command(search_cmd)
```

### 8. 观察者模式 (Observer Pattern)
监听索引操作状态。

```python
from _index_interface import DefaultIndexObserver

observer = DefaultIndexObserver()
indexer.add_observer(observer)
# 操作时会自动通知观察者
```

## 使用示例

### 基础使用 - 外观模式

```python
from _model_interface import ModelFacade
from _index_interface import IndexFacade

# 创建特征提取器
model_facade = ModelFacade()
extractor = model_facade.create_extractor(
    model_type="resnet50",
    device="cpu",
    input_size=224
)

# 提取特征
features = extractor.extract_batch(images)

# 创建索引器
index_facade = IndexFacade()
indexer = index_facade.create_indexer(
    vector_dim=features.shape[1],
    strategy_type="ivf"
)

# 构建索引
indexer.build_index(features, ids, "my_index.index")

# 搜索
results, similarities = indexer.search_index(query, ["my_index.index"])
```

### 高级使用 - 建造者模式

```python
from _model_interface import ModelConfigBuilder, ModelFacade
from _index_interface import IndexConfigBuilder, IndexFacade

# 构建模型配置
model_config = (ModelConfigBuilder()
               .set_model_type("resnet101")
               .set_device("cuda")
               .set_input_size(299)
               .set_batch_size(32)
               .set_pretrain(True)
               .build())

# 构建索引配置
index_config = (IndexConfigBuilder()
               .set_vector_dim(2048)
               .set_strategy_type("ivf")
               .set_base_dir("/my/data/path")
               .enable_ivf(nlist=1000, nprobe=50)
               .build())

# 使用配置创建实例
model_facade = ModelFacade()
extractor = model_facade.create_extractor_from_config(model_config)

index_facade = IndexFacade()
indexer = index_facade.create_indexer_from_config(index_config)
```

### 管理器模式 - 单例管理

```python
from _model_interface import get_model_manager
from _index_interface import get_index_manager

# 获取全局管理器
model_manager = get_model_manager()
index_manager = get_index_manager()

# 缓存式获取（相同参数会返回缓存的实例）
extractor = model_manager.get_extractor(
    model_type="resnet50",
    device="cpu",
    cache_key="main_extractor"
)

indexer = index_manager.get_indexer(
    vector_dim=2048,
    strategy_type="ivf",
    cache_key="main_indexer"
)
```

### 便利函数 - 向后兼容

```python
# 简化的便利函数（向后兼容）
from _model_interface import create_feature_extractor
from _index_interface import build_index, search_index

# 创建特征提取器
extractor = create_feature_extractor(model_type="resnet50", device="cpu")

# 构建和搜索索引
build_index(features, ids, "test.index", vector_dim=2048)
results, similarities = search_index(query, ["test.index"], vector_dim=2048)
```

## 扩展新策略

### 添加新的模型策略

```python
from _model_interface import ModelStrategy, ModelStrategyFactory

class MyCustomModelStrategy(ModelStrategy):
    def create_extractor(self, config):
        # 实现自定义模型创建逻辑
        pass
    
    def get_default_config(self):
        return {"model_type": "my_custom_model"}

# 注册新策略
ModelStrategyFactory.register_strategy("custom", MyCustomModelStrategy)
```

### 添加新的索引策略

```python
from _index_interface import IndexStrategy, IndexStrategyFactory

class MyCustomIndexStrategy(IndexStrategy):
    def create_indexer(self, config):
        # 实现自定义索引器创建逻辑
        pass
    
    def get_default_config(self):
        return {"strategy_type": "custom"}
    
    def get_strategy_name(self):
        return "CustomIndex"

# 注册新策略
IndexStrategyFactory.register_strategy("custom", MyCustomIndexStrategy)
```

## 配置参数

### 模型配置参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| device | str | "cpu" | 设备类型 ("cpu" 或 "cuda") |
| model_type | str | "resnet50" | 模型类型 |
| input_size | int | 224 | 输入图像尺寸 |
| batch_size | int | 128 | 批处理大小 |
| pretrain | bool | True | 是否使用预训练模型 |
| normalize_mean | List[float] | [0.485, 0.456, 0.406] | 归一化均值 |
| normalize_std | List[float] | [0.229, 0.224, 0.225] | 归一化标准差 |

### 索引配置参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| vector_dim | int | 2048 | 特征向量维度 |
| strategy_type | str | "ivf" | 索引策略类型 |
| base_dir | str | 当前目录 | 项目根目录 |
| similarity_threshold | float | 10.0 | 相似度阈值 |
| use_ivf | bool | True | 是否使用IVF |
| nlist | int | None | IVF聚类数量（自动计算） |
| nprobe | int | None | IVF探索数量（自动计算） |

## 测试

运行测试文件来验证接口功能：

```bash
python test_gof_interfaces.py
```

测试包括：
- 各种设计模式的功能测试
- 特征提取和索引搜索功能测试
- 向后兼容性测试
- 集成场景测试

## 优势

1. **可扩展性** - 通过策略模式和工厂模式，容易添加新的模型和索引类型
2. **灵活性** - 建造者模式提供灵活的配置构建方式
3. **易用性** - 外观模式简化复杂操作，单例管理器提供全局访问
4. **可维护性** - 清晰的接口分离和适配器模式保持代码整洁
5. **兼容性** - 保持与原有API的向后兼容
6. **可监控性** - 观察者模式提供操作状态监听
7. **可撤销性** - 命令模式支持操作撤销

## 注意事项

1. 新接口文件命名为 `_model_interface.py` 和 `_index_interface.py`，前缀下划线表示这是重构的接口
2. 内部实现未修改，只是在接口层使用适配器模式进行封装
3. 可以通过便利函数保持与原有代码的兼容性
4. 建议逐步迁移到新接口，充分利用设计模式的优势
