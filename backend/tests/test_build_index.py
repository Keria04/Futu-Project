import unittest
import numpy as np
import os
import shutil
import tempfile
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# 导入你的 build_index 函数及配置
from backend.faiss_module.build_index import build_index
from config import config

class TestBuildIndex(unittest.TestCase):
    def setUp(self):
        # 创建临时文件夹，模拟 config.INDEX_FOLDER
        self.temp_dir = tempfile.mkdtemp()
        self.original_index_folder = config.INDEX_FOLDER
        config.INDEX_FOLDER = self.temp_dir

        # 构造测试数据
        self.features = np.random.rand(10, config.VECTOR_DIM).astype('float32')
        self.ids = np.arange(10).astype('int64')
        self.index_name = "test.index"

    def tearDown(self):
        # 清理测试创建的临时目录
        shutil.rmtree(self.temp_dir)
        config.INDEX_FOLDER = self.original_index_folder

    def test_build_index_success(self):
        """测试正常构建索引"""
        build_index(self.features, self.ids, self.index_name)
        saved_path = os.path.join(config.INDEX_FOLDER, self.index_name)
        self.assertTrue(os.path.exists(saved_path))

    def test_none_input_should_raise(self):
        """测试 None 输入应抛出异常"""
        with self.assertRaises(ValueError):
            build_index(None, self.ids, self.index_name)

        with self.assertRaises(ValueError):
            build_index(self.features, None, self.index_name)

    def test_mismatched_length_should_raise(self):
        """测试特征和 ID 长度不匹配应抛出异常"""
        with self.assertRaises(ValueError):
            build_index(self.features, self.ids[:-1], self.index_name)

if __name__ == '__main__':
    unittest.main()