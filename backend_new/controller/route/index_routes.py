"""
索引构建相关路由
"""
from flask import Blueprint, request, jsonify, current_app
import json
import os
import sys
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from redis_client.redis_client import get_redis_client

# 配置后台任务日志记录器
background_logger = logging.getLogger('index_background')
if not background_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    background_logger.addHandler(handler)
    background_logger.setLevel(logging.INFO)

index_bp = Blueprint('index', __name__)

@index_bp.route('/build_index', methods=['POST'])
def build_index():
    """
    构建索引接口 - 控制端负责数据库查询和索引构建
    POST /api/build_index
    """
    try:
        data = request.get_json()
        dataset_names = data.get('dataset_names', [])
        distributed = data.get('distributed', False)
        
        if not dataset_names:
            return jsonify({
                "error": "参数错误",
                "message": "dataset_names 不能为空"
            }), 400
        
        # 生成任务ID和进度文件路径
        task_id = str(uuid.uuid4())
        progress_file = f"/progress/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task_id}.json"
        
        current_app.logger.info(f"开始索引构建任务: {task_id}, 数据集: {dataset_names}")
        
        # 控制端负责数据库查询
        from _database_interface import get_dataset_repository, get_image_repository
        
        try:
            dataset_repo = get_dataset_repository()
            image_repo = get_image_repository()
        except Exception as e:
            current_app.logger.error(f"数据库连接失败: {e}")
            return jsonify({
                "error": "数据库连接失败",
                "message": str(e)
            }), 500
          # 收集所有需要处理的图片信息
        all_images = []
        dataset_info = {}
        
        for dataset_name in dataset_names:
            dataset = dataset_repo.get_dataset_by_name(dataset_name)
            if not dataset:
                # 如果数据集不存在，则创建对应的数据库信息
                try:
                    dataset_id = dataset_repo.create_dataset(dataset_name, f"自动创建的数据集: {dataset_name}")
                    dataset = dataset_repo.get_dataset_by_id(dataset_id)
                    current_app.logger.info(f"已创建新数据集: {dataset_name}, ID: {dataset_id}")
                except Exception as e:
                    current_app.logger.error(f"创建数据集失败: {e}")
                    return jsonify({
                        "error": f"数据集创建失败: {dataset_name}",                        "message": str(e)
                    }), 500
            
            images = image_repo.get_images_by_dataset(dataset['id'])
            if not images:
                # 如果数据库中没有图片记录，尝试扫描对应的文件夹
                current_app.logger.info(f"数据集 {dataset_name} 在数据库中为空，尝试扫描文件夹...")
                try:
                    scanned_images = _scan_dataset_folder(dataset_name, dataset['id'], image_repo)
                    if scanned_images:
                        current_app.logger.info(f"从文件夹扫描到 {len(scanned_images)} 张图片，已添加到数据库")
                        images = scanned_images
                    else:
                        current_app.logger.warning(f"数据集 {dataset_name} 文件夹为空或不存在")
                        continue
                except Exception as e:
                    current_app.logger.error(f"扫描数据集文件夹失败: {e}")
                    continue
                
            # 过滤有效的图片文件
            valid_images = []
            for img in images:
                if os.path.exists(img['file_path']):
                    valid_images.append({
                        'id': img['id'],
                        'path': img['file_path'],
                        'dataset_id': img['dataset_id'],
                        'filename': img.get('filename', os.path.basename(img['file_path']))
                    })
                else:
                    current_app.logger.warning(f"图片文件不存在: {img['file_path']}")
            
            if valid_images:
                all_images.extend(valid_images)
                dataset_info[dataset_name] = {
                    'id': dataset['id'],
                    'image_count': len(valid_images),
                    'total_images': len(images)
                }
        
        if not all_images:
            return jsonify({
                "error": "没有有效的图片文件",
                "message": "请检查数据集中的图片文件路径"
            }), 400
        
        # 初始化进度数据
        progress_data = {
            "task_id": task_id,
            "progress": 0.0,
            "status": "processing",
            "message": f"开始处理 {len(all_images)} 张图片",
            "start_time": datetime.now().isoformat(),
            "dataset_names": dataset_names,
            "dataset_info": dataset_info,
            "total_images": len(all_images),
            "distributed": distributed
        }
        
        # 保存初始进度
        try:
            _save_progress_data(progress_file, progress_data)
        except Exception as e:
            current_app.logger.warning(f"保存进度数据失败: {e}")        # 启动后台任务进行索引构建
        import threading
        build_thread = threading.Thread(
            target=_build_index_background,
            args=(task_id, all_images, dataset_info, progress_file, distributed),
            daemon=True
        )
        build_thread.start()
        
        response = {
            "success": True,
            "msg": "索引构建任务已启动",
            "task_id": task_id,
            "total_images": len(all_images),
            "dataset_info": dataset_info,
            "progress": [
                {
                    "progress_file": progress_file
                }
            ]
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        current_app.logger.error(f"索引构建请求处理失败: {e}")
        return jsonify({
            "error": "索引构建失败",
            "message": str(e)
        }), 500

@index_bp.route('/progress/<path:progress_path>', methods=['GET'])
def get_progress(progress_path):
    """
    获取构建进度接口
    GET /api/progress/{progress_path}
    """
    try:
        # 从进度文件中读取进度数据
        progress_data = _load_progress_data(progress_path)
        
        if not progress_data:
            # 如果没有找到进度文件，可能任务还在队列中或文件被删除
            return jsonify({
                "error": "进度信息不存在",
                "message": f"无法找到进度文件: {progress_path}"
            }), 404
        
        # 如果任务已完成但进度数据较旧，尝试从Redis获取最新结果
        if progress_data.get('status') in ['queued', 'building']:
            task_id = progress_data.get('task_id')
            if task_id:
                redis_client = get_redis_client()
                if redis_client:
                    result = redis_client.get_result(task_id)
                    if result:
                        # 更新进度数据
                        if result.get('success'):
                            progress_data.update({
                                'progress': 100.0,
                                'status': 'completed',
                                'message': '索引构建完成',
                                'completed_at': result.get('processed_at'),
                                'result': result.get('result', {})
                            })
                        else:
                            progress_data.update({
                                'progress': 0.0,
                                'status': 'failed',
                                'message': f"索引构建失败: {result.get('error', '未知错误')}",
                                'failed_at': result.get('processed_at'),
                                'error': result.get('error')
                            })
                        
                        # 保存更新后的进度数据
                        try:
                            _save_progress_data(progress_path, progress_data)
                        except Exception as e:
                            current_app.logger.warning(f"更新进度数据失败: {e}")
        
        return jsonify(progress_data), 200
        
    except Exception as e:
        current_app.logger.error(f"获取进度失败: {e}")
        return jsonify({
            "error": "获取进度失败",
            "message": str(e)
        }), 500


def _save_progress_data(progress_path: str, progress_data: Dict[str, Any]) -> None:
    """保存进度数据到文件"""
    try:
        # 确保progress_path是相对路径且安全
        if progress_path.startswith('/'):
            progress_path = progress_path[1:]
        
        # 构建完整的文件路径
        progress_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'progress')
        os.makedirs(progress_dir, exist_ok=True)
        
        file_path = os.path.join(progress_dir, progress_path.replace('/', '_'))
        
        # 保存数据
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        current_app.logger.error(f"保存进度数据失败: {e}")
        raise


def _load_progress_data(progress_path: str) -> Dict[str, Any]:
    """从文件加载进度数据"""
    try:
        # 确保progress_path是相对路径且安全
        if progress_path.startswith('/'):
            progress_path = progress_path[1:]
        
        # 构建完整的文件路径
        progress_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'progress')
        file_path = os.path.join(progress_dir, progress_path.replace('/', '_'))
        
        # 加载数据
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return None
            
    except Exception as e:
        current_app.logger.error(f"加载进度数据失败: {e}")
        return None


@index_bp.route('/build_status/<task_id>', methods=['GET']) 
def get_build_status(task_id):
    """
    根据任务ID获取构建状态
    GET /api/build_status/{task_id}
    """
    try:
        redis_client = get_redis_client()
        if not redis_client:
            return jsonify({
                "error": "服务不可用",
                "message": "无法连接到任务队列服务"
            }), 503
        
        # 从Redis获取任务结果
        result = redis_client.get_result(task_id)
        
        if not result:
            return jsonify({
                "task_id": task_id,
                "status": "running",
                "message": "任务正在处理中..."
            }), 200
        
        # 处理任务结果
        if result.get('success'):
            return jsonify({
                "task_id": task_id,
                "status": "completed",
                "message": "索引构建完成",
                "result": result.get('result', {}),
                "processed_at": result.get('processed_at')
            }), 200
        else:
            return jsonify({
                "task_id": task_id,
                "status": "failed", 
                "message": "索引构建失败",
                "error": result.get('error', '未知错误'),
                "processed_at": result.get('processed_at')
            }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取构建状态失败: {e}")
        return jsonify({
            "error": "获取状态失败",
            "message": str(e)
        }), 500


def _build_index_background(task_id: str, images: List[Dict], dataset_info: Dict, 
                           progress_file: str, distributed: bool):
    """后台索引构建任务 - 在控制端执行"""
    import time
    import numpy as np
    from faiss_module.build_index import build_index
    
    try:
        background_logger.info(f"开始后台索引构建任务: {task_id}")
          # 更新进度：开始特征提取
        _update_progress(progress_file, 10.0, "extracting", "开始检查现有特征向量...")
        
        # 检查数据库中哪些图片已经有特征向量
        from _database_interface import get_image_repository
        image_repo = get_image_repository()
        
        images_need_features = []  # 需要提取特征的图片
        existing_features = []     # 已有特征的数据
        existing_image_ids = []    # 已有特征的图片ID
        
        background_logger.info(f"开始检查 {len(images)} 张图片的特征向量状态...")
        
        for img in images:
            try:
                # 获取图片的详细信息，包括特征向量
                image_detail = image_repo.get_image_by_id(img['id'])
                
                if image_detail and image_detail.get('feature_vector'):
                    # 图片已有特征向量，解析并添加到现有特征列表
                    try:
                        feature_data = json.loads(image_detail['feature_vector'])
                        if feature_data and len(feature_data) > 0:
                            existing_features.append(feature_data)
                            existing_image_ids.append(img['id'])
                            background_logger.debug(f"图片 {img['id']} 已有特征向量，跳过计算")
                            continue
                    except (json.JSONDecodeError, TypeError) as e:
                        background_logger.warning(f"图片 {img['id']} 特征向量格式异常，将重新计算: {e}")
                
                # 图片没有特征向量或特征向量无效，需要重新提取
                images_need_features.append(img)
                
            except Exception as e:
                background_logger.warning(f"检查图片 {img['id']} 特征向量失败: {e}")
                # 如果检查失败，保险起见加入计算队列
                images_need_features.append(img)
        
        background_logger.info(f"特征向量检查完成 - 已有特征: {len(existing_features)} 张，需要计算: {len(images_need_features)} 张")
        
        # 批量请求计算端提取特征（仅对需要的图片）
        new_features = []
        new_image_ids = []
        batch_size = 32  # 批处理大小
        total_images = len(images)
        total_need_calculation = len(images_need_features)        
        redis_client = get_redis_client()
        if not redis_client:
            raise Exception("Redis客户端不可用")
        
        # 仅对需要提取特征的图片进行处理
        if images_need_features:
            _update_progress(progress_file, 15.0, "extracting", 
                           f"开始提取特征 - 需要计算: {total_need_calculation} 张，已有特征: {len(existing_features)} 张")
            
            for i in range(0, len(images_need_features), batch_size):
                batch_images = images_need_features[i:i+batch_size]
                batch_paths = [img['path'] for img in batch_images]
                batch_ids = [img['id'] for img in batch_images]
                
                # 发送批量特征提取任务到计算端
                feature_task_data = {
                    'task_type': 'batch_feature_extraction',
                    'image_paths': batch_paths
                }
                
                try:
                    feature_task_id = redis_client.publish_task('compute:batch_feature_extraction', feature_task_data)
                    
                    # 等待特征提取结果
                    result = redis_client.get_result(feature_task_id, timeout=120)  # 给更长的超时时间
                    
                    if result and result.get('success'):
                        batch_features = result.get('result', [])
                        
                        # 处理批量结果
                        for j, feature_result in enumerate(batch_features):
                            if feature_result.get('success') and feature_result.get('features'):
                                new_features.append(feature_result['features'])
                                new_image_ids.append(batch_ids[j])
                    
                    # 清理结果
                    redis_client.delete_result(feature_task_id)
                    
                    # 更新进度
                    current_batch_end = min(i + batch_size, len(images_need_features))
                    calculation_progress = (current_batch_end / total_need_calculation) * 60.0 if total_need_calculation > 0 else 60.0
                    overall_progress = 15.0 + calculation_progress  # 15%-75%用于特征提取
                    
                    _update_progress(progress_file, overall_progress, "extracting", 
                                   f"已计算 {len(new_features)}/{total_need_calculation} 张新图片的特征，总计 {len(existing_features) + len(new_features)}/{total_images} 张")
                    
                except Exception as e:
                    background_logger.error(f"批量特征提取失败: {e}")
                    # 继续处理下一批
                    continue
        else:
            background_logger.info("所有图片都已有特征向量，跳过特征提取阶段")
            _update_progress(progress_file, 75.0, "extracting", 
                           f"所有图片都已有特征向量，共 {len(existing_features)} 张")
        
        # 合并已有特征和新提取的特征
        all_features = existing_features + new_features
        image_ids = existing_image_ids + new_image_ids
        
        if not all_features:
            raise Exception("没有可用的特征向量数据")
        
        background_logger.info(f"特征处理完成 - 已有: {len(existing_features)} 个，新提取: {len(new_features)} 个，总计: {len(all_features)} 个特征向量")          # 将新提取的特征向量存入数据库
        if new_features and new_image_ids:
            background_logger.info(f"开始将 {len(new_features)} 个新特征向量存入数据库...")
            
            try:
                # 统计处理结果
                total_count = len(new_image_ids)
                success_count = 0
                failure_count = 0
                
                # 批量处理新特征向量存储
                for idx, (image_id, feature_vector) in enumerate(zip(new_image_ids, new_features)):
                    try:
                        # 数据格式转换和验证
                        if feature_vector is None:
                            background_logger.warning(f"图片 {image_id} 的特征向量为空，跳过")
                            failure_count += 1
                            continue
                        
                        # 转换为可存储的JSON格式
                        if isinstance(feature_vector, np.ndarray):
                            feature_json = json.dumps(feature_vector.tolist())
                        elif isinstance(feature_vector, list):
                            feature_json = json.dumps(feature_vector)
                        else:
                            background_logger.warning(f"图片 {image_id} 特征向量格式不支持: {type(feature_vector)}")
                            failure_count += 1
                            continue                        # 更新数据库记录 - 使用通用的update_image方法
                        update_data = {"feature_vector": feature_json}
                        
                        # 添加调试信息
                        background_logger.debug(f"尝试更新图片 {image_id} 的特征向量，数据长度: {len(feature_json) if feature_json else 0}")
                        
                        update_success = image_repo.update_image(image_id, update_data)
                        
                        if update_success:
                            success_count += 1
                            background_logger.debug(f"成功更新图片 {image_id} 的特征向量")
                        else:
                            background_logger.warning(f"数据库更新失败 - 图片ID: {image_id}")
                            failure_count += 1
                          # 定期输出进度日志
                        current_progress = idx + 1
                        if current_progress % 50 == 0 or current_progress == total_count:
                            background_logger.info(
                                f"新特征存储进度: {current_progress}/{total_count} "
                                f"(成功: {success_count}, 失败: {failure_count})"
                            )
                            
                    except Exception as e:
                        failure_count += 1
                        background_logger.error(f"处理图片 {image_id} 特征向量时发生错误: {e}")
                        background_logger.error(f"错误类型: {type(e).__name__}")
                        # 记录更多调试信息
                        if hasattr(e, '__traceback__'):
                            import traceback
                            background_logger.error(f"错误堆栈: {traceback.format_exc()}")
                        continue
                
                # 输出最终统计结果
                background_logger.info(
                    f"新特征向量存储完成 - 总计: {total_count}, "
                    f"成功: {success_count}, 失败: {failure_count}"
                )
                
                # 如果成功率过低，记录警告
                success_rate = success_count / total_count if total_count > 0 else 1.0
                if success_rate < 0.8:  # 成功率低于80%
                    background_logger.warning(
                        f"新特征向量存储成功率较低: {success_rate:.2%}, "
                        f"请检查数据库连接和数据完整性"
                    )
                
            except Exception as e:
                background_logger.error(f"新特征向量存储过程失败: {e}")
                background_logger.error(f"错误详情: {type(e).__name__}")
                # 继续执行后续的索引构建流程
        else:
            background_logger.info("没有新特征向量需要存储到数据库")        
        # 更新进度：开始构建索引
        _update_progress(progress_file, 80.0, "building", f"开始构建FAISS索引，使用 {len(all_features)} 个特征向量...")
        
        # 转换为numpy数组
        features_array = np.array(all_features, dtype=np.float32)
        ids_array = np.array(image_ids, dtype=np.int64)
        
        background_logger.info(f"准备构建索引，特征形状: {features_array.shape}")
        background_logger.info(f"特征来源统计 - 已有: {len(existing_features)} 个，新提取: {len(new_features)} 个")
        
        # 构建FAISS索引（在控制端）
        index_files = []
        total_features = 0
        
        if distributed:
            # 分布式构建 - 按数据集分别构建索引
            for dataset_name, info in dataset_info.items():
                dataset_id = info['id']
                
                # 筛选属于此数据集的特征
                dataset_mask = []
                dataset_features = []
                dataset_ids = []
                
                for idx, img_id in enumerate(image_ids):
                    # 这里需要根据image_id找到对应的dataset_id
                    # 由于我们有images信息，可以建立映射
                    img_dataset_id = next((img['dataset_id'] for img in images if img['id'] == img_id), None)
                    if img_dataset_id == dataset_id:
                        dataset_features.append(all_features[idx])
                        dataset_ids.append(img_id)
                
                if dataset_features:
                    dataset_features_array = np.array(dataset_features, dtype=np.float32)
                    dataset_ids_array = np.array(dataset_ids, dtype=np.int64)
                    
                    index_name = f"{dataset_id}.index"
                    build_index(dataset_features_array, dataset_ids_array, index_name)
                    
                    index_files.append(index_name)
                    total_features += len(dataset_features_array)
                    
                    background_logger.info(f"数据集 {dataset_name} (ID: {dataset_id}) 索引构建完成: {index_name}")
        else:
            # 统一构建索引 - 使用所有数据集ID组合命名
            dataset_ids_str = "_".join(str(info['id']) for info in dataset_info.values())
            index_name = f"{dataset_ids_str}.index"
            build_index(features_array, ids_array, index_name)
            
            index_files.append(index_name)
            total_features = len(features_array)
            
            background_logger.info(f"统一索引构建完成: {index_name}")
          # 更新进度：完成
        end_time = datetime.now()
        completion_message = (
            f"索引构建完成，共处理 {total_features} 个特征向量 "
            f"(已有: {len(existing_features)} 个，新提取: {len(new_features)} 个)"
        )
        
        _update_progress(progress_file, 100.0, "completed", completion_message, {
            'index_files': index_files,
            'total_features': total_features,
            'existing_features_count': len(existing_features),
            'new_features_count': len(new_features),
            'skipped_calculation_count': len(existing_features),
            'completed_at': end_time.isoformat()
        })
        
        background_logger.info(f"索引构建任务完成: {task_id}")
        background_logger.info(f"索引文件: {index_files}")
        background_logger.info(f"优化效果 - 跳过了 {len(existing_features)} 张图片的特征计算，仅计算了 {len(new_features)} 张新图片")
        
    except Exception as e:
        background_logger.error(f"索引构建后台任务失败: {e}")
        import traceback
        background_logger.error(traceback.format_exc())
        
        # 更新进度：失败
        _update_progress(progress_file, 0.0, "failed", f"索引构建失败: {str(e)}", {
            'error': str(e),
            'failed_at': datetime.now().isoformat()
        })


def _update_progress(progress_file: str, progress: float, status: str, message: str, extra_data: Dict = None):
    """更新进度信息"""
    try:
        # 读取现有进度数据
        existing_data = _load_progress_data(progress_file) or {}
        
        # 更新进度信息
        existing_data.update({
            'progress': progress,
            'status': status,
            'message': message,
            'updated_at': datetime.now().isoformat()
        })
        
        # 添加额外数据
        if extra_data:
            existing_data.update(extra_data)
        
        # 保存更新后的数据
        _save_progress_data(progress_file, existing_data)
        
    except Exception as e:
        current_app.logger.error(f"更新进度失败: {e}")


def _scan_dataset_folder(dataset_name: str, dataset_id: int, image_repo) -> List[Dict]:
    """
    扫描数据集文件夹，将图片文件信息添加到数据库
    """
    try:        # 构建数据集文件夹路径
        # 数据集文件夹在项目根目录的 datasets/ 下
        # 当前文件路径: backend_new/controller/route/index_routes.py
        # 需要往上3级到项目根目录 Futu-Project/
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 到 backend_new/
        project_root = os.path.dirname(current_dir)  # 到 Futu-Project/
        dataset_folder = os.path.join(project_root, 'datasets', dataset_name)
        
        current_app.logger.info(f"扫描数据集文件夹: {dataset_folder}")
        current_app.logger.debug(f"项目根目录: {project_root}")
        current_app.logger.debug(f"当前文件路径: {os.path.abspath(__file__)}")
        
        if not os.path.exists(dataset_folder):
            current_app.logger.warning(f"数据集文件夹不存在: {dataset_folder}")
            return []
        
        if not os.path.isdir(dataset_folder):
            current_app.logger.warning(f"路径不是文件夹: {dataset_folder}")
            return []
        
        # 支持的图片格式
        supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
        
        # 扫描文件夹中的图片文件
        image_files = []
        for filename in os.listdir(dataset_folder):
            file_path = os.path.join(dataset_folder, filename)
            
            # 检查是否是文件且是支持的图片格式
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(filename.lower())
                if ext in supported_extensions:
                    image_files.append((filename, file_path))
        
        if not image_files:
            current_app.logger.info(f"文件夹 {dataset_folder} 中没有找到支持的图片文件")
            return []
        
        current_app.logger.info(f"找到 {len(image_files)} 个图片文件，开始添加到数据库...")
        
        # 批量添加图片信息到数据库
        added_images = []
        for filename, file_path in image_files:
            try:
                # 获取文件大小
                file_size = os.path.getsize(file_path)
                
                # 添加图片记录到数据库
                image_id = image_repo.add_image(
                    dataset_id=dataset_id,
                    filename=filename,
                    file_path=file_path,
                    file_size=file_size,
                    checksum=""  # 可以后续添加文件校验和计算
                )
                
                if image_id:
                    # 构建图片信息字典（与数据库查询结果格式一致）
                    image_info = {
                        'id': image_id,
                        'dataset_id': dataset_id,
                        'filename': filename,
                        'file_path': file_path,
                        'file_size': file_size,
                        'checksum': '',
                        'created_at': datetime.now().isoformat(),
                        'metadata_json': None,
                        'feature_vector': None
                    }
                    added_images.append(image_info)
                    current_app.logger.debug(f"已添加图片: {filename} (ID: {image_id})")
                
            except Exception as e:
                current_app.logger.error(f"添加图片 {filename} 失败: {e}")
                continue
        
        current_app.logger.info(f"成功添加 {len(added_images)} 张图片到数据库")
        return added_images
        
    except Exception as e:
        current_app.logger.error(f"扫描数据集文件夹失败: {e}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return []


def _calculate_file_checksum(file_path: str) -> str:
    """
    计算文件的MD5校验和（可选功能）
    """
    try:
        import hashlib
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        current_app.logger.warning(f"计算文件校验和失败 {file_path}: {e}")
        return ""
