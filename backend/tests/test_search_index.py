import numbers
import unittest
import numpy as np
import os
import shutil
import tempfile
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import config
from backend.faiss_module.indexer import FaissIndexer
from backend.faiss_module.search_index import search_index


class TestSearchIndex(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_index_folder = config.INDEX_FOLDER
        config.INDEX_FOLDER = self.temp_dir

        self.dim = config.VECTOR_DIM
        self.index1 = "test1.index"
        self.index2 = "test2.index"

        # 创建两份非常接近的索引
        self.id1 = np.arange(5)
        self.vec1 = np.random.rand(5, self.dim).astype("float32")
        self.id2 = np.arange(5, 10)
        self.vec2 = np.random.rand(5, self.dim).astype("float32")

        self.query_vec = self.vec1[0]  # 确保能命中 top1

        # 写入索引1
        self.indexer1 = FaissIndexer(dim=self.dim, index_path=os.path.join(self.temp_dir, self.index1), use_IVF=True)
        self.indexer1.build_index(self.vec1, self.id1)
        self.indexer1.save_index()

        # 写入索引2
        self.indexer2 = FaissIndexer(dim=self.dim, index_path=os.path.join(self.temp_dir, self.index2), use_IVF=True)
        self.indexer2.build_index(self.vec2, self.id2)
        self.indexer2.save_index()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        config.INDEX_FOLDER = self.original_index_folder

    def test_search_single_index(self):
        ids, sims = search_index(self.query_vec, self.index1, top_k=3)
        self.assertEqual(len(ids), 3)
        self.assertTrue(all(isinstance(i, numbers.Integral) for i in ids))
        self.assertTrue(all(0 <= s <= 100 for s in sims))

    def test_search_multiple_indices(self):
        ids, sims = search_index(self.query_vec, [self.index1, self.index2], top_k=5)
        self.assertEqual(len(ids), 5)
        self.assertTrue(all(isinstance(i, numbers.Integral) for i in ids))
        self.assertTrue(all(0 <= s <= 100 for s in sims))

    def test_missing_index_file(self):
        # 一个索引存在，一个不存在
        ids, sims = search_index(self.query_vec, [self.index1, "missing.index"], top_k=3)
        self.assertEqual(len(ids), 3)

    def test_top_k_less_than_one(self):
        with self.assertRaises(ValueError):
            search_index(self.query_vec, self.index1, top_k=0)

    def test_query_vector_dimension(self):
        # 一维向量输入测试
        ids, sims = search_index(self.query_vec.flatten(), self.index1, top_k=2)
        self.assertEqual(len(ids), 2)

        # 三维错误向量
        with self.assertRaises(ValueError):
            search_index(self.query_vec.reshape(1, 1, -1), self.index1, top_k=2)