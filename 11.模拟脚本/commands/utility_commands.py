"""
工具类命令
"""
from typing import Dict, Any
import time
import re
from .base_command import BaseCommand

class SleepCommand(BaseCommand):
    """睡眠命令"""
    
    def execute(self, seconds: float = 1.0) -> Dict[str, Any]:
        """
        执行睡眠
        
        Args:
            seconds: 睡眠时间（秒）
            
        Returns:
            Dict[str, Any]: 睡眠结果
        """
        print(f"😴 睡眠 {seconds} 秒...")
        time.sleep(seconds)
        return {"slept": seconds}

class PrintCommand(BaseCommand):
    """打印命令"""
    
    def execute(self, message: str = "", **kwargs) -> Dict[str, Any]:
        """
        执行打印
        
        Args:
            message: 要打印的消息
            **kwargs: 其他参数（忽略）
            
        Returns:
            Dict[str, Any]: 打印结果
        """
        # 解析message中的返回值引用
        resolved_message = self._resolve_message_content(message)
        print(f"📢 {resolved_message}")
        return {"printed": resolved_message}
    
    def _resolve_message_content(self, message: str) -> str:
        """解析字符串中的返回值引用"""
        # 使用正则表达式找到所有的 ret["xxx"]["yyy"] 模式
        pattern = r'ret\["([^"]+)"\]\["([^"]+)"\]'
        
        def replace_func(match):
            cmd_name = match.group(1)
            field_name = match.group(2)
            
            result = self.results.get(cmd_name)
            if result is None:
                return f"[命令'{cmd_name}'结果不存在]"
            
            if isinstance(result, dict):
                value = result.get(field_name)
                if value is None:
                    return f"[字段'{field_name}'不存在]"
                return str(value)
            else:
                return f"[命令'{cmd_name}'结果不是字典]"
        
        # 替换所有匹配的部分
        resolved = re.sub(pattern, replace_func, message)
        
        # 也处理简单的 ret["xxx"] 模式（只有命令名，没有字段）
        simple_pattern = r'ret\["([^"]+)"\](?!\[)'
        
        def simple_replace_func(match):
            cmd_name = match.group(1)
            result = self.results.get(cmd_name)
            if result is None:
                return f"[命令'{cmd_name}'结果不存在]"
            return str(result)
        
        resolved = re.sub(simple_pattern, simple_replace_func, resolved)
        
        return resolved
