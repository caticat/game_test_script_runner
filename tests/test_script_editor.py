#!/usr/bin/env python3
"""
简单测试script_editor的现代化功能
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'script_runner'))

from script_editor import ScriptEditor

def test_script_editor():
    """测试脚本编辑器功能"""
    print("🧪 测试脚本编辑器...")
    
    editor = ScriptEditor()
    
    # 测试基本功能
    print(f"✅ 初始化成功")
    print(f"📁 脚本目录: {editor.get_scripts_directory()}")
    print(f"🔧 可用命令数: {len(editor.executor.get_available_commands())}")
    
    # 测试命令获取
    commands = editor.executor.get_available_commands()
    print(f"📋 可用命令: {', '.join(sorted(commands.keys()))}")
    
    # 测试命令描述
    print("\n🔍 命令描述:")
    for cmd in sorted(commands.keys()):
        desc = editor._get_command_description(cmd)
        print(f"  • {cmd}: {desc}")
    
    print("\n✅ 所有测试通过!")

if __name__ == "__main__":
    test_script_editor()
