"""
测试重构后的数据库操作
验证所有接口是否正常工作
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlite_module import (
    get_database_manager, 
    create_dataset, 
    add_image_to_dataset,
    get_datasets,
    get_images_by_dataset_id,
    update_dataset_stats,
    delete_dataset,
    initialize_database
)


def test_database_operations():
    """测试数据库操作"""
    print("=== 测试数据库重构结果 ===\n")
    
    # 1. 初始化数据库
    print("1. 初始化数据库...")
    try:
        initialize_database()
        print("✓ 数据库初始化成功")
    except Exception as e:
        print(f"✗ 数据库初始化失败: {e}")
        return
    
    # 2. 创建测试数据集
    print("\n2. 创建测试数据集...")
    try:
        dataset_id = create_dataset("测试数据集重构", "用于测试重构后的数据库操作")
        print(f"✓ 数据集创建成功, ID: {dataset_id}")
    except Exception as e:
        print(f"✗ 数据集创建失败: {e}")
        return
    
    # 3. 添加测试图片
    print("\n3. 添加测试图片...")
    try:
        image_id1 = add_image_to_dataset(dataset_id, "test1.jpg", "/path/to/test1.jpg", 1024, "hash1")
        image_id2 = add_image_to_dataset(dataset_id, "test2.jpg", "/path/to/test2.jpg", 2048, "hash2")
        print(f"✓ 图片添加成功, IDs: {image_id1}, {image_id2}")
    except Exception as e:
        print(f"✗ 图片添加失败: {e}")
        return
    
    # 4. 查询数据集列表
    print("\n4. 查询所有数据集...")
    try:
        datasets = get_datasets()
        print(f"✓ 查询到 {len(datasets)} 个数据集")
        for dataset in datasets:
            print(f"   - {dataset['name']}: {dataset['description']}")
    except Exception as e:
        print(f"✗ 查询数据集失败: {e}")
    
    # 5. 查询数据集中的图片
    print("\n5. 查询数据集中的图片...")
    try:
        images = get_images_by_dataset_id(dataset_id)
        print(f"✓ 查询到 {len(images)} 张图片")
        for image in images:
            print(f"   - {image['filename']}: {image['file_size']} bytes")
    except Exception as e:
        print(f"✗ 查询图片失败: {e}")
    
    # 6. 更新数据集统计信息
    print("\n6. 更新数据集统计信息...")
    try:
        success = update_dataset_stats(dataset_id)
        print(f"✓ 统计信息更新{'成功' if success else '失败'}")
    except Exception as e:
        print(f"✗ 统计信息更新失败: {e}")
    
    # 7. 验证仓储模式
    print("\n7. 验证仓储模式...")
    try:
        db_manager = get_database_manager()
        dataset_repo = db_manager.get_dataset_repository()
        image_repo = db_manager.get_image_repository()
        
        # 通过仓储获取数据
        dataset = dataset_repo.get_dataset_by_id(dataset_id)
        stats = dataset_repo.get_dataset_stats(dataset_id)
        images = image_repo.get_images_by_dataset(dataset_id)
        
        print(f"✓ 仓储模式工作正常")
        print(f"   - 数据集: {dataset['name']}")
        print(f"   - 统计: {stats['image_count']} 张图片, {stats['total_size_bytes']} bytes")
        print(f"   - 图片数量: {len(images)}")
    except Exception as e:
        print(f"✗ 仓储模式测试失败: {e}")
    
    # 8. 清理测试数据
    print("\n8. 清理测试数据...")
    try:
        success = delete_dataset(dataset_id)
        print(f"✓ 测试数据清理{'成功' if success else '失败'}")
    except Exception as e:
        print(f"✗ 清理测试数据失败: {e}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_database_operations()
