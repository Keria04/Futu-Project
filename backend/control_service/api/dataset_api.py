"""
数据集管理API路由
"""
import sys
import os
from flask import Blueprint, request, jsonify

# 添加路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from control_service.services import database_service

dataset_bp = Blueprint('dataset', __name__, url_prefix='/api')


@dataset_bp.route('/datasets', methods=['GET'])
def api_get_datasets():
    """获取所有数据集API - 自动扫描datasets目录"""
    try:
        datasets = []
        datasets_dir = "datasets"
        
        if os.path.exists(datasets_dir):
            for folder_name in os.listdir(datasets_dir):
                folder_path = os.path.join(datasets_dir, folder_name)
                if os.path.isdir(folder_path):
                    # 统计图片数量
                    image_count = 0
                    for file in os.listdir(folder_path):
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                            image_count += 1
                    
                    dataset_info = {
                        "id": folder_name,
                        "name": f"Dataset{folder_name}",
                        "folder": folder_name,
                        "image_count": image_count,
                        "description": f"数据集 {folder_name}，包含 {image_count} 张图片"
                    }
                    datasets.append(dataset_info)
        
        return jsonify({"datasets": datasets})
        
    except Exception as e:
        return jsonify({"msg": f"获取数据集失败: {str(e)}"}), 500


@dataset_bp.route('/get_dataset_id', methods=['POST'])
def api_get_dataset_id():
    """获取数据集ID API"""
    try:
        data = request.get_json()
        dataset_name = data.get('name')
        
        if not dataset_name:
            return jsonify({"msg": "缺少数据集名称"}), 400
        
        dataset_id = database_service.get_dataset_id(dataset_name)
        
        if dataset_id is None:
            return jsonify({"msg": "数据集不存在"}), 404
        
        return jsonify({
            "id": dataset_id,
            "name": dataset_name
        })
        
    except Exception as e:
        return jsonify({"msg": f"获取数据集ID失败: {str(e)}"}), 500


@dataset_bp.route('/dataset/<dataset_name>/images', methods=['GET'])
def api_get_dataset_images(dataset_name):
    """获取数据集图片列表API"""
    try:
        images = database_service.get_images_by_dataset(dataset_name)
        return jsonify({"images": images})
        
    except Exception as e:
        return jsonify({"msg": f"获取数据集图片失败: {str(e)}"}), 500


@dataset_bp.route('/image/<int:image_id>', methods=['GET'])
def api_get_image_info(image_id):
    """获取图片信息API"""
    try:
        image_info = database_service.get_image_by_id(image_id)
        
        if image_info is None:
            return jsonify({"msg": "图片不存在"}), 404
        
        return jsonify({"image": image_info})
        
    except Exception as e:
        return jsonify({"msg": f"获取图片信息失败: {str(e)}"}), 500
