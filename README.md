# 浮图Project
2025年-大二-软件开发实训课程项目 组长：蔡怡乐 组员：香安涛 郑达均  何家齐 



## 文件结构

```
Futu-Project/
├── README.md                          # 项目说明文档
├── LICENSE                            # 开源许可证
├── requirement.txt                    # Python 依赖列表
├── backend/                           # 后端服务代码
│   ├── app.py                         # 后端主程序入口
│   ├── worker.py                      # Celery后台任务处理
│   ├── start_worker.py                # 启动Worker脚本
│   ├── start_worker_simple.py         # 简化Worker启动脚本
│   ├── test_celery_dispatch.py        # Celery调度测试
│   ├── fix_queue_and_test.py          # 队列修复和测试
│   ├── database_module/               # 数据库模块
│   │   ├── __init__.py
│   │   ├── database.py                # 数据库核心功能
│   │   ├── schema.py                  # 数据库表结构
│   │   ├── query.py                   # 查询功能
│   │   └── modify.py                  # 修改功能
│   ├── model_module/                  # 特征提取模型
│   │   ├── __init__.py
│   │   └── feature_extractor.py       # 特征提取器
│   ├── faiss_module/                  # Faiss索引模块
│   │   ├── __init__.py
│   │   ├── build_index.py             # 构建索引
│   │   ├── indexer.py                 # 索引器接口
│   │   ├── search_index.py            # 查询索引
│   │   ├── update_index.py            # 更新索引
│   │   ├── repeated_search.py         # 重复搜索功能
│   │   └── faiss_utils/               # Faiss工具包
│   ├── index_manage_module/           # 索引管理模块
│   │   ├── __init__.py
│   │   ├── api.py                     # 索引管理API
│   │   ├── factory.py                 # 索引工厂
│   │   └── index_builder.py           # 索引构建器
│   ├── search_module/                 # 搜索模块
│   │   ├── __init__.py
│   │   └── search.py                  # 搜索功能
│   └── route/                         # 路由定义
│       ├── __init__.py
│       ├── build_index.py             # 构建索引路由
│       ├── get_dataset_id.py          # 获取数据集ID路由
│       ├── get_datasets.py            # 获取数据集路由
│       ├── image.py                   # 图片处理路由
│       ├── index.py                   # 索引路由
│       ├── repeated_search.py         # 重复搜索路由
│       ├── search.py                  # 搜索路由
│       └── upload_images.py           # 图片上传路由
├── frontend/                          # 前端 Vue 项目
│   ├── index.html                     # HTML 模板入口
│   ├── package.json                   # 项目依赖说明
│   ├── jsconfig.json                  # JavaScript配置
│   ├── vite.config.js                 # Vite 配置文件
│   ├── public/                        # 静态资源
│   └── src/                           # 前端核心源码
├── config/                            # 配置文件
│   ├── config.py                      # 配置项定义
│   └── defaultconfig.json             # 默认配置
├── data/                              # 数据存储目录
│   ├── main.db                        # SQLite主数据库
│   ├── indexes/                       # 索引文件存储
│   │   ├── 1.index                    # 数据集1索引
│   │   ├── 2.index                    # 数据集2索引
│   │   └── 3.index                    # 数据集3索引
│   ├── progress/                      # 进度文件存储
│   │   ├── 1_progress.txt             # 数据集1进度
│   │   ├── 2_progress.txt             # 数据集2进度
│   │   └── 3_progress.txt             # 数据集3进度
│   └── uploads/                       # 用户上传图片
├── datasets/                          # 数据集目录
│   ├── 1/                             # 数据集1图片
│   ├── 2/                             # 数据集2图片
│   └── 3/                             # 数据集3图片
├── docs/                              # 项目相关文档
│   ├── 浮图-软件架构文档.md
│   ├── 浮图-软件架构文档.pdf
│   ├── 浮图-项目开发计划书.md
│   ├── 浮图-项目开发计划书.pdf
│   ├── 浮图-数据库设计文档.pdf
│   ├── 开发规范.md
│   ├── 设计文档.md
│   ├── 数据库设计文档.md
│   ├── 性能测试使用文档.md
│   ├── 软件需求规约.doc
│   ├── 工作周报/                      # 项目周报
│   ├── 文档用图片/                    # 架构图、用例图等插图
│   ├── 用例规约_第三周/               # 用例规约文档
│   └── 用例实现规约_第三周/           # 用例实现规约
├── scripts/                           # 脚本与快捷启动工具
│   ├── start.bat                      # Windows 启动脚本
│   ├── start.sh                       # Linux/Mac 启动脚本
│   ├── start_worker.bat               # Windows Worker启动脚本
│   ├── config_optimizer.py            # 配置优化器
│   ├── generate_test_images.py        # 生成测试图像
│   ├── performance_examples.py        # 性能测试示例
│   ├── performance_testbench.py       # 性能测试平台
│   ├── quick_performance_test.py      # 快速性能测试
│   ├── run_performance_test.py        # 运行性能测试
│   ├── testbench_configs.json         # 测试平台配置
│   └── verify_testbench.py            # 验证测试平台
└── uploads/                           # 临时上传目录
```



## 快速开始

### 系统要求

- **Python**: 3.8.0 或更高版本
- **Anaconda**: 推荐使用Anaconda进行环境管理
- **Node.js**: 用于前端开发（推荐版本 16+）

### 安装依赖

1. **安装Python依赖包**

```bash
pip install -r requirement.txt
```

2. **安装Faiss、PyTorch和TorchVision**

```bash
conda install -c conda-forge faiss-cpu pytorch torchvision
```

3. **安装前端依赖**（首次运行时会自动执行）

```bash
cd frontend
npm install
```

### 启动应用

项目提供了便捷的启动脚本，会自动检测端口占用并启动前后端服务。

#### Windows 用户

1. **启动主应用**

```batch
cd scripts
.\start.bat
```

启动脚本会：
- 检测端口19197（前端）和19198（后端）是否被占用
- 如有占用会询问是否终止占用进程
- 自动启动前端开发服务器（Vue + Vite）
- 自动启动后端Flask服务器
- 延时5秒后自动打开浏览器访问 http://localhost:19197

2. **启动Celery Worker（可选）**

如需使用后台任务处理功能：

```batch
cd scripts
.\start_worker.bat
```

Worker脚本会：
- 启动Celery Worker进程处理后台任务
- 使用solo池模式（适合Windows环境）
- 提供详细的日志输出

#### Linux & macOS 用户

1. **赋予脚本执行权限**

```bash
cd scripts
chmod +x start.sh
```

2. **启动应用**

```bash
./start.sh
```

启动脚本会：
- 检测端口19197（前端）和19198（后端）是否被占用
- 如有占用会询问是否终止占用进程  
- 自动启动前端开发服务器（Vue + Vite）
- 自动启动后端Flask服务器
- 延时5秒后自动打开默认浏览器访问 http://localhost:19197

#### 手动启动（如脚本无法正常工作）

如果自动启动脚本遇到问题，可以手动启动：

1. **启动后端服务**

```bash
# 在项目根目录
set KMP_DUPLICATE_LIB_OK=TRUE  # Windows
export KMP_DUPLICATE_LIB_OK=TRUE  # Linux/macOS
python backend/app.py
```

2. **启动前端服务**

```bash
cd frontend
npm install
npm run dev
```

3. **启动Celery Worker**（可选）

```bash
cd backend
python -m celery -A worker worker --loglevel=info --pool=solo
```

### 访问应用

启动成功后，应用将在以下地址运行：

- **前端界面**: http://localhost:19197
- **后端API**: http://localhost:19198

### 故障排除

1. **端口占用问题**: 
   - Windows脚本会自动检测并询问是否终止占用进程
   - 也可手动使用 `netstat -ano | findstr :端口号` 查找并终止进程

2. **Celery启动卡住**: 
   - 按 Ctrl+C 停止，然后手动运行启动命令
   - 确保Redis或RabbitMQ等消息队列服务正在运行

3. **依赖安装问题**: 
   - 确保使用正确的Python环境
   - 建议使用虚拟环境隔离依赖

4. **权限问题**（Linux/macOS）: 
   - 确保脚本有执行权限：`chmod +x start.sh`



## 性能测试

本项目提供了完整的性能测试和优化工具套件，用于评估和优化系统性能。

### 快速开始

```bash
# 快速性能测试（推荐）
python run_performance_test.py quick

# 完整性能基准测试
python run_performance_test.py full

# 配置参数优化
python run_performance_test.py optimize

# 验证测试工具
python run_performance_test.py verify

# 运行示例
python run_performance_test.py examples
```

### 测试功能

- **远程 vs 本地计算性能对比** - 评估Celery分布式计算与本地计算的性能差异
- **簇大小影响分析** - 分析FAISS索引的N_LIST参数对检索性能的影响
- **批处理大小优化** - 找到最优的batchsize配置
- **设备性能对比** - 比较CPU和GPU的性能表现
- **配置参数自动优化** - 自动寻找最佳配置组合

### 详细文档

查看 [性能测试文档](scripts/PERFORMANCE_TESTBENCH_README.md) 了解更多详细信息。