"""
命令管理器
"""
from typing import Dict, Callable
from .auth_commands import AuthCommand, SelectAreaCommand
from .network_commands import ConnectGateCommand, ConnectLoginCommand
from .game_commands import LoginCommand
from .utility_commands import SleepCommand, PrintCommand

class CommandManager:
    """命令管理器"""
    
    def __init__(self, executor_ref):
        """
        初始化命令管理器
        
        Args:
            executor_ref: ScriptExecutor实例的引用
        """
        self.executor = executor_ref
        self.commands = {}
        self._register_commands()
    
    def _register_commands(self):
        """注册所有可用的命令"""
        # HTTP认证相关
        self.commands["auth"] = AuthCommand(self.executor)
        self.commands["select_area"] = SelectAreaCommand(self.executor)
        
        # TCP连接相关
        self.commands["connect_gate"] = ConnectGateCommand(self.executor)
        self.commands["connect_login"] = ConnectLoginCommand(self.executor)
        
        # 游戏服相关
        self.commands["login"] = LoginCommand(self.executor)
        
        # 工具函数
        self.commands["sleep"] = SleepCommand(self.executor)
        self.commands["print"] = PrintCommand(self.executor)
    
    def get_command(self, cmd_name: str):
        """
        获取命令实例
        
        Args:
            cmd_name: 命令名称
            
        Returns:
            BaseCommand: 命令实例
            
        Raises:
            ValueError: 如果命令不存在
        """
        if cmd_name not in self.commands:
            raise ValueError(f"未知命令: {cmd_name}")
        return self.commands[cmd_name]
    
    def execute_command(self, cmd_name: str, **kwargs):
        """
        执行命令
        
        Args:
            cmd_name: 命令名称
            **kwargs: 命令参数
            
        Returns:
            Any: 命令执行结果
        """
        command = self.get_command(cmd_name)
        return command.execute(**kwargs)
    
    def get_available_commands(self) -> Dict[str, str]:
        """
        获取所有可用命令的列表
        
        Returns:
            Dict[str, str]: 命令名称和描述的映射
        """
        return {
            # HTTP认证相关
            "auth": "HTTP认证获取OpenId和LoginToken",
            "select_area": "选择游戏区服，获取网关信息和签名",
            
            # TCP连接相关
            "connect_gate": "连接到游戏网关",
            "connect_login": "连接到登录服",
            
            # 游戏服相关
            "login": "游戏服登录",
            
            # 工具函数
            "sleep": "睡眠指定时间",
            "print": "打印消息（支持返回值引用）"
        }
