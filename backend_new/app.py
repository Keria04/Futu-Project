"""
浮图项目 Flask 后端应用主文件
"""
from flask import Flask, request
import os
from config import config

# 尝试导入 CORS，如果没有安装则跳过
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("警告: flask-cors 未安装，CORS 功能将不可用")

def create_app(config_name=None):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    config_name = config_name or os.environ.get('FLASK_CONFIG', 'default')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
      # 配置CORS
    if CORS_AVAILABLE:
        CORS(app, origins=app.config['CORS_ORIGINS'])
    else:        # 如果没有 CORS 库，手动添加 CORS 头
        @app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Origin', 'http://localhost:19197')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
        
        @app.before_request
        def handle_preflight():
            if request.method == "OPTIONS":
                from flask import make_response
                response = make_response()
                response.headers.add("Access-Control-Allow-Origin", "http://localhost:19197")
                response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
                response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
                return response
    
    # 注册蓝图
    from route.index_routes import index_bp
    from route.search_routes import search_bp
    from route.dataset_routes import dataset_bp
    from route.duplicate_routes import duplicate_bp
    from route.static_routes import static_bp
    
    app.register_blueprint(index_bp, url_prefix='/api')
    app.register_blueprint(search_bp, url_prefix='/api')
    app.register_blueprint(dataset_bp, url_prefix='/api')
    app.register_blueprint(duplicate_bp, url_prefix='/api')
    app.register_blueprint(static_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=19198, debug=True)
