# 测试模拟脚本功能

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from script_executor import ScriptExecutor

async def test_basic_functionality():
    """测试基本功能"""
    print("🧪 测试模拟脚本基本功能")
    
    executor = ScriptExecutor()
    
    # 简单的测试脚本
    test_scripts = [
        {"cmd": "print", "message": "开始测试"},
        {"cmd": "sleep", "seconds": 1.0},
        {"cmd": "print", "message": "测试完成"}
    ]
    
    try:
        results = await executor.execute_script(test_scripts)
        print("\n✅ 基本功能测试通过")
        print(f"📊 结果: {results}")
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
    finally:
        executor.close()

async def test_parameter_reference():
    """测试参数引用功能"""
    print("\n🧪 测试参数引用功能")
    
    executor = ScriptExecutor()
    
    # 模拟一个返回结果
    executor.results["mock_cmd"] = {"field1": "value1", "field2": 123}
    
    # 测试参数引用
    test_value = executor._resolve_value("ret[\"mock_cmd\"][\"field1\"]")
    
    if test_value == "value1":
        print("✅ 参数引用测试通过")
    else:
        print(f"❌ 参数引用测试失败: 期望 'value1', 得到 '{test_value}'")
    
    executor.close()

def test_command_registration():
    """测试命令注册功能"""
    print("\n🧪 测试命令注册功能")
    
    executor = ScriptExecutor()
    
    expected_commands = [
        "auth", "select_area", "connect_gate", "connect_login", 
        "login", "sleep", "print"
    ]
    
    missing_commands = []
    for cmd in expected_commands:
        if cmd not in executor.command_functions:
            missing_commands.append(cmd)
    
    if not missing_commands:
        print("✅ 命令注册测试通过")
        print(f"📝 已注册命令: {list(executor.command_functions.keys())}")
    else:
        print(f"❌ 命令注册测试失败，缺少命令: {missing_commands}")
    
    executor.close()

async def main():
    """主测试函数"""
    print("🚀 开始测试模拟脚本工具")
    print("=" * 50)
    
    # 运行测试
    test_command_registration()
    await test_basic_functionality()
    await test_parameter_reference()
    
    print("\n🎉 所有测试完成!")

if __name__ == "__main__":
    asyncio.run(main())
