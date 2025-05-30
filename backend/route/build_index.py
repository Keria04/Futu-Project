from flask import Blueprint, jsonify, request
from config import config
from index_builder_module.api import build_dataset_index

build_index_bp = Blueprint('build_index', __name__)

@build_index_bp.route('/api/build_index', methods=['POST'])
def api_build_index():
    data = request.get_json()
    dataset_dir = data.get("dataset_dir", config.DATASET_DIR)
    dataset_name = data.get("dataset_name", "default")
    distributed = data.get("distributed", False)
    try:
        ok = build_dataset_index(dataset_dir, dataset_name, distributed=distributed)
    except Exception as e:
        print(f"构建索引时发生错误: {str(e)}")
        return jsonify({"msg": f"构建失败，错误信息: {str(e)}"}), 500
    if ok:
        return jsonify({"msg": "数据集特征与索引已构建完成，可以进行图片检索。"})
    else:
        return jsonify({"msg": "构建失败。"}), 501

@build_index_bp.route('/api/build_index_distributed', methods=['POST'])
def api_build_index_distributed():
    data = request.get_json()
    dataset_dir = data.get("dataset_dir", config.DATASET_DIR)
    dataset_name = data.get("dataset_name", "default")
    ok = build_dataset_index(dataset_dir, dataset_name, distributed=True)
    if ok:
        return jsonify({"msg": "远程数据集特征与索引已构建完成，可以进行图片检索。"})
    else:
        return jsonify({"msg": "远程构建失败，已跳过。"}), 500
