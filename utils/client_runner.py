"""
客户端运行器 - 统一封装连接、命令处理和输入循环
"""
import asyncio
import sys
import inspect
from typing import Dict, Callable, Any, Optional, List
from network.clients.tcp_client import SocketClient
from network.protocol.registry import auto_register_handlers
from utils.config_manager import config_manager


class ClientRunner:
    """统一的客户端运行器"""
    
    def __init__(self, module_name: str, client_type: str = "login"):
        """
        初始化客户端运行器
        
        Args:
            module_name: 模块名称，用于显示
            client_type: 客户端类型，"login" 或 "gate"
        """
        self.module_name = module_name
        self.client_type = client_type
        self.client = None
        self.commands = {}
        self.command_descriptions = {}
        
    def _extract_commands_from_module(self, module: Any) -> Dict[str, Callable]:
        """从模块中提取命令函数"""
        commands = {}
        descriptions = {}
        
        # 获取模块的所有属性
        all_attrs = []
        if hasattr(module, '_globals'):
            # 使用内部的globals字典
            all_attrs = list(module._globals.keys())
        elif hasattr(module, '__dict__'):
            all_attrs = list(module.__dict__.keys())
        else:
            all_attrs = [name for name in dir(module) if not name.startswith('_')]
        
        # 查找所有以 _req 结尾的属性
        req_attrs = [name for name in all_attrs if name.endswith('_req')]
        
        # 获取所有以 _req 结尾的函数
        for name in req_attrs:
            try:
                if hasattr(module, '_globals'):
                    func = module._globals.get(name)
                else:
                    func = getattr(module, name)
                
                if callable(func):
                    # 提取命令名称（去掉 _req 后缀）
                    cmd_name = name[:-4]
                    commands[cmd_name] = func
                    
                    # 从函数文档字符串中提取描述
                    doc = func.__doc__
                    if doc:
                        descriptions[cmd_name] = doc.strip().split('\n')[0]
                    else:
                        descriptions[cmd_name] = f"执行 {cmd_name} 操作"
            except Exception as e:
                # 静默忽略错误
                pass
        
        return commands, descriptions
    
    def _get_emoji_for_command(self, cmd_name: str) -> str:
        """根据命令名称获取合适的emoji"""
        emoji_map = {
            'login': '🔐',
            'ban': '🚫',
            'unban': '✅',
            'get': '📋',
            'status': '📊',
            'test': '🧪',
            'send': '📤',
            'receive': '📥',
            'connect': '🔗',
            'disconnect': '🔌',
            'start': '▶️',
            'stop': '⏹️',
            'reset': '🔄',
            'check': '🔍',
            'query': '❓',
            'update': '🔄',
            'delete': '🗑️',
            'create': '➕',
            'modify': '✏️',
            'export': '📤',
            'import': '📥',
        }
        
        for key, emoji in emoji_map.items():
            if key in cmd_name.lower():
                return emoji
        
        return '🔧'  # 默认emoji
    
    def _show_help(self, commands: Dict[str, Callable], descriptions: Dict[str, str]):
        """显示帮助信息"""
        print(f"\n📝 {self.module_name} 可用命令:")
        
        # 按命令名称排序
        sorted_commands = sorted(commands.keys())
        
        for cmd_name in sorted_commands:
            emoji = self._get_emoji_for_command(cmd_name)
            description = descriptions.get(cmd_name, f"执行 {cmd_name} 操作")
            print(f"  {cmd_name:<10} - {emoji} {description}")
        
        print(f"  {'help':<10} - 📚 显示此帮助信息")
        print(f"  {'quit':<10} - 🚪 退出程序 (可输入 quit/q/0)")
        print()
    
    async def _handle_input(self, commands: Dict[str, Callable], descriptions: Dict[str, str]):
        """处理用户输入"""
        import aioconsole
        
        client_name = "login" if self.client_type == "login" else "gate"
        
        while True:
            try:
                command = await aioconsole.ainput(f"[{client_name}] 请输入命令 (输入 help 查看帮助): ")
                command = command.strip()
                
                if command.lower() in ['quit', 'q', '0']:
                    print("👋 退出程序...")
                    break
                elif command.lower() == 'help':
                    self._show_help(commands, descriptions)
                elif command in commands:
                    # 执行命令
                    try:
                        commands[command](self.client)
                        print("⏳ 请求已发送，等待服务器响应...")
                    except Exception as e:
                        print(f"❌ 命令执行失败: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"❌ 未知命令: {command}，输入 help 查看可用命令")
                    
            except KeyboardInterrupt:
                print("\n👋 收到中断信号，退出程序...")
                break
            except EOFError:
                print("\n👋 输入结束，退出程序...")
                break
    
    async def run(self, module: Any, title: Optional[str] = None):
        """
        运行客户端
        
        Args:
            module: 包含命令函数的模块
            title: 可选的标题，默认使用模块名称
        """
        if title is None:
            title = f"{self.module_name}测试工具"
        
        print(f"=== {title} ===")
        
        # 从模块中提取命令
        commands, descriptions = self._extract_commands_from_module(module)
        
        if not commands:
            print("⚠️ 未找到任何可用命令（_req 函数）")
            return
        
        # 显示初始帮助
        self._show_help(commands, descriptions)
        
        # 获取配置
        cfg = config_manager.get_config()
        if self.client_type == "login":
            host = cfg["login"]["host"]
            port = cfg["login"]["port"]
        else:
            host = cfg["gate"]["host"]
            port = cfg["gate"]["port"]
        
        # 创建客户端
        self.client = SocketClient(host, port)
        self.client.dst_gate = (self.client_type == "gate")
        
        # 连接
        connected = await self.client.connect()
        if not connected:
            print(f"❌ 连接失败: {host}:{port}")
            print("💡 请确保服务器正在运行")
            print("💡 可以检查配置文件中的服务器地址和端口")
            return
        
        print(f"✅ 已连接到{'网关' if self.client_type == 'gate' else '登录服'}: {host}:{port}")
        
        # 自动注册协议处理函数
        auto_register_handlers(self.client, module)
        
        # 创建输入处理任务
        input_task = asyncio.create_task(self._handle_input(commands, descriptions))
        
        # 等待输入任务完成
        await input_task
        
        # 停止客户端
        await self.client.stop()


def run_client(module_name: str, client_type: str = "login", title: Optional[str] = None):
    """
    便捷函数：运行客户端
    
    Args:
        module_name: 模块名称
        client_type: 客户端类型，"login" 或 "gate"
        title: 可选的标题
    """
    # 直接在这里获取调用模块的globals
    frame = inspect.currentframe()
    try:
        caller_frame = frame.f_back  # 这是调用 run_client 的帧
        caller_globals = caller_frame.f_globals
    finally:
        del frame
    
    async def async_main():
        runner = ClientRunner(module_name, client_type)
        
        # 创建模块对象，直接使用调用者的globals
        class ModuleWrapper:
            def __init__(self, globals_dict):
                self._globals = globals_dict
                
            def __getattr__(self, name):
                if name in self._globals:
                    return self._globals[name]
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
            
            def __dir__(self):
                return list(self._globals.keys())
        
        module_obj = ModuleWrapper(caller_globals)
        
        await runner.run(module_obj, title)
    
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\n👋 程序被中断")
    except Exception as e:
        print(f"❌ 程序运行错误: {e}")
        import traceback
        traceback.print_exc()
