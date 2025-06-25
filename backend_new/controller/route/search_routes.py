"""
图片搜索相关路由
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os

search_bp = Blueprint('search', __name__)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@search_bp.route('/search', methods=['POST'])
def search_image():
    """
    图片相似度搜索接口
    POST /api/search
    """
    try:
        # 检查是否有文件上传
        if 'query_img' not in request.files:
            return jsonify({
                "error": "未找到查询图片",
                "message": "请上传查询图片"
            }), 400
            
        file = request.files['query_img']
        if file.filename == '':
            return jsonify({
                "error": "未选择文件",
                "message": "请选择要上传的图片文件"
            }), 400
            
        if not allowed_file(file.filename):
            return jsonify({
                "error": "文件格式不支持",
                "message": "支持的格式: PNG, JPG, JPEG, GIF, BMP, WEBP"
            }), 400
        
        # 获取搜索参数
        crop_x = request.form.get('crop_x', 0, type=int)
        crop_y = request.form.get('crop_y', 0, type=int)
        crop_w = request.form.get('crop_w', 0, type=int)
        crop_h = request.form.get('crop_h', 0, type=int)
        dataset_names = request.form.getlist('dataset_names[]')
        
        # 保存上传的文件
        filename = secure_filename(file.filename)
        # TODO: 保存文件到合适的位置
        
        # TODO: 实现图片搜索逻辑
        # 这里应该调用图片搜索服务
          # 暂时返回模拟搜索结果
        mock_results = [
            {
                "image_path": "/show_image/datasets/1/circles_10.jpg",
                "img_url": "/show_image/datasets/1/circles_10.jpg",
                "fname": "circles_10.jpg",
                "idx": 1,
                "similarity": 95.0,
                "dataset": "dataset1"
            },
            {
                "image_path": "/show_image/datasets/1/circles_11.jpg",
                "img_url": "/show_image/datasets/1/circles_11.jpg", 
                "fname": "circles_11.jpg",
                "idx": 2,
                "similarity": 89.0,
                "dataset": "dataset1"
            },
            {
                "image_path": "/show_image/datasets/2/sample_01.jpg",
                "img_url": "/show_image/datasets/2/sample_01.jpg",
                "fname": "sample_01.jpg",
                "idx": 3,
                "similarity": 82.0,
                "dataset": "dataset2"
            }
        ]
        
        response = {
            "results": mock_results,
            "total_found": len(mock_results),
            "search_params": {
                "crop_region": {
                    "x": crop_x,
                    "y": crop_y,
                    "width": crop_w,
                    "height": crop_h
                },
                "datasets": dataset_names
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "error": "搜索失败",
            "message": str(e)
        }), 500
