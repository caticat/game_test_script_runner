"""
命令基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import sys
import os

# 添加上级目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class BaseCommand(ABC):
    """命令基类"""
    
    def __init__(self, executor_ref):
        """
        初始化命令
        
        Args:
            executor_ref: ScriptExecutor实例的引用
        """
        self.executor = executor_ref
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行命令
        
        Args:
            **kwargs: 命令参数
            
        Returns:
            Dict[str, Any]: 命令执行结果
        """
        pass
    
    async def execute_async(self, **kwargs) -> Dict[str, Any]:
        """
        异步执行命令 - 默认实现调用同步方法
        
        Args:
            **kwargs: 命令参数
            
        Returns:
            Dict[str, Any]: 命令执行结果
        """
        return self.execute(**kwargs)
    
    @property
    def results(self) -> Dict[str, Any]:
        """获取所有命令的执行结果"""
        return self.executor.results
    
    @property
    def current_client(self):
        """获取当前客户端连接"""
        return self.executor.current_client
    
    @current_client.setter
    def current_client(self, client):
        """设置当前客户端连接"""
        self.executor.current_client = client
    
    def complete_command(self, cmd: str, result: Any = None):
        """标记命令完成"""
        self.executor._complete_command(cmd, result)
    
    def get_config(self):
        """获取配置"""
        from utils.config_manager import config_manager
        return config_manager.get_config()
