# 模拟脚本执行器

import sys
import os
import asyncio
import threading
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.utils import Utils
from commands import CommandManager

external_path = "Q:/kof/dev/proto_python"
sys.path.append(external_path)

@dataclass
class ScriptCommand:
    """脚本命令数据类"""
    cmd: str
    params: Dict[str, Any]
    timeout: int = 30  # 默认超时时间30秒

class ScriptExecutor:
    """脚本执行器"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {}  # 存储每个命令的返回结果
        self.waiting_commands: Dict[str, threading.Event] = {}  # 等待命令完成的事件
        self.current_client: Optional[Any] = None
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.script_base_dir: Optional[str] = None  # 脚本文件的基准目录
        
        # 初始化命令管理器
        self.command_manager = CommandManager(self)
    
    def _register_commands(self):
        """注册可用的命令函数"""
        # HTTP认证相关
        self.command_functions["auth"] = self._auth_command
        self.command_functions["select_area"] = self._select_area_command
        
        # TCP连接相关
        self.command_functions["connect_gate"] = self._connect_gate_command
        self.command_functions["connect_login"] = self._connect_login_command
        
        # 游戏服相关
        self.command_functions["login"] = self._login_command
        
        # 工具函数
        self.command_functions["sleep"] = self._sleep_command
        self.command_functions["print"] = self._print_command
    
    def _resolve_value(self, value: Any) -> Any:
        """解析参数值，支持从之前的返回结果中获取"""
        if isinstance(value, str) and value.startswith("ret["):
            # 格式: ret["command"]["field"]
            try:
                # 移除 ret[ 前缀和最后的 ]
                content = value[4:-1]  # 去掉 "ret[" 和 "]"
                
                # 分割路径，支持多级访问
                parts = []
                current = ""
                in_quotes = False
                quote_char = None
                
                i = 0
                while i < len(content):
                    char = content[i]
                    
                    if char in ['"', "'"] and (i == 0 or content[i-1] != '\\'):
                        if not in_quotes:
                            in_quotes = True
                            quote_char = char
                        elif char == quote_char:
                            in_quotes = False
                            quote_char = None
                    elif char == '[' and not in_quotes:
                        if current:
                            parts.append(current.strip('"\''))
                            current = ""
                    elif char == ']' and not in_quotes:
                        if current:
                            parts.append(current.strip('"\''))
                            current = ""
                    elif char != '[' and char != ']':
                        current += char
                    
                    i += 1
                
                if current:
                    parts.append(current.strip('"\''))
                
                # 获取值
                if len(parts) >= 1:
                    cmd_name = parts[0]
                    result = self.results.get(cmd_name)
                    
                    if result is None:
                        print(f"⚠️  命令 '{cmd_name}' 的结果不存在")
                        return None
                    
                    # 如果有字段名，则获取字段
                    if len(parts) >= 2:
                        field_name = parts[1]
                        if isinstance(result, dict):
                            return result.get(field_name)
                        else:
                            print(f"⚠️  命令 '{cmd_name}' 的结果不是字典类型")
                            return None
                    else:
                        return result
                        
            except Exception as e:
                print(f"⚠️  解析返回值失败: {value}, 错误: {e}")
                return value
        return value
    
    def _resolve_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """解析所有参数"""
        resolved = {}
        for key, value in params.items():
            resolved[key] = self._resolve_value(value)
        return resolved
    
    async def execute_script(self, scripts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """执行脚本"""
        print("🚀 开始执行脚本...")
        
        # 处理include指令，展开包含的文件
        expanded_scripts = self._process_includes(scripts, self.script_base_dir)
        
        print(f"📋 共有 {len(expanded_scripts)} 个命令（包含文件展开后）")
        print("=" * 50)
        
        for i, script_dict in enumerate(expanded_scripts, 1):
            try:
                # 跳过include指令（已经在_process_includes中处理）
                if "include" in script_dict:
                    continue
                
                # 解析命令
                cmd = script_dict["cmd"]
                params = script_dict.copy()
                del params["cmd"]
                timeout = params.pop("timeout", 30)
                comment = params.pop("comment", None)  # 提取注释字段，不传递给命令
                
                command = ScriptCommand(cmd=cmd, params=params, timeout=timeout)
                
                # 显示注释（如果有）
                if comment:
                    print(f"💬 {comment}")
                
                print(f"🔄 [{i}/{len(expanded_scripts)}] 执行命令: {cmd}")
                
                # 解析参数
                resolved_params = self._resolve_params(command.params)
                print(f"📝 参数: {resolved_params}")
                
                # 执行命令
                result = await self._execute_command(command, resolved_params)
                
                # 对于需要等待应答的命令，使用应答处理器设置的结果
                if command.cmd in ["auth", "select_area", "login"]:
                    final_result = self.results.get(command.cmd)
                    if final_result is not None:
                        result = final_result
                
                # 保存结果
                self.results[cmd] = result
                print(f"✅ 命令 {cmd} 执行完成")
                
                if result:
                    print(f"📤 返回结果: {result}")
                
                print("-" * 30)
                
            except Exception as e:
                print(f"❌ 命令 {cmd} 执行失败: {e}")
                print("-" * 30)
                # 根据需要决定是否继续执行
                # break  # 如果需要在出错时停止，取消注释这行
        
        print("🎉 脚本执行完成!")
        return self.results
    
    async def _execute_command(self, command: ScriptCommand, params: Dict[str, Any]) -> Any:
        """执行单个命令"""
        # 创建等待事件
        event = threading.Event()
        self.waiting_commands[command.cmd] = event
        
        try:
            # 在线程池中执行命令
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, 
                self._execute_command_sync, 
                command.cmd,
                params
            )
            
            # 等待命令完成（如果需要）
            if command.cmd in ["auth", "select_area", "login"]:
                await asyncio.wait_for(
                    asyncio.to_thread(event.wait),
                    timeout=command.timeout
                )
            
            return result
            
        finally:
            # 清理等待事件
            if command.cmd in self.waiting_commands:
                del self.waiting_commands[command.cmd]
    
    def _execute_command_sync(self, cmd: str, params: Dict[str, Any]) -> Any:
        """同步执行命令"""
        return self.command_manager.execute_command(cmd, **params)
    
    def _complete_command(self, cmd: str, result: Any = None):
        """标记命令完成"""
        if result is not None:
            self.results[cmd] = result
        
        if cmd in self.waiting_commands:
            self.waiting_commands[cmd].set()
    
    def get_available_commands(self) -> Dict[str, str]:
        """获取所有可用命令的列表"""
        return self.command_manager.get_available_commands()

    def close(self):
        """关闭连接"""
        if self.current_client:
            self.current_client.stop()
            self.current_client = None
        
        self.executor.shutdown(wait=True)
    
    def _load_script_file(self, file_path: str, base_dir: str = None) -> List[Dict[str, Any]]:
        """加载脚本文件"""
        import json
        import os
        
        # 如果是相对路径，则相对于base_dir或当前脚本文件目录
        if not os.path.isabs(file_path):
            if base_dir:
                file_path = os.path.join(base_dir, file_path)
            else:
                # 获取当前脚本文件的目录
                current_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(current_dir, file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ 脚本文件未找到: {file_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ 脚本文件格式错误: {file_path}, 错误: {e}")
            return []
        except Exception as e:
            print(f"❌ 加载脚本文件失败: {file_path}, 错误: {e}")
            return []

    def _process_includes(self, scripts: List[Dict[str, Any]], base_dir: str = None) -> List[Dict[str, Any]]:
        """处理include指令，展开包含的文件"""
        expanded_scripts = []
        
        for script_dict in scripts:
            # 检查是否有include字段
            if "include" in script_dict:
                include_files = script_dict["include"]
                if isinstance(include_files, str):
                    include_files = [include_files]
                
                # 显示include信息
                comment = script_dict.get("comment", "")
                if comment:
                    print(f"💬 {comment}")
                
                print(f"📂 包含文件: {', '.join(include_files)}")
                
                # 递归加载并处理每个包含的文件
                for include_file in include_files:
                    print(f"🔄 正在加载: {include_file}")
                    included_scripts = self._load_script_file(include_file, base_dir)
                    if included_scripts:
                        # 递归处理包含文件中的include，使用相同的base_dir
                        processed_scripts = self._process_includes(included_scripts, base_dir)
                        expanded_scripts.extend(processed_scripts)
                        print(f"✅ 已包含 {len(processed_scripts)} 个命令从 {include_file}")
                    else:
                        print(f"⚠️  文件 {include_file} 为空或加载失败")
                
                print("-" * 30)
            else:
                # 普通命令，直接添加
                expanded_scripts.append(script_dict)
        
        return expanded_scripts

    def set_script_base_dir(self, script_file_path: str = None):
        """设置脚本文件的基准目录"""
        import os
        if script_file_path:
            self.script_base_dir = os.path.dirname(os.path.abspath(script_file_path))
        else:
            self.script_base_dir = None

# 使用示例
async def main():
    """主函数示例"""
    executor = ScriptExecutor()
    
    # 示例脚本
    scripts = [
        {"cmd": "auth", "user_name": "q1", "channel": "dev"},
        {"cmd": "select_area", "open_id": "ret[\"auth\"][\"OpenId\"]", "area_id": 1, "login_token": "ret[\"auth\"][\"LoginToken\"]"},
        {"cmd": "connect_gate"},
        {"cmd": "login", "signature": "ret[\"select_area\"][\"Signature\"]", "role_id": 903, "user_name": "q1"},
        {"cmd": "sleep", "seconds": 2.0},
        {"cmd": "print", "message": "脚本执行完成!"}
    ]
    
    try:
        results = await executor.execute_script(scripts)
        print("\n🎯 最终结果:")
        Utils.print_dict(results)
    finally:
        executor.close()

if __name__ == "__main__":
    asyncio.run(main())
