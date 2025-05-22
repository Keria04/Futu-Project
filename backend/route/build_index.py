from flask import Blueprint, jsonify, current_app
from config import config

build_index_bp = Blueprint('build_index', __name__)

@build_index_bp.route('/api/build_index', methods=['POST'])
def api_build_index():
    from app import prepare_index
    prepare_index(distributed=False)
    return jsonify({"msg": "本地数据集特征与索引已构建完成，可以进行图片检索。"})

@build_index_bp.route('/api/build_index_distributed', methods=['POST'])
def api_build_index_distributed():
    from app import prepare_index, DISTRIBUTED_AVAILABLE
    if DISTRIBUTED_AVAILABLE:
        ok = prepare_index(distributed=True)
        if ok:
            return jsonify({"msg": "远程数据集特征与索引已构建完成，可以进行图片检索。"})
        else:
            return jsonify({"msg": "远程构建失败，已跳过。"}), 500
    else:
        return jsonify({"msg": "远程worker不可用，无法远程构建。"}), 400
