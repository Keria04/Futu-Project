# 浮图Project
2025年-大二-软件开发实训课程项目 组长：蔡怡乐 组员：香安涛 郑达均 罗伟 何家齐 



## 文件结构

```
Futu-Project/
├── README.md           # 项目说明文档
├── /config						#  配置文件
├── /backend						# 后端实现代码
│   ├── /databases			# 数据库实现与储存
│   ├── /models					# 面向对象代码
│   ├── /routes					# 后端路由代码
│   ├── /utils					# 微函数代码
├── /fronted						# 前端实现代码
│   ├── /public					# vue资源库
│   ├── /src						# 前端代码
├── /scripts						# 启动脚本
```



## 开始

系统环境：
python3.12.0+、anaconda

运行./scripts/start.sh

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

*如果是* *.bat* *文件，则使用* *start.bat* *运行。*

