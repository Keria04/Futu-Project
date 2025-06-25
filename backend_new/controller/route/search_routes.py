"""
图片搜索相关路由
"""
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import sys
import uuid
import tempfile
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
import json
from PIL import Image

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from redis_client.redis_client import get_redis_client

search_bp = Blueprint('search', __name__)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@search_bp.route('/search', methods=['POST'])
def search_image():
    """
    图片相似度搜索接口
    POST /api/search
    """
    try:
        # 检查是否有文件上传
        if 'query_img' not in request.files:
            return jsonify({
                "error": "未找到查询图片",
                "message": "请上传查询图片"
            }), 400
            
        file = request.files['query_img']
        if file.filename == '':
            return jsonify({
                "error": "未选择文件",
                "message": "请选择要上传的图片文件"
            }), 400
            
        if not allowed_file(file.filename):
            return jsonify({
                "error": "文件格式不支持",
                "message": "支持的格式: PNG, JPG, JPEG, GIF, BMP, WEBP"
            }), 400
        
        # 获取搜索参数
        crop_x = request.form.get('crop_x', 0, type=int)
        crop_y = request.form.get('crop_y', 0, type=int)
        crop_w = request.form.get('crop_w', 0, type=int)
        crop_h = request.form.get('crop_h', 0, type=int)
        dataset_names = request.form.getlist('dataset_names[]')
        top_k = request.form.get('top_k', 10, type=int)  # 默认返回前10个结果
        similarity_threshold = request.form.get('similarity_threshold', 50.0, type=float)  # 相似度阈值
        
        if not dataset_names:
            return jsonify({
                "error": "参数错误",
                "message": "dataset_names 不能为空"
            }), 400
        
        current_app.logger.info(f"开始图片搜索: 数据集={dataset_names}, top_k={top_k}, 相似度阈值={similarity_threshold}")
        
        # 保存查询图片到临时文件
        query_image_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                file.save(tmp_file.name)
                query_image_path = tmp_file.name
                current_app.logger.info(f"查询图片已保存到: {query_image_path}")
            
            # 处理裁剪参数
            cropped_image_path = None
            if crop_w > 0 and crop_h > 0:
                cropped_image_path = _crop_image(query_image_path, crop_x, crop_y, crop_w, crop_h)
                if cropped_image_path:
                    current_app.logger.info(f"图片已裁剪: {crop_x},{crop_y},{crop_w},{crop_h}")
                    final_image_path = cropped_image_path
                else:
                    final_image_path = query_image_path
            else:
                final_image_path = query_image_path
            
            # 提取查询图片的特征向量
            query_features = _extract_image_features(final_image_path)
            if query_features is None:
                return jsonify({
                    "error": "特征提取失败",
                    "message": "无法提取查询图片的特征向量"
                }), 500
            
            current_app.logger.info(f"查询图片特征提取完成，特征维度: {query_features.shape}")
            
            # 获取数据库接口
            from _database_interface import get_dataset_repository, get_image_repository
            dataset_repo = get_dataset_repository()
            image_repo = get_image_repository()
            
            # 查找指定数据集的索引并进行搜索
            search_results = []
            
            for dataset_name in dataset_names:
                dataset = dataset_repo.get_dataset_by_name(dataset_name)
                if not dataset:
                    current_app.logger.warning(f"数据集不存在: {dataset_name}")
                    continue
                
                dataset_id = dataset['id']
                
                # 搜索该数据集的索引
                dataset_results = _search_dataset_index(
                    dataset_id, dataset_name, query_features, top_k, similarity_threshold
                )
                
                if dataset_results:
                    search_results.extend(dataset_results)
                    current_app.logger.info(f"数据集 {dataset_name} 搜索到 {len(dataset_results)} 个结果")
            
            # 按相似度排序并限制结果数量
            search_results.sort(key=lambda x: x['similarity'], reverse=True)
            search_results = search_results[:top_k]
            
            # 补充图片的详细信息
            enriched_results = []
            for result in search_results:
                try:
                    image_detail = image_repo.get_image_by_id(result['image_id'])
                    if image_detail:
                        enriched_result = _enrich_search_result(result, image_detail, dataset_names)
                        enriched_results.append(enriched_result)
                except Exception as e:
                    current_app.logger.warning(f"补充图片信息失败 ID={result['image_id']}: {e}")
                    continue
            
            response = {
                "success": True,
                "results": enriched_results,
                "total_found": len(enriched_results),
                "search_params": {
                    "crop_region": {
                        "x": crop_x,
                        "y": crop_y,
                        "width": crop_w,
                        "height": crop_h
                    } if crop_w > 0 and crop_h > 0 else None,
                    "datasets": dataset_names,
                    "top_k": top_k,
                    "similarity_threshold": similarity_threshold
                },
                "query_info": {
                    "original_filename": file.filename,
                    "query_time": datetime.now().isoformat()
                }
            }
            
            current_app.logger.info(f"搜索完成，返回 {len(enriched_results)} 个结果")
            return jsonify(response), 200
            
        finally:
            # 清理临时文件
            if query_image_path and os.path.exists(query_image_path):
                os.unlink(query_image_path)
            if cropped_image_path and os.path.exists(cropped_image_path):
                os.unlink(cropped_image_path)
        
    except Exception as e:
        current_app.logger.error(f"图片搜索失败: {e}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            "error": "搜索失败",
            "message": str(e)
        }), 500


def _crop_image(image_path: str, x: int, y: int, w: int, h: int) -> str:
    """裁剪图片"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            cropped_path = tmp_file.name
        
        with Image.open(image_path) as img:
            # 确保裁剪区域在图片范围内
            img_width, img_height = img.size
            x = max(0, min(x, img_width))
            y = max(0, min(y, img_height))
            w = min(w, img_width - x)
            h = min(h, img_height - y)
            
            if w > 0 and h > 0:
                cropped_img = img.crop((x, y, x + w, y + h))
                cropped_img.save(cropped_path, 'JPEG')
                return cropped_path
            else:
                return None
                
    except Exception as e:
        current_app.logger.error(f"图片裁剪失败: {e}")
        return None


def _extract_image_features(image_path: str) -> np.ndarray:
    """提取图片特征向量"""
    try:
        # 使用Redis发送特征提取任务到计算端
        redis_client = get_redis_client()
        if not redis_client:
            current_app.logger.error("Redis客户端不可用")
            return None
        
        # 发送特征提取任务
        task_data = {
            'task_type': 'feature_extraction',
            'image_path': image_path
        }
        
        task_id = redis_client.publish_task('compute:feature_extraction', task_data)
        current_app.logger.info(f"已发送特征提取任务: {task_id}")
        
        # 等待结果
        result = redis_client.get_result(task_id, timeout=30)
        redis_client.delete_result(task_id)  # 清理结果
        
        if result and result.get('success'):
            features = result.get('features')
            if features:
                return np.array(features, dtype=np.float32)
            else:
                current_app.logger.error("特征提取返回空结果")
                return None
        else:
            error_msg = result.get('error', '未知错误') if result else '任务超时'
            current_app.logger.error(f"特征提取失败: {error_msg}")
            return None
            
    except Exception as e:
        current_app.logger.error(f"特征提取异常: {e}")
        return None


def _search_dataset_index(dataset_id: int, dataset_name: str, query_features: np.ndarray, 
                         top_k: int, similarity_threshold: float) -> List[Dict[str, Any]]:
    """搜索指定数据集的索引"""
    try:
        # 构建索引文件名
        index_filename = f"{dataset_id}.index"
        
        # 使用索引接口进行搜索
        from _index_interface import get_index_manager
        
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        # 创建索引器
        index_manager = get_index_manager()
        indexer = index_manager.get_indexer(
            vector_dim=query_features.shape[0],
            strategy_type="ivf",
            base_dir=project_root,
            cache_key=f"search_{dataset_id}"
        )
        
        current_app.logger.info(f"开始搜索数据集 {dataset_name} (ID: {dataset_id}) 的索引: {index_filename}")
        
        # 执行搜索
        results, similarities = indexer.search_index(
            query_features.reshape(1, -1),  # 确保是2D数组
            [index_filename],
            top_k
        )
        
        current_app.logger.info(f"搜索完成，返回 {len(results)} 个结果")
        
        # 处理搜索结果
        dataset_results = []
        for i, (image_id, similarity) in enumerate(zip(results, similarities)):
            # 将距离转换为相似度（距离越小相似度越高）
            # 这里使用一个简单的转换公式，可能需要根据实际情况调整
            similarity_score = max(0, 100 - similarity)
            
            # 过滤低相似度结果
            if similarity_score >= similarity_threshold:
                dataset_results.append({
                    'image_id': int(image_id),
                    'similarity': float(similarity_score),
                    'distance': float(similarity),
                    'dataset_id': dataset_id,
                    'dataset_name': dataset_name,
                    'rank': i + 1
                })
        
        current_app.logger.info(f"数据集 {dataset_name} 搜索到 {len(dataset_results)} 个符合条件的结果")
        return dataset_results
        
    except Exception as e:
        current_app.logger.error(f"搜索数据集 {dataset_name} 索引失败: {e}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return []


def _enrich_search_result(result: Dict[str, Any], image_detail: Dict[str, Any], 
                         dataset_names: List[str]) -> Dict[str, Any]:
    """补充搜索结果的详细信息"""
    try:
        file_path = image_detail.get('file_path', '')
        filename = image_detail.get('filename', '')
        
        # 构建图片URL
        # 假设图片路径格式为: /path/to/datasets/dataset_name/filename
        if file_path:
            # 提取相对于项目根目录的路径
            if 'datasets' in file_path:
                # 找到datasets部分
                parts = file_path.split('datasets')
                if len(parts) > 1:
                    relative_path = 'datasets' + parts[1]
                    image_url = f"/show_image/{relative_path}"
                else:
                    image_url = f"/show_image/{file_path}"
            else:
                image_url = f"/show_image/{file_path}"
        else:
            image_url = ""
        
        enriched_result = {
            "image_id": result['image_id'],
            "image_path": file_path,
            "img_url": image_url,
            "fname": filename,
            "similarity": round(result['similarity'], 2),
            "distance": round(result['distance'], 4),
            "dataset": result['dataset_name'],
            "dataset_id": result['dataset_id'],
            "rank": result['rank'],
            "file_size": image_detail.get('file_size', 0),
            "created_at": image_detail.get('created_at', ''),
        }
        
        # 添加元数据（如果存在）
        if image_detail.get('metadata_json'):
            try:
                metadata = json.loads(image_detail['metadata_json'])
                enriched_result['metadata'] = metadata
            except (json.JSONDecodeError, TypeError):
                pass
        
        return enriched_result
        
    except Exception as e:
        current_app.logger.error(f"补充搜索结果信息失败: {e}")
        # 返回基本信息
        return {
            "image_id": result['image_id'],
            "similarity": result['similarity'],
            "dataset": result['dataset_name'],
            "error": "Failed to load image details"
        }
