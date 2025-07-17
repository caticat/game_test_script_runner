"""
网络连接相关命令
"""
import asyncio
from typing import Dict, Any
from .base_command import BaseCommand
from utils.tcp_client import SocketClient
from utils.websocket_client import WebSocketClient

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
    
    def _connect_tcp(self, host: str, port: int) -> Dict[str, Any]:
        """连接 TCP 服务器"""
        client = SocketClient(host, port)
        client.dst_gate = True
        client.connect()
        
        # 设置当前客户端
        self.current_client = client
        
        print(f"✅ 已连接到网关(TCP): {host}:{port}")
        return {"connected": True, "host": host, "port": port, "type": "tcp"}
    
    def _connect_websocket(self, url: str) -> Dict[str, Any]:
        """连接 WebSocket 服务器"""
        try:
            # 创建 WebSocket 客户端
            ws_client = WebSocketClient(url)
            
            # 设置为网关连接
            ws_client.dst_gate = True
            
            # 使用异步方式连接
            import threading
            import time
            
            def connect_in_thread():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                ws_client.loop = loop  # 保存循环引用
                
                try:
                    connected = loop.run_until_complete(ws_client.connect())
                    
                    # 保持事件循环运行，直到被显式停止
                    if connected:
                        # 在后台运行事件循环
                        def run_forever():
                            try:
                                loop.run_forever()
                            except:
                                pass
                        
                        import threading
                        loop_thread = threading.Thread(target=run_forever, daemon=True)
                        loop_thread.start()
                        ws_client.loop_thread = loop_thread
                    
                    return connected
                except Exception as e:
                    try:
                        loop.close()
                    except:
                        pass
                    raise e
            
            # 在新线程中连接
            connected_future = [None]
            
            def thread_func():
                connected_future[0] = connect_in_thread()
            
            thread = threading.Thread(target=thread_func, daemon=True)
            thread.start()
            thread.join(timeout=10)  # 等待连接完成
            
            connected = connected_future[0]
            
            if connected:
                # 包装客户端以提供兼容接口
                wrapped_client = WebSocketClientWrapper(ws_client)
                self.current_client = wrapped_client
                
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


class WebSocketClientWrapper:
    """WebSocket 客户端包装器，提供与 SocketClient 兼容的接口"""
    
    def __init__(self, ws_client: WebSocketClient):
        self.ws_client = ws_client
        self.running = ws_client.running
        # 不需要创建新的事件循环，直接使用WebSocket客户端的循环
    
    def send(self, proto_id: int, payload: bytes):
        """发送消息"""
        self.ws_client.send(proto_id, payload)
    
    def regist_handler(self, proto_id: int, handler):
        """注册处理器"""
        self.ws_client.regist_handler(proto_id, handler)
    
    def stop(self):
        """停止客户端"""
        print("🔧 正在停止WebSocket客户端...")
        self.ws_client.stop()
        
        # 在WebSocket客户端的循环中断开连接
        if self.ws_client.loop and not self.ws_client.loop.is_closed():
            try:
                # 停止事件循环
                self.ws_client.loop.call_soon_threadsafe(self.ws_client.loop.stop)
                
                # 等待循环线程结束
                if hasattr(self.ws_client, 'loop_thread') and self.ws_client.loop_thread:
                    self.ws_client.loop_thread.join(timeout=1.0)
                
                # 关闭事件循环
                self.ws_client.loop.close()
                
                print("✅ WebSocket客户端已停止")
            except Exception as e:
                print(f"⚠️ 停止WebSocket客户端时出错: {e}")
        else:
            print("✅ WebSocket客户端已停止")


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
