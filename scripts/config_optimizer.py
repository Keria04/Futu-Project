#!/usr/bin/env python3
"""
配置参数优化器
用于自动寻找最佳的配置参数组合，以获得最佳性能
"""

import sys
import os
import time
import json
import statistics
import itertools
from datetime import datetime
from PIL import Image
import numpy as np

# 添加路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from config import config
from backend.model_module.feature_extractor import feature_extractor

class ConfigOptimizer:
    """配置参数优化器"""
    
    def __init__(self):
        self.original_config = {}
        self.backup_config()
        self.test_images = []
        self.optimization_results = {}
        
    def backup_config(self):
        """备份原始配置"""
        self.original_config = {
            'device': config.device,
            'batchsize': config.batchsize,
            'N_LIST': config.N_LIST,
            'DISTRIBUTED_AVAILABLE': config.DISTRIBUTED_AVAILABLE,
        }
        
    def restore_config(self):
        """恢复原始配置"""
        for key, value in self.original_config.items():
            setattr(config, key, value)
            
    def generate_test_images(self, count=20):
        """生成测试图像"""
        print(f"生成 {count} 张测试图像...")
        self.test_images = []
        
        for i in range(count):
            color = (
                int(np.random.randint(0, 256)),
                int(np.random.randint(0, 256)),
                int(np.random.randint(0, 256))
            )
            img = Image.new('RGB', (224, 224), color=color)
            self.test_images.append(img)
            
        print(f"✅ 已生成 {len(self.test_images)} 张测试图像")
        
    def evaluate_config(self, test_config, test_image_count=10):
        """评估单个配置的性能"""
        # 应用配置
        for key, value in test_config.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        # 准备测试数据
        test_batch = self.test_images[:test_image_count]
        
        try:
            # 执行多次测试取平均值
            times = []
            for _ in range(3):
                start_time = time.time()
                features = feature_extractor(test_batch)
                end_time = time.time()
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            throughput = len(test_batch) / avg_time
            per_image_time = avg_time / len(test_batch)
            
            return {
                'success': True,
                'avg_time': avg_time,
                'throughput': throughput,
                'per_image_time': per_image_time,
                'times': times,
                'images_processed': len(test_batch)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        
    def grid_search_optimization(self):
        """网格搜索优化"""
        print("\n🔍 开始网格搜索优化...")
        print("="*60)
        
        # 定义搜索空间
        param_grid = {
            'device': ['cpu'],  # 如果有GPU可以添加 'cuda'
            'batchsize': [1, 4, 8, 16, 32, 64],
            'N_LIST': [1, 5, 10, 20],
        }
        
        # 如果支持GPU，添加GPU选项
        try:
            import torch
            if torch.cuda.is_available():
                param_grid['device'].append('cuda')
                print("✅ 检测到GPU，将测试GPU配置")
        except ImportError:
            pass
        
        # 生成所有参数组合
        param_names = list(param_grid.keys())
        param_values = [param_grid[name] for name in param_names]
        param_combinations = list(itertools.product(*param_values))
        
        print(f"总共 {len(param_combinations)} 个配置组合需要测试")
        
        results = []
        best_config = None
        best_throughput = 0
        
        for i, param_combo in enumerate(param_combinations):
            test_config = dict(zip(param_names, param_combo))
            
            print(f"\n进度: {i+1}/{len(param_combinations)} - 测试配置: {test_config}")
            
            result = self.evaluate_config(test_config)
            result['config'] = test_config
            results.append(result)
            
            if result['success']:
                throughput = result['throughput']
                print(f"  吞吐量: {throughput:.2f} 图像/秒")
                
                if throughput > best_throughput:
                    best_throughput = throughput
                    best_config = test_config
                    print(f"  🎯 新的最佳配置!")
            else:
                print(f"  ❌ 失败: {result['error']}")
        
        self.optimization_results['grid_search'] = {
            'results': results,
            'best_config': best_config,
            'best_throughput': best_throughput
        }
        
        return best_config, best_throughput
        
    def adaptive_optimization(self):
        """自适应优化 - 基于当前最佳配置进行局部搜索"""
        print("\n🎯 开始自适应优化...")
        print("="*60)
        
        if 'grid_search' not in self.optimization_results:
            print("❌ 请先运行网格搜索")
            return None, 0
        
        best_config = self.optimization_results['grid_search']['best_config']
        if not best_config:
            print("❌ 没有找到有效的基准配置")
            return None, 0
        
        print(f"基准配置: {best_config}")
        
        current_config = best_config.copy()
        current_throughput = self.optimization_results['grid_search']['best_throughput']
        
        # 自适应搜索批处理大小
        print("\n优化批处理大小...")
        batchsize = current_config['batchsize']
        
        # 向上搜索
        for new_batchsize in [batchsize * 2, batchsize * 4]:
            if new_batchsize > 128:  # 设置上限
                break
                
            test_config = current_config.copy()
            test_config['batchsize'] = new_batchsize
            
            print(f"  测试批处理大小: {new_batchsize}")
            result = self.evaluate_config(test_config)
            
            if result['success'] and result['throughput'] > current_throughput:
                current_config = test_config
                current_throughput = result['throughput']
                print(f"    ✅ 改进! 新吞吐量: {current_throughput:.2f}")
            else:
                print(f"    ❌ 无改进")
                break
        
        # 向下搜索（如果向上搜索没有改进）
        if current_config['batchsize'] == batchsize:
            for new_batchsize in [max(1, batchsize // 2), max(1, batchsize // 4)]:
                test_config = current_config.copy()
                test_config['batchsize'] = new_batchsize
                
                print(f"  测试批处理大小: {new_batchsize}")
                result = self.evaluate_config(test_config)
                
                if result['success'] and result['throughput'] > current_throughput:
                    current_config = test_config
                    current_throughput = result['throughput']
                    print(f"    ✅ 改进! 新吞吐量: {current_throughput:.2f}")
                else:
                    print(f"    ❌ 无改进")
                    break
        
        # 优化簇大小
        print("\n优化簇大小...")
        n_list = current_config['N_LIST']
        
        for new_n_list in [n_list * 2, n_list // 2, n_list + 5, max(1, n_list - 5)]:
            if new_n_list <= 0 or new_n_list > 100:
                continue
                
            test_config = current_config.copy()
            test_config['N_LIST'] = new_n_list
            
            print(f"  测试簇大小: {new_n_list}")
            result = self.evaluate_config(test_config)
            
            if result['success'] and result['throughput'] > current_throughput:
                current_config = test_config
                current_throughput = result['throughput']
                print(f"    ✅ 改进! 新吞吐量: {current_throughput:.2f}")
        
        self.optimization_results['adaptive'] = {
            'final_config': current_config,
            'final_throughput': current_throughput
        }
        
        return current_config, current_throughput
        
    def benchmark_optimized_config(self, optimized_config):
        """对优化后的配置进行基准测试"""
        print("\n📊 对优化配置进行基准测试...")
        print("="*60)
        
        # 测试不同工作负载
        workloads = [
            {'name': '轻量级', 'image_count': 5},
            {'name': '中等', 'image_count': 10},
            {'name': '重负载', 'image_count': 20}
        ]
        
        benchmark_results = {}
        
        for workload in workloads:
            print(f"\n测试工作负载: {workload['name']} ({workload['image_count']} 图像)")
            
            # 原始配置测试
            self.restore_config()
            original_result = self.evaluate_config(self.original_config, workload['image_count'])
            
            # 优化配置测试
            optimized_result = self.evaluate_config(optimized_config, workload['image_count'])
            
            if original_result['success'] and optimized_result['success']:
                improvement = optimized_result['throughput'] / original_result['throughput']
                time_saved = original_result['avg_time'] - optimized_result['avg_time']
                
                print(f"  原始配置: {original_result['throughput']:.2f} 图像/秒")
                print(f"  优化配置: {optimized_result['throughput']:.2f} 图像/秒")
                print(f"  改进倍数: {improvement:.2f}x")
                print(f"  时间节省: {time_saved:.3f}s")
                
                benchmark_results[workload['name']] = {
                    'original': original_result,
                    'optimized': optimized_result,
                    'improvement': improvement,
                    'time_saved': time_saved
                }
            else:
                print(f"  ❌ 测试失败")
                benchmark_results[workload['name']] = {'error': '测试失败'}
        
        return benchmark_results
        
    def generate_optimization_report(self):
        """生成优化报告"""
        print("\n📋 生成优化报告...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = os.path.join("..", "performance_reports", f"optimization_{timestamp}")
        os.makedirs(report_dir, exist_ok=True)
        
        # 保存原始数据
        with open(os.path.join(report_dir, "optimization_results.json"), "w", encoding='utf-8') as f:
            json.dump(self.optimization_results, f, indent=2, ensure_ascii=False)
        
        # 生成Markdown报告
        report_path = os.path.join(report_dir, "optimization_report.md")
        with open(report_path, "w", encoding='utf-8') as f:
            f.write("# 配置优化报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 原始配置
            f.write("## 原始配置\n\n")
            f.write("| 参数 | 值 |\n")
            f.write("|------|----|\n")
            for key, value in self.original_config.items():
                f.write(f"| {key} | {value} |\n")
            f.write("\n")
            
            # 网格搜索结果
            if 'grid_search' in self.optimization_results:
                grid_result = self.optimization_results['grid_search']
                f.write("## 网格搜索结果\n\n")
                
                if grid_result['best_config']:
                    f.write("### 最佳配置\n\n")
                    f.write("| 参数 | 值 |\n")
                    f.write("|------|----|\n")
                    for key, value in grid_result['best_config'].items():
                        f.write(f"| {key} | {value} |\n")
                    f.write(f"\n最佳吞吐量: {grid_result['best_throughput']:.2f} 图像/秒\n\n")
                
                # Top 10 配置
                successful_results = [r for r in grid_result['results'] if r['success']]
                top_configs = sorted(successful_results, key=lambda x: x['throughput'], reverse=True)[:10]
                
                f.write("### Top 10 配置\n\n")
                f.write("| 排名 | 设备 | 批处理大小 | 簇大小 | 吞吐量(图像/s) |\n")
                f.write("|------|------|------------|--------|-----------------|\n")
                for i, result in enumerate(top_configs, 1):
                    config_info = result['config']
                    f.write(f"| {i} | {config_info['device']} | {config_info['batchsize']} | {config_info['N_LIST']} | {result['throughput']:.2f} |\n")
                f.write("\n")
            
            # 自适应优化结果
            if 'adaptive' in self.optimization_results:
                adaptive_result = self.optimization_results['adaptive']
                f.write("## 自适应优化结果\n\n")
                f.write("| 参数 | 值 |\n")
                f.write("|------|----|\n")
                for key, value in adaptive_result['final_config'].items():
                    f.write(f"| {key} | {value} |\n")
                f.write(f"\n最终吞吐量: {adaptive_result['final_throughput']:.2f} 图像/秒\n\n")
            
            # 基准测试结果
            if 'benchmark' in self.optimization_results:
                benchmark_result = self.optimization_results['benchmark']
                f.write("## 基准测试对比\n\n")
                f.write("| 工作负载 | 原始吞吐量 | 优化吞吐量 | 改进倍数 | 时间节省(s) |\n")
                f.write("|----------|------------|------------|----------|-------------|\n")
                for workload_name, result in benchmark_result.items():
                    if 'error' not in result:
                        f.write(f"| {workload_name} | {result['original']['throughput']:.2f} | {result['optimized']['throughput']:.2f} | {result['improvement']:.2f}x | {result['time_saved']:.3f} |\n")
                    else:
                        f.write(f"| {workload_name} | N/A | N/A | N/A | N/A |\n")
                f.write("\n")
        
        print(f"✅ 优化报告已生成: {report_path}")
        return report_path
        
    def run_full_optimization(self):
        """运行完整优化流程"""
        print("🚀 开始配置参数优化")
        print("="*60)
        
        start_time = time.time()
        
        try:
            # 生成测试图像
            self.generate_test_images(count=20)
            
            # 网格搜索
            best_config, best_throughput = self.grid_search_optimization()
            
            if best_config:
                print(f"\n🎯 网格搜索最佳配置: {best_config}")
                print(f"最佳吞吐量: {best_throughput:.2f} 图像/秒")
                
                # 自适应优化
                final_config, final_throughput = self.adaptive_optimization()
                
                if final_config:
                    print(f"\n🏆 最终优化配置: {final_config}")
                    print(f"最终吞吐量: {final_throughput:.2f} 图像/秒")
                    
                    # 基准测试
                    benchmark_results = self.benchmark_optimized_config(final_config)
                    self.optimization_results['benchmark'] = benchmark_results
                    
                    # 生成报告
                    report_path = self.generate_optimization_report()
                    
                    # 计算总体改进
                    original_throughput = self.evaluate_config(self.original_config, 10)['throughput']
                    total_improvement = final_throughput / original_throughput if original_throughput > 0 else 0
                    
                    print(f"\n✅ 优化完成!")
                    print(f"原始性能: {original_throughput:.2f} 图像/秒")
                    print(f"优化性能: {final_throughput:.2f} 图像/秒")
                    print(f"总体改进: {total_improvement:.2f}x")
                    
                    total_time = time.time() - start_time
                    print(f"总优化时间: {total_time:.2f}秒")
                    
                    return final_config
                else:
                    print("❌ 自适应优化失败")
            else:
                print("❌ 网格搜索失败，没有找到有效配置")
                
        except Exception as e:
            print(f"❌ 优化过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # 恢复原始配置
            self.restore_config()
            
        return None


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='配置参数优化器')
    parser.add_argument('--mode', choices=['full', 'grid', 'adaptive'], default='full',
                      help='优化模式: full(完整优化), grid(仅网格搜索), adaptive(仅自适应优化)')
    
    args = parser.parse_args()
    
    optimizer = ConfigOptimizer()
    
    if args.mode == 'full':
        optimized_config = optimizer.run_full_optimization()
        if optimized_config:
            print(f"\n💡 建议将以下配置写入config.py:")
            for key, value in optimized_config.items():
                print(f"{key} = {repr(value)}")
    
    elif args.mode == 'grid':
        optimizer.generate_test_images()
        best_config, best_throughput = optimizer.grid_search_optimization()
        if best_config:
            print(f"\n🎯 最佳配置: {best_config}")
            print(f"最佳吞吐量: {best_throughput:.2f} 图像/秒")
    
    elif args.mode == 'adaptive':
        print("❌ 自适应模式需要先运行网格搜索")


if __name__ == "__main__":
    main()
