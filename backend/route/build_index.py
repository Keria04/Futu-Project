from flask import Blueprint, jsonify, request
from config import config
from index_manage_module.api import build_dataset_index
import os

build_index_bp = Blueprint('build_index', __name__)

@build_index_bp.route('/api/build_index', methods=['POST'])
def api_build_index():
    data = request.get_json()
    # 支持多个数据集名称
    dataset_names = data.get("dataset_names") or []
    if not dataset_names:
        # 兼容单个名称
        single_name = data.get("dataset_name")
        if single_name:
            dataset_names = [single_name]
    distributed = data.get("distributed", False)
    if not dataset_names:
        print("缺少数据集名称")
        return jsonify({"msg": "缺少数据集名称"}), 400

    print(f"开始构建索引，数据集名称: {dataset_names}, 分布式: {distributed}")

    results = []
    for dataset_name in dataset_names:
        dataset_dir = os.path.join(config.DATASET_DIR, dataset_name)
        if not os.path.isdir(dataset_dir):
            print(f"数据集目录不存在: {dataset_dir}")
            results.append({"dataset": dataset_name, "success": False, "msg": f"数据集目录不存在: {dataset_dir}"})
            continue
        try:
            ok = build_dataset_index(dataset_dir, dataset_name, distributed=distributed)
            if ok:
                results.append({"dataset": dataset_name, "success": True, "msg": "数据集特征与索引已构建完成，可以进行图片检索。"})
            else:
                results.append({"dataset": dataset_name, "success": False, "msg": "构建失败。"})
        except Exception as e:
            print(f"构建索引时发生错误: {str(e)}")
            results.append({"dataset": dataset_name, "success": False, "msg": f"构建失败，错误信息: {str(e)}"})
    # 汇总返回
    if all(r["success"] for r in results):
        return jsonify({"msg": "全部数据集特征与索引已构建完成，可以进行图片检索。", "results": results})
    else:
        return jsonify({"msg": "部分或全部数据集构建失败。", "results": results}), 500

@build_index_bp.route('/api/build_index_distributed', methods=['POST'])
def api_build_index_distributed():
    data = request.get_json()
    dataset_names = data.get("dataset_names") or []
    if not dataset_names:
        single_name = data.get("dataset_name")
        if single_name:
            dataset_names = [single_name]
    if not dataset_names:
        return jsonify({"msg": "缺少数据集名称"}), 400

    results = []
    for dataset_name in dataset_names:
        dataset_dir = os.path.join(config.DATASET_DIR, dataset_name)
        if not os.path.isdir(dataset_dir):
            results.append({"dataset": dataset_name, "success": False, "msg": f"数据集目录不存在: {dataset_dir}"})
            continue
        try:
            ok = build_dataset_index(dataset_dir, dataset_name, distributed=True)
            if ok:
                results.append({"dataset": dataset_name, "success": True, "msg": "远程数据集特征与索引已构建完成，可以进行图片检索。"})
            else:
                results.append({"dataset": dataset_name, "success": False, "msg": "远程构建失败。"})
        except Exception as e:
            results.append({"dataset": dataset_name, "success": False, "msg": f"远程构建失败，错误信息: {str(e)}"})
    if all(r["success"] for r in results):
        return jsonify({"msg": "全部远程数据集特征与索引已构建完成，可以进行图片检索。", "results": results})
    else:
        return jsonify({"msg": "部分或全部远程数据集构建失败。", "results": results}), 500
