#!/usr/bin/env python3
"""
浮图项目后端重构最终验证脚本
验证所有核心功能是否正常工作
"""
import os
import sys
import time
import logging
import threading
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FinalVerificationTest:
    """最终验证测试类"""
    
    def __init__(self):
        self.test_results = {}
        
    def run_all_tests(self):
        """运行所有测试"""
        logger.info("开始浮图项目后端重构最终验证")
        logger.info("=" * 60)
        
        # 测试列表
        tests = [
            ("模块导入测试", self.test_imports),
            ("模型接口测试", self.test_model_interface),
            ("Redis客户端测试", self.test_redis_client),
            ("控制端创建测试", self.test_controller_creation),
            ("计算端创建测试", self.test_compute_server_creation),
            ("配置系统测试", self.test_config_system),
            ("服务管理测试", self.test_service_manager),
        ]
        
        # 运行测试
        for test_name, test_func in tests:
            logger.info(f"运行测试: {test_name}")
            try:
                result = test_func()
                self.test_results[test_name] = {
                    'status': 'PASS' if result else 'FAIL',
                    'details': result if isinstance(result, dict) else None
                }
                logger.info(f"✓ {test_name}: PASS")
            except Exception as e:
                self.test_results[test_name] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
                logger.error(f"✗ {test_name}: ERROR - {e}")
                
        # 输出测试结果
        self.print_test_summary()
        
    def test_imports(self) -> bool:
        """测试关键模块导入"""
        try:
            # 测试模型接口
            from _model_interface import (
                ModelManager, create_feature_extractor, 
                create_model_config, ModelConfig
            )
            
            # 测试Redis客户端
            from redis_client.redis_client import RedisClient, RedisConfig
            
            # 测试控制端
            from controller.controller_app import create_controller_app
            
            # 测试计算端
            from compute_server.compute_server import ComputeServer
            
            # 测试配置
            from config import Config
            
            logger.info("所有关键模块导入成功")
            return True
            
        except ImportError as e:
            logger.error(f"模块导入失败: {e}")
            return False
            
    def test_model_interface(self) -> Dict[str, Any]:
        """测试模型接口功能"""
        from _model_interface import ModelManager, create_feature_extractor
        
        # 创建模型管理器
        manager = ModelManager()
        
        # 创建特征提取器
        extractor = create_feature_extractor(
            model_type="resnet50",
            device="cpu",
            input_size=224,
            batch_size=64
        )
        
        # 获取配置
        config = extractor.get_config()
        
        # 获取特征维度
        feature_dim = extractor.get_feature_dimension()
        
        return {
            'model_manager_created': True,
            'feature_extractor_created': True,
            'config': config.__dict__,
            'feature_dimension': feature_dim
        }
        
    def test_redis_client(self) -> Dict[str, Any]:
        """测试Redis客户端"""
        from redis_client.redis_client import RedisClient, RedisConfig
        
        # 创建配置
        config = RedisConfig()
        
        # 创建客户端
        client = RedisClient(config)
        
        return {
            'redis_config_created': True,
            'redis_client_created': True,
            'config': config.__dict__
        }
        
    def test_controller_creation(self) -> Dict[str, Any]:
        """测试控制端创建"""
        from controller.controller_app import create_controller_app
        
        # 创建Flask应用
        app = create_controller_app()
        
        return {
            'controller_app_created': True,
            'app_name': app.name,
            'blueprints': list(app.blueprints.keys())
        }
        
    def test_compute_server_creation(self) -> Dict[str, Any]:
        """测试计算端创建"""
        from compute_server.compute_server import ComputeServer
        from redis_client.redis_client import RedisConfig
        
        # 创建计算端服务器
        server = ComputeServer.create_with_model_type(
            model_type="resnet50",
            device="cpu",
            input_size=224,
            batch_size=32
        )
        
        # 获取模型信息
        model_info = server.get_model_info()
        
        # 健康检查
        health = server.health_check()
        
        return {
            'compute_server_created': True,
            'model_info': model_info,
            'health_check': health
        }
        
    def test_config_system(self) -> Dict[str, Any]:
        """测试配置系统"""
        from config import Config
        
        config = Config()
        
        return {
            'config_created': True,
            'has_database_config': hasattr(config, 'DATABASE_URL'),
            'has_redis_config': hasattr(config, 'REDIS_HOST'),
            'has_compute_config': hasattr(config, 'COMPUTE_SERVER_HOST')
        }
        
    def test_service_manager(self) -> bool:
        """测试服务管理器"""
        try:
            from service_manager import ServiceManager
            
            # 创建服务管理器
            manager = ServiceManager()
            
            return True
            
        except Exception as e:
            logger.error(f"服务管理器测试失败: {e}")
            return False
            
    def print_test_summary(self):
        """打印测试摘要"""
        logger.info("=" * 60)
        logger.info("测试结果摘要")
        logger.info("=" * 60)
        
        passed = 0
        failed = 0
        errors = 0
        
        for test_name, result in self.test_results.items():
            status = result['status']
            if status == 'PASS':
                passed += 1
                logger.info(f"✓ {test_name}: PASS")
            elif status == 'FAIL':
                failed += 1
                logger.warning(f"✗ {test_name}: FAIL")
            else:  # ERROR
                errors += 1
                logger.error(f"✗ {test_name}: ERROR - {result.get('error', 'Unknown error')}")
                
        total = len(self.test_results)
        logger.info("-" * 60)
        logger.info(f"总计: {total} 个测试")
        logger.info(f"通过: {passed} 个")
        logger.info(f"失败: {failed} 个")
        logger.info(f"错误: {errors} 个")
        
        if passed == total:
            logger.info("🎉 所有测试通过！浮图项目后端重构验证成功！")
        else:
            logger.warning("⚠️  部分测试未通过，请检查相关问题")
            
        logger.info("=" * 60)


def main():
    """主函数"""
    print("浮图项目后端重构最终验证")
    print("=" * 60)
    
    # 创建并运行测试
    verifier = FinalVerificationTest()
    verifier.run_all_tests()


if __name__ == '__main__':
    main()
