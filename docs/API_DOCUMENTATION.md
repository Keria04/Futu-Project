# 浮图图片检索系统 - 前后端API接口文档

## 概述

本文档详细描述了浮图图片检索系统前端与后端之间的所有API接口。系统采用Flask后端 + Vue3前端的架构，提供数据集管理、图片检索、索引构建和重复检测等功能。

## 系统架构

```
前端 (Vue 3 + Vite)
├── 数据集概览 (DatasetOverview.vue)
├── 图片检索 (ImageSearch.vue)  
├── 索引构建 (IndexBuilder.vue)
└── 重复检测 (DuplicateDetector.vue)

后端 (Flask)
├── 数据集管理接口
├── 图片检索接口
├── 索引构建接口
└── 重复检测接口
```

## 基础配置

- **后端基础URL**: `http://localhost:19198`
- **前端访问URL**: `http://localhost:19197`
- **API前缀**: `/api`
- **请求超时**: 30秒
- **支持的图片格式**: JPG, PNG, GIF, BMP, WEBP

## API接口列表

### 1. 数据集管理相关接口

#### 1.1 获取数据集列表 [新增]
- **接口路径**: `GET /api/datasets`
- **功能描述**: 获取所有可用的数据集信息，自动扫描datasets目录
- **前端调用位置**: `DatasetOverview.vue`
- **请求参数**: 无
- **响应数据**:
```json
{
  "datasets": [
    {
      "id": "1",                                    // 数据集ID
      "name": "Dataset1",                           // 数据集名称
      "folder": "1",                                // 文件夹名称
      "image_count": 251,                           // 图片数量
      "description": "数据集 1，包含 251 张图片"      // 描述信息
    },
    {
      "id": "2",
      "name": "Dataset2", 
      "folder": "2",
      "image_count": 100,
      "description": "数据集 2，包含 100 张图片"
    }
  ]
}
```

#### 1.2 获取数据集ID
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

### 3. 索引构建相关接口

#### 3.1 构建索引
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

#### 3.2 获取构建进度
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
- **接口路径**: `POST /api/get_dataset_id`
- **功能描述**: 根据数据集名称获取对应的内部ID
- **前端调用位置**: `DuplicateDetector.vue`
- **请求参数**:
```json
{
  "name": "dataset1"  // 数据集名称
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

1. **datasetApi**: 数据集管理相关
   - `getDatasets()`: 获取所有数据集列表 [新增]
   - `getDatasetId(name)`: 获取数据集ID

2. **searchApi**: 图片检索相关
   - `searchImage(formData)`: 图片相似度检索

3. **indexApi**: 索引构建相关
   - `buildIndex(dataset_names, distributed)`: 构建索引
   - `getProgress(progressUrl)`: 获取构建进度

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

## 前端页面与API的映射关系

| 页面模块 | 组件文件 | 使用的API接口 | 主要功能 |
|----------|----------|---------------|----------|
| **数据集概览** | `DatasetOverview.vue` | `datasetApi.getDatasets` | 查看所有数据集信息、图片数量统计 |
| **图片检索** | `ImageSearch.vue` | `searchApi.searchImage` | 上传图片、相似度检索、结果展示 |
| **索引构建** | `IndexBuilder.vue` | `indexApi.buildIndex`<br>`indexApi.getProgress` | 构建数据集索引、进度监控 |
| **重复检测** | `DuplicateDetector.vue` | `datasetApi.getDatasetId`<br>`duplicateApi.findDuplicates` | 检测重复图片、批量去重 |
| **搜索结果** | `SearchResults.vue` | 图片URL: `/api/image/{dataset}/{id}` | 搜索结果展示 |
| **重复结果** | `DuplicateResults.vue` | 图片URL: `/api/image/{dataset}/{id}` | 重复检测结果展示 |

## 页面导航流程

```
数据集概览 (首页)
├── 查看数据集信息
├── 导航到图片检索 ──→ 图片检索页面
├── 导航到索引构建 ──→ 索引构建页面
└── 导航到重复检测 ──→ 重复检测页面

统一导航栏
├── 数据集概览 (默认首页)
├── 图片检索
├── 构建索引  
└── 重复检测
```

## 数据流向图

```
用户操作 → 前端组件 → API封装层 → HTTP请求 → Flask后端路由
                ↑                                        ↓
            UI更新 ← JSON响应 ← HTTP响应 ← 业务逻辑处理 ← 数据库/文件系统
```

## 错误处理机制

### 前端错误处理策略
- **网络错误**: 统一显示连接失败提示
- **API错误**: 根据HTTP状态码显示相应错误信息
- **数据验证**: 前端表单验证，防止无效请求
- **用户反馈**: 通过MessageDisplay组件统一显示消息

### 常见错误码及处理
- **200**: 请求成功
- **400**: 请求参数错误 → 提示用户检查输入
- **404**: 资源不存在 → 提示数据集或图片不存在
- **500**: 服务器错误 → 提示系统暂时不可用
- **timeout**: 请求超时 → 提示网络超时，建议重试

## 开发注意事项

### 新增功能说明
1. **数据集自动发现**: 系统会自动扫描`datasets`目录，无需手动配置
2. **统一导航**: 所有页面采用统一的顶部导航栏设计
3. **响应式界面**: 支持桌面和移动设备的良好显示效果
4. **实时数据**: 数据集信息会实时更新图片数量统计

### 技术要点
1. **文件上传**: 图片检索接口使用FormData格式，需要设置正确的Content-Type
2. **进度轮询**: 索引构建使用轮询机制获取进度，避免长时间阻塞
3. **图片访问**: 所有图片通过专用的图片访问接口获取，支持跨域访问
4. **错误处理**: 前端需要处理网络错误、超时等异常情况
5. **数据验证**: 前端在发送请求前进行基本的数据验证

### 部署配置
- **开发环境**: 前端端口19197，后端端口19198
- **代理配置**: Vite已配置API代理，前端请求会自动转发到后端
- **跨域处理**: 后端需要配置CORS支持（如需要）

## API测试建议

### 测试工具
- **Postman**: 完整的API测试和文档
- **curl**: 命令行快速测试
- **浏览器开发者工具**: 前端调试和网络监控

### 测试用例示例

```bash
# 获取数据集列表 [新增]
curl -X GET http://localhost:19198/api/datasets

# 构建索引
curl -X POST http://localhost:19198/api/build_index \
  -H "Content-Type: application/json" \
  -d '{"dataset_names": ["1"], "distributed": false}'

# 获取数据集ID
curl -X POST http://localhost:19198/api/get_dataset_id \
  -H "Content-Type: application/json" \
  -d '{"name": "1"}'

# 图片检索 (需要实际图片文件)
curl -X POST http://localhost:19198/api/search \
  -F "query_img=@test.jpg" \
  -F "dataset_names=1"

# 重复检测
curl -X POST http://localhost:19198/api/repeated_search \
  -H "Content-Type: application/json" \
  -d '{"index_id": 1, "threshold": 90, "deduplicate": false}'
```

## 版本更新记录

### v1.1.0 (2025年6月23日) - 当前版本
**新增功能:**
- ✨ 数据集自动发现API (`GET /api/datasets`)
- ✨ 统一导航栏界面重构
- ✨ 数据集概览页面重新设计
- 🎨 现代化UI设计和响应式布局
- 📱 移动端适配优化

**技术改进:**
- 🔧 API接口重新组织和文档化
- 🔧 前端组件模块化重构
- 🔧 错误处理机制完善
- 🔧 代码结构优化

### v1.0.0 (之前版本)
**基础功能:**
- 🚀 图片相似度检索
- 🏗️ 数据集索引构建
- 🎯 重复图片检测
- 💾 SQLite数据库支持
- 📊 FAISS向量搜索

---

**文档版本**: v1.1.0  
**最后更新**: 2025年6月23日  
**维护人员**: 浮图开发团队  
**项目地址**: 浮图图片检索系统
