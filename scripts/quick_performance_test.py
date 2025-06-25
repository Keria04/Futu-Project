#!/usr/bin/env python3
"""
快速性能测试脚本
用于快速评估当前配置的性能表现
"""

import sys
import os
import time
import json
import statistics
import numpy as np
from datetime import datetime
from PIL import Image
from io import BytesIO

# 添加路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from config import config
from backend.model_module.feature_extractor import feature_extractor

def generate_test_image(size=(224, 224), color=None):
    """生成单个测试图像"""
    if color is None:
        color = (
            int(np.random.randint(0, 256)),
            int(np.random.randint(0, 256)),
            int(np.random.randint(0, 256))
        )
    return Image.new('RGB', size, color=color)

def test_current_config():
    """测试当前配置的性能"""
    print("🔧 当前配置信息:")
    print(f"  设备: {config.device}")
    print(f"  批处理大小: {config.batchsize}")
    print(f"  簇大小 (N_LIST): {config.N_LIST}")
    print(f"  分布式可用: {config.DISTRIBUTED_AVAILABLE}")
    print()
    
    # 生成测试图像
    print("📸 生成测试图像...")
    test_images = []
    for i in range(10):
        img = generate_test_image()
        test_images.append(img)
    print(f"✅ 已生成 {len(test_images)} 张测试图像")
      # 测试特征提取性能
    print("\n⚡ 测试特征提取性能...")
    
    # 实例化特征提取器
    from backend.model_module.feature_extractor import feature_extractor
    extractor = feature_extractor()
    
    # 单图像测试
    print("  单图像处理:")
    single_times = []
    for _ in range(5):
        start_time = time.time()
        features = extractor.calculate(test_images[0])
        end_time = time.time()
        single_times.append(end_time - start_time)
    
    avg_single = statistics.mean(single_times)
    print(f"    平均时间: {avg_single:.3f}s")
    print(f"    吞吐量: {1.0/avg_single:.2f} 图像/秒")
      # 批处理测试
    batch_size = min(config.batchsize, len(test_images))
    print(f"  批处理 ({batch_size} 图像):")
    batch_times = []
    for _ in range(3):
        start_time = time.time()
        features = extractor.calculate_batch(test_images[:batch_size])
        end_time = time.time()
        batch_times.append(end_time - start_time)
    
    avg_batch = statistics.mean(batch_times)
    batch_throughput = batch_size / avg_batch
    print(f"    平均时间: {avg_batch:.3f}s")
    print(f"    吞吐量: {batch_throughput:.2f} 图像/秒")
    print(f"    单图像平均时间: {avg_batch/batch_size:.3f}s")
    
    # 效率分析
    efficiency = (avg_single * batch_size) / avg_batch if avg_batch > 0 else 0
    print(f"    批处理效率: {efficiency:.2f}x")
    
    return {
        'single_image': {
            'avg_time': avg_single,
            'throughput': 1.0/avg_single if avg_single > 0 else 0,
            'times': single_times
        },
        'batch_processing': {
            'batch_size': batch_size,
            'avg_time': avg_batch,
            'throughput': batch_throughput,
            'per_image_time': avg_batch/batch_size if batch_size > 0 else 0,
            'efficiency': efficiency,
            'times': batch_times
        }
    }

def test_distributed_availability():
    """测试分布式计算可用性"""
    print("\n🌐 测试分布式计算可用性...")
    
    if not config.DISTRIBUTED_AVAILABLE:
        print("❌ 分布式计算已禁用")
        return False
    
    try:
        # 检查Redis连接
        import redis
        r = redis.Redis(
            host=config.REDIS_HOST, 
            port=config.REDIS_PORT, 
            db=config.REDIS_BROKER_DB
        )
        r.ping()
        print("✅ Redis连接正常")
        
        # 检查Celery Worker
        from backend.worker import celery_app
        i = celery_app.control.inspect()
        active_workers = i.active()
        
        if active_workers:
            print(f"✅ 发现 {len(active_workers)} 个活跃Worker")
            return True
        else:
            print("❌ 没有发现活跃的Worker")
            return False
            
    except Exception as e:
        print(f"❌ 分布式计算不可用: {e}")
        return False

def compare_local_vs_distributed():
    """比较本地和分布式计算性能"""
    print("\n⚖️  比较本地 vs 分布式计算...")
    
    # 生成测试图像
    test_img = generate_test_image()
    img_buffer = BytesIO()
    test_img.save(img_buffer, format='JPEG')
    img_data = img_buffer.getvalue()
    import base64
    img_data_b64 = base64.b64encode(img_data).decode('utf-8')
    
    results = {}
      # 本地计算测试
    print("  🏠 本地计算:")
    original_distributed = config.DISTRIBUTED_AVAILABLE
    config.DISTRIBUTED_AVAILABLE = False
    
    # 实例化特征提取器
    from backend.model_module.feature_extractor import feature_extractor
    extractor = feature_extractor()
    
    local_times = []
    for _ in range(3):
        start_time = time.time()
        features = extractor.calculate(test_img)
        end_time = time.time()
        local_times.append(end_time - start_time)
    
    local_avg = statistics.mean(local_times)
    print(f"    平均时间: {local_avg:.3f}s")
    results['local'] = {'avg_time': local_avg, 'times': local_times}
    
    # 分布式计算测试
    config.DISTRIBUTED_AVAILABLE = original_distributed
    
    if test_distributed_availability():
        print("  ☁️  分布式计算:")
        try:
            from backend.worker import generate_embeddings_task
            
            dist_times = []
            for _ in range(3):
                start_time = time.time()
                future = generate_embeddings_task.delay(img_data_b64)
                result = future.get(timeout=30)
                end_time = time.time()
                dist_times.append(end_time - start_time)
            
            dist_avg = statistics.mean(dist_times)
            print(f"    平均时间: {dist_avg:.3f}s")
            
            # 计算加速比
            speedup = local_avg / dist_avg if dist_avg > 0 else 0
            print(f"    加速比: {speedup:.2f}x")
            
            results['distributed'] = {
                'avg_time': dist_avg, 
                'times': dist_times,
                'speedup': speedup
            }
            
        except Exception as e:
            print(f"    ❌ 分布式测试失败: {e}")
            results['distributed'] = {'error': str(e)}
    else:
        print("  ❌ 分布式计算不可用，跳过测试")
        results['distributed'] = {'error': '分布式计算不可用'}
    
    return results

def test_different_batch_sizes():
    """测试不同批处理大小的性能"""
    print("\n📊 测试不同批处理大小...")
    
    # 生成足够的测试图像
    test_images = [generate_test_image() for _ in range(32)]
    batch_sizes = [1, 2, 4, 8, 16]
    results = {}
    
    original_batchsize = config.batchsize
    
    for batch_size in batch_sizes:
        if batch_size > len(test_images):
            continue
            
        print(f"  批处理大小: {batch_size}")
        config.batchsize = batch_size
        
        # 实例化特征提取器
        from backend.model_module.feature_extractor import feature_extractor
        extractor = feature_extractor()
        
        times = []
        for _ in range(3):
            start_time = time.time()
            features = extractor.calculate_batch(test_images[:batch_size])
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        throughput = batch_size / avg_time
        per_image_time = avg_time / batch_size
        
        results[batch_size] = {
            'avg_time': avg_time,
            'throughput': throughput,
            'per_image_time': per_image_time,
            'times': times
        }
        
        print(f"    平均时间: {avg_time:.3f}s")
        print(f"    吞吐量: {throughput:.2f} 图像/秒")
        print(f"    单图像时间: {per_image_time:.3f}s")
    
    # 恢复原始配置
    config.batchsize = original_batchsize
    
    return results

def generate_quick_report(results):
    """生成快速报告"""
    print("\n" + "="*60)
    print("📋 快速性能报告")
    print("="*60)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"测试时间: {timestamp}")
    print()
    
    # 当前配置性能
    if 'current_config' in results:
        current = results['current_config']
        print("📊 当前配置性能:")
        print(f"  单图像处理: {current['single_image']['avg_time']:.3f}s")
        print(f"  单图像吞吐量: {current['single_image']['throughput']:.2f} 图像/秒")
        print(f"  批处理效率: {current['batch_processing']['efficiency']:.2f}x")
        print()
    
    # 本地 vs 分布式对比
    if 'local_vs_distributed' in results:
        comparison = results['local_vs_distributed']
        print("⚖️  本地 vs 分布式对比:")
        if 'local' in comparison:
            print(f"  本地计算: {comparison['local']['avg_time']:.3f}s")
        if 'distributed' in comparison and 'error' not in comparison['distributed']:
            print(f"  分布式计算: {comparison['distributed']['avg_time']:.3f}s")
            print(f"  加速比: {comparison['distributed']['speedup']:.2f}x")
        elif 'distributed' in comparison:
            print(f"  分布式计算: 失败 ({comparison['distributed']['error']})")
        print()
    
    # 批处理大小性能
    if 'batch_sizes' in results:
        batch_results = results['batch_sizes']
        print("📈 批处理大小性能:")
        print("  大小 | 时间(s) | 吞吐量(图像/s) | 单图像时间(s)")
        print("  -----|---------|---------------|---------------")
        for batch_size, metrics in batch_results.items():
            print(f"  {batch_size:4d} | {metrics['avg_time']:7.3f} | {metrics['throughput']:13.2f} | {metrics['per_image_time']:13.3f}")
        print()
    
    # 建议
    print("💡 性能优化建议:")
    
    if 'batch_sizes' in results:
        # 找到最佳批处理大小
        best_batch = max(results['batch_sizes'].items(), 
                        key=lambda x: x[1]['throughput'])
        print(f"  • 推荐批处理大小: {best_batch[0]} (吞吐量: {best_batch[1]['throughput']:.2f} 图像/秒)")
    
    if 'local_vs_distributed' in results:
        comparison = results['local_vs_distributed']
        if 'distributed' in comparison and 'speedup' in comparison['distributed']:
            speedup = comparison['distributed']['speedup']
            if speedup > 1.2:
                print(f"  • 建议使用分布式计算 (加速比: {speedup:.2f}x)")
            elif speedup < 0.8:
                print("  • 建议使用本地计算 (分布式计算较慢)")
            else:
                print("  • 本地和分布式计算性能相近，可根据需要选择")
        else:
            print("  • 检查分布式计算配置，确保Worker正常运行")
    
    # 检查配置合理性
    current_config = results.get('current_config', {})
    if current_config:
        single_throughput = current_config['single_image']['throughput']
        if single_throughput < 1.0:
            print("  • 考虑使用更强的硬件或优化模型配置")
        
        efficiency = current_config['batch_processing']['efficiency']
        if efficiency < 2.0:
            print("  • 考虑调整批处理大小以提高效率")

def main():
    """主函数"""
    print("🚀 快速性能测试")
    print("="*60)
    
    results = {}
    
    # 测试当前配置
    results['current_config'] = test_current_config()
    
    # 测试分布式计算可用性并比较性能
    results['local_vs_distributed'] = compare_local_vs_distributed()
    
    # 测试不同批处理大小
    results['batch_sizes'] = test_different_batch_sizes()
    
    # 生成报告
    generate_quick_report(results)
      # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("../performance_reports", exist_ok=True)
    
    with open(f"../performance_reports/quick_test_{timestamp}.json", "w", encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 测试完成，结果已保存到 performance_reports/quick_test_{timestamp}.json")

if __name__ == "__main__":
    main()
