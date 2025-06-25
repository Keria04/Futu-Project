"""
数据集管理相关路由
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import os

dataset_bp = Blueprint('dataset', __name__)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@dataset_bp.route('/datasets', methods=['GET'])
def get_datasets():
    """
    获取所有数据集列表接口
    GET /api/datasets
    """
    try:
        # TODO: 从数据库获取真实的数据集信息
        # 这里应该调用数据集管理服务
          # 暂时返回模拟数据
        mock_datasets = [
            {
                "id": 1,
                "name": "dataset1",
                "description": "第一个测试数据集",
                "image_count": 150,
                "created_at": "2025-01-01T00:00:00Z",
                "first_image_url": "/show_image/datasets/1/circles_10.jpg",
                "sample_images": [
                    "/show_image/datasets/1/circles_10.jpg",
                    "/show_image/datasets/1/circles_11.jpg",
                    "/show_image/datasets/1/circles_12.jpg"
                ]
            },
            {
                "id": 2,
                "name": "dataset2", 
                "description": "第二个测试数据集",
                "image_count": 89,
                "created_at": "2025-01-15T10:30:00Z",
                "first_image_url": "/show_image/datasets/2/sample_01.jpg",
                "sample_images": [
                    "/show_image/datasets/2/sample_01.jpg",
                    "/show_image/datasets/2/sample_02.jpg"
                ]
            },
            {
                "id": 3,
                "name": "dataset3",
                "description": "第三个测试数据集", 
                "image_count": 234,
                "created_at": "2025-02-01T14:20:00Z",
                "first_image_url": "/show_image/datasets/3/image_001.jpg",
                "sample_images": [
                    "/show_image/datasets/3/image_001.jpg",
                    "/show_image/datasets/3/image_002.jpg",
                    "/show_image/datasets/3/image_003.jpg"
                ]
            }
        ]
        
        response = {
            "datasets": mock_datasets,
            "total_count": len(mock_datasets)
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "error": "获取数据集列表失败",
            "message": str(e)
        }), 500

@dataset_bp.route('/get_dataset_id', methods=['POST'])
def get_dataset_id():
    """
    根据数据集名称获取ID接口
    POST /api/get_dataset_id
    """
    try:
        data = request.get_json()
        dataset_name = data.get('name')
        
        if not dataset_name:
            return jsonify({
                "error": "缺少数据集名称",
                "message": "请提供数据集名称"
            }), 400
        
        # TODO: 从数据库查询真实的数据集ID
        # 这里应该调用数据集查询服务
        
        # 暂时返回模拟数据
        mock_id_mapping = {
            "dataset1": 1,
            "dataset2": 2, 
            "dataset3": 3
        }
        
        dataset_id = mock_id_mapping.get(dataset_name)
        if dataset_id is None:
            return jsonify({
                "error": "数据集不存在",
                "message": f"未找到名为 '{dataset_name}' 的数据集"
            }), 404
        
        response = {
            "dataset_id": dataset_id,
            "dataset_name": dataset_name
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "error": "获取数据集ID失败",
            "message": str(e)
        }), 500

@dataset_bp.route('/upload_images', methods=['POST'])
def upload_images():
    """
    上传图片到数据集接口
    POST /api/upload_images
    """
    try:
        # 检查是否有文件上传
        if 'images' not in request.files:
            return jsonify({
                "error": "未找到图片文件",
                "message": "请选择要上传的图片文件"
            }), 400
        
        files = request.files.getlist('images')
        dataset_id = request.form.get('dataset')
        
        if not dataset_id:
            return jsonify({
                "error": "缺少数据集ID",
                "message": "请指定目标数据集"
            }), 400
        
        if not files or all(f.filename == '' for f in files):
            return jsonify({
                "error": "未选择文件",
                "message": "请选择要上传的图片文件"
            }), 400
        
        uploaded_count = 0
        failed_files = []
        
        for file in files:
            if file.filename == '':
                continue
                
            if not allowed_file(file.filename):
                failed_files.append({
                    "filename": file.filename,
                    "reason": "文件格式不支持"
                })
                continue
            
            # 保存文件
            filename = secure_filename(file.filename)
            # TODO: 保存文件到指定数据集目录
            # TODO: 将文件信息保存到数据库
            
            uploaded_count += 1
        
        response = {
            "success": True,
            "uploaded_count": uploaded_count,
            "failed_count": len(failed_files),
            "message": f"成功上传{uploaded_count}张图片",
            "failed_files": failed_files
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "error": "上传图片失败",
            "message": str(e)
        }), 500
