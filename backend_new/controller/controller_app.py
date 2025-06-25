"""
控制端Flask应用 - 负责API接口、数据库操作和FAISS索引管理
"""
from flask import Flask, request, jsonify
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from redis_client.redis_client import init_redis_client, get_redis_client

# 尝试导入 CORS，如果没有安装则跳过
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("警告: flask-cors 未安装，CORS 功能将不可用")


def create_controller_app(config_name=None):
    """控制端应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    config_name = config_name or os.environ.get('FLASK_CONFIG', 'default')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 初始化Redis客户端
    try:
        init_redis_client()
        app.logger.info("Redis客户端初始化成功")
    except Exception as e:
        app.logger.error(f"Redis客户端初始化失败: {e}")
        # 可以选择是否继续运行
        if not app.config.get('REDIS_OPTIONAL', False):
            raise
    
    # 配置CORS
    if CORS_AVAILABLE:
        CORS(app, origins=app.config['CORS_ORIGINS'])
    else:
        # 如果没有 CORS 库，手动添加 CORS 头
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
    from .route.index_routes import index_bp
    from .route.search_routes import search_bp
    from .route.dataset_routes import dataset_bp
    from .route.duplicate_routes import duplicate_bp
    from .route.static_routes import static_bp
    
    app.register_blueprint(index_bp, url_prefix='/api')
    app.register_blueprint(search_bp, url_prefix='/api')
    app.register_blueprint(dataset_bp, url_prefix='/api')
    app.register_blueprint(duplicate_bp, url_prefix='/api')
    app.register_blueprint(static_bp)
    
    # 添加健康检查端点
    @app.route('/health')
    def health_check():
        """健康检查端点"""
        redis_client = get_redis_client()
        
        return {
            'status': 'healthy',
            'service': 'controller',
            'redis_connected': redis_client.is_connected() if redis_client else False,
            'timestamp': __import__('time').time()
        }
    
    # 添加计算端通信接口
    @app.route('/api/compute/feature_extraction', methods=['POST'])
    def request_feature_extraction():
        """请求特征提取"""
        from flask import jsonify
        
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': '缺少请求数据'}), 400
            
            redis_client = get_redis_client()
            if not redis_client.is_connected():
                return jsonify({'error': 'Redis连接失败'}), 503
            
            # 发布任务到计算端
            task_data = {
                'task_type': 'single_feature_extraction',
                'image_path': data.get('image_path')
            }
            
            task_id = redis_client.publish_task('compute:feature_extraction', task_data)
            
            # 等待结果
            result = redis_client.get_result(task_id, timeout=30)
            
            if result is None:
                return jsonify({'error': '任务超时'}), 408
            
            # 清理结果
            redis_client.delete_result(task_id)
            
            if result.get('success'):
                return jsonify({
                    'success': True,
                    'features': result['result'],
                    'task_id': task_id
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', '未知错误')
                }), 500
                
        except Exception as e:
            app.logger.error(f"特征提取请求失败: {e}")
            return jsonify({'error': '内部服务器错误'}), 500
    
    @app.route('/api/compute/batch_feature_extraction', methods=['POST'])
    def request_batch_feature_extraction():
        """请求批量特征提取"""
        from flask import jsonify
        
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': '缺少请求数据'}), 400
            
            redis_client = get_redis_client()
            if not redis_client.is_connected():
                return jsonify({'error': 'Redis连接失败'}), 503
            
            # 发布任务到计算端  
            task_data = {
                'task_type': 'batch_feature_extraction',
                'image_paths': data.get('image_paths', [])
            }
            
            task_id = redis_client.publish_task('compute:batch_feature_extraction', task_data)
            
            # 等待结果
            timeout = data.get('timeout', 60)  # 批量处理需要更长时间
            result = redis_client.get_result(task_id, timeout=timeout)
            
            if result is None:
                return jsonify({'error': '任务超时'}), 408
            
            # 清理结果
            redis_client.delete_result(task_id)
            
            if result.get('success'):
                return jsonify({
                    'success': True,
                    'results': result['result'],
                    'task_id': task_id
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', '未知错误')
                }), 500
                
        except Exception as e:
            app.logger.error(f"批量特征提取请求失败: {e}")
            return jsonify({'error': '内部服务器错误'}), 500
    
    @app.route('/api/compute/model_info', methods=['GET'])
    def request_model_info():
        """请求模型信息"""
        try:
            redis_client = get_redis_client()
            if not redis_client.is_connected():
                return jsonify({'error': 'Redis连接失败'}), 503
            
            # 发布任务到计算端
            task_data = {
                'task_type': 'model_info'
            }
            
            task_id = redis_client.publish_task('compute:model_info', task_data)
            
            # 等待结果
            result = redis_client.get_result(task_id, timeout=10)
            
            if result is None:
                return jsonify({'error': '任务超时'}), 408
            
            # 清理结果
            redis_client.delete_result(task_id)
            
            if result.get('success'):
                return jsonify({
                    'success': True,
                    'model_info': result['result'],
                    'task_id': task_id
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', '未知错误')
                }), 500
                
        except Exception as e:
            app.logger.error(f"获取模型信息失败: {e}")
            return jsonify({'error': '内部服务器错误'}), 500
    
    @app.route('/api/compute/update_model', methods=['POST'])
    def request_update_model():
        """请求更新模型配置"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': '缺少请求数据'}), 400
            
            redis_client = get_redis_client()
            if not redis_client.is_connected():
                return jsonify({'error': 'Redis连接失败'}), 503
            
            # 发布任务到计算端
            task_data = {
                'task_type': 'update_model',
                'model_type': data.get('model_type'),
                'device': data.get('device'),
                'input_size': data.get('input_size'),
                'batch_size': data.get('batch_size'),
                'pretrain': data.get('pretrain')
            }
            
            task_id = redis_client.publish_task('compute:update_model', task_data)
            
            # 等待结果
            timeout = data.get('timeout', 30)
            result = redis_client.get_result(task_id, timeout=timeout)
            
            if result is None:
                return jsonify({'error': '任务超时'}), 408
            
            # 清理结果
            redis_client.delete_result(task_id)
            
            if result.get('success'):
                return jsonify({
                    'success': True,
                    'result': result['result'],
                    'task_id': task_id
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', '未知错误')
                }), 500
                
        except Exception as e:
            app.logger.error(f"更新模型配置失败: {e}")
            return jsonify({'error': '内部服务器错误'}), 500
    
    @app.route('/api/compute/health', methods=['GET'])
    def request_compute_health():
        """请求计算端健康检查"""
        try:
            redis_client = get_redis_client()
            if not redis_client.is_connected():
                return jsonify({'error': 'Redis连接失败'}), 503
            
            # 发布任务到计算端
            task_data = {
                'task_type': 'health_check'
            }
            
            task_id = redis_client.publish_task('compute:health_check', task_data)
            
            # 等待结果
            result = redis_client.get_result(task_id, timeout=10)
            
            if result is None:
                return jsonify({'error': '计算端无响应'}), 408
            
            # 清理结果
            redis_client.delete_result(task_id)
            
            if result.get('success'):
                return jsonify({
                    'success': True,
                    'health_info': result['result'],
                    'task_id': task_id
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', '未知错误')
                }), 500
                
        except Exception as e:
            app.logger.error(f"计算端健康检查失败: {e}")
            return jsonify({'error': '内部服务器错误'}), 500
    
    return app


if __name__ == '__main__':
    app = create_controller_app()
    app.run(host='0.0.0.0', port=19198, debug=True)
