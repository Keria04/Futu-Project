from flask import Blueprint, request, jsonify
from search_module.search import search_image

search_bp = Blueprint('search', __name__)

@search_bp.route('/api/search', methods=['POST'])
def api_search():
    # 查询个数
    top_k = int(request.form.get('top_k', 10))
    
    # 支持多个数据集名称（dataset_names[]），优先取多个，否则取单个
    dataset_names = request.form.getlist('dataset_names[]')
    if not dataset_names:
        dataset_name = request.form.get('dataset_name')
        if dataset_name:
            dataset_names = [dataset_name]
    file = request.files.get('query_img')
    try:
        x = int(request.form.get('crop_x', 0))
        y = int(request.form.get('crop_y', 0))
        w = int(request.form.get('crop_w', 0))
        h = int(request.form.get('crop_h', 0))
    except Exception:
        x, y, w, h = 0, 0, 0, 0

    if not dataset_names or not any(dataset_names):
        print("缺少数据集名称")
        return jsonify({"msg": "缺少数据集名称"}), 400
    if not file or not file.filename:
        print("未上传图片")
        return jsonify({"msg": "未上传图片"}), 400

    # 传递所有数据集名称
    result = search_image(dataset_names, file, (x, y, w, h), top_k)
    if isinstance(result, dict) and "error" in result:
        print(f"检索失败: {result['error']}")
        return jsonify({"msg": result["error"]}), 400
    return jsonify({"results": result})
