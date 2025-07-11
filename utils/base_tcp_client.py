# TCP客户端基础类 - 消除重复代码

import sys
import inspect
import os
from typing import Dict, Callable, Tuple, Optional
from utils.tcp_client import SocketClient
from utils.config_manager import config_manager

class BaseTCPClient:
    """TCP客户端基础类，提供通用的命令处理和自动注册功能"""
    
    def __init__(self, server_type: str = "login", caller_module=None):
        """
        初始化TCP客户端
        
        Args:
            server_type: 服务器类型 ("login" 或 "gate")
            caller_module: 调用者模块，用于自动注册函数
        """
        self.server_type = server_type
        self.client: Optional[SocketClient] = None
        self.command_handlers: Dict[str, Callable] = {}
        self.ack_handlers: Dict[str, Tuple[int, Callable]] = {}
        self.caller_module = caller_module
        
        # 添加默认命令
        self.command_handlers["quit"] = self._quit_command
        
        # 设置Proto路径
        self._setup_proto_path()
        
        # 自动注册命令和处理器
        self._auto_register_commands_and_handlers()
    
    def _setup_proto_path(self):
        """设置Proto文件路径"""
        # 从配置文件或环境变量读取，避免硬编码
        proto_path = config_manager.get_proto_path()
        if proto_path not in sys.path:
            sys.path.append(proto_path)
    
    def _auto_register_commands_and_handlers(self):
        """自动注册命令和应答处理器"""
        # 确定要扫描的模块
        if self.caller_module:
            current_module = self.caller_module
        else:
            # 通过调用栈找到实际定义命令函数的模块
            frame = inspect.currentframe()
            try:
                # 向上查找调用栈，找到非base_tcp_client模块的帧
                caller_frame = frame.f_back.f_back  # 跳过__init__调用
                while caller_frame:
                    caller_module_name = caller_frame.f_globals.get('__name__')
                    if caller_module_name and not caller_module_name.endswith('base_tcp_client'):
                        # 找到了调用模块
                        current_module = sys.modules[caller_module_name]
                        break
                    caller_frame = caller_frame.f_back
                else:
                    # 如果没找到，使用当前模块
                    current_module = sys.modules[self.__class__.__module__]
            finally:
                del frame
        
        # 注册函数
        for name, obj in inspect.getmembers(current_module, inspect.isfunction):
            if name.endswith('_req'):
                # 注册请求命令
                key = name[:-4]
                self.command_handlers[key] = obj
            elif name.endswith('_ack'):
                # 注册应答处理器
                key = name[:-4]
                id_var_name = f'{key}_id'
                proto_id = getattr(current_module, id_var_name, None)
                if proto_id is not None:
                    self.ack_handlers[key] = (proto_id, obj)
                else:
                    print(f"[警告] 未找到变量 {id_var_name}，无法注册 {name}")
        
        print(f"[信息] 已注册 {len(self.command_handlers)-1} 个命令和 {len(self.ack_handlers)} 个处理器")
    
    def _quit_command(self, client: SocketClient) -> None:
        """退出命令"""
        print("退出程序...")
        exit(0)
    
    def _register_ack_handlers(self):
        """注册应答处理器到客户端"""
        for name, (proto_id, handler_fn) in self.ack_handlers.items():
            self.client.regist_handler(proto_id, handler_fn)
    
    def connect_and_run(self) -> None:
        """连接服务器并运行主循环"""
        cfg = config_manager.get_config()
        
        # 根据服务器类型选择配置
        if self.server_type == "login":
            host = cfg["login"]["host"]
            port = cfg["login"]["port"]
            dst_gate = False
        else:  # gate
            host = cfg["gate"]["host"]
            port = cfg["gate"]["port"]
            dst_gate = True
        
        self.client = SocketClient(host, port)
        self.client.dst_gate = dst_gate
        
        try:
            print(f"连接到 {self.server_type} 服务器: {host}:{port}")
            self.client.connect()
            self._register_ack_handlers()
            
            # 主命令循环
            while self.client.running.is_set():
                try:
                    msg = input("请输入命令: ").strip().lower()
                    if not msg:
                        continue
                        
                    cmd_fn = self.command_handlers.get(msg)
                    if not cmd_fn:
                        print(f"未知命令: {msg}")
                        self._print_available_commands()
                        continue
                        
                    cmd_fn(self.client)
                except KeyboardInterrupt:
                    print("\n程序被中断")
                    break
                except Exception as e:
                    print(f"执行命令时出错: {e}")
                    
        finally:
            if self.client:
                self.client.stop()
    
    def _print_available_commands(self):
        """打印可用命令"""
        print("可用命令:")
        for cmd in sorted(self.command_handlers.keys()):
            print(f"  - {cmd}")
    
    def add_command(self, command: str, handler: Callable):
        """手动添加命令处理器"""
        self.command_handlers[command] = handler
    
    def add_ack_handler(self, proto_id: int, handler: Callable):
        """手动添加应答处理器"""
        self.ack_handlers[f"custom_{proto_id}"] = (proto_id, handler)
