from flask import Blueprint, jsonify, current_app
from config import config
import os
import base64
from PIL import Image
from model_module.feature_extractor import feature_extractor
from faiss_module.build_index import build_index
from worker import generate_embeddings_task
import numpy as np


build_index_bp = Blueprint('build_index', __name__)

@build_index_bp.route('/api/build_index', methods=['POST'])
def api_build_index():
    prepare_index(distributed=False)
    return jsonify({"msg": "本地数据集特征与索引已构建完成，可以进行图片检索。"})

@build_index_bp.route('/api/build_index_distributed', methods=['POST'])
def api_build_index_distributed():
    from app import prepare_index, DISTRIBUTED_AVAILABLE
    if DISTRIBUTED_AVAILABLE:
        ok = prepare_index(distributed=True)
        if ok:
            return jsonify({"msg": "远程数据集特征与索引已构建完成，可以进行图片检索。"})
        else:
            return jsonify({"msg": "远程构建失败，已跳过。"}), 500
    else:
        return jsonify({"msg": "远程worker不可用，无法远程构建。"}), 400

DATASET_DIR = config.DATASET_DIR
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
    print("ids内容:", ids)
    print("features内容:", features)
    print(f"特征已保存到 {FEATURES_PATH}，ID已保存到 {IDS_PATH}")
    
    # 使用build_index构建索引
    build_index()
    print("索引已构建完成。")
    print("数据集特征与索引构建完成，可以进行图片检索。")
    return True
