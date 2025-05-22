from flask import Blueprint, send_from_directory
import os
from config import config

image_bp = Blueprint('image', __name__)

DATASET_DIR = config.DATASET_DIR

@image_bp.route('/show_image/<filename>')
def show_image(filename):
    return send_from_directory(DATASET_DIR, filename)
