from flask import Blueprint, send_from_directory
import os
from config import config

image_bp = Blueprint('image', __name__)

@image_bp.route('/show_image/<dataset>/<filename>')
def show_image(dataset, filename):
    # 兼容多数据集目录
    dataset_dir = os.path.join(config.DATASET_DIR, dataset)
    return send_from_directory(dataset_dir, filename)
