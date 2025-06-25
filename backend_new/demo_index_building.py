#!/usr/bin/env python3
"""
索引构建功能演示脚本
展示从API请求到任务完成的完整流程
"""
import requests
import json
import time
import threading
import logging
from typing import Dict, Any

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IndexBuildingDemo:
    """索引构建功能演示类"""
    
    def __init__(self, controller_url: str = "http://localhost:19198"):
        self.controller_url = controller_url
        self.session = requests.Session()
    
    def demonstrate_full_workflow(self):
        """演示完整的索引构建工作流程"""
        print("=" * 80)
        print("🚀 浮图项目索引构建功能演示")
        print("=" * 80)
        
        # 步骤1: 健康检查
        print("\n📋 步骤 1: 服务健康检查")
        if not self._check_service_health():
            print("❌ 服务健康检查失败，请确保控制端正在运行")
            return
        print("✅ 控制端服务运行正常")
        
        # 步骤2: 提交索引构建任务
        print("\n📋 步骤 2: 提交索引构建任务")
        task_result = self._submit_index_task()
        if not task_result:
            print("❌ 任务提交失败")
            return
        
        task_id = task_result.get('task_id')
        progress_file = task_result.get('progress', [{}])[0].get('progress_file')
        
        print(f"✅ 任务提交成功")
        print(f"   任务ID: {task_id}")
        print(f"   进度文件: {progress_file}")
        
        # 步骤3: 监控构建进度
        print("\n📋 步骤 3: 监控构建进度")
        final_result = self._monitor_progress(progress_file, task_id)
        
        # 步骤4: 显示最终结果
        print("\n📋 步骤 4: 构建结果")
        self._display_final_result(final_result)
        
        print("\n" + "=" * 80)
        print("🎉 索引构建功能演示完成！")
        print("=" * 80)
    
    def _check_service_health(self) -> bool:
        """检查服务健康状态"""
        try:
            response = self.session.get(f"{self.controller_url}/api/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print(f"   服务状态: {health_data.get('status', 'unknown')}")
                print(f"   Redis连接: {'✅' if health_data.get('redis_connected') else '❌'}")
                return health_data.get('status') == 'healthy'
        except Exception as e:
            print(f"   健康检查异常: {e}")
        return False
    
    def _submit_index_task(self) -> Dict[str, Any]:
        """提交索引构建任务"""
        payload = {
            "dataset_names": ["demo_dataset"],
            "distributed": False
        }
        
        try:
            print(f"   请求数据: {json.dumps(payload, indent=2)}")
            response = self.session.post(
                f"{self.controller_url}/api/build_index",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return result
            else:
                print(f"   请求失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"   请求异常: {e}")
            return None
    
    def _monitor_progress(self, progress_file: str, task_id: str) -> Dict[str, Any]:
        """监控构建进度"""
        print("   开始监控进度...")
        
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            try:
                # 方式1: 通过进度文件查询
                if progress_file:
                    progress_response = self.session.get(
                        f"{self.controller_url}/api{progress_file}",
                        timeout=10
                    )
                    
                    if progress_response.status_code == 200:
                        progress_data = progress_response.json()
                        status = progress_data.get('status', 'unknown')
                        progress = progress_data.get('progress', 0)
                        message = progress_data.get('message', '')
                        
                        print(f"   [{attempt:2d}] 进度: {progress:5.1f}% | 状态: {status:10s} | {message}")
                        
                        if status in ['completed', 'failed']:
                            return progress_data
                
                # 方式2: 通过任务ID查询
                if task_id:
                    status_response = self.session.get(
                        f"{self.controller_url}/api/build_status/{task_id}",
                        timeout=10
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if status_data.get('status') in ['completed', 'failed']:
                            print(f"   任务状态更新: {status_data.get('status')}")
                            return status_data
                
                time.sleep(2)
                
            except Exception as e:
                print(f"   监控异常: {e}")
                time.sleep(2)
        
        print("   监控超时")
        return {'status': 'timeout', 'message': '监控超时'}
    
    def _display_final_result(self, result: Dict[str, Any]):
        """显示最终结果"""
        status = result.get('status', 'unknown')
        
        if status == 'completed':
            print("🎉 索引构建成功！")
            
            # 显示构建结果
            build_result = result.get('result', {})
            if build_result:
                print("   构建详情:")
                print(f"   - 索引文件: {build_result.get('index_files', [])}")
                print(f"   - 特征总数: {build_result.get('total_features', 0)}")
                print(f"   - 构建时间: {build_result.get('build_time', 0)} 秒")
            
        elif status == 'failed':
            print("❌ 索引构建失败")
            error_msg = result.get('error', result.get('message', '未知错误'))
            print(f"   错误信息: {error_msg}")
            
        elif status == 'timeout':
            print("⏰ 监控超时")
            print("   任务可能仍在后台进行，请稍后通过API查询状态")
            
        else:
            print(f"ℹ️  任务状态: {status}")
            print(f"   消息: {result.get('message', '无其他信息')}")
    
    def show_api_examples(self):
        """显示API使用示例"""
        print("\n" + "=" * 80)
        print("📖 API 使用示例")
        print("=" * 80)
        
        examples = [
            {
                "title": "1. 提交索引构建任务",
                "method": "POST",
                "url": "/api/build_index",
                "body": {
                    "dataset_names": ["dataset1", "dataset2"],
                    "distributed": False
                }
            },
            {
                "title": "2. 查询构建进度",
                "method": "GET",
                "url": "/api/progress/{progress_path}",
                "body": None
            },
            {
                "title": "3. 查询任务状态",
                "method": "GET", 
                "url": "/api/build_status/{task_id}",
                "body": None
            },
            {
                "title": "4. 健康检查",
                "method": "GET",
                "url": "/api/health",
                "body": None
            }
        ]
        
        for example in examples:
            print(f"\n{example['title']}")
            print(f"   {example['method']} {self.controller_url}{example['url']}")
            if example['body']:
                print(f"   请求体: {json.dumps(example['body'], indent=4)}")
    
    def interactive_demo(self):
        """交互式演示"""
        print("\n" + "=" * 80)
        print("🎮 交互式演示模式")
        print("=" * 80)
        
        while True:
            print("\n请选择操作:")
            print("1. 完整工作流程演示")
            print("2. 健康检查")
            print("3. 提交构建任务")
            print("4. 查看API示例")
            print("0. 退出")
            
            choice = input("\n请输入选项 (0-4): ").strip()
            
            if choice == '0':
                print("👋 感谢使用！")
                break
            elif choice == '1':
                self.demonstrate_full_workflow()
            elif choice == '2':
                print("\n📋 执行健康检查...")
                self._check_service_health()
            elif choice == '3':
                print("\n📋 提交构建任务...")
                result = self._submit_index_task()
                if result:
                    print("✅ 任务提交成功")
                else:
                    print("❌ 任务提交失败")
            elif choice == '4':
                self.show_api_examples()
            else:
                print("❌ 无效选项，请重新选择")


def main():
    """主函数"""
    demo = IndexBuildingDemo()
    
    print("欢迎使用浮图项目索引构建功能演示！")
    print("请确保以下服务正在运行:")
    print("- Redis 服务器")
    print("- 控制端 (python run.py controller)")
    print("- 计算端 (python run.py compute)")
    
    # 自动演示
    if input("\n是否运行完整演示? (y/n): ").lower().startswith('y'):
        demo.demonstrate_full_workflow()
    
    # 交互模式
    if input("\n是否进入交互模式? (y/n): ").lower().startswith('y'):
        demo.interactive_demo()


if __name__ == '__main__':
    main()
