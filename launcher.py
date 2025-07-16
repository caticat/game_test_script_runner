#!/usr/bin/env python3
# 协议测试工具启动器

import os
import sys
import subprocess
from typing import Dict, List

class TestToolLauncher:
    """测试工具启动器"""
    
    def __init__(self):
        self.tools = {
            "1": {
                "name": "HTTP认证测试",
                "file": "src/auth_server/01.http_auth.py",
                "description": "测试HTTP登录认证和选服功能"
            },
            "2": {
                "name": "账号封禁管理",
                "file": "src/auth_server/02.封禁账号.py",
                "description": "管理账号封禁/解封功能"
            },
            "3": {
                "name": "角色数据变更",
                "file": "src/auth_server/03.模拟角色数据变更.py",
                "description": "模拟角色数据变更通知"
            },
            "4": {
                "name": "登录测试",
                "file": "src/gateway/01.登录.py",
                "description": "游戏服TCP连接和登录测试"
            },
            "5": {
                "name": "模拟脚本工具",
                "file": "src/script_runner/main.py",
                "description": "按顺序执行测试命令，支持参数引用和异步等待"
            }
        }
    
    def show_menu(self):
        """显示主菜单"""
        print("=" * 50)
        print("        协议测试工具集合")
        print("=" * 50)
        print()
        
        for key, tool in self.tools.items():
            print(f"{key}. {tool['name']}")
            print(f"   {tool['description']}")
            print()
        
        print("0. 退出 (可输入 0/q/quit)")
        print("=" * 50)
    
    def run_tool(self, tool_key: str):
        """运行指定的测试工具"""
        if tool_key not in self.tools:
            print(f"无效的工具选择: {tool_key}")
            return
        
        tool = self.tools[tool_key]
        script_path = os.path.join(os.path.dirname(__file__), tool["file"])
        
        if not os.path.exists(script_path):
            print(f"脚本文件不存在: {script_path}")
            return
        
        print(f"启动 {tool['name']}...")
        print(f"文件: {tool['file']}")
        print("-" * 30)
        
        try:
            # 运行脚本
            subprocess.run([sys.executable, script_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"脚本运行失败: {e}")
        except KeyboardInterrupt:
            print("\n脚本被用户中断")
        except Exception as e:
            print(f"运行脚本时发生错误: {e}")
    
    def run(self):
        """运行主程序"""
        while True:
            self.show_menu()
            
            try:
                choice = input("请选择要运行的工具 (0-5): ").strip()
                
                if choice == "0" or choice.lower() == "q" or choice.lower() == "quit":
                    print("👋 再见！")
                    break
                elif choice in self.tools:
                    self.run_tool(choice)
                    input("\n按Enter键返回主菜单...")
                else:
                    print("无效的选择，请重新输入")
                    input("按Enter键继续...")
            except KeyboardInterrupt:
                print("\n\n程序被用户中断")
                break
            except Exception as e:
                print(f"发生错误: {e}")
                input("按Enter键继续...")

def main():
    """主函数"""
    launcher = TestToolLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
