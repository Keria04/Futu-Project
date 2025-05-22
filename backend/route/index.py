from flask import Blueprint, jsonify

index_bp = Blueprint('index', __name__)

@index_bp.route('/', methods=['GET'])
def index():
    return jsonify({"msg": "请使用前端页面进行操作。"})
