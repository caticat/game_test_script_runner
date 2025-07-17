# 测试运行器 - 统一运行所有测试

import sys
import os
import asyncio

# 添加src/script_runner目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', 'script_runner'))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行模拟脚本工具测试套件")
    print("=" * 60)
    
    test_results = []
    
    # 测试1: 基本功能测试
    print("\n📦 测试套件 1: 基本功能测试")
    print("-" * 40)
    try:
        from test_script import main as test_script_main
        await test_script_main()
        test_results.append(("基本功能测试", True, ""))
    except Exception as e:
        test_results.append(("基本功能测试", False, str(e)))
        print(f"❌ 基本功能测试失败: {e}")
    
    # 测试2: 自动参数获取测试
    print("\n📦 测试套件 2: 自动参数获取测试")
    print("-" * 40)
    try:
        from test_auto_params import main as test_auto_params_main
        await test_auto_params_main()
        test_results.append(("自动参数获取测试", True, ""))
    except Exception as e:
        test_results.append(("自动参数获取测试", False, str(e)))
        print(f"❌ 自动参数获取测试失败: {e}")
    
    # 显示测试总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, success, error_msg in test_results:
        if success:
            print(f"✅ {test_name}: 通过")
            passed += 1
        else:
            print(f"❌ {test_name}: 失败 - {error_msg}")
            failed += 1
    
    print("-" * 60)
    print(f"📈 总计: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试都通过了！")
        return True
    else:
        print("⚠️  有测试失败，请检查相关功能")
        return False

def main():
    """主函数"""
    return asyncio.run(run_all_tests())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
