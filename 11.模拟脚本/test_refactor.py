"""
测试重构后的脚本执行器
"""
import asyncio
import sys
import os

# 添加上级目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from script_executor import ScriptExecutor

async def test_refactored_executor():
    """测试重构后的脚本执行器"""
    executor = ScriptExecutor()
    
    print("🧪 测试重构后的脚本执行器...")
    print("📋 可用命令列表:")
    commands = executor.get_available_commands()
    for cmd, desc in commands.items():
        print(f"  {cmd}: {desc}")
    
    # 测试简单的命令
    simple_scripts = [
        {
            "cmd": "print",
            "message": "=== 测试重构后的执行器 ===",
            "comment": "测试打印命令"
        },
        {
            "cmd": "sleep",
            "seconds": 0.5,
            "comment": "测试睡眠命令"
        },
        {
            "cmd": "print",
            "message": "重构测试完成！",
            "comment": "完成测试"
        }
    ]
    
    try:
        results = await executor.execute_script(simple_scripts)
        print(f"\n🎯 测试结果: {len(results)} 个命令执行完成")
        for cmd, result in results.items():
            print(f"  {cmd}: {result}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        executor.close()

if __name__ == "__main__":
    asyncio.run(test_refactored_executor())
