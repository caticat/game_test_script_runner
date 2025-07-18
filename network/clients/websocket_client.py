"""
WebSocket 客户端 - 纯异步版本
"""
import asyncio
import json
from typing import Optional
import websockets
from websockets.client import WebSocketClientProtocol
from ..protocol.codec import Codec
from utils.debug_utils import debug_print
from .base_client import BaseClient, Packet


class WebSocketClient(BaseClient):
    """异步WebSocket客户端"""
    
    def __init__(self, url: str):
        """
        初始化WebSocket客户端
        
        Args:
            url: WebSocket URL (如: wss://127.0.0.1/gateway)
        """
        super().__init__(url)
        self.url = url
        self.websocket: Optional[WebSocketClientProtocol] = None
        
    async def connect(self):
        """异步连接到WebSocket服务器"""
        try:
            self.websocket = await websockets.connect(self.url)
            self.connection = self.websocket
            print(f"✅ WebSocket已连接: {self.url}")
            
            # 获取事件循环
            self.loop = asyncio.get_event_loop()
            
            # 创建异步任务
            read_task = asyncio.create_task(self._async_read_loop())
            write_task = asyncio.create_task(self._async_write_loop())
            logic_task = asyncio.create_task(self._async_logic_loop())
            
            self.tasks = [read_task, write_task, logic_task]
            
            return True
            
        except Exception as e:
            print(f"❌ WebSocket连接失败: {e}")
            return False
    
    async def disconnect(self):
        """异步断开WebSocket连接"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            self.connection = None
            
        print("✅ WebSocket已断开连接")

    async def _async_recv_data(self) -> bytes:
        """异步接收WebSocket数据"""
        if not self.websocket:
            return b""
        try:
            # 接收WebSocket消息
            message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
            
            if isinstance(message, str):
                # 处理文本消息
                await self._handle_text_message(message)
                return b""  # 文本消息不返回二进制数据
            elif isinstance(message, bytes):
                # 返回二进制消息
                return message
            else:
                return b""
                
        except asyncio.TimeoutError:
            return b""
        except websockets.exceptions.ConnectionClosed:
            print("🔗 WebSocket连接已关闭")
            return b""

    async def _async_send_data(self, data: bytes):
        """异步发送WebSocket数据"""
        if not self.websocket:
            raise Exception("WebSocket not connected")
        debug_print(f"🔧 [WebSocket] 准备发送数据: {len(data)} bytes")
        await self.websocket.send(data)
        print(f"✅ [WebSocket] 数据已发送成功")

    async def _handle_text_message(self, message: str):
        """处理文本消息"""
        try:
            data = json.loads(message)
            print(f"� 收到文本消息: {data}")
            # 可以根据需要处理文本消息
        except json.JSONDecodeError:
            print(f"⚠️ 无法解析文本消息: {message}")

    async def _async_read_loop(self):
        """重写异步读取循环以处理WebSocket特殊逻辑"""
        decode_fun = Packet.decode_gate if self.dst_gate else Packet.decode_login
        
        while self.running.is_set() and self.websocket:
            try:
                # 接收WebSocket消息
                message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                
                if isinstance(message, str):
                    # 处理文本消息
                    await self._handle_text_message(message)
                elif isinstance(message, bytes):
                    # 处理二进制消息
                    self.recv_buffer += message
                    
                    # 解析数据包
                    while True:
                        pkt, self.recv_buffer = decode_fun(self.recv_buffer)
                        if pkt is None:
                            break
                        await self.read_queue.put(pkt)
                    
            except asyncio.TimeoutError:
                continue
            except websockets.exceptions.ConnectionClosed:
                print("🔗 WebSocket连接已关闭")
                break
            except Exception as e:
                if self.running.is_set():
                    print(f"❌ WebSocket读取失败: {e}")
                break
