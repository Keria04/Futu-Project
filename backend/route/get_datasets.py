import os
from flask import Blueprint, jsonify
from urllib.parse import quote  # 新增

# 创建蓝图
bp = Blueprint('get_datasets', __name__, url_prefix='/api')

@bp.route('/datasets', methods=['GET'])
def get_datasets():
    """
    获取所有可用的数据集
    通过检查datasets目录下的文件夹来判断
    """
    try:
        datasets_dir = 'datasets'
        datasets = []
        
        # 检查datasets目录是否存在
        if not os.path.exists(datasets_dir):
            return jsonify({'datasets': []})
        
        # 遍历datasets目录下的所有文件夹
        for item in os.listdir(datasets_dir):
            item_path = os.path.join(datasets_dir, item)
            
            # 只包含目录，不包含文件
            if os.path.isdir(item_path):
                # 统计该数据集中的图片数量
                image_count = 0
                image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
                image_files = []
                if os.path.exists(item_path):
                    for file in os.listdir(item_path):
                        if any(file.lower().endswith(ext) for ext in image_extensions):
                            image_count += 1
                            image_files.append(file)
                
                # 查找第一张图片并URL编码
                first_image_url = None
                if image_files:
                    first_image_url = f"/datasets/{quote(item)}/{quote(image_files[0])}"
                
                datasets.append({
                    'id': item,
                    'name': item,  # 只用目录名作为卡片名称
                    'folder': item,
                    'image_count': image_count,
                    'description': f'{item}，包含 {image_count} 张图片',
                    'first_image_url': first_image_url
                })
        
        # 不再对id做int排序，直接按名称排序，支持任意英文/数字目录名
        datasets.sort(key=lambda x: x['id'])
        
        return jsonify({'datasets': datasets})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
