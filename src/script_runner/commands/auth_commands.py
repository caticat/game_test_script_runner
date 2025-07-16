"""
HTTP认证相关命令
"""
from typing import Dict, Any
from .base_command import BaseCommand
from utils.utils import Utils

class AuthCommand(BaseCommand):
    """HTTP认证命令"""
    
    def execute(self, user_name: str = "q1", channel: str = "dev") -> Dict[str, Any]:
        """
        执行HTTP认证
        
        Args:
            user_name: 用户名
            channel: 渠道
            
        Returns:
            Dict[str, Any]: 认证结果
        """
        payload = {
            "Channel": channel,
            "Code": user_name,
        }
        result = Utils.send_to_login("auth_step", payload)
        self.complete_command("auth", result)
        return result

class SelectAreaCommand(BaseCommand):
    """选择区服命令"""
    
    def execute(self, open_id: str, area_id: int = 1, login_token: str = "") -> Dict[str, Any]:
        """
        执行选择区服
        
        Args:
            open_id: 开放ID
            area_id: 区域ID
            login_token: 登录令牌
            
        Returns:
            Dict[str, Any]: 选服结果
        """
        payload = {
            "OpenId": open_id,
            "AreaId": area_id,
            "LoginToken": login_token,
        }
        result = Utils.send_to_login("select_area", payload)
        self.complete_command("select_area", result)
        return result
