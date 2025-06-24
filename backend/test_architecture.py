"""
架构测试脚本
"""
import sys
import os

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    
    try:
        from shared import redis_client, task_manager, MessageProtocol
        print("✓ 共享模块导入成功")
    except Exception as e:
        print(f"✗ 共享模块导入失败: {e}")
    
    try:
        from control_service.services import database_service, search_service, index_service
        print("✓ 控制端服务模块导入成功")
    except Exception as e:
        print(f"✗ 控制端服务模块导入失败: {e}")
    
    try:
        from control_service.api import search_bp, index_bp, dataset_bp, image_bp
        print("✓ 控制端API模块导入成功")
    except Exception as e:
        print(f"✗ 控制端API模块导入失败: {e}")
    
    try:
        from compute_service.model_module.feature_extractor import feature_extractor
        print("✓ 计算端模型模块导入成功")
    except Exception as e:
        print(f"✗ 计算端模型模块导入失败: {e}")

def test_redis_connection():
    """测试Redis连接"""
    print("\n测试Redis连接...")
    
    try:
        from shared import redis_client
        if redis_client.ping():
            print("✓ Redis连接成功")
        else:
            print("✗ Redis连接失败")
    except Exception as e:
        print(f"✗ Redis连接测试失败: {e}")

def test_database_service():
    """测试数据库服务"""
    print("\n测试数据库服务...")
    
    try:
        from control_service.services import database_service
        datasets = database_service.get_datasets()
        print(f"✓ 数据库服务正常，找到 {len(datasets)} 个数据集")
    except Exception as e:
        print(f"✗ 数据库服务测试失败: {e}")

def test_task_protocol():
    """测试任务协议"""
    print("\n测试任务协议...")
    
    try:
        from shared import MessageProtocol, TaskType, TaskMessage
        
        # 创建测试任务
        task = MessageProtocol.create_feature_extraction_task("test_image_data")
        print(f"✓ 任务创建成功，ID: {task.task_id}")
        
        # 测试序列化
        json_str = task.to_json()
        task_restored = TaskMessage.from_json(json_str)
        print("✓ 任务序列化和反序列化成功")
        
    except Exception as e:
        print(f"✗ 任务协议测试失败: {e}")

def main():
    """主测试函数"""
    print("=" * 50)
    print("🧪 浮图图像搜索系统架构测试")
    print("=" * 50)
    
    test_imports()
    test_redis_connection()
    test_database_service()
    test_task_protocol()
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    main()
