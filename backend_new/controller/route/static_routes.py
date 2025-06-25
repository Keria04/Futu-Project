"""
静态资源相关路由
"""
from flask import Blueprint, send_from_directory, jsonify, current_app
import os

static_bp = Blueprint('static', __name__)

@static_bp.route('/show_image/<path:image_path>')
def serve_image(image_path):
    """
    提供图片静态资源接口
    GET /show_image/{image_path}
    """
    try:
        # 构建完整的图片路径
        # 这里假设图片存储在项目根目录下的datasets文件夹中
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        
        # 分解路径
        path_parts = image_path.split('/')
        if len(path_parts) < 2:
            return jsonify({
                "error": "路径无效",
                "message": "图片路径格式不正确"
            }), 400
        
        # 构建实际文件路径
        if path_parts[0] == 'datasets':
            # 处理 /show_image/datasets/1/image.jpg 这样的路径
            directory = os.path.join(base_path, 'datasets', path_parts[1])
            filename = '/'.join(path_parts[2:])
        else:
            # 处理其他路径
            directory = os.path.join(base_path, path_parts[0])
            filename = '/'.join(path_parts[1:])
        
        # 安全检查：确保路径在允许的目录内
        real_directory = os.path.realpath(directory)
        real_base = os.path.realpath(base_path)
        
        if not real_directory.startswith(real_base):
            return jsonify({
                "error": "访问被拒绝",
                "message": "不允许访问此路径"
            }), 403
        
        # 检查文件是否存在
        full_path = os.path.join(directory, filename)
        if not os.path.exists(full_path):
            return jsonify({
                "error": "文件不存在",
                "message": f"未找到图片文件: {image_path}"
            }), 404
        
        # 检查是否为图片文件
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({
                "error": "文件类型不支持",
                "message": "只支持图片文件"
            }), 400
        
        # 返回文件
        return send_from_directory(directory, filename)
        
    except Exception as e:
        return jsonify({
            "error": "获取图片失败",
            "message": str(e)
        }), 500

@static_bp.route('/progress/<path:progress_path>')
def serve_progress(progress_path):
    """
    提供进度文件接口
    GET /progress/{progress_path}
    """
    try:
        # TODO: 实现进度文件的读取逻辑
        # 这里应该从实际的进度文件中读取数据
        
        # 暂时返回模拟进度数据
        import random
        progress = random.uniform(0, 100)
        status = "building" if progress < 100 else "done"
        
        response = {
            "progress": progress,
            "status": status,
            "message": f"进度: {progress:.1f}%",
            "progress_file": progress_path
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "error": "获取进度失败", 
            "message": str(e)
        }), 500
