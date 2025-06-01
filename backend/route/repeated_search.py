from flask import Blueprint, request, jsonify
from faiss_module.repeated_search import repeated_search

bp = Blueprint('repeated_search', __name__)

@bp.route('/api/repeated_search', methods=['POST'])
def repeated_search_api():
    data = request.json
    index_id = data.get('index_id')
    threshold = float(data.get('threshold', 95.0))
    deduplicate = bool(data.get('deduplicate', False))
    if not index_id:
        return jsonify({"error": "缺少 index_id"}), 400
    try:
        groups = repeated_search(index_id, threshold, deduplicate)
        # 转为普通int，避免 int64 不能序列化
        groups = [[int(i) for i in group] for group in groups]
        return jsonify({"groups": groups})
    except Exception as e:
        print(f"Error in repeated_search: {e}")
        return jsonify({"error": str(e)}), 500
