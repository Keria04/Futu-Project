import os
import base64
import numpy as np
from PIL import Image
from model_module.feature_extractor import feature_extractor
from faiss_module.build_index import build_index
from worker import generate_embeddings_task
from database_module.modify import insert_one, insert_multi, update
from database_module.query import query_one
from config import config
import datetime

class IndexBuilder:
    """
    索引构建核心类，外部请通过 factory.py 或 api.py 调用，不要直接实例化本类
    """
    def __init__(self, dataset_dir, dataset_name, distributed=False):
        self.dataset_dir = dataset_dir
        self.dataset_name = dataset_name
        self.distributed = distributed
        self.img_exts = ('.jpg', '.jpeg', '.png', '.bmp')
        self.features_path = getattr(config, "FEATURE_PATH", "features.npy")
        self.ids_path = getattr(config, "ID_PATH", "ids.npy")
        self.index_path = getattr(config, "INDEX_PATH", "index.bin")
        self.id_map = {}
        self.distributed_available = getattr(config, "DISTRIBUTED_AVAILABLE", False)

    def build(self):
        img_files = [f for f in os.listdir(self.dataset_dir) if f.lower().endswith(self.img_exts) and f != 'query.jpg']
        img_files.sort()
        if not img_files:
            print(f"数据集目录 {self.dataset_dir} 下没有可用图片文件")
            raise ValueError(f"数据集目录 {self.dataset_dir} 下没有可用图片文件")
        features = []
        ids = []
        image_records = []
        self.id_map.clear()
        if self.distributed and self.distributed_available:
            print("尝试使用远程特征提取构建索引...")
            task_futures = []
            for idx, fname in enumerate(img_files):
                path = os.path.join(self.dataset_dir, fname)
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
                    self.id_map[idx] = fname
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
                path = os.path.join(self.dataset_dir, fname)
                img = Image.open(path)
                feat = embedder.calculate(img)
                self.id_map[idx] = fname
                features.append(feat)
                ids.append(idx)
            print("已采用本地特征提取。")
        features = np.stack(features).astype('float32')
        ids = np.array(ids, dtype='int64')
        # np.save(self.features_path, features)
        # np.save(self.ids_path, ids)
        # print("ids内容:", ids)
        # print("features内容:", features)
        # print(f"特征已保存到 {self.features_path}，ID已保存到 {self.ids_path}")

        # 写入数据库
        dataset_id = self._update_database(len(img_files), features.nbytes)

        # 先删除该数据集下旧图片记录，再插入新记录
        from database_module.modify import delete
        delete("images", {"dataset_id": dataset_id})

        # 不再手动指定 id 字段，交由数据库自增主键分配，避免 UNIQUE constraint failed
        for idx, fname in enumerate(img_files):
            image_path = os.path.join(self.dataset_dir, fname)
            feature_vector = features[idx].tobytes()
            image_records.append({
                "dataset_id": dataset_id,
                "image_path": image_path,
                "resource_type": "control",
                "metadata_json": None,
                "feature_vector": feature_vector,
                "external_ids": None
            })
        from database_module.modify import insert_multi
        insert_multi("images", image_records)
        print(f"已写入 {len(image_records)} 条图片特征到数据库。")

        # 重新查询插入后的图片id顺序，保证索引id与数据库一致
        from database_module.query import query_multi
        rows = query_multi(
            "images",
            columns="id",
            where={"dataset_id": dataset_id},
            order_by="id ASC"
        )
        db_ids = np.array([row[0] for row in rows], dtype='int64')

        # 使用build_index构建索引，传入数据集名称作为索引文件名
        build_index(features, db_ids, name=f"{dataset_id}.index")

        return True

    def _update_database(self, image_count, feature_bytes):
        now = datetime.datetime.now()
        # 查询数据集是否已存在
        dataset = query_one("datasets", where={"name": self.dataset_name})
        if dataset is None:
            # 新建数据集
            dataset_id = insert_one("datasets", {
                "name": self.dataset_name,
                "created_at": now,
                "last_rebuild": now,
                "image_count": image_count,
                "size": str(feature_bytes)
            })
        else:
            # 更新数据集
            update("datasets", {
                "last_rebuild": now,
                "image_count": image_count,
                "size": str(feature_bytes)
            }, where={"name": self.dataset_name})
            dataset_id = dataset[0]  # 假设id在第一个字段
        return dataset_id
