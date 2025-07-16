"""
测试命令：DefGh
"""
from typing import Dict, Any
from ..base_command import BaseCommand

class DefGhCommand(BaseCommand):
    """DefGh测试命令"""
    
    def execute(self, message: str = "Hello from DefGh!") -> Dict[str, Any]:
        """
        执行DefGh命令
        
        Args:
            message: 要显示的消息
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        print(f"🎯 DefGh命令执行: {message}")
        
        result = {
            "success": True,
            "message": message,
            "command": "abc.def_gh",
            "timestamp": self._get_timestamp()
        }
        
        return result
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class AnotherTestCommand(BaseCommand):
    """另一个测试命令"""
    
    def execute(self, value: int = 42) -> Dict[str, Any]:
        """
        执行另一个测试命令
        
        Args:
            value: 测试值
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        print(f"🔥 AnotherTest命令执行: value={value}")
        
        result = {
            "success": True,
            "value": value,
            "doubled": value * 2,
            "command": "abc.another_test"
        }
        
        return result
