from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename

upload_bp = Blueprint('upload_images', __name__)

@upload_bp.route('/api/upload_images', methods=['POST'])
def upload_images():
    dataset = request.form.get('dataset')
    if not dataset:
        return jsonify({'error': '缺少数据集参数'}), 400
    files = request.files.getlist('images')
    if not files:
        return jsonify({'error': '未选择图片'}), 400
    dataset_dir = os.path.join('datasets', dataset)
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)
    saved = []
    for file in files:
        filename = secure_filename(file.filename)
        save_path = os.path.join(dataset_dir, filename)
        file.save(save_path)
        saved.append(filename)
    return jsonify({'msg': '上传成功', 'saved': saved, 'dataset': dataset})
