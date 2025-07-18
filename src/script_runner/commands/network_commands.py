"""
网络连接相关命令
"""
import asyncio
from typing import Dict, Any
from .base_command import BaseCommand
from network.clients.tcp_client import SocketClient
from network.clients.websocket_client import WebSocketClient

class ConnectGateCommand(BaseCommand):
    """连接网关命令"""
    
    def execute(self, host: str = "", port: int = 0) -> Dict[str, Any]:
        """
        连接到游戏网关
        
        Args:
            host: 服务器地址（支持 TCP 地址或 WebSocket URL）
            port: 端口号（WebSocket 时忽略）
        
        Returns:
            Dict[str, Any]: 连接结果
        """
        if host == "":
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
        
        # 判断是否为 WebSocket URL
        if host.startswith(('ws://', 'wss://')):
            return self._connect_websocket(host)
        else:
            return self._connect_tcp(host, port)
    
    async def execute_async(self, host: str = "", port: int = 0) -> Dict[str, Any]:
        """
        异步连接到游戏网关
        
        Args:
            host: 服务器地址（支持 TCP 地址或 WebSocket URL）
            port: 端口号（WebSocket 时忽略）
        
        Returns:
            Dict[str, Any]: 连接结果
        """
        if host == "":
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
        
        # 判断是否为 WebSocket URL
        if host.startswith(('ws://', 'wss://')):
            return await self._connect_websocket_async(host)
        else:
            return await self._connect_tcp_async(host, port)
    
    async def _connect_tcp_async(self, host: str, port: int) -> Dict[str, Any]:
        """异步连接 TCP 服务器"""
        try:
            # 创建异步TCP客户端
            client = SocketClient(host, port)
            client.dst_gate = True
            
            # 异步连接
            connected = await client.connect()
            
            if connected:
                # 设置当前客户端
                self.current_client = client
                print(f"✅ 已连接到网关(TCP): {host}:{port}")
                return {"connected": True, "host": host, "port": port, "type": "tcp"}
            else:
                return {"connected": False, "host": host, "port": port, "type": "tcp", "error": "连接失败"}
                
        except Exception as e:
            print(f"❌ TCP 连接失败: {e}")
            return {"connected": False, "host": host, "port": port, "type": "tcp", "error": str(e)}
    
    def _connect_tcp(self, host: str, port: int) -> Dict[str, Any]:
        """连接 TCP 服务器"""
        try:
            # 创建异步TCP客户端
            client = SocketClient(host, port)
            client.dst_gate = True
            
            # 在当前事件循环中连接
            loop = asyncio.get_event_loop()
            connected = loop.run_until_complete(client.connect())
            
            if connected:
                # 设置当前客户端
                self.current_client = client
                print(f"✅ 已连接到网关(TCP): {host}:{port}")
                return {"connected": True, "host": host, "port": port, "type": "tcp"}
            else:
                return {"connected": False, "host": host, "port": port, "type": "tcp", "error": "连接失败"}
                
        except Exception as e:
            print(f"❌ TCP 连接失败: {e}")
            return {"connected": False, "host": host, "port": port, "type": "tcp", "error": str(e)}
    
    async def _connect_tcp_async(self, host: str, port: int) -> Dict[str, Any]:
        """异步连接 TCP 服务器"""
        try:
            # 创建异步TCP客户端
            client = SocketClient(host, port)
            client.dst_gate = True
            
            # 连接
            connected = await client.connect()
            
            if connected:
                # 设置当前客户端
                self.current_client = client
                print(f"✅ 已连接到网关(TCP): {host}:{port}")
                return {"connected": True, "host": host, "port": port, "type": "tcp"}
            else:
                return {"connected": False, "host": host, "port": port, "type": "tcp", "error": "连接失败"}
                
        except Exception as e:
            print(f"❌ TCP 异步连接失败: {e}")
            return {"connected": False, "host": host, "port": port, "type": "tcp", "error": str(e)}
    
    async def _connect_websocket_async(self, url: str) -> Dict[str, Any]:
        """异步连接 WebSocket 服务器"""
        try:
            # 创建 WebSocket 客户端
            ws_client = WebSocketClient(url)
            
            # 设置为网关连接
            ws_client.dst_gate = True
            
            # 异步连接
            connected = await ws_client.connect()
            
            if connected:
                # 直接使用WebSocket客户端
                self.current_client = ws_client
                
                print(f"✅ 已连接到网关(WebSocket): {url}")
                return {"connected": True, "url": url, "type": "websocket"}
            else:
                return {"connected": False, "url": url, "type": "websocket", "error": "连接失败"}
                
        except Exception as e:
            error_msg = str(e)
            
            # 提供更友好的错误信息
            if "SSL: WRONG_VERSION_NUMBER" in error_msg:
                error_msg = "SSL版本错误 - 请检查是否应使用 ws:// 而非 wss://"
            elif "SSL:" in error_msg:
                error_msg = f"SSL连接错误: {error_msg}"
            elif "Connection refused" in error_msg:
                error_msg = "连接被拒绝 - 请检查服务器是否正在运行"
            elif "Name or service not known" in error_msg:
                error_msg = "无法解析主机名 - 请检查URL是否正确"
            
            print(f"❌ WebSocket 连接失败: {error_msg}")
            return {"connected": False, "url": url, "type": "websocket", "error": error_msg}
    
    def _connect_websocket(self, url: str) -> Dict[str, Any]:
        """连接 WebSocket 服务器"""
        try:
            # 创建 WebSocket 客户端
            ws_client = WebSocketClient(url)
            
            # 设置为网关连接
            ws_client.dst_gate = True
            
            # 在当前事件循环中连接
            loop = asyncio.get_event_loop()
            connected = loop.run_until_complete(ws_client.connect())
            
            if connected:
                # 直接使用WebSocket客户端
                self.current_client = ws_client
                
                print(f"✅ 已连接到网关(WebSocket): {url}")
                return {"connected": True, "url": url, "type": "websocket"}
            else:
                return {"connected": False, "url": url, "type": "websocket", "error": "连接失败"}
                
        except Exception as e:
            error_msg = str(e)
            
            # 提供更友好的错误信息
            if "SSL: WRONG_VERSION_NUMBER" in error_msg:
                error_msg = "SSL版本错误 - 请检查是否应使用 ws:// 而非 wss://"
            elif "SSL:" in error_msg:
                error_msg = f"SSL连接错误: {error_msg}"
            elif "Connection refused" in error_msg:
                error_msg = "连接被拒绝 - 请检查服务器是否正在运行"
            elif "Name or service not known" in error_msg:
                error_msg = "无法解析主机名 - 请检查URL是否正确"
            
            print(f"❌ WebSocket 连接失败: {error_msg}")
            return {"connected": False, "url": url, "type": "websocket", "error": error_msg}
    
    async def _connect_websocket_async(self, url: str) -> Dict[str, Any]:
        """异步连接 WebSocket 服务器"""
        try:
            # 创建 WebSocket 客户端
            ws_client = WebSocketClient(url)
            
            # 设置为网关连接
            ws_client.dst_gate = True
            
            # 连接
            connected = await ws_client.connect()
            
            if connected:
                # 直接使用WebSocket客户端
                self.current_client = ws_client
                
                print(f"✅ 已连接到网关(WebSocket): {url}")
                return {"connected": True, "url": url, "type": "websocket"}
            else:
                return {"connected": False, "url": url, "type": "websocket", "error": "连接失败"}
                
        except Exception as e:
            error_msg = str(e)
            
            # 提供更友好的错误信息
            if "SSL: WRONG_VERSION_NUMBER" in error_msg:
                error_msg = "SSL版本错误 - 请检查是否应使用 ws:// 而非 wss://"
            elif "SSL:" in error_msg:
                error_msg = f"SSL连接错误: {error_msg}"
            elif "Connection refused" in error_msg:
                error_msg = "连接被拒绝 - 请检查服务器是否正在运行"
            elif "Name or service not known" in error_msg:
                error_msg = "无法解析主机名 - 请检查URL是否正确"
            
            print(f"❌ WebSocket 异步连接失败: {error_msg}")
            return {"connected": False, "url": url, "type": "websocket", "error": error_msg}


class ConnectLoginCommand(BaseCommand):
    """连接登录服命令"""
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        连接到登录服
        
        Returns:
            Dict[str, Any]: 连接结果
        """
        try:
            cfg = self.get_config()
            host = cfg["login"]["host"]
            port = cfg["login"]["port"]
            
            client = SocketClient(host, port)
            client.dst_gate = False
            
            # 在当前事件循环中连接
            loop = asyncio.get_event_loop()
            connected = loop.run_until_complete(client.connect())
            
            if connected:
                # 设置当前客户端
                self.current_client = client
                
                print(f"✅ 已连接到登录服: {host}:{port}")
                return {"connected": True, "host": host, "port": port, "type": "tcp"}
            else:
                return {"connected": False, "host": host, "port": port, "type": "tcp", "error": "连接失败"}
                
        except Exception as e:
            print(f"❌ 登录服连接失败: {e}")
            return {"connected": False, "error": str(e), "type": "tcp"}
    
    async def execute_async(self, **kwargs) -> Dict[str, Any]:
        """
        异步连接到登录服
        
        Returns:
            Dict[str, Any]: 连接结果
        """
        try:
            cfg = self.get_config()
            host = cfg["login"]["host"]
            port = cfg["login"]["port"]
            
            client = SocketClient(host, port)
            client.dst_gate = False
            
            # 异步连接
            connected = await client.connect()
            
            if connected:
                # 设置当前客户端
                self.current_client = client
                
                print(f"✅ 已连接到登录服: {host}:{port}")
                return {"connected": True, "host": host, "port": port, "type": "tcp"}
            else:
                return {"connected": False, "host": host, "port": port, "type": "tcp", "error": "连接失败"}
                
        except Exception as e:
            print(f"❌ 登录服连接失败: {e}")
            return {"connected": False, "error": str(e), "type": "tcp"}
