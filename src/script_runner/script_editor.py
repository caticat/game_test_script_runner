# 交互式脚本编辑器和运行器

import sys
import os
import json
import asyncio
from typing import Dict, List, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from script_executor import ScriptExecutor
from utils.utils import Utils
from utils.config_manager import config_manager

class ScriptEditor:
    """脚本编辑器"""
    
    def __init__(self):
        self.scripts: List[Dict[str, Any]] = []
        self.executor = ScriptExecutor()
        self.scripts_path = config_manager.get_scripts_path()
        
        # 确保脚本目录存在
        if not os.path.exists(self.scripts_path):
            os.makedirs(self.scripts_path)
    
    def get_scripts_directory(self) -> str:
        """获取脚本目录的完整路径"""
        if os.path.isabs(self.scripts_path):
            return self.scripts_path
        # 脚本目录相对于项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(project_root, self.scripts_path)
    
    def show_menu(self):
        """显示主菜单"""
        print("\n" + "=" * 60)
        print("          🎯 模拟脚本工具 - 交互式编辑器")
        print("=" * 60)
        print("📝 当前脚本:")
        if not self.scripts:
            print("  (空)")
        else:
            for i, script in enumerate(self.scripts, 1):
                cmd = script.get('cmd', '未知命令')
                desc = self._get_command_description(cmd)
                print(f"  {i}. {cmd} - {desc}")
        
        print(f"\n📁 脚本目录: {self.get_scripts_directory()}")
        
        print("\n🔧 可用命令:")
        print("  1. add      - 添加脚本命令")
        print("  2. edit     - 编辑脚本命令") 
        print("  3. delete   - 删除脚本命令")
        print("  4. clear    - 清空脚本")
        print("  5. load     - 从文件加载脚本")
        print("  6. save     - 保存脚本到文件")
        print("  7. run      - 运行脚本")
        print("  8. browse   - 浏览脚本目录")
        print("  9. example  - 查看示例脚本")
        print("  10. help    - 查看帮助")
        print("  11. commands - 查看所有可用命令")
        print("  0. quit     - 退出 (可输入 0/q/quit)")
        print("=" * 60)
    
    def _get_command_description(self, cmd: str) -> str:
        """获取命令描述"""
        available_commands = self.executor.get_available_commands()
        return available_commands.get(cmd, "未知命令")
    
    def add_command(self):
        """添加命令"""
        print("\n📝 添加新命令")
        self.show_available_commands()
        
        # 获取当前可用命令
        available_commands = self.executor.get_available_commands()
        
        cmd = input("\n请输入命令名称: ").strip()
        if not cmd:
            print("❌ 命令名称不能为空")
            return
        
        # 检查命令是否存在
        if cmd not in available_commands:
            print(f"❌ 未知命令: {cmd}")
            print(f"可用命令: {', '.join(available_commands.keys())}")
            return
        
        script = {"cmd": cmd}
        
        # 使用更智能的参数输入系统
        self._input_command_parameters(script, cmd)
        
        # 设置超时时间
        timeout = input("超时时间(秒) (默认: 30): ").strip()
        if timeout:
            try:
                script["timeout"] = int(timeout)
            except ValueError:
                print("⚠️  超时时间格式错误，使用默认值 30")
        
        self.scripts.append(script)
        print(f"✅ 已添加命令: {json.dumps(script, indent=2, ensure_ascii=False)}")
    
    def _input_command_parameters(self, script: Dict[str, Any], cmd: str):
        """智能输入命令参数"""
        print(f"\n💡 {cmd} 命令参数输入:")
        
        # 预定义的常见命令参数配置
        command_params = {
            "auth": [
                {"name": "user_name", "type": "str", "default": "q1", "desc": "用户名"},
                {"name": "channel", "type": "str", "default": "dev", "desc": "渠道"}
            ],
            "select_area": [
                {"name": "open_id", "type": "str", "default": "ret[\"auth\"][\"OpenId\"]", "desc": "OpenId"},
                {"name": "area_id", "type": "int", "default": 1, "desc": "区域ID"},
                {"name": "login_token", "type": "str", "default": "ret[\"auth\"][\"LoginToken\"]", "desc": "LoginToken"}
            ],
            "login": [
                {"name": "signature", "type": "str", "default": "ret[\"select_area\"][\"Signature\"]", "desc": "签名(可自动获取)"},
                {"name": "role_id", "type": "int", "default": "ret[\"select_area\"][\"RoleId\"]", "desc": "角色ID(可自动获取)"},
                {"name": "user_name", "type": "str", "default": "ret[\"auth\"][\"OpenId\"]", "desc": "用户名(可自动获取)"},
                {"name": "area_id", "type": "int", "default": 1, "desc": "区域ID"},
                {"name": "channel", "type": "str", "default": "dev", "desc": "渠道"},
                {"name": "platform", "type": "str", "default": "windows", "desc": "平台"}
            ],
            "sleep": [
                {"name": "seconds", "type": "float", "default": 1.0, "desc": "睡眠时间(秒)"}
            ],
            "print": [
                {"name": "message", "type": "str", "default": "", "desc": "要打印的消息"}
            ]
        }
        
        if cmd in command_params:
            # 使用预定义的参数配置
            for param in command_params[cmd]:
                self._input_parameter(script, param)
        else:
            # 通用参数输入
            print("请输入参数 (格式: key=value，空行结束):")
            while True:
                param = input("参数: ").strip()
                if not param:
                    break
                if "=" in param:
                    key, value = param.split("=", 1)
                    script[key.strip()] = self._parse_value(value.strip())
    
    def _input_parameter(self, script: Dict[str, Any], param: Dict[str, Any]):
        """输入单个参数"""
        name = param["name"]
        param_type = param["type"]
        default = param["default"]
        desc = param["desc"]
        
        prompt = f"{desc} (默认: {default}): "
        value = input(prompt).strip()
        
        if not value:
            # 使用默认值
            if isinstance(default, str) and default.startswith("ret["):
                # 保留引用表达式
                script[name] = default
            else:
                script[name] = default
        else:
            # 解析用户输入
            script[name] = self._parse_value(value)
    
    def _parse_value(self, value: str) -> Any:
        """解析参数值"""
        # 如果是引用表达式，直接返回
        if value.startswith("ret["):
            return value
        
        # 尝试解析为数字
        try:
            if "." in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            # 返回字符串
            return value
    
    def show_available_commands(self):
        """显示可用命令"""
        print("\n🔧 可用命令:")
        
        # 从executor获取最新的命令列表
        commands = self.executor.get_available_commands()
        
        # 按命令名称排序
        for cmd in sorted(commands.keys()):
            desc = commands[cmd]
            print(f"  • {cmd:<15} - {desc}")
        
        print(f"\n📊 总计: {len(commands)} 个命令")
        
        print("\n💡 参数使用说明:")
        print("  • 直接输入: \"q1\", 123, 1.5")
        print("  • 引用返回值: ret[\"auth\"][\"OpenId\"]")
        print("  • 引用整个返回: ret[\"auth\"]")
        print("  • 部分命令支持自动参数获取")
        
        print("\n🔗 常见命令流程:")
        print("  1. auth → select_area → connect_gate → login")
        print("  2. connect_login → auth → select_area → connect_gate → login")
        print("  3. 在命令间使用 sleep 添加延迟")
        print("  4. 使用 print 显示调试信息")
    
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
        scripts_dir = self.get_scripts_directory()
        
        print(f"\n📂 从脚本目录加载: {scripts_dir}")
        
        # 列出可用的脚本文件
        try:
            script_files = [f for f in os.listdir(scripts_dir) if f.endswith('.json')]
            if not script_files:
                print("❌ 脚本目录中没有找到 .json 文件")
                filename = input("请输入完整文件路径: ").strip()
            else:
                print("📋 可用脚本文件:")
                for i, filename in enumerate(script_files, 1):
                    print(f"  {i}. {filename}")
                
                choice = input("选择文件 (输入序号) 或输入完整路径: ").strip()
                
                if choice.isdigit() and 1 <= int(choice) <= len(script_files):
                    filename = os.path.join(scripts_dir, script_files[int(choice) - 1])
                else:
                    filename = choice
        except OSError:
            print("❌ 无法访问脚本目录")
            filename = input("请输入完整文件路径: ").strip()
        
        if not filename:
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                self.scripts = json.loads(content)
            print(f"✅ 已从 {filename} 加载脚本")
            print(f"📊 加载了 {len(self.scripts)} 个命令")
        except FileNotFoundError:
            print(f"❌ 文件 {filename} 不存在")
        except json.JSONDecodeError as e:
            print(f"❌ 文件格式错误: {e}")
        except Exception as e:
            print(f"❌ 加载失败: {e}")
    
    def browse_scripts(self):
        """浏览脚本目录"""
        scripts_dir = self.get_scripts_directory()
        
        print(f"\n📂 浏览脚本目录: {scripts_dir}")
        
        try:
            files = os.listdir(scripts_dir)
            script_files = [f for f in files if f.endswith('.json')]
            
            if not script_files:
                print("📭 目录为空或没有 .json 文件")
                return
            
            print("📋 可用脚本文件:")
            for i, filename in enumerate(script_files, 1):
                file_path = os.path.join(scripts_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = json.load(f)
                        cmd_count = len(content) if isinstance(content, list) else 1
                        print(f"  {i}. {filename:<20} ({cmd_count} 个命令)")
                except:
                    print(f"  {i}. {filename:<20} (格式错误)")
            
            choice = input("\n选择文件查看详情 (输入序号，空行返回): ").strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(script_files):
                filename = script_files[int(choice) - 1]
                self._preview_script(os.path.join(scripts_dir, filename))
                
        except OSError as e:
            print(f"❌ 无法访问脚本目录: {e}")
    
    def _preview_script(self, file_path: str):
        """预览脚本内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            print(f"\n📄 脚本预览: {os.path.basename(file_path)}")
            print("-" * 50)
            
            if isinstance(content, list):
                for i, script in enumerate(content, 1):
                    cmd = script.get('cmd', '未知命令')
                    desc = self._get_command_description(cmd)
                    print(f"  {i}. {cmd} - {desc}")
            else:
                print(f"  单个命令: {content}")
                
            print("-" * 50)
            print(json.dumps(content, indent=2, ensure_ascii=False))
            
            if input("\n是否加载此脚本? (y/N): ").strip().lower() == 'y':
                self.scripts = content if isinstance(content, list) else [content]
                print(f"✅ 已加载 {len(self.scripts)} 个命令")
                
        except Exception as e:
            print(f"❌ 预览失败: {e}")
    
    def save_script(self):
        """保存脚本到文件"""
        if not self.scripts:
            print("❌ 没有可保存的脚本")
            return
        
        scripts_dir = self.get_scripts_directory()
        
        print(f"\n💾 保存脚本到: {scripts_dir}")
        
        filename = input("请输入文件名 (不含路径): ").strip()
        if not filename:
            return
        
        # 确保文件扩展名
        if not filename.endswith('.json'):
            filename += '.json'
        
        file_path = os.path.join(scripts_dir, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.scripts, f, indent=2, ensure_ascii=False)
            print(f"✅ 脚本已保存到 {file_path}")
            print(f"📊 保存了 {len(self.scripts)} 个命令")
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
        print("\n📖 示例脚本:")
        
        examples = {
            "完整登录流程": [
                {"cmd": "auth", "user_name": "q1", "channel": "dev"},
                {"cmd": "select_area", "open_id": "ret[\"auth\"][\"OpenId\"]", "area_id": 1, "login_token": "ret[\"auth\"][\"LoginToken\"]"},
                {"cmd": "connect_gate"},
                {"cmd": "login"},
                {"cmd": "sleep", "seconds": 2.0},
                {"cmd": "print", "message": "登录流程完成!"}
            ],
            "HTTP认证测试": [
                {"cmd": "auth", "user_name": "test_user", "channel": "dev"},
                {"cmd": "print", "message": "认证结果: ret[\"auth\"]"}
            ],
            "批量测试": [
                {"cmd": "auth", "user_name": "user1", "channel": "dev"},
                {"cmd": "sleep", "seconds": 1.0},
                {"cmd": "auth", "user_name": "user2", "channel": "dev"},
                {"cmd": "sleep", "seconds": 1.0},
                {"cmd": "auth", "user_name": "user3", "channel": "dev"}
            ]
        }
        
        print("� 可用示例:")
        example_keys = list(examples.keys())
        for i, name in enumerate(example_keys, 1):
            print(f"  {i}. {name}")
        
        choice = input("\n选择示例 (输入序号): ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(example_keys):
            selected_name = example_keys[int(choice) - 1]
            selected_example = examples[selected_name]
            
            print(f"\n📄 示例: {selected_name}")
            print(json.dumps(selected_example, indent=2, ensure_ascii=False))
            
            print("\n💡 说明:")
            print("  • connect_gate 会自动使用 select_area 返回的网关地址")
            print("  • login 会自动获取必要的认证参数")
            print("  • 使用 ret[\"命令名\"][\"字段名\"] 引用前面命令的返回值")
            
            if input("\n是否加载此示例? (y/N): ").strip().lower() == 'y':
                self.scripts = selected_example
                print(f"✅ 示例脚本已加载 ({len(self.scripts)} 个命令)")
        else:
            print("❌ 无效选择")
    
    def show_help(self):
        """显示帮助信息"""
        print("\n📚 帮助信息:")
        print("=" * 50)
        
        print("🎯 脚本编辑器功能:")
        print("  • 交互式创建和编辑脚本")
        print("  • 智能参数输入和验证")
        print("  • 自动命令发现和描述")
        print("  • 脚本文件管理和预览")
        
        print("\n📝 脚本格式:")
        print("  • 脚本为 JSON 格式的命令列表")
        print("  • 每个命令包含 cmd 和相关参数")
        print("  • 按顺序执行，支持参数引用")
        
        print("\n🔗 参数引用:")
        print("  • 直接值: \"q1\", 123, 1.5")
        print("  • 引用字段: ret[\"auth\"][\"OpenId\"]")
        print("  • 引用整个返回: ret[\"auth\"]")
        print("  • 支持嵌套引用和复杂表达式")
        
        print("\n🚀 常用命令流程:")
        print("  1. HTTP认证: auth")
        print("  2. 选择区服: select_area")
        print("  3. 连接网关: connect_gate")
        print("  4. 游戏登录: login")
        print("  5. 添加延迟: sleep")
        print("  6. 调试输出: print")
        
        print("\n💡 使用技巧:")
        print("  • 使用 browse 浏览现有脚本")
        print("  • 使用 example 查看示例")
        print("  • 使用 commands 查看所有命令")
        print("  • 脚本保存在配置的 scripts_path 目录")
        print("  • 支持自动参数获取和智能默认值")
        
        print("\n⚙️ 配置:")
        print(f"  • 脚本目录: {self.get_scripts_directory()}")
        print(f"  • 默认超时: 30 秒")
        print(f"  • 可用命令: {len(self.executor.get_available_commands())} 个")
        
        print("=" * 50)
    
    async def run(self):
        """运行主程序"""
        print("🎯 欢迎使用模拟脚本工具!")
        print(f"📁 工作目录: {self.get_scripts_directory()}")
        
        while True:
            self.show_menu()
            try:
                choice = input("请选择操作: ").strip()
                
                if choice == "0" or choice.lower() == "quit" or choice.lower() == "q":
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
                elif choice == "8" or choice.lower() == "browse":
                    self.browse_scripts()
                elif choice == "9" or choice.lower() == "example":
                    self.show_example()
                elif choice == "10" or choice.lower() == "help":
                    self.show_help()
                elif choice == "11" or choice.lower() == "commands":
                    self.show_available_commands()
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
