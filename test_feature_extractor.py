#!/usr/bin/env python3
"""
测试特征提取器是否正常工作
"""

import os
import sys
import numpy as np
from PIL import Image

# 添加后端路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend_new')
sys.path.insert(0, backend_path)

from model_module.feature_extractor import feature_extractor, ModelConfig

def test_feature_extractor():
    """测试特征提取器"""
    print("=== 测试特征提取器 ===")
    
    # 寻找测试图片
    test_image = None
    for dataset_path in ["datasets/1", "datasets/2", "datasets/3"]:
        if os.path.exists(dataset_path):
            for root, dirs, files in os.walk(dataset_path):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        test_image = os.path.join(root, file)
                        break
                if test_image:
                    break
            if test_image:
                break
    
    if not test_image:
        print("❌ 未找到测试图片")
        return False
    
    print(f"📸 测试图片: {test_image}")
    
    try:
        # 创建特征提取器
        config = ModelConfig()
        extractor = feature_extractor(config)
        
        print(f"🔧 特征提取器初始化成功")
        print(f"   - 模型类型: {extractor.model_type}")
        print(f"   - 设备: {extractor.device}")
        print(f"   - 预期维度: {extractor.dimension}")
        
        # 加载图片
        image = Image.open(test_image)
        print(f"📷 图片加载成功: {image.size}, 模式: {image.mode}")
        
        # 提取特征
        print("🚀 开始特征提取...")
        features = extractor.calculate(image)
        
        print(f"✅ 特征提取成功")
        print(f"   - 特征类型: {type(features)}")
        print(f"   - 特征形状: {features.shape if hasattr(features, 'shape') else len(features)}")
        print(f"   - 特征维度: {len(features.flatten()) if hasattr(features, 'flatten') else len(features)}")
        print(f"   - 前5个值: {features.flatten()[:5] if hasattr(features, 'flatten') else features[:5]}")
        
        # 检查特征是否有效
        if hasattr(features, 'shape'):
            if features.shape[0] > 0:
                print("✅ 特征向量有效")
                return True
            else:
                print("❌ 特征向量为空")
                return False
        elif len(features) > 0:
            print("✅ 特征向量有效")
            return True
        else:
            print("❌ 特征向量为空")
            return False
        
    except Exception as e:
        print(f"❌ 特征提取失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_feature_extractor()
    print(f"\n{'✅ 测试通过' if success else '❌ 测试失败'}")
