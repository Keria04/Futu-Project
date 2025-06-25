"""
搜索API路由
"""
import sys
import os
from flask import Blueprint, request, jsonify
from PIL import Image
import io

# 添加路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from control_service.services import search_service

search_bp = Blueprint('search', __name__, url_prefix='/api')


@search_bp.route('/search', methods=['POST'])
def api_search():
    """图像搜索API"""
    try:
        # 获取数据集名称
        dataset_names = request.form.getlist('dataset_names[]')
        if not dataset_names:
            dataset_name = request.form.get('dataset_name')
            if dataset_name:
                dataset_names = [dataset_name]
        
        # 获取查询图片
        file = request.files.get('query_img')
        if not file or not file.filename:
            return jsonify({"msg": "未上传图片"}), 400
        
        # 获取裁剪参数
        try:
            x = int(request.form.get('crop_x', 0))
            y = int(request.form.get('crop_y', 0))
            w = int(request.form.get('crop_w', 0))
            h = int(request.form.get('crop_h', 0))
            crop_info = (x, y, w, h) if any([x, y, w, h]) else None
        except Exception:
            crop_info = None
        
        if not dataset_names or not any(dataset_names):
            return jsonify({"msg": "缺少数据集名称"}), 400
        
        # 加载图片
        query_image = Image.open(io.BytesIO(file.read()))
        
        # 执行搜索
        results = search_service.search_image(query_image, dataset_names, crop_info)
        
        return jsonify({"results": results})
        
    except Exception as e:
        return jsonify({"msg": f"搜索失败: {str(e)}"}), 500


@search_bp.route('/repeated_search', methods=['POST'])
def api_repeated_search():
    """重复图像搜索API"""
    try:
        data = request.get_json()
        index_id = data.get('index_id')
        threshold = data.get('threshold', 95)
        deduplicate = data.get('deduplicate', False)
        
        if index_id is None:
            return jsonify({"msg": "缺少数据集ID"}), 400
        
        # 执行重复图像搜索
        results = search_service.search_repeated_images(
            index_id=index_id,
            threshold=threshold,
            deduplicate=deduplicate
        )
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"msg": f"重复图像搜索失败: {str(e)}"}), 500
