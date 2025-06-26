#!/usr/bin/env python3
"""
性能测试工具演示脚本
用于验证测试工具是否正常工作
"""

import sys
import os

# 添加路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def check_dependencies():
    """检查依赖包"""
    print("🔍 检查依赖包...")
    
    required_packages = [
        'numpy', 'PIL', 'matplotlib', 'seaborn', 
        'tabulate', 'redis', 'celery'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            else:
                __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (缺失)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺失依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirement.txt")
        return False
    else:
        print("✅ 所有依赖包已安装")
        return True

def check_config():
    """检查配置"""
    print("\n🔧 检查配置...")
    
    try:
        from config import config
        print(f"  设备: {config.device}")
        print(f"  批处理大小: {config.batchsize}")
        print(f"  簇大小: {config.N_LIST}")
        print(f"  分布式可用: {config.DISTRIBUTED_AVAILABLE}")
        print("✅ 配置加载正常")
        return True
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

def check_model():
    """检查模型模块"""
    print("\n🤖 检查模型模块...")
    
    try:
        from backend.model_module.feature_extractor import feature_extractor
        # 实例化特征提取器
        extractor = feature_extractor()
        print("✅ 特征提取器加载正常")
        return True
    except Exception as e:
        print(f"❌ 特征提取器加载失败: {e}")
        return False

def run_mini_test():
    """运行迷你测试"""
    print("\n🧪 运行迷你测试...")
    
    try:
        import numpy as np
        from PIL import Image
        from backend.model_module.feature_extractor import feature_extractor
        
        # 生成测试图像
        test_img = Image.new('RGB', (224, 224), color=(255, 0, 0))
        print("  ✅ 测试图像生成成功")
          # 测试特征提取
        extractor = feature_extractor()
        import time
        start_time = time.time()
        features = extractor.calculate_batch([test_img])
        end_time = time.time()
        
        print(f"  ✅ 特征提取成功")
        print(f"  处理时间: {end_time - start_time:.3f}s")
        print(f"  特征维度: {features.shape if hasattr(features, 'shape') else 'Unknown'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 迷你测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_redis():
    """检查Redis连接"""
    print("\n🔗 检查Redis连接...")
    
    try:
        from config import config
        import redis
        
        r = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_BROKER_DB
        )
        r.ping()
        print("✅ Redis连接正常")
        return True
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        print("  提示: 请确保Redis服务已启动")
        return False

def main():
    """主函数"""
    print("🚀 性能测试工具验证")
    print("="*50)
    
    checks = [
        ("依赖包检查", check_dependencies),
        ("配置检查", check_config),
        ("模型模块检查", check_model),
        ("Redis连接检查", check_redis),
        ("迷你测试", run_mini_test),
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\n{name}:")
        if check_func():
            passed += 1
        
    print("\n" + "="*50)
    print(f"📊 验证结果: {passed}/{total} 项通过")
    
    if passed == total:
        print("🎉 所有检查通过！可以开始使用性能测试工具")
        print("\n💡 建议运行:")
        print("  python quick_performance_test.py")
    else:
        print("⚠️  部分检查失败，请解决问题后重试")
        
        if passed >= 3:  # 至少基础功能可用
            print("\n💡 基础功能可用，可以运行本地测试:")
            print("  python quick_performance_test.py")

if __name__ == "__main__":
    main()
