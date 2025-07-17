#!/usr/bin/env python3
"""
测试快速运行器功能
"""
import sys
import os
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'script_runner'))

from quick_runner import QuickRunner

async def test_quick_runner():
    """测试快速运行器"""
    print("🧪 测试快速运行器功能")
    print("=" * 40)
    
    runner = QuickRunner()
    
    # 测试脚本目录
    print(f"📁 脚本目录: {runner.examples_dir}")
    print(f"📁 目录存在: {runner.examples_dir.exists()}")
    
    # 测试脚本列表
    examples = runner.list_examples()
    print(f"📋 找到 {len(examples)} 个脚本文件:")
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example}")
    
    # 测试脚本内容显示
    if examples:
        print(f"\n🔍 测试显示第一个脚本内容:")
        content = runner.show_script_content(examples[0])
        if content:
            print("✅ 脚本内容读取成功")
        else:
            print("❌ 脚本内容读取失败")
    
    print("\n✅ 快速运行器测试完成")

if __name__ == "__main__":
    asyncio.run(test_quick_runner())
