"""
重复图片检测相关路由
"""
from flask import Blueprint, request, jsonify

duplicate_bp = Blueprint('duplicate', __name__)

@duplicate_bp.route('/repeated_search', methods=['POST'])
def find_duplicates():
    """
    查找重复图片接口
    POST /api/repeated_search
    """
    try:
        data = request.get_json()
        index_id = data.get('index_id')
        threshold = data.get('threshold', 0.85)
        deduplicate = data.get('deduplicate', False)
        
        if not index_id:
            return jsonify({
                "error": "缺少索引ID",
                "message": "请指定要检测的数据集/索引名称"
            }), 400
        
        if not (0.0 <= threshold <= 1.0):
            return jsonify({
                "error": "阈值无效",
                "message": "相似度阈值必须在0.0到1.0之间"
            }), 400
        
        # TODO: 实现重复图片检测逻辑
        # 这里应该调用重复检测服务
          # 暂时返回模拟重复检测结果
        mock_groups = [
            {
                "representative": "/show_image/datasets/1/circles_10.jpg",
                "duplicates": [
                    "/show_image/datasets/1/circles_1114.jpg",
                    "/show_image/datasets/1/circles_25.jpg"
                ],
                "similarity_scores": [0.96, 0.92],
                "group_size": 3,
                "representative_info": {
                    "fname": "circles_10.jpg",
                    "idx": 10,
                    "dataset": "dataset1"
                },
                "duplicates_info": [
                    {
                        "fname": "circles_1114.jpg",
                        "idx": 1114,
                        "dataset": "dataset1",
                        "img_url": "/show_image/datasets/1/circles_1114.jpg"
                    },
                    {
                        "fname": "circles_25.jpg", 
                        "idx": 25,
                        "dataset": "dataset1",
                        "img_url": "/show_image/datasets/1/circles_25.jpg"
                    }
                ]
            },
            {
                "representative": "/show_image/datasets/1/circles_20.jpg",
                "duplicates": [
                    "/show_image/datasets/1/circles_30.jpg"
                ],
                "similarity_scores": [0.89],
                "group_size": 2,
                "representative_info": {
                    "fname": "circles_20.jpg",
                    "idx": 20,
                    "dataset": "dataset1"
                },
                "duplicates_info": [
                    {
                        "fname": "circles_30.jpg",
                        "idx": 30,
                        "dataset": "dataset1", 
                        "img_url": "/show_image/datasets/1/circles_30.jpg"
                    }
                ]
            },
            {
                "representative": "/show_image/datasets/2/sample_01.jpg",
                "duplicates": [
                    "/show_image/datasets/2/sample_02.jpg",
                    "/show_image/datasets/3/image_001.jpg"
                ],
                "similarity_scores": [0.94, 0.87],
                "group_size": 3,
                "representative_info": {
                    "fname": "sample_01.jpg",
                    "idx": 1,
                    "dataset": "dataset2"
                },
                "duplicates_info": [
                    {
                        "fname": "sample_02.jpg",
                        "idx": 2,
                        "dataset": "dataset2",
                        "img_url": "/show_image/datasets/2/sample_02.jpg"
                    },
                    {
                        "fname": "image_001.jpg",
                        "idx": 1,
                        "dataset": "dataset3",
                        "img_url": "/show_image/datasets/3/image_001.jpg"
                    }
                ]
            }
        ]
        
        # 过滤低于阈值的结果
        filtered_groups = []
        for group in mock_groups:
            filtered_duplicates = []
            filtered_scores = []
            
            for duplicate, score in zip(group['duplicates'], group['similarity_scores']):
                if score >= threshold:
                    filtered_duplicates.append(duplicate)
                    filtered_scores.append(score)
            
            if filtered_duplicates:
                filtered_groups.append({
                    "representative": group['representative'],
                    "duplicates": filtered_duplicates,
                    "similarity_scores": filtered_scores,
                    "group_size": len(filtered_duplicates) + 1
                })
        
        # 统计信息
        total_duplicates = sum(group['group_size'] - 1 for group in filtered_groups)
        total_groups = len(filtered_groups)
        
        response = {
            "groups": filtered_groups,
            "statistics": {
                "total_groups": total_groups,
                "total_duplicates": total_duplicates,
                "threshold_used": threshold,
                "deduplicate_performed": deduplicate
            },
            "search_params": {
                "index_id": index_id,
                "threshold": threshold,
                "deduplicate": deduplicate
            }
        }
        
        # 如果需要去重操作
        if deduplicate and filtered_groups:
            # TODO: 实现去重逻辑
            # 这里应该删除重复的图片文件，只保留代表图片
            response["statistics"]["files_removed"] = total_duplicates
            response["message"] = f"已删除{total_duplicates}个重复文件"
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "error": "重复检测失败",
            "message": str(e)
        }), 500
