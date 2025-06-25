#!/usr/bin/env python3
"""
浮图项目快速设置脚本
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        return False
    print(f"✓ Python版本: {sys.version}")
    return True


def check_redis():
    """检查Redis服务"""
    try:
        result = subprocess.run(['redis-server', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✓ Redis版本: {result.stdout.strip()}")
            return True
    except:
        pass
    
    try:
        result = subprocess.run(['redis-cli', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✓ Redis客户端: {result.stdout.strip()}")
            return True
    except:
        pass
    
    print("⚠ 未找到Redis，请确保Redis已安装")
    return False


def install_requirements():
    """安装依赖包"""
    requirements_file = Path(__file__).parent.parent / "requirement.txt"
    
    if not requirements_file.exists():
        print("⚠ 未找到requirement.txt文件")
        return False
    
    print("安装Python依赖包...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
        ], check=True, capture_output=True, text=True)
        print("✓ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 依赖包安装失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False


def create_directories():
    """创建必要的目录"""
    base_dir = Path(__file__).parent
    directories = [
        base_dir / "data" / "indexes",
        base_dir / "data" / "progress", 
        base_dir / "uploads",
        base_dir / "logs"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ 创建目录: {directory}")
    
    return True


def setup_environment():
    """设置环境变量"""
    env_file = Path(__file__).parent / ".env"
    
    if env_file.exists():
        print("✓ .env文件已存在")
        return True
    
    env_content = """# 浮图项目环境变量配置
FLASK_CONFIG=development
FLASK_HOST=0.0.0.0
FLASK_PORT=19198
FLASK_DEBUG=True

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# 计算端配置
COMPUTE_WORKERS=2
FEATURE_TIMEOUT=30
BATCH_FEATURE_TIMEOUT=60

# 日志配置
LOG_LEVEL=INFO
"""
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"✓ 创建环境配置文件: {env_file}")
    return True


def test_setup():
    """测试设置"""
    print("\n测试基本功能...")
    
    # 测试模块导入
    try:
        sys.path.append(str(Path(__file__).parent))
        
        # 测试Redis客户端
        from redis_client.redis_client import RedisClient
        print("✓ Redis客户端模块导入成功")
        
        # 测试模型模块
        from model_module.feature_extractor import feature_extractor
        print("✓ 特征提取模块导入成功")
        
        # 测试控制端应用
        from controller.controller_app import create_controller_app
        print("✓ 控制端应用模块导入成功")
        
        # 测试计算端服务
        from compute_server.compute_server import ComputeServer
        print("✓ 计算端服务模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 模块导入测试失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("浮图项目快速设置")
    print("=" * 60)
    
    steps = [
        ("检查Python版本", check_python_version),
        ("检查Redis服务", check_redis),
        ("创建必要目录", create_directories),
        ("设置环境变量", setup_environment),
        ("安装依赖包", install_requirements),
        ("测试基本功能", test_setup),
    ]
    
    success_count = 0
    total_count = len(steps)
    
    for name, func in steps:
        print(f"\n{name}...")
        try:
            if func():
                success_count += 1
            else:
                print(f"⚠ {name} 未完全成功")
        except Exception as e:
            print(f"✗ {name} 失败: {e}")
    
    print("\n" + "=" * 60)
    print(f"设置完成: {success_count}/{total_count} 步骤成功")
    
    if success_count == total_count:
        print("\n✓ 设置完成！可以开始使用浮图项目。")
        print("\n启动命令示例:")
        print("  python run.py both                    # 启动所有服务")
        print("  python run.py controller              # 只启动控制端")
        print("  python run.py compute --workers 4     # 只启动计算端")
        print("  python test_architecture.py           # 测试架构")
    else:
        print("\n⚠ 设置过程中遇到一些问题，请检查上述错误信息。")
    
    return success_count == total_count


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
