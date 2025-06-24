"""
简化控制端应用 - 仅提供基本API
"""
import os
import sys
from flask import Flask, jsonify

# 尝试导入CORS，如果没有安装则跳过
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False

def create_simple_app():
    """创建简化应用"""
    app = Flask(__name__)
    
    # 配置CORS（如果可用）
    if CORS_AVAILABLE:
        CORS(app)
    
    # 基本健康检查接口
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "ok",
            "mode": "simple",
            "message": "浮图图像搜索系统运行中（简化模式）"
        })
    
    @app.route('/api/datasets', methods=['GET'])
    def get_datasets():
        # 扫描datasets目录
        datasets = []
        datasets_dir = os.path.join("datasets")
        if os.path.exists(datasets_dir):
            for item in os.listdir(datasets_dir):
                item_path = os.path.join(datasets_dir, item)
                if os.path.isdir(item_path):
                    # 计算图片数量
                    image_count = 0
                    for file in os.listdir(item_path):
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                            image_count += 1
                    
                    datasets.append({
                        "id": hash(item) % 1000,
                        "name": item,
                        "description": f"数据集 {item}",
                        "image_count": image_count,
                        "has_index": False
                    })
        
        return jsonify({"datasets": datasets})
    
    @app.route('/api/search', methods=['POST'])
    def search():
        return jsonify({
            "msg": "搜索功能需要Redis和计算端支持，当前为简化模式",
            "results": []
        })
    
    # 创建必要目录
    os.makedirs('data/indexes', exist_ok=True)
    os.makedirs('data/uploads', exist_ok=True)
    os.makedirs('data/progress', exist_ok=True)
    os.makedirs('datasets', exist_ok=True)
    
    return app

def run_simple_app():
    """运行简化应用"""
    # 设置工作目录
    current_dir = os.getcwd()
    target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if current_dir != target_dir:
        os.chdir(target_dir)
    
    print("启动浮图图像搜索系统（简化模式）")
    
    app = create_simple_app()
    
    try:        app.run(
            host='0.0.0.0',
            port=19198,
            debug=False  # 关闭debug模式避免重启问题
        )
    except KeyboardInterrupt:
        print("停止服务...")

if __name__ == '__main__':
    run_simple_app()
