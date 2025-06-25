#!/usr/bin/env python3
"""
浮图项目服务管理脚本
"""
import os
import sys
import argparse
import subprocess
import signal
import time
import json
import requests
from typing import Dict, List, Optional


class ServiceManager:
    """服务管理器"""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.config = {
            'controller': {
                'script': 'run.py',
                'args': ['controller'],
                'health_url': 'http://localhost:19198/health'
            },
            'compute': {
                'script': 'run.py', 
                'args': ['compute'],
                'health_url': None
            },
            'redis': {
                'script': None,
                'command': 'redis-server',
                'health_url': None
            }
        }
    
    def start_service(self, service_name: str, **kwargs) -> bool:
        """启动单个服务"""
        if service_name in self.processes:
            print(f"服务 {service_name} 已在运行中")
            return True
        
        config = self.config.get(service_name)
        if not config:
            print(f"未知服务: {service_name}")
            return False
        
        try:
            if service_name == 'redis':
                # 启动Redis服务
                cmd = ['redis-server']
                if os.name == 'nt':  # Windows
                    cmd = ['redis-server.exe']
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
                )
            else:
                # 启动Python服务
                cmd = [sys.executable, config['script']] + config['args']
                
                # 添加额外参数
                for key, value in kwargs.items():
                    if key == 'host':
                        cmd.extend(['--host', value])
                    elif key == 'port':
                        cmd.extend(['--port', str(value)])
                    elif key == 'workers':
                        cmd.extend(['--workers', str(value)])
                    elif key == 'debug' and value:
                        cmd.append('--debug')
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
                )
            
            self.processes[service_name] = process
            print(f"服务 {service_name} 启动成功，PID: {process.pid}")
            return True
            
        except Exception as e:
            print(f"启动服务 {service_name} 失败: {e}")
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """停止单个服务"""
        if service_name not in self.processes:
            print(f"服务 {service_name} 未在运行")
            return True
        
        try:
            process = self.processes[service_name]
            
            if os.name == 'nt':  # Windows
                process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                process.terminate()
            
            # 等待进程结束
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            del self.processes[service_name]
            print(f"服务 {service_name} 已停止")
            return True
            
        except Exception as e:
            print(f"停止服务 {service_name} 失败: {e}")
            return False
    
    def restart_service(self, service_name: str, **kwargs) -> bool:
        """重启单个服务"""
        print(f"重启服务 {service_name}...")
        self.stop_service(service_name)
        time.sleep(2)
        return self.start_service(service_name, **kwargs)
    
    def check_service(self, service_name: str) -> Dict[str, any]:
        """检查服务状态"""
        result = {
            'name': service_name,
            'running': False,
            'pid': None,
            'healthy': False,
            'health_info': None
        }
        
        # 检查进程是否运行
        if service_name in self.processes:
            process = self.processes[service_name]
            if process.poll() is None:  # 进程仍在运行
                result['running'] = True
                result['pid'] = process.pid
        
        # 检查健康状态
        config = self.config.get(service_name)
        if config and config.get('health_url'):
            try:
                response = requests.get(config['health_url'], timeout=5)
                if response.status_code == 200:
                    result['healthy'] = True
                    result['health_info'] = response.json()
            except:
                pass
        
        return result
    
    def status(self) -> List[Dict[str, any]]:
        """获取所有服务状态"""
        return [self.check_service(name) for name in self.config.keys()]
    
    def stop_all(self):
        """停止所有服务"""
        print("停止所有服务...")
        for service_name in list(self.processes.keys()):
            self.stop_service(service_name)
    
    def start_all(self, **kwargs):
        """启动所有服务"""
        print("启动所有服务...")
        
        # 先启动Redis
        if 'redis' in self.config:
            self.start_service('redis')
            time.sleep(2)
        
        # 启动计算端
        if 'compute' in self.config:
            self.start_service('compute', **kwargs)
            time.sleep(2)
        
        # 启动控制端
        if 'controller' in self.config:
            self.start_service('controller', **kwargs)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='浮图项目服务管理')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # start命令
    start_parser = subparsers.add_parser('start', help='启动服务')
    start_parser.add_argument('service', nargs='?', choices=['controller', 'compute', 'redis', 'all'], 
                             default='all', help='要启动的服务')
    start_parser.add_argument('--host', default='0.0.0.0', help='控制端主机地址')
    start_parser.add_argument('--port', type=int, default=19198, help='控制端端口')
    start_parser.add_argument('--workers', type=int, default=2, help='计算端工作线程数')
    start_parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    # stop命令
    stop_parser = subparsers.add_parser('stop', help='停止服务')
    stop_parser.add_argument('service', nargs='?', choices=['controller', 'compute', 'redis', 'all'],
                            default='all', help='要停止的服务')
    
    # restart命令
    restart_parser = subparsers.add_parser('restart', help='重启服务')
    restart_parser.add_argument('service', nargs='?', choices=['controller', 'compute', 'redis', 'all'],
                               default='all', help='要重启的服务')
    restart_parser.add_argument('--host', default='0.0.0.0', help='控制端主机地址')
    restart_parser.add_argument('--port', type=int, default=19198, help='控制端端口')
    restart_parser.add_argument('--workers', type=int, default=2, help='计算端工作线程数')
    restart_parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    # status命令
    status_parser = subparsers.add_parser('status', help='查看服务状态')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = ServiceManager()
    
    try:
        if args.command == 'start':
            kwargs = {
                'host': args.host,
                'port': args.port,
                'workers': args.workers,
                'debug': args.debug
            }
            
            if args.service == 'all':
                manager.start_all(**kwargs)
            else:
                manager.start_service(args.service, **kwargs)
        
        elif args.command == 'stop':
            if args.service == 'all':
                manager.stop_all()
            else:
                manager.stop_service(args.service)
        
        elif args.command == 'restart':
            kwargs = {
                'host': args.host,
                'port': args.port,
                'workers': args.workers,
                'debug': args.debug
            }
            
            if args.service == 'all':
                manager.stop_all()
                time.sleep(2)
                manager.start_all(**kwargs)
            else:
                manager.restart_service(args.service, **kwargs)
        
        elif args.command == 'status':
            status_list = manager.status()
            print("\n服务状态:")
            print("-" * 60)
            for status in status_list:
                print(f"服务: {status['name']}")
                print(f"  运行中: {status['running']}")
                print(f"  PID: {status['pid']}")
                print(f"  健康: {status['healthy']}")
                if status['health_info']:
                    print(f"  健康信息: {status['health_info']}")
                print()
        
        # 如果启动了服务，保持运行状态
        if args.command in ['start', 'restart'] and manager.processes:
            print("服务运行中，按 Ctrl+C 停止所有服务...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n接收到停止信号")
                manager.stop_all()
    
    except Exception as e:
        print(f"操作失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
