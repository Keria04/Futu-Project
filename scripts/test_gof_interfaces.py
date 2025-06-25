#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GOF接口测试 - 测试重构后的模型和索引接口

这个测试文件演示了如何使用新的GOF设计模式接口：
1. 测试模型接口的各种设计模式
2. 测试索引接口的各种设计模式
3. 展示向后兼容性
"""

import os
import sys
import numpy as np
from PIL import Image

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def create_test_images(num_images=3):
    """创建测试图像"""
    images = []
    for i in range(num_images):
        if i == 0:
            img_array = np.full((224, 224, 3), [255, 0, 0], dtype=np.uint8)  # 红色
        elif i == 1:
            img_array = np.full((224, 224, 3), [0, 255, 0], dtype=np.uint8)  # 绿色
        else:
            img_array = np.full((224, 224, 3), [0, 0, 255], dtype=np.uint8)  # 蓝色
        
        images.append(Image.fromarray(img_array))
    
    return images

def test_model_interface():
    """测试模型接口"""
    print("=" * 60)
    print("测试模型接口 - GOF设计模式")
    print("=" * 60)
    
    # 导入新的接口
    from _model_interface import (
        ModelFacade, ModelManager, ModelConfigBuilder,
        create_feature_extractor, create_model_config
    )
    
    print("1. 测试外观模式 (Facade Pattern)")
    facade = ModelFacade()
    
    # 简化的接口调用
    extractor = facade.create_extractor(
        model_type="resnet18",
        device="cpu",
        input_size=224,
        batch_size=4
    )
    
    print(f"   ✅ 创建特征提取器成功")
    print(f"   模型配置: {extractor.get_config().__dict__}")
    print(f"   特征维度: {extractor.get_feature_dimension()}")
    
    print("\n2. 测试建造者模式 (Builder Pattern)")
    builder = ModelConfigBuilder()
    config = (builder
             .set_model_type("resnet18")
             .set_device("cpu")
             .set_input_size(224)
             .set_batch_size(4)
             .set_pretrain(True)
             .build())
    
    extractor2 = facade.create_extractor_from_config(config)
    print(f"   ✅ 使用建造者模式创建提取器成功")
    
    print("\n3. 测试单例模式 (Singleton Pattern)")
    manager1 = ModelManager()
    manager2 = ModelManager()
    print(f"   管理器实例相同: {manager1 is manager2}")
    
    extractor3 = manager1.get_extractor(model_type="resnet18", device="cpu")
    print(f"   ✅ 单例管理器创建提取器成功")
    
    print("\n4. 测试特征提取功能")
    images = create_test_images(3)
    
    # 单张图像特征提取
    feature = extractor.extract_single(images[0])
    print(f"   单张图像特征形状: {feature.shape}")
    
    # 批量特征提取
    features = extractor.extract_batch(images)
    print(f"   批量特征形状: {features.shape}")
    
    print("\n5. 测试便利函数 (向后兼容)")
    extractor4 = create_feature_extractor(
        model_type="resnet18",
        device="cpu"
    )
    print(f"   ✅ 便利函数创建提取器成功")
    
    return features

def test_index_interface(features):
    """测试索引接口"""
    print("\n" + "=" * 60)
    print("测试索引接口 - GOF设计模式")
    print("=" * 60)
    
    # 导入新的接口
    from _index_interface import (
        IndexFacade, IndexManager, IndexConfigBuilder,
        create_vector_indexer, create_index_config,
        BuildIndexCommand, SearchIndexCommand
    )
    
    print("1. 测试外观模式 (Facade Pattern)")
    facade = IndexFacade()
    
    # 简化的接口调用
    indexer = facade.create_indexer(
        vector_dim=features.shape[1],
        strategy_type="ivf",
        base_dir=project_root,
        similarity_threshold=5.0
    )
    
    print(f"   ✅ 创建索引器成功")
    print(f"   可用策略: {facade.get_available_strategies()}")
    
    print("\n2. 测试建造者模式 (Builder Pattern)")
    builder = IndexConfigBuilder()
    config = (builder
             .set_vector_dim(features.shape[1])
             .set_base_dir(project_root)
             .set_strategy_type("ivf")
             .enable_ivf()
             .build())
    
    indexer2 = facade.create_indexer_from_config(config)
    print(f"   ✅ 使用建造者模式创建索引器成功")
    
    print("\n3. 测试命令模式 (Command Pattern)")
    ids = np.arange(len(features)).astype('int64')
    index_name = "gof_test.index"
    
    # 创建构建命令
    build_cmd = BuildIndexCommand(indexer, features, ids, index_name)
    
    # 执行命令
    index_path = facade.execute_command(build_cmd)
    print(f"   ✅ 执行构建命令成功: {index_path}")
    
    # 创建搜索命令
    query = features[0:1]  # 使用第一个特征作为查询
    search_cmd = SearchIndexCommand(indexer, query, [index_name], top_k=2)
    
    # 执行搜索命令
    results, similarities = facade.execute_command(search_cmd)
    print(f"   搜索结果ID: {results}")
    print(f"   相似度: {[f'{s:.1f}%' for s in similarities]}")
    
    print("\n4. 测试观察者模式 (Observer Pattern)")
    from _index_interface import DefaultIndexObserver
    
    # 添加观察者
    observer = DefaultIndexObserver()
    indexer.add_observer(observer)
    
    # 重新构建索引以触发观察者
    print("   重新构建索引以展示观察者模式:")
    indexer.build_index(features, ids, "gof_observer_test.index")
    
    print("\n5. 测试单例模式 (Singleton Pattern)")
    manager1 = IndexManager()
    manager2 = IndexManager()
    print(f"   管理器实例相同: {manager1 is manager2}")
    
    indexer3 = manager1.get_indexer(
        vector_dim=features.shape[1],
        strategy_type="flat",
        base_dir=project_root
    )
    print(f"   ✅ 单例管理器创建索引器成功")
    
    print("\n6. 测试策略模式 (Strategy Pattern)")
    # 测试不同的索引策略
    strategies = ["flat", "ivf"]
    for strategy in strategies:
        strategy_indexer = facade.create_indexer(
            vector_dim=features.shape[1],
            strategy_type=strategy,
            base_dir=project_root
        )
        print(f"   ✅ 创建 {strategy} 策略索引器成功")
    
    print("\n7. 测试便利函数 (向后兼容)")
    from _index_interface import build_index, search_index
    
    # 使用便利函数构建索引
    index_path = build_index(
        features, ids, "gof_convenience.index",
        vector_dim=features.shape[1],
        base_dir=project_root
    )
    print(f"   便利函数构建索引: {index_path}")
    
    # 使用便利函数搜索
    results, similarities = search_index(
        query, ["gof_convenience.index"],
        vector_dim=features.shape[1],
        top_k=2,
        base_dir=project_root
    )
    print(f"   便利函数搜索结果: {results}, 相似度: {[f'{s:.1f}%' for s in similarities]}")

def test_integration():
    """测试集成场景"""
    print("\n" + "=" * 60)
    print("测试集成场景 - 端到端工作流")
    print("=" * 60)
    
    from _model_interface import get_model_manager
    from _index_interface import get_index_manager
    
    print("1. 获取管理器实例")
    model_manager = get_model_manager()
    index_manager = get_index_manager()
    
    print("2. 创建特征提取器")
    extractor = model_manager.get_extractor(
        model_type="resnet18",
        device="cpu",
        cache_key="integration_test"
    )
    
    print("3. 提取图像特征")
    images = create_test_images(5)
    features = extractor.extract_batch(images)
    print(f"   提取特征形状: {features.shape}")
    
    print("4. 创建索引器")
    indexer = index_manager.get_indexer(
        vector_dim=features.shape[1],
        strategy_type="ivf",
        base_dir=project_root,
        cache_key="integration_test"
    )
    
    print("5. 构建索引")
    ids = np.arange(len(features)).astype('int64')
    index_path = indexer.build_index(features, ids, "integration_test.index")
    print(f"   索引路径: {index_path}")
    
    print("6. 搜索测试")
    query = features[0:1]
    results, similarities = indexer.search_index(query, ["integration_test.index"], top_k=3)
    print(f"   搜索结果: {results}")
    print(f"   相似度: {[f'{s:.1f}%' for s in similarities]}")
    
    print("7. 获取索引信息")
    info = indexer.get_index_info("integration_test.index")
    print(f"   索引信息: 存在={info['exists']}, 大小={info.get('file_size', 0)} bytes")
    
    return True

def main():
    """主函数"""
    print("GOF设计模式接口测试")
    print("测试日期:", "2025年6月25日")
    
    try:
        # 测试模型接口
        features = test_model_interface()
        
        # 测试索引接口
        test_index_interface(features)
        
        # 测试集成场景
        test_integration()
        
        print("\n" + "=" * 60)
        print("✅ 所有GOF接口测试通过!")
        print("=" * 60)
        
        print("\n📝 设计模式总结:")
        print("1. 工厂模式 - 创建不同类型的提取器和索引器")
        print("2. 策略模式 - 支持不同的模型和索引策略")
        print("3. 外观模式 - 简化复杂的模块调用")
        print("4. 建造者模式 - 灵活构建配置对象") 
        print("5. 适配器模式 - 适配现有内部实现")
        print("6. 单例模式 - 全局管理器实例")
        print("7. 命令模式 - 封装索引操作")
        print("8. 观察者模式 - 监听操作状态")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
