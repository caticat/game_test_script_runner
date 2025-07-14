"""
网络连接相关命令
"""
from typing import Dict, Any
from .base_command import BaseCommand
from utils.tcp_client import SocketClient

class ConnectGateCommand(BaseCommand):
    """连接网关命令"""
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        连接到游戏网关
        
        Returns:
            Dict[str, Any]: 连接结果
        """
        # 优先从select_area返回值中获取网关信息
        select_area_result = self.results.get("select_area")
        if select_area_result and "GateHost" in select_area_result and "GateTcpPort" in select_area_result:
            host = select_area_result["GateHost"]
            port = select_area_result["GateTcpPort"]
        else:
            # 如果没有select_area结果，使用配置文件中的默认值
            print("⚠️  未找到select_area返回的网关信息，使用配置文件默认值")
            cfg = self.get_config()
            host = cfg["gate"]["host"]
            port = cfg["gate"]["port"]
        
        client = SocketClient(host, port)
        client.dst_gate = True
        client.connect()
        
        # 设置当前客户端
        self.current_client = client
        
        print(f"✅ 已连接到网关: {host}:{port}")
        return {"connected": True, "host": host, "port": port}

class ConnectLoginCommand(BaseCommand):
    """连接登录服命令"""
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        连接到登录服
        
        Returns:
            Dict[str, Any]: 连接结果
        """
        cfg = self.get_config()
        host = cfg["login"]["host"]
        port = cfg["login"]["port"]
        
        client = SocketClient(host, port)
        client.dst_gate = False
        client.connect()
        
        # 设置当前客户端
        self.current_client = client
        
        print(f"✅ 已连接到登录服: {host}:{port}")
        return {"connected": True, "host": host, "port": port}
