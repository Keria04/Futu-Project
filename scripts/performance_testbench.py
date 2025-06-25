#!/usr/bin/env python3
"""
性能测试基准工具 (Performance Testbench)
用于评估远程和本地两种计算方式的性能，以及分析各种配置参数对性能的影响

主要测试项目：
1. 远程（Celery分布式）vs 本地计算性能对比
2. 簇大小（N_LIST）对检索性能的影响
3. 批处理大小（batchsize）对特征提取性能的影响
4. 设备类型（CPU vs GPU）对性能的影响
5. 不同数据集大小对性能的影响
"""

import sys
import os
import time
import json
import base64
import statistics
import numpy as np
from datetime import datetime
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate

# 添加路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# 导入项目模块
from config import config
from backend.model_module.feature_extractor import feature_extractor
from backend.faiss_module.search_index import search_index
from backend.database_module.query import query_multi
from backend.search_module.search import search_image

class PerformanceTestbench:
    """性能测试基准类"""
    
    def __init__(self):
        self.results = {}
        self.test_images = []
        self.original_config = {}
        self.backup_config()
        
    def backup_config(self):
        """备份原始配置"""
        self.original_config = {
            'device': config.device,
            'batchsize': config.batchsize,
            'N_LIST': config.N_LIST,
            'DISTRIBUTED_AVAILABLE': config.DISTRIBUTED_AVAILABLE,
            'CELERY_TASK_TIME_LIMIT': config.CELERY_TASK_TIME_LIMIT,
            'CELERY_TASK_SOFT_TIME_LIMIT': config.CELERY_TASK_SOFT_TIME_LIMIT
        }
        
    def restore_config(self):
        """恢复原始配置"""
        for key, value in self.original_config.items():
            setattr(config, key, value)
            
    def generate_test_images(self, count=20, size=(224, 224)):
        """生成测试图像"""
        print(f"生成 {count} 张测试图像...")
        self.test_images = []
        
        for i in range(count):
            # 生成随机颜色的图像
            color = (
                int(np.random.randint(0, 256)),
                int(np.random.randint(0, 256)),
                int(np.random.randint(0, 256))
            )
            img = Image.new('RGB', size, color=color)
            
            # 添加一些简单的模式
            if i % 4 == 0:  # 添加圆形
                from PIL import ImageDraw
                draw = ImageDraw.Draw(img)
                draw.ellipse([50, 50, 174, 174], fill=(255, 255, 255))
            elif i % 4 == 1:  # 添加矩形
                from PIL import ImageDraw
                draw = ImageDraw.Draw(img)
                draw.rectangle([50, 50, 174, 174], fill=(255, 255, 255))
            
            # 转换为base64
            img_buffer = BytesIO()
            img.save(img_buffer, format='JPEG')
            img_data = img_buffer.getvalue()
            img_data_b64 = base64.b64encode(img_data).decode('utf-8')
            
            self.test_images.append({
                'id': i,
                'image': img,
                'base64': img_data_b64,
                'size': len(img_data)
            })
            
        print(f"✅ 已生成 {len(self.test_images)} 张测试图像")
        
    def test_feature_extraction_performance(self):
        """测试特征提取性能"""
        print("\n" + "="*80)
        print("📊 特征提取性能测试")
        print("="*80)
        
        batch_sizes = [1, 4, 8, 16, 32, 64, 128]
        devices = ['cpu']
        
        # 如果支持GPU，添加GPU测试
        try:
            import torch
            if torch.cuda.is_available():
                devices.append('cuda')
        except ImportError:
            pass
            
        results = {}
        
        for device in devices:
            print(f"\n🔧 测试设备: {device}")
            results[device] = {}
            
            # 设置设备
            original_device = config.device
            config.device = device
            
            for batch_size in batch_sizes:
                if batch_size > len(self.test_images):
                    continue
                    
                print(f"  批处理大小: {batch_size}")
                config.batchsize = batch_size
                
                # 准备测试图像
                test_batch = [img['image'] for img in self.test_images[:batch_size]]
                
                # 执行多次测试取平均值
                times = []
                for _ in range(3):
                    start_time = time.time()
                    features = feature_extractor(test_batch)
                    end_time = time.time()
                    times.append(end_time - start_time)
                
                avg_time = statistics.mean(times)
                throughput = batch_size / avg_time  # 图像/秒
                
                results[device][batch_size] = {
                    'avg_time': avg_time,
                    'throughput': throughput,
                    'times': times
                }
                
                print(f"    平均时间: {avg_time:.3f}s, 吞吐量: {throughput:.2f} 图像/秒")
            
            # 恢复设备设置
            config.device = original_device
            
        self.results['feature_extraction'] = results
        return results
        
    def test_distributed_vs_local(self):
        """测试分布式 vs 本地计算性能"""
        print("\n" + "="*80)
        print("🌐 分布式 vs 本地计算性能测试")
        print("="*80)
        
        results = {'local': {}, 'distributed': {}}
        
        # 测试图像数量
        test_counts = [1, 5, 10, 20]
        
        for count in test_counts:
            if count > len(self.test_images):
                continue
                
            print(f"\n📋 测试图像数量: {count}")
            test_batch = self.test_images[:count]
            
            # 本地计算测试
            print("  🏠 本地计算测试...")
            config.DISTRIBUTED_AVAILABLE = False
            
            local_times = []
            for _ in range(3):
                start_time = time.time()
                for img_data in test_batch:
                    features = feature_extractor([img_data['image']])
                end_time = time.time()
                local_times.append(end_time - start_time)
            
            local_avg = statistics.mean(local_times)
            local_throughput = count / local_avg
            
            results['local'][count] = {
                'avg_time': local_avg,
                'throughput': local_throughput,
                'times': local_times
            }
            
            print(f"    平均时间: {local_avg:.3f}s, 吞吐量: {local_throughput:.2f} 图像/秒")
            
            # 分布式计算测试
            print("  ☁️  分布式计算测试...")
            config.DISTRIBUTED_AVAILABLE = True
            
            try:
                from backend.worker import generate_embeddings_task
                
                distributed_times = []
                for _ in range(3):
                    start_time = time.time()
                    futures = []
                    
                    for img_data in test_batch:
                        future = generate_embeddings_task.delay(img_data['base64'])
                        futures.append(future)
                    
                    # 等待所有任务完成
                    for future in futures:
                        result = future.get(timeout=30)
                    
                    end_time = time.time()
                    distributed_times.append(end_time - start_time)
                
                distributed_avg = statistics.mean(distributed_times)
                distributed_throughput = count / distributed_avg
                
                results['distributed'][count] = {
                    'avg_time': distributed_avg,
                    'throughput': distributed_throughput,
                    'times': distributed_times
                }
                
                print(f"    平均时间: {distributed_avg:.3f}s, 吞吐量: {distributed_throughput:.2f} 图像/秒")
                
                # 计算性能比较
                speedup = local_avg / distributed_avg if distributed_avg > 0 else 0
                print(f"    加速比: {speedup:.2f}x")
                
            except Exception as e:
                print(f"    ❌ 分布式测试失败: {e}")
                results['distributed'][count] = {'error': str(e)}
        
        self.results['distributed_vs_local'] = results
        return results
        
    def test_faiss_cluster_performance(self):
        """测试FAISS簇大小对检索性能的影响"""
        print("\n" + "="*80)
        print("🔍 FAISS簇大小性能测试")
        print("="*80)
        
        # 不同的簇大小设置
        n_list_values = [1, 5, 10, 20, 50, 100]
        results = {}
        
        # 首先检查是否有数据集
        try:
            dataset_rows = query_multi("datasets", columns="id, name", limit=1)
            if not dataset_rows:
                print("❌ 没有找到数据集，跳过FAISS测试")
                return {}
                
            dataset_id = dataset_rows[0][0]
            print(f"使用数据集ID: {dataset_id}")
            
            # 获取数据集特征
            from backend.search_module.search import get_features_and_ids
            features, ids, image_paths, descriptions = get_features_and_ids(dataset_id)
            
            if features is None or len(features) < 10:
                print("❌ 数据集特征太少，跳过FAISS测试")
                return {}
                
            print(f"数据集包含 {len(features)} 个特征向量")
            
        except Exception as e:
            print(f"❌ 获取数据集失败: {e}")
            return {}
        
        original_n_list = config.N_LIST
        
        for n_list in n_list_values:
            if n_list > len(features) // 2:  # 簇数量不能太大
                continue
                
            print(f"\n🔧 测试簇大小: {n_list}")
            config.N_LIST = n_list
            
            try:
                # 测试查询性能
                query_times = []
                accuracy_scores = []
                
                # 使用前几个特征作为查询
                query_features = features[:min(5, len(features))]
                
                for query_feature in query_features:
                    start_time = time.time()
                    
                    # 执行搜索
                    similar_indices, distances = search_index(
                        dataset_id, query_feature.reshape(1, -1), k=10
                    )
                    
                    end_time = time.time()
                    query_times.append(end_time - start_time)
                    
                    # 简单的准确性评估（检查是否找到相似的结果）
                    if len(similar_indices) > 0:
                        accuracy_scores.append(1.0)
                    else:
                        accuracy_scores.append(0.0)
                
                avg_query_time = statistics.mean(query_times)
                avg_accuracy = statistics.mean(accuracy_scores)
                
                results[n_list] = {
                    'avg_query_time': avg_query_time,
                    'avg_accuracy': avg_accuracy,
                    'query_times': query_times,
                    'throughput': 1.0 / avg_query_time if avg_query_time > 0 else 0
                }
                
                print(f"    平均查询时间: {avg_query_time:.4f}s")
                print(f"    查询吞吐量: {results[n_list]['throughput']:.2f} 查询/秒")
                print(f"    平均准确率: {avg_accuracy:.2f}")
                
            except Exception as e:
                print(f"    ❌ 测试失败: {e}")
                results[n_list] = {'error': str(e)}
        
        # 恢复原始配置
        config.N_LIST = original_n_list
        
        self.results['faiss_cluster'] = results
        return results
        
    def test_concurrent_performance(self):
        """测试并发处理性能"""
        print("\n" + "="*80)
        print("⚡ 并发处理性能测试")
        print("="*80)
        
        concurrent_levels = [1, 2, 4, 8]
        results = {}
        
        for level in concurrent_levels:
            print(f"\n🔧 并发等级: {level}")
            
            test_batch = self.test_images[:min(level * 2, len(self.test_images))]
            
            times = []
            for _ in range(3):
                start_time = time.time()
                
                with ThreadPoolExecutor(max_workers=level) as executor:
                    futures = []
                    for img_data in test_batch:
                        future = executor.submit(feature_extractor, [img_data['image']])
                        futures.append(future)
                    
                    # 等待所有任务完成
                    for future in as_completed(futures):
                        result = future.result()
                
                end_time = time.time()
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            throughput = len(test_batch) / avg_time
            
            results[level] = {
                'avg_time': avg_time,
                'throughput': throughput,
                'times': times,
                'images_processed': len(test_batch)
            }
            print(f"    平均时间: {avg_time:.3f}s")
            print(f"    吞吐量: {throughput:.2f} 图像/秒")
        
        self.results['concurrent'] = results
        return results
        
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*80)
        print("📋 生成性能测试报告")
        print("="*80)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = os.path.join("..", "performance_reports", timestamp)
        os.makedirs(report_dir, exist_ok=True)
        
        # 保存原始数据
        with open(os.path.join(report_dir, "raw_results.json"), "w", encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # 生成文本报告
        report_path = os.path.join(report_dir, "performance_report.md")
        with open(report_path, "w", encoding='utf-8') as f:
            f.write(f"# 性能测试报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 配置信息
            f.write("## 测试配置\n\n")
            f.write("| 配置项 | 值 |\n")
            f.write("|--------|----|\n")
            for key, value in self.original_config.items():
                f.write(f"| {key} | {value} |\n")
            f.write("\n")
            
            # 特征提取性能
            if 'feature_extraction' in self.results:
                f.write("## 特征提取性能\n\n")
                for device, device_results in self.results['feature_extraction'].items():
                    f.write(f"### 设备: {device}\n\n")
                    f.write("| 批处理大小 | 平均时间(s) | 吞吐量(图像/s) |\n")
                    f.write("|------------|-------------|----------------|\n")
                    for batch_size, metrics in device_results.items():
                        f.write(f"| {batch_size} | {metrics['avg_time']:.3f} | {metrics['throughput']:.2f} |\n")
                    f.write("\n")
            
            # 分布式 vs 本地
            if 'distributed_vs_local' in self.results:
                f.write("## 分布式 vs 本地计算性能\n\n")
                f.write("| 图像数量 | 本地时间(s) | 分布式时间(s) | 本地吞吐量 | 分布式吞吐量 | 加速比 |\n")
                f.write("|----------|-------------|---------------|------------|--------------|--------|\n")
                
                local_results = self.results['distributed_vs_local']['local']
                distributed_results = self.results['distributed_vs_local']['distributed']
                
                for count in local_results.keys():
                    local_time = local_results[count]['avg_time']
                    local_throughput = local_results[count]['throughput']
                    
                    if count in distributed_results and 'error' not in distributed_results[count]:
                        dist_time = distributed_results[count]['avg_time']
                        dist_throughput = distributed_results[count]['throughput']
                        speedup = local_time / dist_time if dist_time > 0 else 0
                        f.write(f"| {count} | {local_time:.3f} | {dist_time:.3f} | {local_throughput:.2f} | {dist_throughput:.2f} | {speedup:.2f}x |\n")
                    else:
                        f.write(f"| {count} | {local_time:.3f} | 失败 | {local_throughput:.2f} | N/A | N/A |\n")
                f.write("\n")
            
            # FAISS簇大小性能
            if 'faiss_cluster' in self.results:
                f.write("## FAISS簇大小性能\n\n")
                f.write("| 簇大小 | 平均查询时间(s) | 查询吞吐量(查询/s) | 准确率 |\n")
                f.write("|--------|-----------------|-------------------|--------|\n")
                for n_list, metrics in self.results['faiss_cluster'].items():
                    if 'error' not in metrics:
                        f.write(f"| {n_list} | {metrics['avg_query_time']:.4f} | {metrics['throughput']:.2f} | {metrics['avg_accuracy']:.2f} |\n")
                    else:
                        f.write(f"| {n_list} | 失败 | N/A | N/A |\n")
                f.write("\n")
            
            # 并发性能
            if 'concurrent' in self.results:
                f.write("## 并发处理性能\n\n")
                f.write("| 并发等级 | 处理图像数 | 平均时间(s) | 吞吐量(图像/s) |\n")
                f.write("|----------|------------|-------------|----------------|\n")
                for level, metrics in self.results['concurrent'].items():
                    f.write(f"| {level} | {metrics['images_processed']} | {metrics['avg_time']:.3f} | {metrics['throughput']:.2f} |\n")
                f.write("\n")
        
        # 生成图表
        self.generate_charts(report_dir)
        
        print(f"✅ 报告已生成: {report_path}")
        return report_path
        
    def generate_charts(self, report_dir):
        """生成性能图表"""
        try:
            plt.style.use('seaborn-v0_8')
        except:
            plt.style.use('default')
        
        # 特征提取性能图表
        if 'feature_extraction' in self.results:
            fig, axes = plt.subplots(1, 2, figsize=(15, 6))
            
            for device, device_results in self.results['feature_extraction'].items():
                batch_sizes = list(device_results.keys())
                times = [device_results[bs]['avg_time'] for bs in batch_sizes]
                throughputs = [device_results[bs]['throughput'] for bs in batch_sizes]
                
                axes[0].plot(batch_sizes, times, marker='o', label=f'{device} - 时间')
                axes[1].plot(batch_sizes, throughputs, marker='s', label=f'{device} - 吞吐量')
            
            axes[0].set_xlabel('批处理大小')
            axes[0].set_ylabel('平均时间 (s)')
            axes[0].set_title('特征提取时间 vs 批处理大小')
            axes[0].legend()
            axes[0].grid(True)
            
            axes[1].set_xlabel('批处理大小')
            axes[1].set_ylabel('吞吐量 (图像/s)')
            axes[1].set_title('特征提取吞吐量 vs 批处理大小')
            axes[1].legend()
            axes[1].grid(True)
            
            plt.tight_layout()
            plt.savefig(os.path.join(report_dir, 'feature_extraction_performance.png'), dpi=300, bbox_inches='tight')
            plt.close()
        
        # 分布式 vs 本地性能图表
        if 'distributed_vs_local' in self.results:
            local_results = self.results['distributed_vs_local']['local']
            distributed_results = self.results['distributed_vs_local']['distributed']
            
            counts = list(local_results.keys())
            local_times = [local_results[c]['avg_time'] for c in counts]
            local_throughputs = [local_results[c]['throughput'] for c in counts]
            
            dist_times = []
            dist_throughputs = []
            for c in counts:
                if c in distributed_results and 'error' not in distributed_results[c]:
                    dist_times.append(distributed_results[c]['avg_time'])
                    dist_throughputs.append(distributed_results[c]['throughput'])
                else:
                    dist_times.append(None)
                    dist_throughputs.append(None)
            
            fig, axes = plt.subplots(1, 2, figsize=(15, 6))
            
            axes[0].plot(counts, local_times, marker='o', label='本地计算', linewidth=2)
            if any(t is not None for t in dist_times):
                valid_counts = [c for c, t in zip(counts, dist_times) if t is not None]
                valid_times = [t for t in dist_times if t is not None]
                axes[0].plot(valid_counts, valid_times, marker='s', label='分布式计算', linewidth=2)
            
            axes[0].set_xlabel('图像数量')
            axes[0].set_ylabel('平均时间 (s)')
            axes[0].set_title('处理时间对比')
            axes[0].legend()
            axes[0].grid(True)
            
            axes[1].plot(counts, local_throughputs, marker='o', label='本地计算', linewidth=2)
            if any(t is not None for t in dist_throughputs):
                valid_counts = [c for c, t in zip(counts, dist_throughputs) if t is not None]
                valid_throughputs = [t for t in dist_throughputs if t is not None]
                axes[1].plot(valid_counts, valid_throughputs, marker='s', label='分布式计算', linewidth=2)
            
            axes[1].set_xlabel('图像数量')
            axes[1].set_ylabel('吞吐量 (图像/s)')
            axes[1].set_title('吞吐量对比')
            axes[1].legend()
            axes[1].grid(True)
            
            plt.tight_layout()
            plt.savefig(os.path.join(report_dir, 'distributed_vs_local.png'), dpi=300, bbox_inches='tight')
            plt.close()
        
        # FAISS簇大小性能图表
        if 'faiss_cluster' in self.results:
            valid_results = {k: v for k, v in self.results['faiss_cluster'].items() if 'error' not in v}
            
            if valid_results:
                n_lists = list(valid_results.keys())
                query_times = [valid_results[n]['avg_query_time'] for n in n_lists]
                throughputs = [valid_results[n]['throughput'] for n in n_lists]
                accuracies = [valid_results[n]['avg_accuracy'] for n in n_lists]
                
                fig, axes = plt.subplots(1, 3, figsize=(18, 6))
                
                axes[0].plot(n_lists, query_times, marker='o', linewidth=2, color='red')
                axes[0].set_xlabel('簇大小 (N_LIST)')
                axes[0].set_ylabel('平均查询时间 (s)')
                axes[0].set_title('查询时间 vs 簇大小')
                axes[0].grid(True)
                
                axes[1].plot(n_lists, throughputs, marker='s', linewidth=2, color='blue')
                axes[1].set_xlabel('簇大小 (N_LIST)')
                axes[1].set_ylabel('查询吞吐量 (查询/s)')
                axes[1].set_title('查询吞吐量 vs 簇大小')
                axes[1].grid(True)
                
                axes[2].plot(n_lists, accuracies, marker='^', linewidth=2, color='green')
                axes[2].set_xlabel('簇大小 (N_LIST)')
                axes[2].set_ylabel('准确率')
                axes[2].set_title('准确率 vs 簇大小')
                axes[2].grid(True)
                
                plt.tight_layout()
                plt.savefig(os.path.join(report_dir, 'faiss_cluster_performance.png'), dpi=300, bbox_inches='tight')
                plt.close()
        
        print("✅ 性能图表已生成")
        
    def run_full_benchmark(self):
        """运行完整的性能基准测试"""
        print("🚀 开始运行完整性能基准测试")
        print("=" * 80)
        
        start_time = time.time()
        
        try:
            # 生成测试图像
            self.generate_test_images(count=30)
            
            # 运行各项测试
            self.test_feature_extraction_performance()
            self.test_distributed_vs_local()
            self.test_faiss_cluster_performance()
            self.test_concurrent_performance()
            
            # 生成报告
            report_path = self.generate_report()
            
            total_time = time.time() - start_time
            print(f"\n✅ 完整基准测试完成，总耗时: {total_time:.2f}秒")
            print(f"📄 报告路径: {report_path}")
            
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # 恢复原始配置
            self.restore_config()
            
    def run_custom_test(self, test_configs):
        """运行自定义配置测试"""
        print("🔧 运行自定义配置测试")
        print("=" * 80)
        
        results = {}
        
        for config_name, test_config in test_configs.items():
            print(f"\n📊 测试配置: {config_name}")
            print("-" * 40)
            
            # 应用配置
            for key, value in test_config.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                    print(f"  {key}: {value}")
            
            # 运行特征提取测试
            if not hasattr(self, 'test_images') or not self.test_images:
                self.generate_test_images(count=10)
            
            # 简单的性能测试
            test_batch = self.test_images[:5]
            times = []
            
            for _ in range(3):
                start_time = time.time()
                for img_data in test_batch:
                    features = feature_extractor([img_data['image']])
                end_time = time.time()
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            throughput = len(test_batch) / avg_time
            
            results[config_name] = {
                'config': test_config,
                'avg_time': avg_time,
                'throughput': throughput,
                'times': times
            }
            
            print(f"  结果: 平均时间 {avg_time:.3f}s, 吞吐量 {throughput:.2f} 图像/秒")
        
        # 恢复原始配置
        self.restore_config()
        
        return results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='性能测试基准工具')
    parser.add_argument('--mode', choices=['full', 'quick', 'custom'], default='full',
                      help='测试模式: full(完整测试), quick(快速测试), custom(自定义测试)')
    parser.add_argument('--images', type=int, default=20,
                      help='测试图像数量 (默认: 20)')
    
    args = parser.parse_args()
    
    testbench = PerformanceTestbench()
    
    if args.mode == 'full':
        testbench.run_full_benchmark()
        
    elif args.mode == 'quick':
        print("🏃 快速性能测试")
        testbench.generate_test_images(count=min(args.images, 10))
        testbench.test_feature_extraction_performance()
        testbench.generate_report()
        
    elif args.mode == 'custom':
        # 示例自定义配置
        custom_configs = {
            'cpu_small_batch': {
                'device': 'cpu',
                'batchsize': 4,
                'N_LIST': 5
            },
            'cpu_large_batch': {
                'device': 'cpu',
                'batchsize': 32,
                'N_LIST': 10
            }
        }
        
        # 如果支持GPU，添加GPU配置
        try:
            import torch
            if torch.cuda.is_available():
                custom_configs.update({
                    'gpu_small_batch': {
                        'device': 'cuda',
                        'batchsize': 8,
                        'N_LIST': 5
                    },
                    'gpu_large_batch': {
                        'device': 'cuda',
                        'batchsize': 64,
                        'N_LIST': 20
                    }
                })
        except ImportError:
            pass
        
        testbench.generate_test_images(count=args.images)
        results = testbench.run_custom_test(custom_configs)
        
        # 打印结果对比
        print("\n📊 自定义配置测试结果对比")
        print("=" * 80)
        
        headers = ['配置名称', '平均时间(s)', '吞吐量(图像/s)', '设备', '批处理大小', '簇大小']
        table_data = []
        
        for config_name, result in results.items():
            row = [
                config_name,
                f"{result['avg_time']:.3f}",
                f"{result['throughput']:.2f}",
                result['config'].get('device', 'N/A'),
                result['config'].get('batchsize', 'N/A'),
                result['config'].get('N_LIST', 'N/A')
            ]
            table_data.append(row)
        
        print(tabulate(table_data, headers=headers, tablefmt='grid'))


if __name__ == "__main__":
    main()
