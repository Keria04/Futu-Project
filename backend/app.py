import os
import numpy as np
from PIL import Image
import time
from model_module.calculate_embeded import calaculate_embeded
from faiss_module.build_index import build_index
from faiss_module.search_index import search_index
from config import config

# 配置
DATASET_DIR = os.path.join(os.path.dirname(__file__), '..', 'datasets')
INDEX_PATH = config.INDEX_PATH
QUERY_IMG = os.path.join(DATASET_DIR, 'query.jpg')
FEATURES_PATH = config.FEATURE_PATH
IDS_PATH = config.ID_PATH

# 1. 提取所有图片特征（除query.jpg）
img_exts = ('.jpg', '.jpeg', '.png', '.bmp')
img_files = [f for f in os.listdir(DATASET_DIR) if f.lower().endswith(img_exts) and f != 'query.jpg']
img_files.sort()
img_paths = [os.path.join(DATASET_DIR, f) for f in img_files]

embedder = calaculate_embeded()
features = []
ids = []

start_time = time.time()  # 计时开始
for idx, path in enumerate(img_paths):
    img = Image.open(path)
    feat = embedder.calculate(img)
    features.append(feat)
    ids.append(idx)
features = np.stack(features).astype('float32')
ids = np.array(ids, dtype='int64')
end_time = time.time()  # 计时结束

print(f"特征提取与保存耗时: {end_time - start_time:.2f} 秒")

# 保存特征和ID到 app.py 同层
np.save(FEATURES_PATH, features)
np.save(IDS_PATH, ids)
print(f"特征已保存到 {FEATURES_PATH}，ID已保存到 {IDS_PATH}")

# 2. 构建索引
build_index()

# 3. 查询 query.jpg
query_img = Image.open(QUERY_IMG)
query_feat = embedder.calculate(query_img).reshape(1, -1)

D= search_index(query_feat, top_k=5)

# 4. 输出结果
print("查图结果：")
for i in D:
    print(f"相似图像编号：{i}")
