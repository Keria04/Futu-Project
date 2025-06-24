"""
简化测试脚本
"""
import sys
import os

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_basic_imports():
    """测试基本导入"""
    print("测试基本导入...")
    
    try:
        # 测试共享模块
        from shared.redis_client import redis_client
        print("✓ Redis客户端导入成功")
        
        from shared.message_protocol import TaskMessage, TaskResult, MessageProtocol
        print("✓ 消息协议导入成功")
        
        # 测试创建任务
        task = MessageProtocol.create_feature_extraction_task("test_data")
        print(f"✓ 任务创建成功: {task.task_id}")
        
        return True
        
    except Exception as e:
        print(f"✗ 基本导入测试失败: {e}")
        return False

def test_redis():
    """测试Redis连接"""
    print("\n测试Redis连接...")
    
    try:
        from shared.redis_client import redis_client
        if redis_client.ping():
            print("✓ Redis连接成功")
            return True
        else:
            print("✗ Redis无法ping通")
            return False
    except Exception as e:
        print(f"✗ Redis连接失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 40)
    print("🧪 浮图架构简化测试")
    print("=" * 40)
    
    success = True
    success &= test_basic_imports()
    success &= test_redis()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ 所有测试通过")
    else:
        print("❌ 部分测试失败")

if __name__ == "__main__":
    main()
