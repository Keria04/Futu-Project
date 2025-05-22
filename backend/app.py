import os
# 检查并设置工作目录为 app.py 的上一级目录
current_dir = os.getcwd()
target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if current_dir != target_dir:
    os.chdir(target_dir)


import sys
from flask import Flask
from werkzeug.utils import secure_filename
# 添加项目根路径，便于导入 config 和模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import config
from PIL import Image

app = Flask(__name__)

# 注册蓝图
from route.index import index_bp
from route.build_index import build_index_bp
from route.search import search_bp
from route.image import image_bp

app.register_blueprint(index_bp)
app.register_blueprint(build_index_bp)
app.register_blueprint(search_bp)
app.register_blueprint(image_bp)

if __name__ == '__main__':
    app.run(debug=True, port=19198)
