"""
控制端主应用
负责提供API接口和管理任务调度
"""
import os
import sys
from flask import Flask, jsonify, request
import threading
import time
import logging

# 添加路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from control_service.config import CONTROL_PORT
from control_service.api.search_api import search_bp
from control_service.api.index_api import index_bp
from control_service.api.dataset_api import dataset_bp
from control_service.api.image_api import image_bp
from shared import redis_client


def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    # 添加CORS头部处理（替代flask_cors）
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
      # 注册蓝图
    app.register_blueprint(search_bp)  # search_bp 已经有 url_prefix='/api'
    app.register_blueprint(index_bp)   # index_bp 已经有 url_prefix='/api'
    app.register_blueprint(dataset_bp) # dataset_bp 已经有 url_prefix='/api'
    app.register_blueprint(image_bp)   # image_bp 已经有 url_prefix='/api'
    
    # 健康检查端点
    @app.route('/health')
    def health_check():
        try:
            # 检查Redis连接
            redis_status = redis_client.ping()
            return jsonify({
                'status': 'healthy',
                'redis': 'connected' if redis_status else 'disconnected',
                'timestamp': time.time()
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }), 500
    
    # 根路径
    @app.route('/')
    def index():
        return jsonify({
            'message': '浮图图像搜索系统 - 控制端',
            'version': '1.0.0',
            'endpoints': [
                '/api/search',
                '/api/index',
                '/api/dataset',
                '/api/image',
                '/health'
            ]
        })
    
    return app


def main():
    """主函数"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 启动控制端服务...")
    
    # 检查Redis连接
    try:
        if redis_client.ping():
            print("✓ Redis连接成功")
        else:
            print("⚠ Redis连接失败")
    except Exception as e:
        print(f"⚠ Redis连接检查失败: {e}")
    
    # 创建应用
    app = create_app()
      # 启动服务
    print(f"📊 控制端服务启动于: http://localhost:{CONTROL_PORT}")
    app.run(
        host='0.0.0.0',
        port=CONTROL_PORT,
        debug=False,
        threaded=True
    )


if __name__ == '__main__':
    main()
