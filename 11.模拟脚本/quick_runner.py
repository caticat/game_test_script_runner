# 快速脚本运行器

import sys
import os
import asyncio
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from script_executor import ScriptExecutor

class QuickRunner:
    """快速脚本运行器"""
    
    def __init__(self):
        self.examples_dir = Path(__file__).parent / "examples"
        self.executor = ScriptExecutor()
    
    def list_examples(self):
        """列出示例脚本"""
        if not self.examples_dir.exists():
            print("❌ 示例目录不存在")
            return []
        
        examples = []
        for file in self.examples_dir.glob("*.json"):
            examples.append(file.name)
        
        return examples
    
    def show_script_content(self, filename: str):
        """显示脚本内容"""
        file_path = self.examples_dir / filename
        if not file_path.exists():
            print(f"❌ 文件 {filename} 不存在")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            print(f"📋 脚本内容 ({filename}):")
            print(json.dumps(content, indent=2, ensure_ascii=False))
            return content
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            return None
    
    async def run_script_file(self, filename: str):
        """运行脚本文件"""
        file_path = self.examples_dir / filename
        if not file_path.exists():
            print(f"❌ 文件 {filename} 不存在")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                scripts = json.load(f)
            
            # 设置脚本文件的基准目录
            self.executor.set_script_base_dir(str(file_path))
            
            print(f"🚀 运行脚本: {filename}")
            results = await self.executor.execute_script(scripts)
            
            print("\n🎉 脚本运行完成!")
            print("📊 最终结果:")
            from utils.utils import Utils
            Utils.print_dict(results)
            
        except Exception as e:
            print(f"❌ 运行脚本失败: {e}")
        finally:
            self.executor.close()
    
    async def run_interactive(self):
        """交互式运行"""
        print("🎯 快速脚本运行器")
        print("=" * 40)
        
        examples = self.list_examples()
        if not examples:
            print("❌ 没有找到示例脚本")
            return
        
        print("📁 可用的示例脚本:")
        for i, example in enumerate(examples, 1):
            print(f"  {i}. {example}")
        
        print("\n🔧 操作:")
        print("  - 输入数字选择并运行脚本")
        print("  - 输入 'v数字' 查看脚本内容 (如: v1)")
        print("  - 输入 'q' 退出")
        
        while True:
            try:
                choice = input("\n请选择: ").strip()
                
                if choice.lower() == 'q':
                    print("👋 再见!")
                    break
                
                if choice.startswith('v') and len(choice) > 1:
                    # 查看脚本内容
                    try:
                        index = int(choice[1:]) - 1
                        if 0 <= index < len(examples):
                            self.show_script_content(examples[index])
                        else:
                            print("❌ 序号无效")
                    except ValueError:
                        print("❌ 输入格式错误")
                
                elif choice.isdigit():
                    # 运行脚本
                    index = int(choice) - 1
                    if 0 <= index < len(examples):
                        script_file = examples[index]
                        
                        # 显示脚本内容
                        content = self.show_script_content(script_file)
                        if content is None:
                            continue
                        
                        # 确认运行
                        if input("\n确认运行此脚本? (y/N): ").strip().lower() == 'y':
                            await self.run_script_file(script_file)
                        else:
                            print("❌ 运行已取消")
                    else:
                        print("❌ 序号无效")
                
                else:
                    print("❌ 输入无效")
                
            except KeyboardInterrupt:
                print("\n👋 程序被中断，再见!")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 命令行模式
        script_file = sys.argv[1]
        runner = QuickRunner()
        asyncio.run(runner.run_script_file(script_file))
    else:
        # 交互模式
        runner = QuickRunner()
        asyncio.run(runner.run_interactive())

if __name__ == "__main__":
    main()
