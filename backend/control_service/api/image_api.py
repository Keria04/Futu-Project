"""
图片相关API路由
"""
import sys
import os
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename

# 添加路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

image_bp = Blueprint('image', __name__, url_prefix='/api')


@image_bp.route('/image/<dataset_name>/<int:image_id>')
def api_get_image_by_dataset_and_id(dataset_name, image_id):
    """根据数据集名称和图片ID获取图片文件"""
    try:
        # 从数据库获取图片信息
        from control_service.services import database_service
        image_info = database_service.get_image_by_id(image_id)
        
        if not image_info or image_info.get('dataset') != dataset_name:
            return jsonify({"msg": "图片不存在"}), 404
        
        # 构建图片路径
        image_path = os.path.join("datasets", dataset_name, image_info['filename'])
        
        if os.path.exists(image_path):
            return send_file(image_path)
        else:
            return jsonify({"msg": "图片文件不存在"}), 404
        
    except Exception as e:
        return jsonify({"msg": f"获取图片失败: {str(e)}"}), 500


@image_bp.route('/image/<path:filename>')
def api_get_image(filename):
    """获取图片文件API"""
    try:
        # 安全检查文件名
        safe_filename = secure_filename(filename)
        
        # 在datasets目录中查找图片
        for dataset_dir in os.listdir("datasets"):
            dataset_path = os.path.join("datasets", dataset_dir)
            if os.path.isdir(dataset_path):
                image_path = os.path.join(dataset_path, safe_filename)
                if os.path.exists(image_path):
                    return send_file(image_path)
        
        # 在uploads目录中查找
        upload_path = os.path.join("data/uploads", safe_filename)
        if os.path.exists(upload_path):
            return send_file(upload_path)
        
        return jsonify({"msg": "图片文件不存在"}), 404
        
    except Exception as e:
        return jsonify({"msg": f"获取图片失败: {str(e)}"}), 500


@image_bp.route('/upload', methods=['POST'])
def api_upload_image():
    """上传图片API"""
    try:
        if 'file' not in request.files:
            return jsonify({"msg": "没有文件"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"msg": "没有选择文件"}), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        upload_dir = "data/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        return jsonify({
            "msg": "文件上传成功",
            "filename": filename,
            "url": f"/api/image/{filename}"
        })
        
    except Exception as e:
        return jsonify({"msg": f"上传失败: {str(e)}"}), 500
