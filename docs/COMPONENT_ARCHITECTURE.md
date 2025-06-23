# 浮图前端组件架构文档

## 项目重构说明

原来的巨大单体组件 `TheWelcome.vue` 已被拆分为多个功能独立的组件，提高了代码的可维护性和可复用性。

## 目录结构

```
src/
├── components/              # 组件目录
│   ├── Common/             # 通用组件
│   │   ├── DatasetManager.vue      # 数据集管理器
│   │   ├── ImageCanvas.vue         # 图片画布组件
│   │   ├── MessageDisplay.vue      # 消息显示组件
│   │   └── ProgressBar.vue         # 进度条组件
│   ├── DuplicateDetector/  # 重复检测功能
│   │   ├── DuplicateDetector.vue   # 重复检测主组件
│   │   └── DuplicateResults.vue    # 重复检测结果
│   ├── ImageSearch/        # 图片搜索功能
│   │   ├── ImageSearch.vue         # 图片搜索主组件
│   │   └── SearchResults.vue       # 搜索结果展示
│   ├── IndexBuilder/       # 索引构建功能
│   │   └── IndexBuilder.vue        # 索引构建主组件
│   ├── Layout/            # 布局组件
│   │   └── AppLayout.vue          # 应用主布局
│   └── index.js           # 组件导出索引
├── composables/           # 组合式函数
│   ├── useDatasetManager.js       # 数据集管理逻辑
│   ├── useImageHandler.js         # 图片处理逻辑
│   ├── useLoading.js             # 加载状态管理
│   └── index.js                  # composables 导出索引
├── services/             # 服务层
│   └── api.js           # API 接口封装
└── assets/              # 静态资源
    └── main.css         # 全局样式
```

## 组件功能说明

### 1. 通用组件 (Common)

#### DatasetManager.vue
- 管理数据集名称的添加、删除和输入
- 支持多数据集和单数据集模式
- 提供数据验证功能

#### ImageCanvas.vue
- 提供图片显示和裁剪选择功能
- 支持鼠标交互绘制裁剪框
- 可复用的画布组件

#### MessageDisplay.vue
- 统一的消息显示组件
- 支持不同类型的消息（info, success, warning, error）
- 可自定义样式

#### ProgressBar.vue
- 通用进度条组件
- 支持进度百分比和状态文本显示
- 可控制显示/隐藏状态

### 2. 功能模块组件

#### IndexBuilder (索引构建)
- `IndexBuilder.vue`: 索引构建的主要界面
- 支持本地和远程构建
- 集成进度显示和状态管理

#### ImageSearch (图片搜索)
- `ImageSearch.vue`: 图片搜索的主要界面
- `SearchResults.vue`: 搜索结果的展示组件
- 支持图片上传、裁剪选择和相似度搜索

#### DuplicateDetector (重复检测)
- `DuplicateDetector.vue`: 重复图片检测界面
- `DuplicateResults.vue`: 重复检测结果展示
- 支持阈值设置和重复图片分组显示

### 3. 布局组件 (Layout)

#### AppLayout.vue
- 应用的主要布局结构
- 包含头部、主内容区域和底部
- 响应式设计支持

## Composables (组合式函数)

### useImageHandler.js
- 图片文件处理逻辑
- 画布绘制和裁剪功能
- 鼠标事件处理

### useDatasetManager.js
- 数据集管理逻辑
- 添加、删除数据集
- 数据验证功能

### useLoading.js
- 加载状态管理
- 进度条状态管理
- 统一的状态控制接口

## 服务层 (Services)

### api.js
- 统一的 API 接口封装
- 按功能模块分组的 API 方法
- 请求和响应拦截器配置

## 使用方式

### 1. 导入组件
```javascript
import { IndexBuilder, ImageSearch, DuplicateDetector } from '@/components'
```

### 2. 使用 Composables
```javascript
import { useImageHandler, useDatasetManager } from '@/composables'

const { previewUrl, crop, handleFileChange } = useImageHandler()
const { datasetNames, addDataset, removeDataset } = useDatasetManager()
```

### 3. 使用 API 服务
```javascript
import { indexApi, searchApi, duplicateApi } from '@/services/api'

// 构建索引
await indexApi.buildIndex(['dataset1', 'dataset2'])

// 搜索图片
await searchApi.searchImage(formData)

// 查找重复图片
await duplicateApi.findDuplicates(datasetId, threshold)
```

## 优势

1. **模块化**: 每个功能独立成组件，便于维护和测试
2. **可复用性**: 通用组件可在多个地方复用
3. **责任分离**: 逻辑、UI、API 分层清晰
4. **类型安全**: 更好的 TypeScript 支持（如需要）
5. **性能优化**: 按需加载和懒加载支持
6. **测试友好**: 小组件更容易编写单元测试

## 后续扩展

- 可以继续添加新的功能模块（如用户管理、系统设置等）
- 可以将 composables 进一步细化
- 可以添加状态管理（如 Pinia）
- 可以添加路由管理（如 Vue Router）
