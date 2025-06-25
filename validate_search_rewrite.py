#!/usr/bin/env python3
"""
验证搜索功能重写的脚本
检查代码结构和依赖是否正确
"""

import os
import re
import sys

def check_imports():
    """检查导入语句"""
    print("=== 检查导入依赖 ===")
    
    search_routes_path = "backend_new/controller/route/search_routes.py"
    
    if not os.path.exists(search_routes_path):
        print(f"❌ 文件不存在: {search_routes_path}")
        return False
    
    with open(search_routes_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_imports = [
        "from flask import Blueprint",
        "import numpy as np",
        "from PIL import Image",
        "from redis_client.redis_client import get_redis_client",
        "from _index_interface import get_index_manager",
        "from _database_interface import get_dataset_repository, get_image_repository"
    ]
    
    all_imports_found = True
    for import_stmt in required_imports:
        if import_stmt in content:
            print(f"✅ {import_stmt}")
        else:
            print(f"❌ 缺少导入: {import_stmt}")
            all_imports_found = False
    
    return all_imports_found

def check_main_functions():
    """检查主要函数是否存在"""
    print("\n=== 检查主要函数 ===")
    
    search_routes_path = "backend_new/controller/route/search_routes.py"
    
    with open(search_routes_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_functions = [
        "def search_image():",
        "def _crop_image(",
        "def _extract_image_features(",
        "def _search_dataset_index(",
        "def _enrich_search_result("
    ]
    
    all_functions_found = True
    for func in required_functions:
        if func in content:
            print(f"✅ {func}")
        else:
            print(f"❌ 缺少函数: {func}")
            all_functions_found = False
    
    return all_functions_found

def check_api_structure():
    """检查API结构"""
    print("\n=== 检查API结构 ===")
    
    search_routes_path = "backend_new/controller/route/search_routes.py"
    
    with open(search_routes_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    api_features = [
        "@search_bp.route('/search', methods=['POST'])",
        "request.files['query_img']",
        "dataset_names = request.form.getlist('dataset_names[]')",
        "top_k = request.form.get('top_k'",
        "similarity_threshold = request.form.get('similarity_threshold'",
        "crop_x = request.form.get('crop_x'",
        "_extract_image_features(",
        "_search_dataset_index(",
        "return jsonify(response), 200"
    ]
    
    all_features_found = True
    for feature in api_features:
        if feature in content:
            print(f"✅ {feature}")
        else:
            print(f"❌ 缺少API特性: {feature}")
            all_features_found = False
    
    return all_features_found

def check_dependencies():
    """检查依赖文件是否存在"""
    print("\n=== 检查依赖文件 ===")
    
    dependency_files = [
        "backend_new/_index_interface.py",
        "backend_new/_database_interface.py", 
        "backend_new/redis_client/redis_client.py"
    ]
    
    all_deps_exist = True
    for dep_file in dependency_files:
        if os.path.exists(dep_file):
            print(f"✅ {dep_file}")
        else:
            print(f"❌ 依赖文件不存在: {dep_file}")
            all_deps_exist = False
    
    return all_deps_exist

def check_error_handling():
    """检查错误处理"""
    print("\n=== 检查错误处理 ===")
    
    search_routes_path = "backend_new/controller/route/search_routes.py"
    
    with open(search_routes_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    error_handling_patterns = [
        r"try:",
        r"except.*Exception.*:",
        r"current_app\.logger\.error",
        r"\}\),\s*500",
        r"finally:"
    ]
    
    all_patterns_found = True
    for pattern in error_handling_patterns:
        if re.search(pattern, content):
            print(f"✅ 错误处理模式: {pattern}")
        else:
            print(f"❌ 缺少错误处理: {pattern}")
            all_patterns_found = False
    
    return all_patterns_found

def check_response_format():
    """检查响应格式"""
    print("\n=== 检查响应格式 ===")
    
    search_routes_path = "backend_new/controller/route/search_routes.py"
    
    with open(search_routes_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    response_fields = [
        '"success": True',
        '"results":',
        '"total_found":',
        '"search_params":',
        '"query_info":'
    ]
    
    all_fields_found = True
    for field in response_fields:
        if field in content:
            print(f"✅ 响应字段: {field}")
        else:
            print(f"❌ 缺少响应字段: {field}")
            all_fields_found = False
    
    return all_fields_found

def main():
    """主验证函数"""
    print("🔍 验证图片搜索功能重写")
    
    checks = [
        ("导入依赖", check_imports),
        ("主要函数", check_main_functions),
        ("API结构", check_api_structure),
        ("依赖文件", check_dependencies),
        ("错误处理", check_error_handling),
        ("响应格式", check_response_format)
    ]
    
    all_passed = True
    results = {}
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results[check_name] = result
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ 检查 {check_name} 时发生错误: {e}")
            results[check_name] = False
            all_passed = False
    
    print(f"\n{'='*50}")
    print("📋 验证总结:")
    for check_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {check_name}: {status}")
    
    if all_passed:
        print("\n🎉 所有检查通过！搜索功能重写成功。")
        print("\n📝 下一步建议:")
        print("1. 启动Redis服务")
        print("2. 启动计算端服务")
        print("3. 启动后端服务")
        print("4. 运行测试: python test_search_function.py")
    else:
        print("\n⚠️  部分检查未通过，请检查上述问题。")
    
    return all_passed

if __name__ == '__main__':
    # 改变工作目录到项目根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    success = main()
    sys.exit(0 if success else 1)
