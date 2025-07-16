#!/usr/bin/env python3
"""
简化测试递归命令发现功能
"""
import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 直接测试CommandManager
from src.script_runner.commands.command_manager import CommandManager

class MockExecutor:
    def __init__(self):
        self.results = {}
        self.current_client = None

def test_command_manager():
    """测试命令管理器"""
    print("🧪 测试命令管理器")
    print("=" * 50)
    
    # 创建模拟执行器
    executor = MockExecutor()
    
    # 创建命令管理器
    manager = CommandManager(executor)
    
    # 获取所有可用命令
    available_commands = manager.get_available_commands()
    
    print(f"📋 发现了 {len(available_commands)} 个命令:")
    for cmd_name in sorted(available_commands.keys()):
        description = available_commands[cmd_name]
        print(f"  • {cmd_name:<25} - {description}")
    
    # 检查特定命令
    target_commands = ["abc.def_gh", "abc.another_test", "abc.nested.deep_test"]
    
    print(f"\n🔍 检查目标命令:")
    for cmd in target_commands:
        if cmd in available_commands:
            print(f"  ✅ {cmd} - 已发现")
        else:
            print(f"  ❌ {cmd} - 未发现")
    
    # 测试命令执行
    print(f"\n🧪 测试命令执行:")
    if "abc.def_gh" in available_commands:
        try:
            result = manager.execute_command("abc.def_gh", message="测试消息")
            print(f"  ✅ abc.def_gh 执行成功: {result}")
        except Exception as e:
            print(f"  ❌ abc.def_gh 执行失败: {e}")

if __name__ == "__main__":
    test_command_manager()
