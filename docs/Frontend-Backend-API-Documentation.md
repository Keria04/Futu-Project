# 浮图项目前后端API接口文档

## 概述

本文档详细记录了浮图项目Vue前端与后端的所有API交互接口，包括接口地址、请求参数、响应格式以及在各个组件中的使用情况。

## 项目架构信息

- **前端框架**: Vue 3 + Vite
- **前端端口**: 19197
- **后端端口**: 19198
- **API基础路径**: `/api` (通过Vite代理到后端)
- **请求超时时间**: 30秒

## API配置

### Axios配置 (`src/services/api.js`)

```javascript
const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})
```

### Vite代理配置 (`vite.config.js`)

```javascript
server: {
  port: 19197,
  proxy: {
    '/api': 'http://localhost:19198',
    '/show_image': 'http://localhost:19198'
  }
}
```

## API接口详情

### 1. 索引构建相关接口

#### 1.1 构建索引
- **接口**: `POST /api/build_index`
- **功能**: 为指定数据集构建搜索索引
- **请求参数**:
  ```json
  {
    "dataset_names": ["dataset1", "dataset2"],  // 数据集名称数组
    "distributed": false                        // 是否分布式构建
  }
  ```
- **响应格式**:
  ```json
  {
    "msg": "索引构建成功",
    "progress": [
      {
        "progress_file": "/path/to/progress.json"
      }
    ]
  }
  ```
- **使用组件**:
  - `IndexBuilder.vue` - 索引构建页面
  - `ImageSearch.vue` - 图片搜索页面（搜索前自动构建）
  - `DuplicateDetector.vue` - 重复检测页面（检测前自动构建）

#### 1.2 获取构建进度
- **接口**: `GET {progressUrl}`
- **功能**: 轮询获取索引构建进度
- **请求参数**: 无（URL由构建接口返回）
- **响应格式**:
  ```json
  {
    "progress": 85.5,    // 构建进度百分比
    "status": "building" // 状态：building/done/error
  }
  ```
- **使用场景**: 所有涉及索引构建的操作都会轮询此接口获取进度

### 2. 图片检索相关接口

#### 2.1 图片相似度搜索
- **接口**: `POST /api/search`
- **功能**: 上传查询图片，在指定数据集中搜索相似图片
- **请求参数**: `FormData`
  - `query_img`: 查询图片文件
  - `crop_x`: 裁剪区域X坐标
  - `crop_y`: 裁剪区域Y坐标
  - `crop_w`: 裁剪区域宽度
  - `crop_h`: 裁剪区域高度
  - `dataset_names[]`: 搜索的数据集名称数组
- **响应格式**:
  ```json
  {
    "results": [
      {
        "image_path": "/path/to/image.jpg",
        "similarity": 0.95,
        "dataset": "dataset_name"
      }
    ]
  }
  ```
- **使用组件**: `ImageSearch.vue` - 图片搜索页面

### 3. 数据集相关接口

#### 3.1 获取数据集ID
- **接口**: `POST /api/get_dataset_id`
- **功能**: 根据数据集名称获取对应的ID
- **请求参数**:
  ```json
  {
    "name": "dataset_name"
  }
  ```
- **响应格式**:
  ```json
  {
    "dataset_id": 123
  }
  ```
- **使用状态**: 已定义但未在前端组件中使用

#### 3.2 获取所有数据集列表
- **接口**: `GET /api/datasets`
- **功能**: 获取系统中所有数据集的列表和基本信息
- **请求参数**: 无
- **响应格式**:
  ```json
  {
    "datasets": [
      {
        "id": 1,
        "name": "dataset1",
        "description": "数据集描述",
        "image_count": 150,
        "created_at": "2025-01-01T00:00:00Z",
        "sample_images": [
          "/path/to/sample1.jpg",
          "/path/to/sample2.jpg"
        ]
      }
    ]
  }
  ```
- **使用组件**:
  - `DatasetOverview.vue` - 数据集概览页面
  - `DatasetOverviewNew.vue` - 新版数据集概览页面
  - `DatasetManager.vue` - 数据集管理组件

#### 3.3 上传图片到数据集
- **接口**: `POST /api/upload_images`
- **功能**: 向指定数据集上传图片文件
- **请求参数**: `FormData`
  - `images`: 图片文件数组
  - `dataset`: 目标数据集ID
- **响应格式**:
  ```json
  {
    "success": true,
    "uploaded_count": 5,
    "message": "成功上传5张图片"
  }
  ```
- **使用组件**: `DatasetOverview.vue` - 数据集概览页面的上传功能

### 4. 重复图片检测相关接口

#### 4.1 查找重复图片
- **接口**: `POST /api/repeated_search`
- **功能**: 在指定数据集中查找重复或相似的图片
- **请求参数**:
  ```json
  {
    "index_id": "dataset_name",  // 数据集/索引名称
    "threshold": 0.85,           // 相似度阈值
    "deduplicate": false         // 是否执行去重操作
  }
  ```
- **响应格式**:
  ```json
  {
    "groups": [
      {
        "representative": "/path/to/main.jpg",
        "duplicates": [
          "/path/to/dup1.jpg",
          "/path/to/dup2.jpg"
        ],
        "similarity_scores": [0.95, 0.92]
      }
    ]
  }
  ```
- **使用组件**: `DuplicateDetector.vue` - 重复图片检测页面

### 5. 静态资源接口

#### 5.1 图片资源访问
- **接口**: `GET /show_image/*`
- **功能**: 访问存储在后端的图片资源
- **使用方式**: 
  ```javascript
  // 在组件中修正图片URL
  function fixImageUrl(url) {
    if (!url) return ''
    if (url.startsWith('http')) return url
    return `http://localhost:19198${url}`
  }
  ```
- **代理配置**: 通过Vite代理到后端的静态文件服务

## 组件API使用详情

### IndexBuilder.vue - 索引构建组件

**使用的API接口**:
1. `POST /api/build_index` - 构建索引
2. `GET {progressUrl}` - 获取构建进度

**主要功能流程**:
```javascript
// 1. 验证数据集输入
const validation = validateDatasets()

// 2. 调用构建索引API
const response = await indexApi.buildIndex(validation.names, distributed)

// 3. 如果有进度文件，开始轮询进度
if (response.data.progress && response.data.progress.length > 0) {
  const progressUrl = response.data.progress[0].progress_file
  pollProgress(progressUrl)
}
```

### ImageSearch.vue - 图片搜索组件

**使用的API接口**:
1. `POST /api/build_index` - 搜索前确保索引已构建
2. `GET {progressUrl}` - 获取索引构建进度
3. `POST /api/search` - 执行图片搜索

**主要功能流程**:
```javascript
// 1. 先构建索引
const buildResp = await indexApi.buildIndex(validation.names, false)

// 2. 等待索引构建完成
await pollIndexProgress(progressUrl)

// 3. 准备搜索参数
const formData = new FormData()
formData.append('query_img', selectedFile.value)
formData.append('crop_x', crop.x)
// ... 其他参数

// 4. 执行搜索
const response = await searchApi.searchImage(formData)
```

### DuplicateDetector.vue - 重复检测组件

**使用的API接口**:
1. `POST /api/build_index` - 检测前确保索引已构建
2. `GET {progressUrl}` - 获取索引构建进度
3. `POST /api/repeated_search` - 执行重复检测

**主要功能流程**:
```javascript
// 1. 构建索引
const buildResp = await indexApi.buildIndex([datasetName], false)

// 2. 等待索引构建完成
await pollIndexProgress(progressUrl)

// 3. 执行重复检测
const resp = await duplicateApi.findDuplicates(datasetName, threshold.value)
```

### DatasetOverview.vue - 数据集概览组件

**使用的API接口**:
1. `GET /api/datasets` - 获取数据集列表
2. `POST /api/upload_images` - 上传图片

**主要功能流程**:
```javascript
// 1. 页面加载时获取数据集列表
const response = await datasetApi.getDatasets()
datasets.value = response.data.datasets

// 2. 处理图片上传
const formData = new FormData()
for (let i = 0; i < files.length; i++) {
  formData.append('images', files[i])
}
formData.append('dataset', dataset.id)
const res = await datasetApi.uploadImages(formData)
```

## 错误处理

### 统一错误拦截器
```javascript
// 响应拦截器
api.interceptors.response.use(
  response => {
    return response
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)
```

### 组件级错误处理
所有组件都实现了标准的错误处理模式：
```javascript
try {
  const response = await api.someMethod()
  // 处理成功响应
  message.value = '操作成功'
  messageType.value = 'success'
} catch (error) {
  // 处理错误
  message.value = '操作失败，请重试'
  messageType.value = 'error'
  console.error('Error:', error)
} finally {
  // 清理工作
  stopLoading()
}
```

## 数据流向图

```
前端组件 → API Service → Vite代理 → 后端接口
    ↓           ↓           ↓           ↓
用户交互 → axios请求 → 路由转发 → 业务处理
    ↑           ↑           ↑           ↑
UI更新 ← 响应数据 ← 代理响应 ← 结果返回
```

## 接口依赖关系

1. **索引构建是基础**: 图片搜索和重复检测都依赖于先构建索引
2. **数据集管理是前提**: 所有功能都需要先有数据集和图片数据
3. **进度轮询**: 长时间运行的操作（索引构建）都使用进度轮询机制

## 性能优化建议

1. **缓存数据集列表**: 避免频繁请求 `/api/datasets`
2. **图片懒加载**: 大量图片展示时使用懒加载
3. **请求去重**: 避免重复的索引构建请求
4. **错误重试**: 网络错误时自动重试机制

## 后续扩展计划

1. **批量操作接口**: 批量删除、批量移动等功能
2. **搜索历史**: 保存和管理搜索历史
3. **用户权限**: 添加用户认证和权限管理接口
4. **实时通知**: WebSocket推送构建进度和系统状态

---

**文档版本**: v1.0  
**最后更新**: 2025年6月25日  
**维护者**: 浮图项目开发团队
