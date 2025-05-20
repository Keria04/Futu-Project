import os
import numpy as np
from PIL import Image
import time
from flask import Flask, request, render_template_string, redirect, url_for
from werkzeug.utils import secure_filename
from Model_module.calculate_embeded import calaculate_embeded
from Faiss_module.build_index import build_index
from Faiss_module.search_index import search_index
from config import config

app = Flask(__name__)

DATASET_DIR = os.path.join(os.path.dirname(__file__), '..', 'datasets')
INDEX_PATH = config.INDEX_PATH
FEATURES_PATH = config.FEATURE_PATH
IDS_PATH = config.ID_PATH

# 启动时构建图片向量和索引
def prepare_index():
    img_exts = ('.jpg', '.jpeg', '.png', '.bmp')
    img_files = [f for f in os.listdir(DATASET_DIR) if f.lower().endswith(img_exts) and f != 'query.jpg']
    img_files.sort()
    img_paths = [os.path.join(DATASET_DIR, f) for f in img_files]

    embedder = calaculate_embeded()
    features = []
    ids = []

    start_time = time.time()
    for idx, path in enumerate(img_paths):
        img = Image.open(path)
        feat = embedder.calculate(img)
        features.append(feat)
        ids.append(idx)
    features = np.stack(features).astype('float32')
    ids = np.array(ids, dtype='int64')
    end_time = time.time()
    print(f"特征提取与保存耗时: {end_time - start_time:.2f} 秒")

    np.save(FEATURES_PATH, features)
    np.save(IDS_PATH, ids)
    print(f"特征已保存到 {FEATURES_PATH}，ID已保存到 {IDS_PATH}")

    build_index()
    print("索引已构建完成。")

# 上传页面模板
UPLOAD_HTML = """
<!doctype html>
<title>图片检索</title>
<h1>上传查询图片</h1>
<form method=post enctype=multipart/form-data>
  <input type=file name=query_img>
  <input type=submit value=上传>
</form>
{% if results %}
    <h2>检索结果：</h2>
    <ol>
    {% for fname, dist in results %}
        <li>{{ fname }} (距离: {{ "%.4f"|format(dist) }})</li>
    {% endfor %}
    </ol>
{% endif %}
"""

@app.route('/', methods=['GET', 'POST'])
def upload_and_search():
    results = None
    img_exts = ('.jpg', '.jpeg', '.png', '.bmp')
    img_files = [f for f in os.listdir(DATASET_DIR) if f.lower().endswith(img_exts) and f != 'query.jpg']
    img_files.sort()
    embedder = calaculate_embeded()
    if request.method == 'POST':
        file = request.files.get('query_img')
        if file and file.filename:
            filename = secure_filename(file.filename)
            save_path = os.path.join(config.UPLOAD_FOLDER, filename)
            file.save(save_path)
            img = Image.open(save_path)
            query_feat = embedder.calculate(img).reshape(1, -1)
            indices = search_index(query_feat, top_k=5)  # D 实际为编号list
            results = [(img_files[idx], idx) for idx in indices]
    return render_template_string(UPLOAD_HTML, results=results)

if __name__ == '__main__':
    prepare_index()
    app.run(debug=True)
