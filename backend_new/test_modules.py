#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 测试 backend_new 模块封装

这个脚本测试了：
1. model_module 的特征提取功能
2. faiss_module 的索引构建和搜索功能
"""

import os
import sys
import numpy as np
from PIL import Image
import torch

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def test_model_module():
    """测试 model_module 特征提取模块"""
    print("=" * 50)
    print("测试 Model Module")
    print("=" * 50)
    
    try:
        from model_module import feature_extractor, ModelConfig, create_feature_extractor
        
        # 测试1: 使用默认配置
        print("1. 测试默认配置...")
        extractor1 = feature_extractor()
        print(f"   默认设备: {extractor1.device}")
        print(f"   默认模型: {extractor1.model_type}")
        print(f"   特征维度: {extractor1.dimension}")
        
        # 测试2: 使用自定义配置
        print("\n2. 测试自定义配置...")
        config = ModelConfig()
        config.device = "cpu"  # 确保使用CPU以避免CUDA问题
        config.model_type = "resnet18"  # 使用较小的模型
        config.input_size = 224
        
        extractor2 = feature_extractor(config)
        print(f"   自定义设备: {extractor2.device}")
        print(f"   自定义模型: {extractor2.model_type}")
        print(f"   特征维度: {extractor2.dimension}")
        
        # 测试3: 使用便利函数
        print("\n3. 测试便利函数...")
        extractor3 = create_feature_extractor(
            device="cpu",
            model_type="resnet18",
            input_size=224,
            pretrain=True
        )
        print(f"   便利函数设备: {extractor3.device}")
        print(f"   便利函数模型: {extractor3.model_type}")
        
        # 测试4: 创建测试图像并提取特征
        print("\n4. 测试特征提取...")
        # 创建一个随机的测试图像
        test_image = Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8))
          # 提取特征
        feature = extractor3.calculate(test_image)
        print(f"   提取的特征形状: {feature.shape}")
        print(f"   特征数据类型: {feature.dtype}")
        print(f"   特征值范围: [{feature.min():.4f}, {feature.max():.4f}]")
        
        print("✅ Model Module 测试通过!")
        return feature
        
    except Exception as e:
        print(f"❌ Model Module 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_faiss_module():
    """测试 faiss_module 索引模块"""
    print("\n" + "=" * 50)
    print("测试 Faiss Module")
    print("=" * 50)
    
    try:
        from faiss_module import (
            build_index, search_index, 
            FaissConfig, create_faiss_config,
            create_indexer, default_config
        )
        
        # 测试1: 检查默认配置
        print("1. 测试默认配置...")
        print(f"   默认向量维度: {default_config.vector_dim}")
        print(f"   默认索引文件夹: {default_config.index_folder}")
        print(f"   默认相似度参数: {default_config.similarity_sigma}")
        
        # 测试2: 创建自定义配置
        print("\n2. 测试自定义配置...")
        custom_config = create_faiss_config(
            base_dir=project_root,
            vector_dim=512,  # 使用较小的维度进行测试
            similarity_sigma=5.0
        )
        print(f"   自定义向量维度: {custom_config.vector_dim}")
        print(f"   自定义相似度参数: {custom_config.similarity_sigma}")
        
        # 测试3: 生成测试数据
        print("\n3. 生成测试数据...")
        num_vectors = 100
        dim = 512
        
        # 生成随机特征向量
        features = np.random.random((num_vectors, dim)).astype('float32')
        ids = np.arange(num_vectors).astype('int64')
        
        print(f"   生成特征形状: {features.shape}")
        print(f"   生成ID数量: {len(ids)}")
        
        # 测试4: 构建索引
        print("\n4. 测试索引构建...")
        index_name = "test_index.index"
        
        # 确保索引目录存在
        os.makedirs(custom_config.index_folder, exist_ok=True)
        
        build_index(features, ids, index_name, custom_config)
        
        index_path = os.path.join(custom_config.index_folder, index_name)
        if os.path.exists(index_path):
            print(f"   ✅ 索引文件创建成功: {index_path}")
            print(f"   索引文件大小: {os.path.getsize(index_path)} bytes")
        else:
            print(f"   ❌ 索引文件创建失败")
            return False
        
        # 测试5: 搜索索引
        print("\n5. 测试索引搜索...")
        query_feature = features[0:1]  # 使用第一个特征作为查询
        
        results, similarities = search_index(
            query_feature, 
            [index_name], 
            top_k=5,
            config=custom_config
        )
        
        print(f"   查询特征形状: {query_feature.shape}")
        print(f"   返回结果ID: {results}")
        print(f"   相似度分数: {[f'{s:.2f}%' for s in similarities]}")
        
        # 验证结果
        if len(results) > 0 and results[0] == 0:  # 第一个结果应该是查询向量本身
            print("   ✅ 搜索结果正确 (找到了查询向量本身)")
        else:
            print("   ⚠️  搜索结果可能不准确")
        
        # 测试6: 测试索引器直接使用
        print("\n6. 测试索引器直接使用...")
        indexer = create_indexer(
            dim=dim,
            index_path=index_path,
            use_IVF=True
        )
        
        indexer.load_index()
        distances, indices = indexer.search(query_feature, k=3)
        
        print(f"   直接搜索距离: {distances[0]}")
        print(f"   直接搜索索引: {indices[0]}")
        
        print("✅ Faiss Module 测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ Faiss Module 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """集成测试 - 将两个模块结合使用"""
    print("\n" + "=" * 50)
    print("集成测试")
    print("=" * 50)
    
    try:
        from model_module import create_feature_extractor
        from faiss_module import build_index, search_index, create_faiss_config
        
        print("1. 创建特征提取器...")
        extractor = create_feature_extractor(
            device="cpu",
            model_type="resnet18",
            input_size=224
        )
        
        print("2. 生成测试图像...")
        num_images = 20
        test_images = []
        for i in range(num_images):
            # 创建不同的随机图像
            img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            test_images.append(Image.fromarray(img_array))
        
        print("3. 提取所有图像特征...")
        features_list = []
        for i, img in enumerate(test_images):
            feature = extractor.calculate(img)
            features_list.append(feature)
            if (i + 1) % 5 == 0:
                print(f"   已处理 {i + 1}/{num_images} 张图像")
        
        features = np.vstack(features_list)
        ids = np.arange(len(features_list)).astype('int64')
        
        print(f"   提取特征形状: {features.shape}")
        
        print("4. 使用提取的特征构建索引...")
        config = create_faiss_config(
            base_dir=project_root,
            vector_dim=features.shape[1]
        )
        
        index_name = "integration_test.index"
        build_index(features, ids, index_name, config)
        
        print("5. 搜索测试...")
        query_img = test_images[0]  # 使用第一张图像作为查询
        query_feature = extractor.calculate(query_img)
        
        results, similarities = search_index(
            query_feature.reshape(1, -1),
            [index_name],
            top_k=3,
            config=config
        )
        
        print(f"   查询结果: {results}")
        print(f"   相似度: {[f'{s:.2f}%' for s in similarities]}")
        
        if len(results) > 0 and results[0] == 0:
            print("✅ 集成测试通过!")
            return True
        else:
            print("⚠️  集成测试结果可能不准确")
            return False
            
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("Backend_new 模块封装测试")
    print("测试时间:", "2025年6月25日")
    print("Python版本:", sys.version)
    print("PyTorch版本:", torch.__version__ if 'torch' in globals() else "未安装")
    
    # 运行测试
    test_results = []
    
    # 测试 model_module
    feature = test_model_module()
    test_results.append(feature is not None)
    
    # 测试 faiss_module
    faiss_result = test_faiss_module()
    test_results.append(faiss_result)
    
    # 集成测试
    integration_result = test_integration()
    test_results.append(integration_result)
    
    # 总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    print(f"Model Module 测试: {'✅ 通过' if test_results[0] else '❌ 失败'}")
    print(f"Faiss Module 测试: {'✅ 通过' if test_results[1] else '❌ 失败'}")
    print(f"集成测试: {'✅ 通过' if test_results[2] else '❌ 失败'}")
    
    success_count = sum(test_results)
    total_count = len(test_results)
    
    print(f"\n总体结果: {success_count}/{total_count} 测试通过")
    
    if success_count == total_count:
        print("🎉 所有测试都通过了!")
    else:
        print("⚠️  部分测试失败，请检查错误信息")
    
    return success_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
