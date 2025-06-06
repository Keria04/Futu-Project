# 浮图Project
2025年-大二-软件开发实训课程项目 组长：蔡怡乐 组员：香安涛 郑达均  何家齐 



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
python3.8.0+、anaconda

使用pip安装requirement.txt中的内容

并通过conda install安装faiss，pytorch，torchvision

```bash
conda install -c conda-forge faiss-cpu
conda install pytorch torchvision
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