from flask import Blueprint, jsonify, request, send_file
from config import config
from index_manage_module.api import build_dataset_index
import os
import threading
import time

build_index_bp = Blueprint('build_index', __name__, url_prefix='/api')

from index_manage_module.index_builder import IndexBuilder

progress_dir = "data/progress"
os.makedirs(progress_dir, exist_ok=True)

# 构建索引接口（支持进度条）
@build_index_bp.route('/build_index', methods=['POST'])
def build_index():
    data = request.get_json()
    dataset_names = data.get('dataset_names', [])
    distributed = data.get('distributed', False)
    results = []
    for ds_name in dataset_names:
        dataset_dir = os.path.join("datasets", ds_name)
        progress_file = os.path.join(progress_dir, f"{ds_name}_progress.txt")
        # 清空进度文件
        with open(progress_file, "w", encoding="utf-8") as f:
            f.write("")
        def build_task():
            builder = IndexBuilder(dataset_dir, ds_name, distributed=distributed)
            builder.build(progress_file=progress_file)
        # 后台线程执行
        t = threading.Thread(target=build_task)
        t.start()
        results.append({"dataset": ds_name, "progress_file": f"/api/build_index/progress/{ds_name}"})
    return jsonify({"msg": "索引构建已启动", "progress": results})

# 进度条轮询接口
@build_index_bp.route('/build_index/progress/<dataset_name>', methods=['GET'])
def get_progress(dataset_name):
    progress_file = os.path.join(progress_dir, f"{dataset_name}_progress.txt")
    if not os.path.exists(progress_file):
        return jsonify({"progress": 0, "status": "pending"})
    
    try:
        with open(progress_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines:
                return jsonify({"progress": 0, "status": "pending"})
            
            # 检查是否有完成标记
            if any("索引构建完成" in line for line in lines):
                return jsonify({"progress": 100, "status": "done", "message": "索引构建完成"})
            
            # 查找最后一个包含进度信息的行
            last_line = lines[-1]
            # tqdm格式: "特征提取:  10%|##        | 1/10 [00:00<00:00,  5.00it/s]"
            import re
            m = re.search(r'(\d+)/(\d+)', last_line)
            if m:
                current = int(m.group(1))
                total = int(m.group(2))
                if total == 0:
                    # 没有新图片需要处理，直接返回完成状态
                    return jsonify({"progress": 100, "status": "done", "message": "没有新图片需要处理"})
                percent = int(current / total * 100)
                status = "done" if current == total else "building"
                return jsonify({"progress": percent, "current": current, "total": total, "status": status})
    except Exception as e:
        print(f"读取进度文件出错: {e}")
        pass
    return jsonify({"progress": 0, "status": "pending"})

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
