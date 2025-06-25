# 图片搜索功能使用说明

## 🎉 重写完成

我已经完全重写了图片搜索功能，现在使用真实的FAISS索引进行图片相似度搜索。

## ✅ 验证结果

所有检查都已通过：
- ✅ 导入依赖正确
- ✅ 主要函数完整
- ✅ API结构正确
- ✅ 依赖文件存在
- ✅ 错误处理完善
- ✅ 响应格式标准

## 🔧 主要功能

### 1. 真实的FAISS索引搜索
- 使用 `_index_interface.py` 调用FAISS索引
- 支持多数据集并行搜索
- 基于特征向量的相似度计算

### 2. 完整的图片处理流程
```
上传图片 → 图片裁剪(可选) → 特征提取 → 索引搜索 → 结果排序 → 返回结果
```

### 3. 高级搜索参数
- **top_k**: 返回结果数量限制
- **similarity_threshold**: 相似度阈值过滤
- **crop_region**: 图片裁剪区域
- **dataset_names**: 指定搜索的数据集

## 🚀 使用方法

### 1. 启动必要服务

```bash
# 1. 启动Redis服务 (Windows)
redis-server

# 2. 启动计算端服务
cd backend_new/compute_server
python compute_server_fixed.py

# 3. 启动后端服务
cd backend_new
python run.py
```

### 2. 构建索引 (必须先完成)

在使用搜索功能前，需要先为数据集构建索引：

- 方法1: 使用前端界面的"索引构建"功能
- 方法2: 使用API调用 `POST /api/build_index`

### 3. 测试搜索功能

```bash
# 运行自动化测试
python test_search_function.py

# 或手动测试
curl -X POST http://localhost:5000/api/search \
  -F "query_img=@test_image.jpg" \
  -F "dataset_names[]=1" \
  -F "dataset_names[]=2" \
  -F "top_k=10" \
  -F "similarity_threshold=50.0"
```

## 📊 API使用示例

### 请求示例 (JavaScript)
```javascript
const formData = new FormData();
formData.append('query_img', fileInput.files[0]);
formData.append('dataset_names[]', '1');
formData.append('dataset_names[]', '2');
formData.append('top_k', 10);
formData.append('similarity_threshold', 50.0);

// 可选的裁剪参数
formData.append('crop_x', 100);
formData.append('crop_y', 100);
formData.append('crop_w', 200);
formData.append('crop_h', 200);

fetch('/api/search', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

### 响应示例
```json
{
  "success": true,
  "results": [
    {
      "image_id": 123,
      "image_path": "/path/to/image.jpg",
      "img_url": "/show_image/datasets/1/image.jpg",
      "fname": "image.jpg",
      "similarity": 95.67,
      "distance": 0.0433,
      "dataset": "dataset1",
      "dataset_id": 1,
      "rank": 1,
      "file_size": 156789,
      "created_at": "2025-06-25T10:00:00"
    }
  ],
  "total_found": 5,
  "search_params": {
    "crop_region": {"x": 100, "y": 100, "width": 200, "height": 200},
    "datasets": ["1", "2"],
    "top_k": 10,
    "similarity_threshold": 50.0
  },
  "query_info": {
    "original_filename": "query.jpg",
    "query_time": "2025-06-25T15:44:36"
  }
}
```

## 🔧 技术架构

### 依赖关系
```
search_routes.py
├── _index_interface.py (FAISS索引管理)
├── _database_interface.py (数据库查询)
├── redis_client/ (特征提取通信)
└── PIL (图片处理)
```

### 搜索流程
1. **文件验证**: 检查上传的图片文件格式
2. **参数解析**: 解析搜索参数和裁剪区域
3. **图片预处理**: 保存临时文件，执行裁剪(如需要)
4. **特征提取**: 通过Redis调用计算端提取特征向量
5. **索引搜索**: 使用FAISS索引进行相似度搜索
6. **结果处理**: 合并多数据集结果，按相似度排序
7. **信息补充**: 从数据库获取图片详细信息
8. **响应返回**: 返回格式化的搜索结果

## 🐛 故障排除

### 常见问题

1. **"Redis客户端不可用"**
   - 确保Redis服务正在运行
   - 检查Redis连接配置

2. **"特征提取失败"**
   - 确保计算端服务正在运行
   - 检查图片文件是否损坏

3. **"索引文件不存在"**
   - 先为相关数据集构建索引
   - 检查索引文件路径

4. **"数据集不存在"**
   - 确保数据集已在数据库中创建
   - 检查数据集名称是否正确

### 调试方法

1. **查看日志**
   ```bash
   tail -f backend_new/futu_backend.log
   ```

2. **检查服务状态**
   ```bash
   # 检查后端服务
   curl http://localhost:5000/api/datasets
   
   # 检查Redis连接
   redis-cli ping
   ```

3. **运行测试脚本**
   ```bash
   python test_search_function.py
   ```

## 📈 性能优化

### 搜索性能
- 索引器缓存: 避免重复创建索引器对象
- 并行搜索: 支持多数据集并行查询
- 结果过滤: 相似度阈值预过滤

### 内存管理
- 临时文件自动清理
- Redis任务结果及时删除
- 特征向量高效处理

## 🎯 下一步扩展

可能的功能扩展：
- 批量图片搜索
- 搜索结果缓存
- 搜索历史记录
- 高级相似度算法
- 图片元数据搜索

现在图片搜索功能已经完全重写并可以正常使用！🚀
