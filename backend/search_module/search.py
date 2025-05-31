import numpy as np
import os
from PIL import Image
from werkzeug.utils import secure_filename
from model_module.feature_extractor import feature_extractor
from database_module.query import query_one, query_multi
from config import config
from faiss_module.search_index import search_index
import json

def get_features_and_ids(dataset_id):
    """
    从数据库读取指定数据集的所有图片特征和ID
    :param dataset_id: 数据集ID
    :return: features (np.ndarray), ids (np.ndarray), image_paths (list), descriptions (list)
    """
    rows = query_multi(
        "images",
        columns="id, feature_vector, image_path, metadata_json",
        where={"dataset_id": dataset_id},
        order_by="id ASC"
    )
    if not rows:
        return None, None, None, None
    ids = []
    features = []
    image_paths = []
    descriptions = []
    for row in rows:
        img_id, feat_blob, img_path, metadata_json = row
        ids.append(img_id)
        features.append(np.frombuffer(feat_blob, dtype=np.float32))
        image_paths.append(img_path)
        if metadata_json:
            try:
                desc = json.loads(metadata_json)
            except Exception:
                desc = {}
        else:
            desc = {}
        descriptions.append(desc)
    features = np.stack(features).astype('float32')
    ids = np.array(ids, dtype='int64')
    return features, ids, image_paths, descriptions

def search_image(dataset_names, file_storage, crop_box):
    """
    工厂接口：处理图片检索
    :param dataset_names: 数据集名称列表
    :param file_storage: werkzeug.datastructures.FileStorage 上传的图片对象
    :param crop_box: (x, y, w, h) 裁剪参数
    :return: 检索结果列表
    """
    # 查询所有数据集ID
    dataset_ids = []
    for name in dataset_names:
        dataset = query_one("datasets", where={"name": name})
        if not dataset:
            return {"error": f"数据集不存在: {name}"}
        dataset_ids.append(dataset[0])

    # 合并所有数据集的特征和ID
    all_features, all_ids, all_image_paths, all_descriptions = [], [], [], []
    for dataset_id in dataset_ids:
        features, ids, image_paths, descriptions = get_features_and_ids(dataset_id)
        if features is not None and ids is not None and len(features) > 0:
            all_features.append(features)
            all_ids.append(ids)
            all_image_paths.extend(image_paths)
            all_descriptions.extend(descriptions)
    if not all_features or not all_ids:
        return {"error": "所选数据集没有图片特征"}
    features = np.concatenate(all_features, axis=0)
    ids = np.concatenate(all_ids, axis=0)
    image_paths = all_image_paths
    descriptions = all_descriptions

    # 保存上传图片
    filename = secure_filename(file_storage.filename)
    save_path = os.path.join(config.UPLOAD_FOLDER, filename)
    file_storage.save(save_path)

    # 裁剪图片
    x, y, w, h = crop_box
    img = Image.open(save_path)
    if w > 0 and h > 0:
        img = img.crop((x, y, x + w, y + h))
    embedder = feature_extractor()
    query_feat = embedder.calculate(img).reshape(1, -1)

    # 使用 faiss_module.search_index 查找 top
    # 索引文件名约定为 {数据集编号}.index
    index_names = [f"{dataset_id}.index" for dataset_id in dataset_ids]
    indices, similarities = search_index(query_feat, index_names, top_k=5)

    results = []
    for idx, sim in zip(indices, similarities):
        # idx 可能为 -1（faiss未命中），需判断
        if idx == -1 or idx not in ids:
            continue
        # 找到对应图片路径
        id_pos = np.where(ids == idx)[0]
        if len(id_pos) == 0:
            continue
        img_path = image_paths[id_pos[0]]
        desc = descriptions[id_pos[0]] if descriptions else {}
        # print(f"检索到图片: {img_path}, 相似度: {sim:.4f}")
        # 兼容图片路径为绝对路径或相对路径，取文件名
        fname = os.path.basename(img_path)
        # 若图片实际存储在 data/数据集名/ 下，前端 show_image 需要传递数据集名
        # 这里返回数据集名和文件名，前端拼接 show_image/数据集名/文件名
        # 先尝试从 img_path 提取数据集名
        dataset_dir = os.path.basename(os.path.dirname(img_path))
        img_url = f'/show_image/{dataset_dir}/{fname}'
        results.append({
            "fname": fname,
            "idx": int(idx),
            "img_url": img_url,
            "similarity": float(sim),
            "dataset": dataset_dir,
            "description": desc
        })
    return results
