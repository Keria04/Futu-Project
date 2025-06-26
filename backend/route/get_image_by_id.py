from flask import Blueprint, jsonify
from database_module.query import query_one, query_multi
import os

get_image_by_id_bp = Blueprint('get_image_by_id', __name__)

@get_image_by_id_bp.route('/api/get_image_by_id/<int:image_id>', methods=['GET'])
def get_image_by_id(image_id):
    """
    根据图片ID获取图片信息
    :param image_id: 图片ID
    :return: 包含图片路径和数据集信息的JSON响应
    """
    try:
        # 查询图片信息，联接数据集表获取数据集名称
        image_info = query_one(
            table="images i JOIN datasets d ON i.dataset_id = d.id",
            columns="i.id, i.image_path, i.dataset_id, d.name as dataset_name",
            where={"i.id": image_id}
        )
        
        if not image_info:
            return jsonify({"error": "图片不存在"}), 404
            
        # 解析查询结果
        img_id, image_path, dataset_id, dataset_name = image_info
        
        # 构造图片URL
        # 假设图片路径存储的是相对于数据集目录的路径
        filename = os.path.basename(image_path)
        image_url = f"/show_image/{dataset_name}/{filename}"
        
        return jsonify({
            "id": img_id,
            "image_path": image_path,
            "dataset_id": dataset_id,
            "dataset_name": dataset_name,
            "image_url": image_url,
            "filename": filename
        })
        
    except Exception as e:
        print(f"获取图片信息失败: {e}")
        return jsonify({"error": "获取图片信息失败"}), 500

@get_image_by_id_bp.route('/api/get_images_by_ids', methods=['POST'])
def get_images_by_ids():
    """
    根据多个图片ID批量获取图片信息
    用于重复检测结果的展示
    """
    try:
        from flask import request
        data = request.json
        image_ids = data.get('image_ids', [])
        
        if not image_ids:
            return jsonify({"error": "缺少图片ID列表"}), 400
            
        # 构造IN查询条件
        placeholders = ','.join(['?' for _ in image_ids])
        query = f"""
            SELECT i.id, i.image_path, i.dataset_id, d.name as dataset_name
            FROM images i 
            JOIN datasets d ON i.dataset_id = d.id 
            WHERE i.id IN ({placeholders})
        """
        
        # 执行查询
        from database_module.database import Database
        db = Database()
        cursor = db.execute(query, image_ids)
        results = cursor.fetchall()
        
        if not results:
            return jsonify({"images": []})
            
        # 格式化结果
        images = []
        for img_id, image_path, dataset_id, dataset_name in results:
            filename = os.path.basename(image_path)
            image_url = f"/show_image/{dataset_name}/{filename}"
            
            images.append({
                "id": img_id,
                "image_path": image_path,
                "dataset_id": dataset_id,
                "dataset_name": dataset_name,
                "image_url": image_url,
                "filename": filename
            })
            
        return jsonify({"images": images})
        
    except Exception as e:
        print(f"批量获取图片信息失败: {e}")
        return jsonify({"error": "批量获取图片信息失败"}), 500

@get_image_by_id_bp.route('/api/get_duplicate_groups_with_images', methods=['POST'])
def get_duplicate_groups_with_images():
    """
    获取重复组的详细图片信息
    整合重复检测和图片信息获取的功能
    """
    try:
        from flask import request
        from faiss_module.repeated_search import repeated_search
        
        data = request.json
        index_id = data.get('index_id')
        threshold = float(data.get('threshold', 95.0))
        deduplicate = bool(data.get('deduplicate', False))
        
        if not index_id:
            return jsonify({"error": "缺少 index_id"}), 400
            
        # 执行重复检测
        groups = repeated_search(index_id, threshold, deduplicate)
        groups = [[int(i) for i in group] for group in groups]
        
        # 获取所有涉及的图片ID
        all_image_ids = []
        for group in groups:
            all_image_ids.extend(group)
            
        if not all_image_ids:
            return jsonify({"groups": []})
            
        # 批量获取图片信息
        placeholders = ','.join(['?' for _ in all_image_ids])
        query = f"""
            SELECT i.id, i.image_path, i.dataset_id, d.name as dataset_name
            FROM images i 
            JOIN datasets d ON i.dataset_id = d.id 
            WHERE i.id IN ({placeholders})
        """
        
        from database_module.database import Database
        db = Database()
        cursor = db.execute(query, all_image_ids)
        results = cursor.fetchall()
        
        # 创建ID到图片信息的映射
        image_info_map = {}
        for img_id, image_path, dataset_id, dataset_name in results:
            filename = os.path.basename(image_path)
            image_url = f"/show_image/{dataset_name}/{filename}"
            
            image_info_map[img_id] = {
                "id": img_id,
                "image_path": image_path,
                "dataset_id": dataset_id,
                "dataset_name": dataset_name,
                "image_url": image_url,
                "filename": filename
            }
            
        # 为每个组添加详细的图片信息
        groups_with_images = []
        for group in groups:
            group_images = []
            for img_id in group:
                if img_id in image_info_map:
                    group_images.append(image_info_map[img_id])
                    
            if group_images:  # 只添加有图片信息的组
                groups_with_images.append({
                    "image_ids": group,
                    "images": group_images
                })
                
        return jsonify({"groups": groups_with_images})
        
    except Exception as e:
        print(f"获取重复组详细信息失败: {e}")
        return jsonify({"error": "获取重复组详细信息失败"}), 500
