#  浮图（Futu） - 在线以图搜图平台

![浮图logo](./浮图logo.png)

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

- ✅ 通过Redis实现集群运算与负载均衡

## 🏗️ 技术架构

| 模块    | 技术栈说明                           |
| ------- | ------------------------------------ |
| 前端    | Vue 3 + Axios                        |
| 后端    | Flask (Python)                       |
| AI 模块 | PyTorch（ResNet-50）+ Faiss 向量检索 |
| 数据库  | SQLite 3（轻量级本地数据库）         |
| 负载均衡  | Redis+celery                      |

## 文件结构

```
Futu-Project/
├── README.md                          # 项目说明文档
├── LICENSE                            # 开源许可证
├── requirement.txt                    # Python 依赖列表
├── backend/                           # 后端服务代码
│   ├── app.py                         # 后端主程序入口
│   ├── start_worker.py                # 启动Worker脚本
│   ├── database_module/               # 数据库模块
│   ├── model_module/                  # 特征提取模型
│   ├── faiss_module/                  # Faiss索引模块
│   │   └── faiss_utils/               # Faiss工具包
│   ├── index_manage_module/           # 索引管理模块
│   ├── search_module/                 # 搜索模块
│   └── route/                         # 路由定义
├── frontend/                          # 前端 Vue 项目
│   └── src/                           # 前端核心源码
├── config/                            # 配置文件
│   ├── config.py                      # 配置项定义
│   └── defaultconfig.json             # 预留默认配置
├── data/                              # 数据存储目录
│   ├── main.db                        # SQLite主数据库
│   ├── indexes/                       # 索引文件存储
│   │   ├── 1.index                    # 数据集1索引*可变
│   │   ├── 2.index                    # 数据集2索引*可变
│   │   └── 3.index                    # 数据集3索引*可变
│   ├── progress/                      # 进度文件存储
│   └── uploads/                       # 用户上传图片
├── datasets/                          # 数据集目录
│   ├── 1/                             # 数据集1图片*可变
│   ├── 2/                             # 数据集2图片*可变
│   └── 3/                             # 数据集3图片*可变
├── docs/                              # 项目相关文档
├── scripts/                           # 脚本与快捷启动工具
│   ├── start.bat                      # Windows 启动脚本
│   ├── start.sh                       # Linux/Mac 启动脚本
│   ├── start_worker.bat               # Windows Worker启动脚本
│   ├── run_performance_test.py        # 运行性能测试
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

查看 [性能测试文档](docs/性能测试使用文档.md) 了解更多详细信息。