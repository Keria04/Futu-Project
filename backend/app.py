import os
# 检查并设置工作目录为 app.py 的上一级目录
current_dir = os.getcwd()
target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if current_dir != target_dir:
    os.chdir(target_dir)


import sys
from flask import Flask, send_from_directory
from werkzeug.utils import secure_filename
# 添加项目根路径，便于导入 config 和模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import config
from PIL import Image
from database_module.schema import create_tables
app = Flask(__name__)

# 静态资源映射：将 /datasets/ 映射到项目根目录下 datasets 文件夹
@app.route('/datasets/<path:filename>')
def serve_dataset_image(filename):
    abs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../datasets'))
    abs_file = os.path.join(abs_dir, filename)
    print(f"[DEBUG] 请求图片: {filename}")
    print(f"[DEBUG] 实际查找路径: {abs_file}")
    if not os.path.exists(abs_file):
        print(f"[ERROR] 文件不存在: {abs_file}")
        from flask import abort
        abort(404)
    # 明确指定 mimetype，防止浏览器识别异常
    from mimetypes import guess_type
    mimetype, _ = guess_type(abs_file)
    return send_from_directory(abs_dir, filename, mimetype=mimetype)

# 注册蓝图
from route.index import index_bp
from route.build_index import build_index_bp
from route.search import search_bp
from route.image import image_bp
from route.repeated_search import bp as repeated_search_bp
from route.get_dataset_id import bp as get_dataset_id_bp
from route.get_datasets import bp as get_datasets_bp
from route.upload_images import upload_bp
from route.get_image_by_id import get_image_by_id_bp

app.register_blueprint(index_bp)
app.register_blueprint(build_index_bp)
app.register_blueprint(search_bp)
app.register_blueprint(image_bp)
app.register_blueprint(repeated_search_bp)
app.register_blueprint(get_dataset_id_bp)
app.register_blueprint(get_datasets_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(get_image_by_id_bp)

if __name__ == '__main__':
    # 创建必要目录
    os.makedirs('data/indexes', exist_ok=True)
    os.makedirs('data/uploads', exist_ok=True)
    os.makedirs('datasets', exist_ok=True)
    
    # 确保数据库表已创建
    create_tables()
    
    app.run(debug=True, port=19198)
    # 运行 Flask 应用

