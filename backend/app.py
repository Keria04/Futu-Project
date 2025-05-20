import os
import base64
import sys
import numpy as np
from flask import Flask, request, render_template_string
from werkzeug.utils import secure_filename
# 添加项目根路径，便于导入 config 和模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import config
from PIL import Image

# 尝试导入分布式worker
try:
    from worker import generate_embeddings_task
    DISTRIBUTED_AVAILABLE = True
except Exception as e:
    print("分布式worker不可用，将使用本地特征提取。", e)
    DISTRIBUTED_AVAILABLE = False

from model_module.calculate_embeded import calaculate_embeded

app = Flask(__name__)

DATASET_DIR = os.path.join(os.path.dirname(__file__), '..', 'datasets')
INDEX_PATH = getattr(config, "INDEX_PATH", "index.bin")
FEATURES_PATH = getattr(config, "FEATURE_PATH", "features.npy")
IDS_PATH = getattr(config, "ID_PATH", "ids.npy")
UPLOAD_FOLDER = config.UPLOAD_FOLDER

import faiss

dimension = 2048  # 按你的模型输出维度
index = faiss.IndexFlatL2(dimension)
id_map = {}

def distributed_feature(img_path):
    with open(img_path, 'rb') as f:
        img_data = f.read()
    img_data_b64 = base64.b64encode(img_data).decode('utf-8')
    try:
        future = generate_embeddings_task.delay(img_data_b64)
        embedding_list = future.get(timeout=60)
        embedding = np.array(embedding_list, dtype='float32').reshape(1, -1)
        return embedding
    except Exception as e:
        print("分布式特征提取失败，切换到本地计算。", e)
        return None

def local_feature(img_path):
    embedder = calaculate_embeded()
    img = Image.open(img_path)
    feat = embedder.calculate(img).reshape(1, -1)
    return feat

def prepare_index():
    img_exts = ('.jpg', '.jpeg', '.png', '.bmp')
    img_files = [f for f in os.listdir(DATASET_DIR) if f.lower().endswith(img_exts) and f != 'query.jpg']
    img_files.sort()
    features = []
    ids = []
    task_futures = []
    distributed_failed = False

    if DISTRIBUTED_AVAILABLE:
        print("尝试使用分布式特征提取构建索引...")
        # 分布式特征提取
        for idx, fname in enumerate(img_files):
            path = os.path.join(DATASET_DIR, fname)
            with open(path, 'rb') as f:
                img_data = f.read()
            img_data_b64 = base64.b64encode(img_data).decode('utf-8')
            try:
                future = generate_embeddings_task.delay(img_data_b64)
                task_futures.append((idx, fname, future))
            except Exception as e:
                print(f"分布式任务提交失败: {e}")
                distributed_failed = True
                break

        if not distributed_failed:
            for idx, fname, future in task_futures:
                try:
                    embedding_list = future.get(timeout=60)
                    embedding = np.array(embedding_list, dtype='float32').reshape(1, -1)
                    index.add(embedding)
                    id_map[idx] = fname
                    features.append(embedding.squeeze())
                    ids.append(idx)
                except Exception as e:
                    print(f"处理图片 {fname} 时发生错误: {e}")
                    distributed_failed = True
                    break
            if not distributed_failed:
                print("已采用分布式特征提取。")
    # 如果分布式不可用或失败，则本地计算
    if not DISTRIBUTED_AVAILABLE or distributed_failed:
        print("采用本地特征提取构建索引...")
        embedder = calaculate_embeded()
        for idx, fname in enumerate(img_files):
            path = os.path.join(DATASET_DIR, fname)
            img = Image.open(path)
            feat = embedder.calculate(img)
            index.add(feat.reshape(1, -1))
            id_map[idx] = fname
            features.append(feat)
            ids.append(idx)
        print("已采用本地特征提取。")

    features = np.stack(features).astype('float32')
    ids = np.array(ids, dtype='int64')
    np.save(FEATURES_PATH, features)
    np.save(IDS_PATH, ids)
    print(f"特征已保存到 {FEATURES_PATH}，ID已保存到 {IDS_PATH}")
    print("索引已构建完成。")
    print("数据集特征与索引构建完成，可以进行图片检索。")

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
    {% for fname, idx in results %}
        <li>{{ fname }} (编号: {{ idx }})</li>
    {% endfor %}
    </ol>
{% endif %}
"""

@app.route('/', methods=['GET', 'POST'])
def upload_and_search():
    results = None
    img_exts = ('.jpg', '.jpeg', '.png', '.bmp')
    img_files = [UPLOAD_FOLDER]
    img_files.sort()
    if request.method == 'POST':
        file = request.files.get('query_img')
        if file and file.filename:
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)
            feat = None
            if DISTRIBUTED_AVAILABLE:
                feat = distributed_feature(save_path)
            if feat is None:
                feat = local_feature(save_path)
            D, I = index.search(feat, k=5)
            results = [(id_map.get(int(i), 'Unknown'), int(i)) for i in I[0]]
    return render_template_string(UPLOAD_HTML, results=results)

if __name__ == '__main__':
    prepare_index()
    app.run(debug=True, port=19198)
