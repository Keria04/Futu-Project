#!/usr/bin/env python3
"""
性能测试使用示例
展示如何使用测试工具进行不同类型的性能测试
"""

import sys
import os
import time

# 添加路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def example_1_quick_test():
    """示例1: 快速性能测试"""
    print("📋 示例1: 快速性能测试")
    print("-" * 40)
    print("适用场景: 日常性能检查，验证配置更改")
    print()
    
    try:
        from quick_performance_test import test_current_config
        
        print("正在运行快速测试...")
        result = test_current_config()
        
        print("\n📊 测试结果:")
        if 'single_image' in result:
            single = result['single_image']
            print(f"单图像处理: {single['avg_time']:.3f}s, 吞吐量: {single['throughput']:.2f} 图像/秒")
        
        if 'batch_processing' in result:
            batch = result['batch_processing']
            print(f"批处理效率: {batch['efficiency']:.2f}x")
            
        return True
        
    except Exception as e:
        print(f"❌ 快速测试失败: {e}")
        return False

def example_2_compare_configs():
    """示例2: 比较不同配置"""
    print("\n📋 示例2: 比较不同配置")
    print("-" * 40)
    print("适用场景: 评估配置更改的影响")
    print()
    
    try:
        from config import config
        from backend.model_module.feature_extractor import feature_extractor
        from PIL import Image
          # 生成测试图像
        test_images = [Image.new('RGB', (224, 224), color=(255, 0, 0)) for _ in range(8)]
        
        # 实例化特征提取器
        extractor = feature_extractor()
        
        # 测试不同批处理大小
        batch_sizes = [1, 4, 8]
        original_batchsize = config.batchsize
        
        print("测试不同批处理大小:")
        results = {}
        
        for batch_size in batch_sizes:
            config.batchsize = batch_size
            
            start_time = time.time()
            features = extractor.calculate_batch(test_images[:batch_size])
            end_time = time.time()
            
            duration = end_time - start_time
            throughput = batch_size / duration
            
            results[batch_size] = {
                'time': duration,
                'throughput': throughput
            }
            
            print(f"  批处理大小 {batch_size}: {duration:.3f}s, {throughput:.2f} 图像/秒")
        
        # 恢复配置
        config.batchsize = original_batchsize
        
        # 找出最佳配置
        best_batch = max(results.items(), key=lambda x: x[1]['throughput'])
        print(f"\n💡 最佳批处理大小: {best_batch[0]} (吞吐量: {best_batch[1]['throughput']:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置比较失败: {e}")
        return False

def example_3_distributed_test():
    """示例3: 分布式计算测试"""
    print("\n📋 示例3: 分布式计算测试")
    print("-" * 40)
    print("适用场景: 评估分布式计算性能")
    print()
    
    try:
        from quick_performance_test import test_distributed_availability, compare_local_vs_distributed
        
        # 检查分布式可用性
        if test_distributed_availability():
            print("✅ 分布式计算可用，开始性能对比...")
            result = compare_local_vs_distributed()
            
            if 'local' in result and 'distributed' in result:
                local_time = result['local']['avg_time']
                
                if 'error' not in result['distributed']:
                    dist_time = result['distributed']['avg_time']
                    speedup = result['distributed']['speedup']
                    
                    print(f"本地计算: {local_time:.3f}s")
                    print(f"分布式计算: {dist_time:.3f}s")
                    print(f"加速比: {speedup:.2f}x")
                    
                    if speedup > 1.2:
                        print("💡 建议: 使用分布式计算")
                    elif speedup < 0.8:
                        print("💡 建议: 使用本地计算")
                    else:
                        print("💡 建议: 性能相近，可根据需要选择")
                else:
                    print(f"❌ 分布式测试失败: {result['distributed']['error']}")
        else:
            print("❌ 分布式计算不可用")
            print("💡 提示: 启动Worker后重试")
        
        return True
        
    except Exception as e:
        print(f"❌ 分布式测试失败: {e}")
        return False

def example_4_auto_optimization():
    """示例4: 自动优化（简化版）"""
    print("\n📋 示例4: 自动优化")
    print("-" * 40)
    print("适用场景: 寻找最佳配置参数")
    print()
    
    try:
        from config import config
        from backend.model_module.feature_extractor import feature_extractor
        from PIL import Image
        import statistics
          # 生成测试图像
        test_images = [Image.new('RGB', (224, 224), color=(i*20, 100, 150)) for i in range(10)]
        
        # 实例化特征提取器
        extractor = feature_extractor()
        
        # 测试参数组合
        test_configs = [
            {'batchsize': 4, 'name': '小批处理'},
            {'batchsize': 8, 'name': '中等批处理'},
            {'batchsize': 16, 'name': '大批处理'},
        ]
        
        original_batchsize = config.batchsize
        results = []
        
        print("测试不同配置:")
        
        for test_config in test_configs:
            config.batchsize = test_config['batchsize']
            
            # 多次测试取平均值
            times = []
            for _ in range(3):
                start_time = time.time()
                features = extractor.calculate_batch(test_images[:test_config['batchsize']])
                end_time = time.time()
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            throughput = test_config['batchsize'] / avg_time
            
            results.append({
                'config': test_config,
                'avg_time': avg_time,
                'throughput': throughput
            })
            
            print(f"  {test_config['name']}: {avg_time:.3f}s, {throughput:.2f} 图像/秒")
        
        # 恢复配置
        config.batchsize = original_batchsize
        
        # 找出最佳配置
        best_result = max(results, key=lambda x: x['throughput'])
        print(f"\n🏆 最佳配置: {best_result['config']['name']}")
        print(f"最佳吞吐量: {best_result['throughput']:.2f} 图像/秒")
        
        return True
        
    except Exception as e:
        print(f"❌ 自动优化失败: {e}")
        return False

def main():
    """主函数"""
    print("🎯 性能测试使用示例")
    print("="*50)
    print("本示例展示如何使用测试工具进行不同类型的性能测试")
    print()
    
    examples = [
        ("快速性能测试", example_1_quick_test),
        ("配置参数比较", example_2_compare_configs),
        ("分布式计算测试", example_3_distributed_test),
        ("自动配置优化", example_4_auto_optimization),
    ]
    
    for i, (name, example_func) in enumerate(examples, 1):
        print(f"\n{'='*50}")
        print(f"示例 {i}: {name}")
        print('='*50)
        
        try:
            success = example_func()
            if success:
                print(f"✅ 示例 {i} 完成")
            else:
                print(f"❌ 示例 {i} 失败")
        except KeyboardInterrupt:
            print(f"\n⏹️  示例 {i} 被用户中断")
            break
        except Exception as e:
            print(f"❌ 示例 {i} 出现异常: {e}")
        
        # 暂停一下
        if i < len(examples):
            input("\n按回车键继续下一个示例...")
    
    print("\n" + "="*50)
    print("🎉 所有示例演示完成!")
    print("\n💡 更多功能:")
    print("  python quick_performance_test.py          # 快速测试")
    print("  python performance_testbench.py --mode full  # 完整测试")
    print("  python config_optimizer.py --mode full       # 配置优化")
    print("  scripts\\performance_test.bat               # 图形界面")

if __name__ == "__main__":
    main()
