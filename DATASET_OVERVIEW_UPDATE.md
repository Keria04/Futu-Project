# 浮图图片检索系统 - 更新说明

## 新增功能

### 1. 数据集概览页面
- 全新的数据集管理界面，参考现代化设计
- 支持搜索和过滤数据集
- 显示每个数据集的图片数量和描述
- 提供快捷操作按钮，可以直接跳转到各个功能模块

### 2. 数据集查询API
- 新增 `GET /api/datasets` 接口
- 自动扫描 `datasets` 目录下的文件夹
- 统计每个数据集中的图片数量
- 返回结构化的数据集信息

## 界面特性

### 设计风格
- 紫色渐变背景，现代化视觉效果
- 毛玻璃效果（backdrop-filter）
- 卡片式布局，清晰的信息层次
- 响应式设计，支持移动端

### 交互功能
- 搜索框支持实时过滤
- 数据集卡片支持选择和启用
- 快捷操作栏提供功能导航
- 平滑的动画过渡效果

## 技术实现

### 后端
- Flask 路由：`/api/datasets`
- 自动扫描文件系统
- 支持多种图片格式检测
- 错误处理和异常捕获

### 前端
- Vue 3 Composition API
- 响应式数据管理
- 组件化架构
- Axios HTTP 客户端

## 使用方法

### 开发环境启动
1. 运行 `start_development.bat` 启动脚本
2. 或者手动启动：
   ```bash
   # 启动后端
   python backend/app.py
   
   # 启动前端
   cd frontend
   npm run dev
   ```

### 访问地址
- 前端界面：http://localhost:19197
- 后端API：http://localhost:19198

### 导航说明
- 默认显示数据集概览页面
- 点击快捷操作按钮可以跳转到对应功能
- 支持在不同模块间切换

## API 文档更新

### 获取数据集列表
```
GET /api/datasets
```

**响应示例：**
```json
{
  "datasets": [
    {
      "id": "1",
      "name": "Dataset1",
      "folder": "1",
      "image_count": 251,
      "description": "数据集 1，包含 251 张图片"
    },
    {
      "id": "2", 
      "name": "Dataset2",
      "folder": "2",
      "image_count": 0,
      "description": "数据集 2，包含 0 张图片"
    }
  ]
}
```

## 文件结构

```
frontend/src/components/
├── DatasetOverview/
│   ├── DatasetOverview.vue    # 数据集概览组件
│   └── index.js              # 导出文件
└── ...

backend/route/
├── get_datasets.py           # 数据集查询路由
└── ...
```

## 下一步计划
1. 添加数据集创建和删除功能
2. 实现数据集详情页面
3. 支持批量操作
4. 添加数据集统计图表
5. 支持数据集导入导出

## 注意事项
- 确保 `datasets` 目录存在且有读取权限
- 支持的图片格式：JPG, JPEG, PNG, GIF, BMP, WEBP
- 数据集ID基于文件夹名称，建议使用数字或简短标识符
