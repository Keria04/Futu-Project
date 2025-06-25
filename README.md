#  浮图（Futu） - 在线以图搜图平台

<img src="/Users/caiyile/Desktop/Typoya图库/浮图logo.png" alt="浮图logo" style="zoom:50%;" />

##  🌟 项目简介

“浮图”是一款支持图像上传与查重的在线以图搜图平台，基于 CNN 特征提取与 Faiss 向量检索实现图像相似度比对。用户可上传任意图像，系统将自动返回相似图片结果，并支持重复图像识别、结果展示与图像管理等功能。

## 🧑‍💻项目背景

本项目是华南理工大学软件学院23级双学位班的软件开发实训大作业，项目人数为4人。

- Keria-负责划水，组织开发
- Qadg-负责狠狠code，狠狠注入代码
- 香香-负责了CNN模块以及各种文档的编写
- Max-负责美美的前端页面

##  🖼️ 系统演示

👉 [点此查看系统演示视频](#)  

## ⚙️ 功能特性

- ✅ 图像上传与裁剪

- ✅本地图像库相似度检索

- ✅ 查重图库与去重处理

- ✅ CNN（ResNet）特征提取 + Faiss 检索

- ✅ 图像索引持久化与 SQLite 管理

- ✅ 前后端分离架构：Vue + Flask

## 🏗️ 技术架构

| 模块    | 技术栈说明                           |
| ------- | ------------------------------------ |
| 前端    | Vue 3 + Axios                        |
| 后端    | Flask (Python)                       |
| AI 模块 | PyTorch（ResNet-50）+ Faiss 向量检索 |
| 数据库  | SQLite 3（轻量级本地数据库）         |

## 文件结构

```
Futu-Project/
├── README.md                  # 项目说明文档
├── LICENSE                    # 开源许可证
├── config/                    # 配置文件（如 config.py 和 defaultconfig.json）
│   └── config.py              # 配置项定义
├── backend/                   # 后端服务代码
│   ├── app.py                 # 后端主程序入口
│   ├── database_module/       # 数据库模块
│   │   └── __init__.py
│   ├── model_module/          # 特征提取模型
│   │   └── feature_extractor.py
│   ├── faiss_module/          # Faiss索引模块
│   │   ├── build_index.py     # 构建索引
│   │   ├── indexer.py         # 索引器接口
│   │   ├── search_index.py    # 查询索引
│   │   └── update_index.py    # 更新索引
│   ├── route/                 # 路由定义
│   │   ├── image.py           # 上传图片路由
│   │   ├── index.py           # 索引路由
│   │   └── search.py          # 搜索路由
│   └── worker.py              # 后台任务处理
├── frontend/                  # 前端 Vue 项目
│   ├── public/                # 静态资源（如 favicon）
│   ├── src/                   # 前端核心源码
│   │   ├── App.vue            # 主组件
│   │   ├── main.js            # 应用入口
│   │   ├── assets/            # 前端图片、图标等资源
│   │   └── components/        # 自定义组件
│   ├── index.html             # HTML 模板入口
│   ├── package.json           # 项目依赖说明
│   └── vite.config.js         # Vite 配置文件
├── data/                      # 存储特征向量、索引和上传图片
│   ├── features.npy           # 图像特征文件
│   ├── ids.npy                # 图像ID映射
│   ├── image.index            # Faiss 索引文件
│   └── uploads/               # 用户上传图片示例
│       └── ...                # 多张 .jpg 图片
├── docs/                      # 项目相关文档
│   ├── 软件架构文档.md
│   ├── 项目开发计划书.md / .pdf
│   ├── 数据库设计文档.md
│   ├── 用例规约/             # 包含各类用例规约 Word 文档
│   ├── 实现规约/             # 各功能模块实现规约
│   ├── 工作周报/             # 项目周报
│   └── 文档用图片/           # 架构图、用例图等插图
├── scripts/                   # 脚本与快捷启动工具
│   ├── start.sh               # Linux/Mac 启动脚本
│   ├── start.bat              # Windows 启动脚本
│   ├── generate_test_images.py# 自动生成测试图像脚本
├── requirement.txt            # Python 依赖列表（使用pip安装的）
```



## 开始

系统环境：
python3.8.0、anaconda

使用pip安装requirement.txt中的内容

```bash
pip install -r requirement.txt
```



并通过conda install安装faiss，pytorch，torchvision

```bash
conda install -c conda-forge faiss-cpu pytorch torchvision
```

激活虚拟环境，并运行./scripts/start.sh

**Linux & macOS**

1. 切换到 scripts 目录

```
cd scripts
```

2. 确保脚本具有可执行权限

```
chmod +x start.sh
```

3. 运行脚本

```
./start.sh
```

**Windows**

1. 切换到 scripts 目录

```
cd scripts
```

2. 在 PowerShell 允许脚本执行（如果未启用）

```
Set-ExecutionPolicy RemoteSigned -Scope Process
```

3. 运行脚本

```
.\start.bat
```