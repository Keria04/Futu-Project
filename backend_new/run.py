#!/usr/bin/env python3
"""
浮图项目后端启动脚本
"""
import os
import sys
from app import create_app

def main():
    """主函数"""
    # 设置环境变量
    os.environ.setdefault('FLASK_CONFIG', 'development')
    
    # 创建应用
    app = create_app()
    
    # 获取配置
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 19198))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"浮图项目后端服务启动中...")
    print(f"地址: http://{host}:{port}")
    print(f"调试模式: {'开启' if debug else '关闭'}")
    print(f"配置环境: {os.environ.get('FLASK_CONFIG', 'development')}")
    print("-" * 50)
    
    # 启动应用
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
