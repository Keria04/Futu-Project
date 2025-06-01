from flask import Blueprint, request, jsonify
from database_module.query import query_one

bp = Blueprint('get_dataset_id', __name__)

@bp.route('/api/get_dataset_id', methods=['POST'])
def get_dataset_id():
    data = request.json
    name = data.get('name')
    if not name:
        return jsonify({'error': '缺少数据集名称'}), 400
    dataset = query_one("datasets", where={"name": name})
    if not dataset:
        return jsonify({'error': '未找到数据集'}), 404
    return jsonify({'id': dataset[0]})
