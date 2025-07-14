# 模拟脚本主入口

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def show_main_menu():
    """显示主菜单"""
    print("\n" + "=" * 50)
    print("          🎯 模拟脚本工具集合")
    print("=" * 50)
    print("🔧 可用工具:")
    print("  1. script_editor  - 📝 脚本编辑器 (交互式创建和编辑脚本)")
    print("  2. quick_runner   - ⚡ 快速运行器 (运行示例脚本)")
    print("  3. examples       - 📁 查看示例脚本")
    print("  4. help           - 📚 查看帮助")
    print("  0. quit           - 🚪 退出")
    print("=" * 50)

def show_examples():
    """显示示例脚本"""
    print("\n📁 示例脚本:")
    examples = {
        "login_flow.json": "完整登录流程 (HTTP认证 → 选服 → 连接网关 → 登录)",
        "auth_only.json": "仅HTTP认证和选服",
        "direct_login.json": "直接连接并登录 (需要预先获得的signature)"
    }
    
    for filename, description in examples.items():
        print(f"  📄 {filename}")
        print(f"     {description}")
    
    print("\n💡 新功能:")
    print("  - connect_gate 自动从 select_area 获取网关地址和端口")
    print("  - login 自动从之前命令获取 signature、role_id 和 user_name")
    print("  - 简化脚本编写，减少手动参数配置")
    
    print("\n💡 使用方法:")
    print("  - 选择 '快速运行器' 来运行这些示例")
    print("  - 或者在脚本编辑器中使用 'load' 命令加载")

def show_help():
    """显示帮助信息"""
    print("\n📚 帮助信息:")
    print("🎯 模拟脚本工具功能:")
    print("  1. 按顺序执行测试命令")
    print("  2. 支持参数的动态引用")
    print("  3. 提供交互式编辑界面")
    print("  4. 支持脚本的保存和加载")
    
    print("\n🔧 可用命令:")
    commands = {
        "auth": "HTTP认证登录",
        "select_area": "选择游戏区域",
        "connect_gate": "连接游戏网关",
        "connect_login": "连接登录服务器",
        "login": "游戏服登录",
        "sleep": "等待指定时间",
        "print": "输出调试信息"
    }
    
    for cmd, desc in commands.items():
        print(f"  - {cmd}: {desc}")
    
    print("\n📋 脚本格式:")
    print("  [")
    print("    {\"cmd\": \"auth\", \"user_name\": \"q1\", \"channel\": \"dev\"},")
    print("    {\"cmd\": \"select_area\", \"open_id\": \"ret[\\\"auth\\\"][\\\"OpenId\\\"]\", \"area_id\": 1},")
    print("    {\"cmd\": \"connect_gate\"},")
    print("    {\"cmd\": \"login\", \"signature\": \"ret[\\\"select_area\\\"][\\\"Signature\\\"]\", \"role_id\": 903}")
    print("  ]")
    
    print("\n💡 参数引用:")
    print("  - 使用 ret[\"命令名\"][\"字段名\"] 引用之前命令的返回值")
    print("  - 例: ret[\"auth\"][\"OpenId\"] 获取认证返回的OpenId")
    
    print("\n🚀 快速开始:")
    print("  1. 选择 '快速运行器' 运行示例脚本")
    print("  2. 或选择 '脚本编辑器' 创建自定义脚本")
    print("  3. 脚本会自动处理参数依赖和等待")

async def main():
    """主函数"""
    print("🎯 欢迎使用模拟脚本工具!")
    
    while True:
        show_main_menu()
        try:
            choice = input("请选择操作: ").strip()
            
            if choice == "0" or choice.lower() == "quit":
                print("👋 再见!")
                break
            
            elif choice == "1" or choice.lower() == "script_editor":
                print("🚀 启动脚本编辑器...")
                from script_editor import ScriptEditor
                editor = ScriptEditor()
                await editor.run()
            
            elif choice == "2" or choice.lower() == "quick_runner":
                print("🚀 启动快速运行器...")
                from quick_runner import QuickRunner
                runner = QuickRunner()
                await runner.run_interactive()
            
            elif choice == "3" or choice.lower() == "examples":
                show_examples()
            
            elif choice == "4" or choice.lower() == "help":
                show_help()
            
            else:
                print("❌ 无效选择")
            
            if choice not in ["3", "4", "examples", "help"]:
                input("\n按回车返回主菜单...")
            
        except KeyboardInterrupt:
            print("\n👋 程序被中断，再见!")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            input("按回车继续...")

if __name__ == "__main__":
    asyncio.run(main())
