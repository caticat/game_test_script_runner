"""
原始版本HTTP认证相关命令
"""
from typing import Dict, Any
from ..base_command import BaseCommand
from utils.utils import Utils

class AuthCommand(BaseCommand):
    """原始版本HTTP认证命令"""
    
    def execute(self, user_name: str = "q1", channel: str = "dev", area_id: int = 1) -> Dict[str, Any]:
        """
        执行HTTP认证
        
        Args:
            user_name: 用户名
            channel: 渠道
            area_id: 区域ID
            
        Returns:
            Dict[str, Any]: 认证结果
        """
        payload = {
            "Channel": channel,
            "Code": user_name,
            "AreaId": area_id,
        }
        result = Utils.send_to_login("auth", payload)
        self.complete_command("select_area", result)
        return result