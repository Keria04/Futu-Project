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
    """获取所有数据集API"""
    try:
        datasets = database_service.get_datasets()
        
        # 添加数据集统计信息
        for dataset in datasets:
            dataset_name = dataset['name']
            images = database_service.get_images_by_dataset(dataset_name)
            dataset['image_count'] = len(images)
            
            # 检查索引状态
            index_path = os.path.join("data/indexes", f"{dataset_name}.index")
            dataset['has_index'] = os.path.exists(index_path)
        
        return jsonify({"datasets": datasets})
        
    except Exception as e:
        return jsonify({"msg": f"获取数据集失败: {str(e)}"}), 500


@dataset_bp.route('/dataset/<dataset_name>/id', methods=['GET'])
def api_get_dataset_id(dataset_name):
    """获取数据集ID API"""
    try:
        dataset_id = database_service.get_dataset_id(dataset_name)
        
        if dataset_id is None:
            return jsonify({"msg": "数据集不存在"}), 404
        
        return jsonify({"dataset_id": dataset_id})
        
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
