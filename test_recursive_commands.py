#!/usr/bin/env python3
"""
测试递归命令发现功能
"""
import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.script_runner.script_executor import ScriptExecutor

def test_recursive_command_discovery():
    """测试递归命令发现"""
    print("🧪 测试递归命令发现功能")
    print("=" * 50)
    
    # 创建脚本执行器
    executor = ScriptExecutor()
    
    # 获取所有可用命令
    available_commands = executor.command_manager.get_available_commands()
    
    print(f"📋 发现了 {len(available_commands)} 个命令:")
    print()
    
    # 按命令名称排序并显示
    for cmd_name in sorted(available_commands.keys()):
        description = available_commands[cmd_name]
        print(f"  • {cmd_name:<20} - {description}")
    
    print()
    print("🔍 重点检查新的递归命令:")
    
    # 检查是否发现了新的递归命令
    expected_commands = [
        "abc.def_gh",
        "abc.another_test", 
        "abc.nested.deep_test"
    ]
    
    for cmd_name in expected_commands:
        if cmd_name in available_commands:
            print(f"  ✅ {cmd_name} - 已发现")
        else:
            print(f"  ❌ {cmd_name} - 未发现")
    
    print()
    print("🧪 测试命令执行:")
    
    # 测试执行递归命令
    test_commands = [
        ("abc.def_gh", {"message": "测试递归命令发现！"}),
        ("abc.another_test", {"value": 100}),
        ("abc.nested.deep_test", {"depth": 5, "name": "递归测试"})
    ]
    
    for cmd_name, params in test_commands:
        if cmd_name in available_commands:
            try:
                print(f"▶️  执行命令: {cmd_name}")
                result = executor.command_manager.execute_command(cmd_name, **params)
                print(f"  ✅ 执行成功: {result}")
            except Exception as e:
                print(f"  ❌ 执行失败: {e}")
        else:
            print(f"  ⚠️  命令 {cmd_name} 未发现，跳过测试")
        print()

if __name__ == "__main__":
    test_recursive_command_discovery()
