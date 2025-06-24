"""
索引构建API路由
"""
import sys
import os
from flask import Blueprint, request, jsonify

# 添加路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from control_service.services import index_service, database_service

index_bp = Blueprint('index', __name__, url_prefix='/api')


@index_bp.route('/build_index', methods=['POST'])
def api_build_index():
    """构建索引API"""
    try:
        data = request.get_json()
        dataset_names = data.get('dataset_names', [])
        distributed = data.get('distributed', False)
        
        if not dataset_names:
            return jsonify({"msg": "缺少数据集名称"}), 400
        
        results = []
        for dataset_name in dataset_names:
            dataset_dir = os.path.join("datasets", dataset_name)
            
            if not os.path.exists(dataset_dir):
                results.append({
                    "dataset": dataset_name,
                    "success": False,
                    "message": f"数据集目录不存在: {dataset_dir}"
                })
                continue
            
            # 准备进度文件
            progress_dir = "data/progress"
            os.makedirs(progress_dir, exist_ok=True)
            progress_file = os.path.join(progress_dir, f"{dataset_name}_progress.txt")
            
            # 清空进度文件
            with open(progress_file, "w", encoding="utf-8") as f:
                f.write("")
            
            # 启动构建
            success = index_service.build_dataset_index(
                dataset_name=dataset_name,
                dataset_dir=dataset_dir,
                distributed=distributed,
                progress_file=progress_file
            )
            
            if success:
                results.append({
                    "dataset": dataset_name,
                    "success": True,
                    "progress_url": f"/api/build_index/progress/{dataset_name}"
                })
            else:
                results.append({
                    "dataset": dataset_name,
                    "success": False,
                    "message": "索引构建已在进行中"
                })
        
        return jsonify({
            "msg": "索引构建请求已处理",
            "results": results
        })
        
    except Exception as e:
        return jsonify({"msg": f"构建索引失败: {str(e)}"}), 500


@index_bp.route('/build_index/progress/<dataset_name>', methods=['GET'])
def api_get_progress(dataset_name):
    """获取构建进度API"""
    try:
        progress_file = os.path.join("data/progress", f"{dataset_name}_progress.txt")
        
        if not os.path.exists(progress_file):
            return jsonify({
                "progress": 0,
                "status": "pending",
                "message": "等待开始"
            })
        
        # 读取进度文件
        with open(progress_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        if not lines:
            return jsonify({
                "progress": 0,
                "status": "pending",
                "message": "等待开始"
            })
        
        # 解析最后一行
        last_line = lines[-1].strip()
        
        if last_line.startswith("ERROR"):
            return jsonify({
                "progress": 0,
                "status": "failed",
                "message": last_line.replace("ERROR - ", "")
            })
        elif "100.00%" in last_line:
            return jsonify({
                "progress": 100,
                "status": "completed",
                "message": "索引构建完成"
            })
        else:
            # 解析进度
            try:
                if "%" in last_line:
                    parts = last_line.split("%")
                    progress = float(parts[0])
                    message = parts[1].strip(" - ") if len(parts) > 1 else ""
                else:
                    progress = 0
                    message = last_line
                
                return jsonify({
                    "progress": progress,
                    "status": "processing",
                    "message": message
                })
            except Exception:
                return jsonify({
                    "progress": 0,
                    "status": "processing",
                    "message": last_line
                })
        
    except Exception as e:
        return jsonify({
            "progress": 0,
            "status": "error",
            "message": f"获取进度失败: {str(e)}"
        }), 500


@index_bp.route('/build_index/status/<dataset_name>', methods=['GET'])
def api_get_build_status(dataset_name):
    """获取构建状态API"""
    try:
        status = index_service.get_build_status(dataset_name)
        return jsonify({
            "dataset": dataset_name,
            "status": status
        })
    except Exception as e:
        return jsonify({"msg": f"获取状态失败: {str(e)}"}), 500
