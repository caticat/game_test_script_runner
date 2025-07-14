# 交互式脚本编辑器和运行器

import sys
import os
import json
import asyncio
from typing import Dict, List, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from script_executor import ScriptExecutor
from utils.utils import Utils

class ScriptEditor:
    """脚本编辑器"""
    
    def __init__(self):
        self.scripts: List[Dict[str, Any]] = []
        self.executor = ScriptExecutor()
    
    def show_menu(self):
        """显示主菜单"""
        print("\n" + "=" * 50)
        print("          🎯 模拟脚本工具")
        print("=" * 50)
        print("📝 当前脚本:")
        if not self.scripts:
            print("  (空)")
        else:
            for i, script in enumerate(self.scripts, 1):
                print(f"  {i}. {script['cmd']} - {script}")
        
        print("\n🔧 可用命令:")
        print("  1. add     - 添加脚本命令")
        print("  2. edit    - 编辑脚本命令")
        print("  3. delete  - 删除脚本命令")
        print("  4. clear   - 清空脚本")
        print("  5. load    - 从文件加载脚本")
        print("  6. save    - 保存脚本到文件")
        print("  7. run     - 运行脚本")
        print("  8. example - 查看示例脚本")
        print("  9. help    - 查看帮助")
        print("  0. quit    - 退出")
        print("=" * 50)
    
    def add_command(self):
        """添加命令"""
        print("\n📝 添加新命令")
        self.show_available_commands()
        
        cmd = input("请输入命令名称: ").strip()
        if not cmd:
            print("❌ 命令名称不能为空")
            return
        
        script = {"cmd": cmd}
        
        # 根据命令类型提示参数
        if cmd == "auth":
            script["user_name"] = input("用户名 (默认: q1): ").strip() or "q1"
            script["channel"] = input("渠道 (默认: dev): ").strip() or "dev"
        
        elif cmd == "select_area":
            script["open_id"] = input("OpenId (可使用 ret[\"auth\"][\"OpenId\"]): ").strip()
            script["area_id"] = int(input("区域ID (默认: 1): ").strip() or "1")
            script["login_token"] = input("LoginToken (可使用 ret[\"auth\"][\"LoginToken\"]): ").strip()
        
        elif cmd == "connect_gate":
            print("💡 connect_gate 命令会自动从 select_area 结果中获取网关地址和端口")
            print("   如果没有 select_area 结果，将使用配置文件中的默认值")
            # 不需要额外参数
        
        elif cmd == "connect_login":
            print("💡 connect_login 命令使用配置文件中的登录服地址")
            # 不需要额外参数
        
        elif cmd == "login":
            print("💡 login 命令可以自动获取参数:")
            print("   - signature: 来自 select_area 的 Signature")
            print("   - role_id: 来自 select_area 的 RoleId")
            print("   - user_name: 来自 auth 的 OpenId")
            print("   如果要覆盖自动获取的参数，请手动输入:")
            
            signature = input("签名 (空白=自动获取): ").strip()
            if signature:
                script["signature"] = signature
                
            role_id = input("角色ID (空白=自动获取): ").strip()
            if role_id:
                script["role_id"] = int(role_id)
                
            user_name = input("用户名 (空白=自动获取): ").strip()
            if user_name:
                script["user_name"] = user_name
                
            area_id = input("区域ID (默认: 1): ").strip()
            if area_id:
                script["area_id"] = int(area_id)
            else:
                script["area_id"] = 1
                
            channel = input("渠道 (默认: dev): ").strip()
            if channel:
                script["channel"] = channel
            else:
                script["channel"] = "dev"
                
            platform = input("平台 (默认: windows): ").strip()
            if platform:
                script["platform"] = platform
            else:
                script["platform"] = "windows"
        
        elif cmd == "sleep":
            script["seconds"] = float(input("睡眠时间(秒) (默认: 1.0): ").strip() or "1.0")
        
        elif cmd == "print":
            script["message"] = input("要打印的消息: ").strip()
        
        else:
            # 通用参数输入
            print("请输入参数 (格式: key=value，空行结束):")
            while True:
                param = input("参数: ").strip()
                if not param:
                    break
                if "=" in param:
                    key, value = param.split("=", 1)
                    # 尝试转换数值
                    try:
                        if value.isdigit():
                            script[key.strip()] = int(value.strip())
                        elif value.replace(".", "").isdigit():
                            script[key.strip()] = float(value.strip())
                        else:
                            script[key.strip()] = value.strip()
                    except:
                        script[key.strip()] = value.strip()
        
        # 设置超时时间
        timeout = input("超时时间(秒) (默认: 30): ").strip()
        if timeout:
            script["timeout"] = int(timeout)
        
        self.scripts.append(script)
        print(f"✅ 已添加命令: {script}")
    
    def show_available_commands(self):
        """显示可用命令"""
        print("\n🔧 可用命令:")
        commands = {
            "auth": "HTTP认证 (返回OpenId和LoginToken)",
            "select_area": "选择服务器 (返回网关地址、端口、角色ID和签名)",
            "connect_gate": "连接网关 (自动使用select_area返回的地址)",
            "connect_login": "连接登录服 (使用配置文件地址)",
            "login": "游戏服登录 (自动使用之前命令的返回值)",
            "sleep": "睡眠等待",
            "print": "打印消息"
        }
        
        for cmd, desc in commands.items():
            print(f"  - {cmd}: {desc}")
        
        print("\n💡 自动参数获取:")
        print("  - connect_gate: 自动从select_area获取GateHost和GateTcpPort")
        print("  - login: 自动从auth获取user_name(OpenId)")
        print("  - login: 自动从select_area获取signature(Signature)和role_id(RoleId)")
        
        print("\n💡 参数值支持:")
        print("  - 直接输入: \"q1\", 123, 1.5")
        print("  - 引用返回值: ret[\"auth\"][\"OpenId\"]")
        print("  - 引用整个返回: ret[\"auth\"]")
        print("  - 空值自动获取: login命令的参数可以留空，会自动获取")
    
    def edit_command(self):
        """编辑命令"""
        if not self.scripts:
            print("❌ 没有可编辑的命令")
            return
        
        print("\n✏️  选择要编辑的命令:")
        for i, script in enumerate(self.scripts, 1):
            print(f"  {i}. {script}")
        
        try:
            index = int(input("输入序号: ").strip()) - 1
            if 0 <= index < len(self.scripts):
                print(f"当前命令: {self.scripts[index]}")
                print("请输入新的JSON格式命令 (空行取消):")
                new_cmd = input().strip()
                if new_cmd:
                    self.scripts[index] = json.loads(new_cmd)
                    print("✅ 命令已更新")
            else:
                print("❌ 序号无效")
        except (ValueError, json.JSONDecodeError) as e:
            print(f"❌ 输入错误: {e}")
    
    def delete_command(self):
        """删除命令"""
        if not self.scripts:
            print("❌ 没有可删除的命令")
            return
        
        print("\n🗑️  选择要删除的命令:")
        for i, script in enumerate(self.scripts, 1):
            print(f"  {i}. {script}")
        
        try:
            index = int(input("输入序号: ").strip()) - 1
            if 0 <= index < len(self.scripts):
                deleted = self.scripts.pop(index)
                print(f"✅ 已删除命令: {deleted}")
            else:
                print("❌ 序号无效")
        except ValueError:
            print("❌ 输入错误")
    
    def clear_scripts(self):
        """清空脚本"""
        if input("确认清空所有脚本? (y/N): ").strip().lower() == 'y':
            self.scripts.clear()
            print("✅ 脚本已清空")
    
    def load_script(self):
        """从文件加载脚本"""
        filename = input("请输入文件名: ").strip()
        if not filename:
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.scripts = json.load(f)
            print(f"✅ 已从 {filename} 加载脚本")
        except FileNotFoundError:
            print(f"❌ 文件 {filename} 不存在")
        except json.JSONDecodeError as e:
            print(f"❌ 文件格式错误: {e}")
        except Exception as e:
            print(f"❌ 加载失败: {e}")
    
    def save_script(self):
        """保存脚本到文件"""
        if not self.scripts:
            print("❌ 没有可保存的脚本")
            return
        
        filename = input("请输入保存的文件名: ").strip()
        if not filename:
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.scripts, f, indent=2, ensure_ascii=False)
            print(f"✅ 脚本已保存到 {filename}")
        except Exception as e:
            print(f"❌ 保存失败: {e}")
    
    async def run_script(self):
        """运行脚本"""
        if not self.scripts:
            print("❌ 没有可运行的脚本")
            return
        
        print("\n🚀 开始运行脚本...")
        print("📋 脚本内容:")
        Utils.print_dict(self.scripts)
        
        if input("\n确认运行? (y/N): ").strip().lower() != 'y':
            print("❌ 运行已取消")
            return
        
        try:
            results = await self.executor.execute_script(self.scripts)
            print("\n🎉 脚本运行完成!")
            print("📊 最终结果:")
            Utils.print_dict(results)
        except Exception as e:
            print(f"❌ 脚本运行失败: {e}")
        finally:
            self.executor.close()
    
    def show_example(self):
        """显示示例脚本"""
        print("\n📖 示例脚本 (自动参数获取版本):")
        example = [
            {"cmd": "auth", "user_name": "q1", "channel": "dev"},
            {"cmd": "select_area", "open_id": "ret[\"auth\"][\"OpenId\"]", "area_id": 1, "login_token": "ret[\"auth\"][\"LoginToken\"]"},
            {"cmd": "connect_gate"},
            {"cmd": "login"},
            {"cmd": "sleep", "seconds": 2.0},
            {"cmd": "print", "message": "登录流程完成!"}
        ]
        
        print(json.dumps(example, indent=2, ensure_ascii=False))
        
        print("\n💡 注意:")
        print("  - connect_gate 会自动使用 select_area 返回的 GateHost 和 GateTcpPort")
        print("  - login 会自动使用:")
        print("    * signature: 来自 select_area 的 Signature")
        print("    * role_id: 来自 select_area 的 RoleId")
        print("    * user_name: 来自 auth 的 OpenId")
        
        if input("\n是否加载此示例? (y/N): ").strip().lower() == 'y':
            self.scripts = example
            print("✅ 示例脚本已加载")
    
    def show_help(self):
        """显示帮助信息"""
        print("\n📚 帮助信息:")
        print("1. 脚本按顺序执行，支持参数引用")
        print("2. 参数格式:")
        print("   - 直接值: \"q1\", 123, 1.5")
        print("   - 引用返回值: ret[\"命令名\"][\"字段名\"]")
        print("3. 常用命令流程:")
        print("   auth → select_area → connect_gate → login")
        print("4. 脚本可以保存/加载为JSON文件")
        print("5. 每个命令都有超时设置(默认30秒)")
    
    async def run(self):
        """运行主程序"""
        print("🎯 欢迎使用模拟脚本工具!")
        
        while True:
            self.show_menu()
            try:
                choice = input("请选择操作: ").strip()
                
                if choice == "0" or choice.lower() == "quit":
                    print("👋 再见!")
                    break
                elif choice == "1" or choice.lower() == "add":
                    self.add_command()
                elif choice == "2" or choice.lower() == "edit":
                    self.edit_command()
                elif choice == "3" or choice.lower() == "delete":
                    self.delete_command()
                elif choice == "4" or choice.lower() == "clear":
                    self.clear_scripts()
                elif choice == "5" or choice.lower() == "load":
                    self.load_script()
                elif choice == "6" or choice.lower() == "save":
                    self.save_script()
                elif choice == "7" or choice.lower() == "run":
                    await self.run_script()
                elif choice == "8" or choice.lower() == "example":
                    self.show_example()
                elif choice == "9" or choice.lower() == "help":
                    self.show_help()
                else:
                    print("❌ 无效选择")
                
                input("\n按回车继续...")
                
            except KeyboardInterrupt:
                print("\n👋 程序被中断，再见!")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
                input("按回车继续...")

def main():
    """主函数"""
    editor = ScriptEditor()
    asyncio.run(editor.run())

if __name__ == "__main__":
    main()
