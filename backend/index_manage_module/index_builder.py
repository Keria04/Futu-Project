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
import csv
import json
from tqdm import tqdm

# ========================
# 索引构建核心类定义
# ========================
class IndexBuilder:
    """
    索引构建核心类，外部请通过 factory.py 或 api.py 调用，不要直接实例化本类
    """
    # ---------- 初始化部分 ----------
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

    def _write_progress_to_file(self, progress_file, current, total):
        """将当前进度写入文件"""
        if progress_file:
            try:
                percent = int(current / total * 100) if total > 0 else 100
                progress_bar = "█" * (percent // 10) + "▏" * (1 if percent % 10 >= 5 else 0)
                progress_bar = progress_bar.ljust(10)
                with open(progress_file, "w", encoding="utf-8") as f:
                    f.write(f"特征提取: {percent:3d}%|{progress_bar}| {current}/{total}\n")
            except Exception as e:
                print(f"写入进度文件时出错: {e}")

    # ---------- 索引构建主流程 ----------
    def build(self, progress_file=None):
        # --- 1. 读取图片文件和描述信息 ---
        img_files = [f for f in os.listdir(self.dataset_dir) if f.lower().endswith(self.img_exts) and f != 'query.jpg']
        desc_map = {}
        csv_files = [f for f in os.listdir(self.dataset_dir) if f.lower().endswith('.csv')]
        if csv_files:
            desc_csv_path = os.path.join(self.dataset_dir, csv_files[0])
            with open(desc_csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)
                if rows and len(rows[0]) > 1:
                    header = rows[0][1:]
                    for row in rows[1:]:
                        if not row or len(row) < 2:
                            continue
                        fname = row[0]
                        desc_dict = {header[i]: row[i+1] if i+1 < len(row) else "" for i in range(len(header))}
                        desc_json = json.dumps(desc_dict, ensure_ascii=False)
                        desc_map[fname] = desc_json
        if not img_files:
            print(f"数据集目录 {self.dataset_dir} 下没有可用图片文件")
            raise ValueError(f"数据集目录 {self.dataset_dir} 下没有可用图片文件")
        features = []
        image_records = []
        self.id_map.clear()

        # --- 1.5 读取数据库图片路径，处理新增和已删除图片 ---
        from database_module.query import query_one, query_multi
        dataset = query_one("datasets", where={"name": self.dataset_name})
        dataset_id = dataset[0] if dataset else None
        db_id_path_map = {}
        if dataset_id is not None:
            rows = query_multi(
                "images",
                columns="id, image_path",
                where={"dataset_id": dataset_id}
            )
            db_id_path_map = {row[0]: row[1] for row in rows}
        existing_paths = set(db_id_path_map.values())
        img_paths_set = set(os.path.join(self.dataset_dir, fname) for fname in img_files)

        # 新增图片
        img_files_to_process = [fname for fname in img_files if os.path.join(self.dataset_dir, fname) not in existing_paths]
        print(f"本次需要计算特征的图片数量: {len(img_files_to_process)}")        # 进度条初始化
        total_imgs = len(img_files_to_process)
        pbar = None
        if progress_file:
            if total_imgs > 0:
                # 先清空文件
                with open(progress_file, "w", encoding="utf-8") as f:
                    f.write("")  # 清空文件
                # 使用标准输出的tqdm，手动写入进度到文件
                pbar = tqdm(total=total_imgs, desc="特征提取", ncols=80)
            else:
                # 没有新图片需要处理时，直接写入完成状态
                with open(progress_file, "w", encoding="utf-8") as f:
                    f.write("特征提取: 100%|██████████| 0/0 [00:00<00:00]\n")
                    f.write("索引构建完成\n")
        processed_fnames = []
        # 删除数据库中已不存在的图片
        deleted_db_ids = [img_id for img_id, path in db_id_path_map.items() if path not in img_paths_set]
        if deleted_db_ids:
            from database_module.modify import delete
            for img_id in deleted_db_ids:
                delete("images", {"id": img_id})
            print(f"已从数据库删除 {len(deleted_db_ids)} 条已不存在图片的记录。")

        # --- 2. 特征提取（本地或分布式） ---
        if img_files_to_process:
            if self.distributed and self.distributed_available:
                print("尝试使用远程特征提取构建索引...")
                task_futures = []
                for idx, fname in enumerate(img_files_to_process):
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
                        if pbar: 
                            pbar.update(1)
                            # 更新进度文件
                            self._write_progress_to_file(progress_file, pbar.n, pbar.total)
                    except Exception as e:
                        print(f"处理图片 {fname} 时发生错误: {e}")
                        if pbar: 
                            pbar.update(1)
                            # 更新进度文件
                            self._write_progress_to_file(progress_file, pbar.n, pbar.total)
                        continue
                print("已采用远程特征提取。")
                if pbar:
                    pbar.close()
                    # 手动写入最终进度到文件
                    if progress_file:
                        with open(progress_file, "w", encoding="utf-8") as f:
                            f.write(f"特征提取: 100%|██████████| {total_imgs}/{total_imgs} [完成]\n")
                    # 在进度文件末尾添加完成标记
                    with open(progress_file, "a", encoding="utf-8") as f:
                        f.write("索引构建完成\n")
            else:
                print("采用本地特征提取构建索引...")
                embedder = feature_extractor()
                processed_fnames = []
                for idx, fname in enumerate(img_files_to_process):
                    path = os.path.join(self.dataset_dir, fname)
                    try:
                        img = Image.open(path)
                        feat = embedder.calculate(img)
                        self.id_map[idx] = fname
                        features.append(feat)
                        processed_fnames.append(fname)
                    except Exception as e:
                        print(f"[跳过] 图片 {fname} 处理失败: {e}")
                        continue
                    if pbar: 
                        pbar.update(1)
                        # 更新进度文件
                        self._write_progress_to_file(progress_file, pbar.n, pbar.total)
                print("已采用本地特征提取。")
            if pbar:
                pbar.close()
                # 手动写入最终进度到文件
                if progress_file:
                    with open(progress_file, "w", encoding="utf-8") as f:
                        f.write(f"特征提取: 100%|██████████| {total_imgs}/{total_imgs} [完成]\n")
                # 在进度文件末尾添加完成标记
                with open(progress_file, "a", encoding="utf-8") as f:
                    f.write("索引构建完成\n")
            if features:
                features = np.stack(features).astype('float32')
            # --- 3. 写入数据库（仅插入新图片） ---
            dataset_id = self._update_database(len(img_files), (features.nbytes if len(features) > 0 else 0))
            # 注意：只写入成功处理的图片
            for idx, fname in enumerate(processed_fnames if 'processed_fnames' in locals() else img_files_to_process):
                image_path = os.path.join(self.dataset_dir, fname)
                feature_vector = features[idx].tobytes()
                metadata_json = desc_map.get(fname) if desc_map else None
                image_records.append({
                    "dataset_id": dataset_id,
                    "image_path": image_path,
                    "resource_type": "control",
                    "metadata_json": metadata_json,
                    "feature_vector": feature_vector,
                    "external_ids": None
                })
            if image_records:
                from database_module.modify import insert_multi
                insert_multi("images", image_records)
                print(f"已写入 {len(image_records)} 条新图片特征到数据库。")
            else:
                print("没有新图片需要写入数据库。")
        else:
            # 如果没有新增图片，仍需更新 image_count
            if dataset_id is not None:
                self._update_database(len(img_files), 0)

        # --- 4. 查询数据库所有图片特征，构建索引文件 ---
        rows = query_multi(
            "images",
            columns="id, feature_vector, image_path",
            where={"dataset_id": dataset_id},
            order_by="id ASC"
        )
        # 只保留数据库中图片路径仍然存在于文件夹中的图片
        valid_rows = [row for row in rows if row[2] in img_paths_set]
        if len(valid_rows) > 0:
            db_ids = np.array([row[0] for row in valid_rows], dtype='int64')
            features = np.stack([np.frombuffer(row[1], dtype=np.float32) for row in valid_rows]).astype('float32')
            build_index(features, db_ids, name=f"{dataset_id}.index")
        else:
            print("没有有效图片可用于构建索引。")
        return True

    # ---------- 数据库更新辅助方法 ----------
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

    # ---------- 查询所有图片特征 ----------
    def get_all_image_features(self, dataset_name):
        """
        查询指定数据集下所有图片的id和特征向量（反序列化为numpy数组）
        返回: List[Tuple[int, np.ndarray]]
        """
        from database_module.query import query_one, query_multi
        # 查询数据集id
        dataset = query_one("datasets", where={"name": dataset_name})
        if dataset is None:
            raise ValueError(f"数据集 {dataset_name} 不存在")
        dataset_id = dataset[0]  # id在第一个字段
        # 查询所有图片的id和特征向量
        rows = query_multi(
            "images",
            columns="id, feature_vector",
            where={"dataset_id": dataset_id},
            order_by="id ASC"
        )
        result = []
        for row in rows:
            img_id = row[0]
            feat_bytes = row[1]
            feat = np.frombuffer(feat_bytes, dtype=np.float32)
            result.append((img_id, feat))
        return result
