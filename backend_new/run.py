#!/usr/bin/env python3
"""
浮图项目后端启动脚本
支持分离式架构：控制端、计算端或同时启动
"""
import os
import sys
import argparse
import threading
import time
import logging
from typing import Optional

def setup_logging(level=logging.INFO):
    """设置日志"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('futu_backend.log', encoding='utf-8')
        ]
    )

def start_controller(host: str = '0.0.0.0', port: int = 19198, debug: bool = True):
    """启动控制端"""
    print(f"启动控制端服务...")
    print(f"地址: http://{host}:{port}")
    
    try:
        from controller.controller_app import create_controller_app
        app = create_controller_app()
        app.run(host=host, port=port, debug=debug, threaded=True)
    except ImportError as e:
        print(f"控制端导入失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"控制端启动失败: {e}")
        sys.exit(1)

def start_compute_server(workers: int = 2):
    """启动计算端"""
    print(f"启动计算端服务，工作线程数: {workers}")
    
    try:
        from compute_server.compute_server import ComputeServer
        from redis_client.redis_client import RedisConfig
        
        # 创建配置
        redis_config = RedisConfig()
        
        # 使用默认配置创建计算端服务器
        server = ComputeServer(redis_config, None)  # 使用None让它使用默认配置
        server.start(num_workers=workers)
        
        print("计算端服务器运行中，按 Ctrl+C 停止...")
        
        try:
            while server.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n接收到停止信号")
        finally:
            server.stop()
            
    except ImportError as e:
        print(f"计算端导入失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"计算端启动失败: {e}")
        sys.exit(1)

def start_both(host: str = '0.0.0.0', port: int = 19198, debug: bool = True, workers: int = 2):
    """同时启动控制端和计算端"""
    print(f"同时启动控制端和计算端...")
    
    # 启动计算端线程
    compute_thread = threading.Thread(
        target=start_compute_server,
        args=(workers,),
        name="ComputeServerThread",
        daemon=True
    )
    compute_thread.start()
    
    # 等待计算端启动
    time.sleep(2)
    
    # 启动控制端（在主线程中）
    start_controller(host, port, debug)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='浮图项目后端启动脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
启动模式：
  controller  只启动控制端（Flask API、数据库、FAISS）
  compute     只启动计算端（模型计算服务）  
  both        同时启动控制端和计算端（默认）
  
示例：
  python run.py controller --host 0.0.0.0 --port 19198
  python run.py compute --workers 4
  python run.py both --host 0.0.0.0 --port 19198 --workers 2
        '''
    )
    
    parser.add_argument(
        'mode',
        choices=['controller', 'compute', 'both'],
        default='both',
        nargs='?',
        help='启动模式（默认: both）'
    )
    
    parser.add_argument(
        '--host',
        default=os.environ.get('FLASK_HOST', '0.0.0.0'),
        help='控制端主机地址（默认: 0.0.0.0）'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=int(os.environ.get('FLASK_PORT', 19198)),
        help='控制端端口（默认: 19198）'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        default=os.environ.get('FLASK_DEBUG', 'True').lower() == 'true',
        help='启用调试模式'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=int(os.environ.get('COMPUTE_WORKERS', 2)),
        help='计算端工作线程数（默认: 2）'
    )
    
    parser.add_argument(
        '--config',
        default=os.environ.get('FLASK_CONFIG', 'development'),
        help='配置环境（默认: development）'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别（默认: INFO）'
    )
    
    args = parser.parse_args()
    
    # 设置环境变量
    os.environ.setdefault('FLASK_CONFIG', args.config)
    
    # 设置日志
    log_level = getattr(logging, args.log_level)
    setup_logging(log_level)
    
    print("=" * 60)
    print("浮图项目后端服务")
    print("=" * 60)
    print(f"启动模式: {args.mode}")
    print(f"配置环境: {args.config}")
    print(f"日志级别: {args.log_level}")
    
    if args.mode in ['controller', 'both']:
        print(f"控制端地址: http://{args.host}:{args.port}")
        print(f"调试模式: {'开启' if args.debug else '关闭'}")
    
    if args.mode in ['compute', 'both']:
        print(f"计算端工作线程: {args.workers}")
    
    print("-" * 60)
    
    # 根据模式启动服务
    try:
        if args.mode == 'controller':
            start_controller(args.host, args.port, args.debug)
        elif args.mode == 'compute':
            start_compute_server(args.workers)
        elif args.mode == 'both':
            start_both(args.host, args.port, args.debug, args.workers)
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
