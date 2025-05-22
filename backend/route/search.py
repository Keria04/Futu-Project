from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import os
from model_module.feature_extractor import feature_extractor
from faiss_module.search_index import search_index
from config import config

search_bp = Blueprint('search', __name__)

DATASET_DIR = config.DATASET_DIR
UPLOAD_FOLDER = config.UPLOAD_FOLDER

@search_bp.route('/api/search', methods=['POST'])
def api_search():
    img_exts = ('.jpg', '.jpeg', '.png', '.bmp')
    img_files = [f for f in os.listdir(DATASET_DIR) if f.lower().endswith(img_exts)]
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
