import os
import base64
import sys
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
# 添加项目根路径，便于导入 config 和模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import config
from PIL import Image

from model_module.feature_extractor import feature_extractor
from faiss_module.build_index import build_index
from faiss_module.search_index import search_index
from worker import generate_embeddings_task

app = Flask(__name__)

DATASET_DIR = os.path.join(os.path.dirname(__file__), '..', 'datasets')
INDEX_PATH = getattr(config, "INDEX_PATH", "index.bin")
FEATURES_PATH = getattr(config, "FEATURE_PATH", "features.npy")
IDS_PATH = getattr(config, "ID_PATH", "ids.npy")
UPLOAD_FOLDER = config.UPLOAD_FOLDER
DISTRIBUTED_AVAILABLE = getattr(config, "DISTRIBUTED_AVAILABLE", False)
id_map = {}

def prepare_index(distributed=False):
    img_exts = ('.jpg', '.jpeg', '.png', '.bmp')
    img_files = [f for f in os.listdir(DATASET_DIR) if f.lower().endswith(img_exts) and f != 'query.jpg']
    img_files.sort()
    features = []
    ids = []
    id_map.clear()
    if distributed and DISTRIBUTED_AVAILABLE:
        print("尝试使用远程特征提取构建索引...")
        task_futures = []
        for idx, fname in enumerate(img_files):
            path = os.path.join(DATASET_DIR, fname)
            with open(path, 'rb') as f:
                img_data = f.read()
            img_data_b64 = base64.b64encode(img_data).decode('utf-8')
            try:
                future = generate_embeddings_task.delay(img_data_b64)
                task_futures.append((idx, fname, future))
            except Exception as e:
                print(f"远程任务提交失败: {e}")
                return False
        for idx, fname, future in task_futures:
            try:
                embedding_list = future.get(timeout=60)
                embedding = np.array(embedding_list, dtype='float32').reshape(1, -1)
                id_map[idx] = fname
                features.append(embedding.squeeze())
                ids.append(idx)
            except Exception as e:
                print(f"处理图片 {fname} 时发生错误: {e}")
                return False
        print("已采用远程特征提取。")
    else:
        print("采用本地特征提取构建索引...")
        embedder = feature_extractor()
        for idx, fname in enumerate(img_files):
            path = os.path.join(DATASET_DIR, fname)
            img = Image.open(path)
            feat = embedder.calculate(img)
            id_map[idx] = fname
            features.append(feat)
            ids.append(idx)
        print("已采用本地特征提取。")
    features = np.stack(features).astype('float32')
    ids = np.array(ids, dtype='int64')
    np.save(FEATURES_PATH, features)
    np.save(IDS_PATH, ids)
    print(f"特征已保存到 {FEATURES_PATH}，ID已保存到 {IDS_PATH}")
    
    # 使用build_index构建索引
    build_index()
    print("索引已构建完成。")
    print("数据集特征与索引构建完成，可以进行图片检索。")
    return True

@app.route('/', methods=['GET'])
def index():
    return jsonify({"msg": "请使用前端页面进行操作。"})

@app.route('/api/build_index', methods=['POST'])
def api_build_index():
    prepare_index(distributed=False)
    return jsonify({"msg": "本地数据集特征与索引已构建完成，可以进行图片检索。"})

@app.route('/api/build_index_distributed', methods=['POST'])
def api_build_index_distributed():
    if DISTRIBUTED_AVAILABLE:
        ok = prepare_index(distributed=True)
        if ok:
            return jsonify({"msg": "远程数据集特征与索引已构建完成，可以进行图片检索。"})
        else:
            return jsonify({"msg": "远程构建失败，已跳过。"}), 500
    else:
        return jsonify({"msg": "远程worker不可用，无法远程构建。"}), 400

@app.route('/api/search', methods=['POST'])
def api_search():
    img_exts = ('.jpg', '.jpeg', '.png', '.bmp')
    img_files = [f for f in os.listdir(DATASET_DIR) if f.lower().endswith(img_exts) and f != 'query.jpg']
    img_files.sort()
    file = request.files.get('query_img')
    if not file or not file.filename:
        return jsonify({"msg": "未上传图片"}), 400
    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)
    try:
        x = int(request.form.get('crop_x', 0))
        y = int(request.form.get('crop_y', 0))
        w = int(request.form.get('crop_w', 0))
        h = int(request.form.get('crop_h', 0))
    except Exception:
        x, y, w, h = 0, 0, 0, 0
    img = Image.open(save_path)
    if w > 0 and h > 0:
        img = img.crop((x, y, x + w, y + h))
    embedder = feature_extractor()
    query_feat = embedder.calculate(img).reshape(1, -1)
    indices = search_index(query_feat, top_k=5)
    results = []
    for idx in indices:
        fname = img_files[idx]
        img_url = '/show_image/' + fname
        results.append({"fname": fname, "idx": idx, "img_url": img_url})
    return jsonify({"results": results})

@app.route('/show_image/<filename>')
def show_image(filename):
    return send_from_directory(DATASET_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True, port=19198)
