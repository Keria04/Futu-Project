# 浮图图片检索系统 - 前后端API接口文档

## 概述

本文档详细描述了浮图图片检索系统前端与后端之间的所有API接口。系统采用Flask后端 + Vue3前端的架构，所有接口均以REST API形式提供。

## 基础配置

- **后端基础URL**: `http://localhost:19198`
- **API前缀**: `/api`
- **请求超时**: 30秒
- **支持的图片格式**: JPG, PNG, GIF, BMP, WEBP

## API接口列表

### 1. 索引构建相关接口

#### 1.1 构建索引
- **接口路径**: `POST /api/build_index`
- **功能描述**: 为指定数据集构建图片特征索引
- **前端调用位置**: `IndexBuilder.vue`
- **请求参数**:
```json
{
  "dataset_names": ["dataset1", "dataset2"],  // 数据集名称列表
  "distributed": false                        // 是否分布式构建
}
```
- **响应数据**:
```json
{
  "msg": "索引构建已启动",
  "progress": [
    {
      "dataset": "dataset1",
      "progress_file": "/api/build_index/progress/dataset1"
    }
  ]
}
```

#### 1.2 获取构建进度
- **接口路径**: `GET /api/build_index/progress/{dataset_name}`
- **功能描述**: 获取指定数据集的索引构建进度
- **前端调用位置**: `IndexBuilder.vue` (轮询调用)
- **路径参数**:
  - `dataset_name`: 数据集名称
- **响应数据**:
```json
{
  "progress": 85,           // 进度百分比 (0-100)
  "status": "building",     // 状态: pending/building/done/error
  "message": "正在提取特征...", // 当前状态描述 (可选)
  "current": 85,            // 当前处理数量 (可选)
  "total": 100              // 总数量 (可选)
}
```

**特殊情况处理**:
- 当没有新图片需要处理时，直接返回 `{"progress": 100, "status": "done", "message": "没有新图片需要处理"}`
- 当索引构建完成时，返回 `{"progress": 100, "status": "done", "message": "索引构建完成"}`

### 2. 图片检索相关接口

#### 2.1 图片相似度检索
- **接口路径**: `POST /api/search`
- **功能描述**: 上传查询图片，在指定数据集中搜索相似图片
- **前端调用位置**: `ImageSearch.vue`
- **请求格式**: `multipart/form-data`
- **请求参数**:
```
query_img: File                    // 查询图片文件
dataset_names: ["dataset1"]       // 搜索的数据集列表
crop_x: 100                       // 裁剪区域X坐标 (可选)
crop_y: 100                       // 裁剪区域Y坐标 (可选)
crop_w: 200                       // 裁剪区域宽度 (可选)
crop_h: 200                       // 裁剪区域高度 (可选)
```
- **响应数据**:
```json
{
  "results": [
    {
      "idx": 123,                           // 图片索引ID
      "fname": "image1.jpg",                // 文件名
      "img_url": "/api/image/dataset1/123", // 图片访问URL
      "dataset": "dataset1",                // 所属数据集
      "similarity": 95.67,                  // 相似度百分比
      "description": {                      // 图片描述信息 (可选)
        "category": "风景",
        "color": "蓝色"
      }
    }
  ]
}
```

### 3. 数据集管理相关接口

#### 3.1 获取数据集ID
- **接口路径**: `POST /api/get_dataset_id`
- **功能描述**: 根据数据集名称获取对应的内部ID
- **前端调用位置**: `DuplicateDetector.vue`
- **请求参数**:
```json
{
  "name": "dataset1"  // 数据集名称
}
```
- **响应数据**:
```json
{
  "id": 1,              // 数据集内部ID
  "name": "dataset1"    // 数据集名称
}
```

### 4. 重复图片检测相关接口

#### 4.1 查找重复图片
- **接口路径**: `POST /api/repeated_search`
- **功能描述**: 在指定数据集中查找相似度超过阈值的重复图片
- **前端调用位置**: `DuplicateDetector.vue`
- **请求参数**:
```json
{
  "index_id": 1,          // 数据集ID
  "threshold": 95,        // 相似度阈值 (80-100)
  "deduplicate": false    // 是否执行去重操作
}
```
- **响应数据**:
```json
{
  "groups": [
    [123, 456, 789],      // 重复图片组1的ID列表
    [101, 102]            // 重复图片组2的ID列表
  ],
  "total_groups": 2,      // 重复组总数
  "total_duplicates": 5   // 重复图片总数
}
```

### 5. 图片访问相关接口

#### 5.1 获取图片文件
- **接口路径**: `GET /api/image/{dataset_name}/{image_id}`
- **功能描述**: 根据数据集名称和图片ID获取图片文件
- **前端调用位置**: 在搜索结果中作为图片src使用
- **路径参数**:
  - `dataset_name`: 数据集名称
  - `image_id`: 图片ID
- **响应**: 返回图片二进制文件

## 前端API封装

前端在 `src/services/api.js` 中对所有后端接口进行了封装：

### API模块划分

1. **indexApi**: 索引构建相关
   - `buildIndex(dataset_names, distributed)`: 构建索引
   - `getProgress(progressUrl)`: 获取构建进度

2. **searchApi**: 图片检索相关
   - `searchImage(formData)`: 图片相似度检索

3. **datasetApi**: 数据集管理相关
   - `getDatasetId(name)`: 获取数据集ID

4. **duplicateApi**: 重复检测相关
   - `findDuplicates(index_id, threshold, deduplicate)`: 查找重复图片

### 请求拦截器配置

```javascript
// 基础配置
const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器 - 可扩展认证功能
api.interceptors.request.use(config => config)

// 响应拦截器 - 统一错误处理
api.interceptors.response.use(response => response, error => {
  console.error('API Error:', error)
  return Promise.reject(error)
})
```

## 前端组件与API的映射关系

| 组件 | 使用的API接口 | 功能描述 |
|------|---------------|----------|
| `IndexBuilder.vue` | `indexApi.buildIndex`<br>`indexApi.getProgress` | 索引构建和进度监控 |
| `ImageSearch.vue` | `searchApi.searchImage` | 图片上传和相似度检索 |
| `DuplicateDetector.vue` | `datasetApi.getDatasetId`<br>`duplicateApi.findDuplicates` | 重复图片检测 |
| `SearchResults.vue` | 使用图片URL: `/api/image/{dataset}/{id}` | 搜索结果展示 |
| `DuplicateResults.vue` | 使用图片URL: `/api/image/{dataset}/{id}` | 重复检测结果展示 |

## 错误处理机制

### 前端错误处理
- 所有API调用都包装在try-catch中
- 使用统一的消息提示组件显示错误信息
- 通过MessageDisplay组件展示不同类型的消息

### 常见错误码
- **400**: 请求参数错误
- **404**: 数据集或图片不存在
- **500**: 服务器内部错误
- **timeout**: 请求超时（30秒）

## 数据流向图

```
前端组件 → API封装层 → Axios请求 → Flask后端 → 业务逻辑 → 数据库/文件系统
    ↑                                                           ↓
响应处理 ← JSON响应 ← HTTP响应 ← API路由 ← 处理结果 ← 数据处理
```

## 开发注意事项

1. **文件上传**: 图片检索接口使用FormData格式，需要设置正确的Content-Type
2. **进度轮询**: 索引构建使用轮询机制获取进度，避免长时间阻塞
3. **图片访问**: 所有图片通过专用的图片访问接口获取，支持跨域访问
4. **错误处理**: 前端需要处理网络错误、超时等异常情况
5. **数据验证**: 前端在发送请求前进行基本的数据验证

## API测试建议

可以使用以下工具测试接口：
- **Postman**: 完整的API测试
- **curl**: 命令行快速测试
- **浏览器开发者工具**: 前端调试

### 测试用例示例

```bash
# 构建索引
curl -X POST http://localhost:19198/api/build_index \
  -H "Content-Type: application/json" \
  -d '{"dataset_names": ["test"], "distributed": false}'

# 获取数据集ID
curl -X POST http://localhost:19198/api/get_dataset_id \
  -H "Content-Type: application/json" \
  -d '{"name": "test"}'

# 图片检索 (需要实际图片文件)
curl -X POST http://localhost:19198/api/search \
  -F "query_img=@test.jpg" \
  -F "dataset_names=test"
```

---

**文档版本**: v1.0  
**最后更新**: 2025年6月23日  
**维护人员**: 开发团队
