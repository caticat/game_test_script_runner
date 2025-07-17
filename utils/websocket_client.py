"""
WebSocket 客户端
"""
import asyncio
import json
import queue
import struct
import threading
from typing import Dict, Callable, Optional
import websockets
from websockets.client import WebSocketClientProtocol
from utils.protocol_codec import Codec
from utils.debug_utils import debug_print

class WebSocketClient:
    """WebSocket 客户端"""
    
    def __init__(self, url: str):
        """
        初始化 WebSocket 客户端
        
        Args:
            url: WebSocket URL (如: wss://127.0.0.1/gateway)
        """
        self.url = url
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.read_queue = queue.Queue()
        self.write_queue = queue.Queue()
        self.running = threading.Event()
        self.running.set()
        self.lock = threading.Lock()
        self.seq = 0
        self.handlers: Dict[int, Callable] = {}
        self.dst_gate = True
        self.loop = None
        self.tasks = []
        
    async def connect(self):
        """连接到 WebSocket 服务器"""
        try:
            self.websocket = await websockets.connect(self.url)
            print(f"✅ WebSocket 已连接: {self.url}")
            
            # 创建事件循环任务
            self.loop = asyncio.get_event_loop()
            
            # 创建读写任务
            read_task = asyncio.create_task(self._read_loop())
            write_task = asyncio.create_task(self._write_loop())
            logic_task = asyncio.create_task(self._logic_loop())
            
            self.tasks = [read_task, write_task, logic_task]
            
            return True
            
        except Exception as e:
            print(f"❌ WebSocket 连接失败: {e}")
            return False
    
    async def disconnect(self):
        """断开 WebSocket 连接"""
        self.running.clear()
        
        # 取消所有任务
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # 等待任务完成
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        # 关闭 WebSocket 连接
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            
        print("✅ WebSocket 已断开连接")
    
    def send(self, proto_id: int, payload: bytes):
        """发送消息"""
        self.seq += 1
        
        if self.dst_gate:
            # 使用网关协议格式
            packet = self._encode_gate_packet(proto_id, self.seq, payload)
            debug_print(f"🔧 [WebSocket] 使用网关协议发送: proto_id={proto_id}, seq={self.seq}, payload_len={len(payload)}")
        else:
            # 使用登录服协议格式
            packet = self._encode_login_packet(0, proto_id, self.seq, 0, 0, payload)
            debug_print(f"🔧 [WebSocket] 使用登录服协议发送: proto_id={proto_id}, seq={self.seq}, payload_len={len(payload)}")
        
        debug_print(f"🔧 [WebSocket] 数据包长度: {len(packet)} bytes")
        debug_print(f"🔧 [WebSocket] 数据包头部: {packet[:20].hex()}")
        
        # 将数据包放入写队列
        self.write_queue.put(packet)
        debug_print(f"🔧 [WebSocket] 数据包已放入写队列")
    
    def _encode_gate_packet(self, proto_id: int, seq: int, payload: bytes) -> bytes:
        """编码网关数据包"""
        total_len = 10 + len(payload)  # 4 + 2 + 4 + payload
        # 使用与TCP客户端相同的格式: <IHI
        return struct.pack('<IHI', total_len, proto_id, seq) + payload
    
    def _encode_login_packet(self, role_id: int, proto_id: int, seq: int, 
                           server_id: int, server_type: int, payload: bytes) -> bytes:
        """编码登录服数据包"""
        total_len = 18 + len(payload)
        return struct.pack('<IIhIhh', total_len, role_id, proto_id, seq, server_id, server_type) + payload
    
    def regist_handler(self, proto_id: int, handler: Callable):
        """注册协议处理器"""
        self.handlers[proto_id] = handler
    
    async def _read_loop(self):
        """读取循环"""
        while self.running.is_set() and self.websocket:
            try:
                # 接收 WebSocket 消息
                message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                
                if isinstance(message, str):
                    # 处理文本消息
                    await self._handle_text_message(message)
                elif isinstance(message, bytes):
                    # 处理二进制消息
                    await self._handle_binary_message(message)
                    
            except asyncio.TimeoutError:
                continue
            except websockets.exceptions.ConnectionClosed:
                print("🔗 WebSocket 连接已关闭")
                break
            except Exception as e:
                if self.running.is_set():
                    print(f"❌ WebSocket 读取失败: {e}")
                break
    
    async def _handle_text_message(self, message: str):
        """处理文本消息"""
        try:
            data = json.loads(message)
            print(f"📨 收到文本消息: {data}")
            # 可以根据需要处理文本消息
        except json.JSONDecodeError:
            print(f"⚠️ 无法解析文本消息: {message}")
    
    async def _handle_binary_message(self, data: bytes):
        """处理二进制消息"""
        # 解析二进制数据包
        if self.dst_gate:
            packet = self._decode_gate_packet(data)
        else:
            packet = self._decode_login_packet(data)
        
        if packet:
            self.read_queue.put(packet)
    
    def _decode_gate_packet(self, data: bytes) -> Optional[Dict]:
        """解码网关数据包"""
        if len(data) < 10:
            return None
        
        total_len, proto_id, seq = struct.unpack('<IHI', data[:10])
        payload = data[10:total_len]
        
        return {
            'proto_id': proto_id,
            'seq': seq,
            'payload': payload
        }
    
    def _decode_login_packet(self, data: bytes) -> Optional[Dict]:
        """解码登录服数据包"""
        if len(data) < 18:
            return None
        
        total_len, role_id, proto_id, seq, server_id, server_type = struct.unpack('<IIhIhh', data[:18])
        payload = data[18:total_len]
        
        return {
            'total_len': total_len,
            'role_id': role_id,
            'proto_id': proto_id,
            'seq': seq,
            'server_id': server_id,
            'server_type': server_type,
            'payload': payload
        }
    
    async def _write_loop(self):
        """写入循环"""
        while self.running.is_set() and self.websocket:
            try:
                # 从写队列获取数据（使用非阻塞方式）
                try:
                    data = self.write_queue.get_nowait()
                    debug_print(f"🔧 [WebSocket] 准备发送数据: {len(data)} bytes")
                    
                    # 发送二进制数据
                    await self.websocket.send(data)
                    
                    print(f"✅ [WebSocket] 数据已发送成功")
                    
                except queue.Empty:
                    # 队列为空，等待一下
                    await asyncio.sleep(0.1)
                    continue
                    
            except websockets.exceptions.ConnectionClosed:
                print("🔗 WebSocket 连接已关闭")
                break
            except Exception as e:
                if self.running.is_set():
                    print(f"❌ WebSocket 写入失败: {e}")
                break
    
    async def _logic_loop(self):
        """逻辑处理循环"""
        while self.running.is_set():
            try:
                # 从读队列获取数据包（使用非阻塞方式）
                try:
                    packet = self.read_queue.get_nowait()
                    await self._handle_packet(packet)
                except queue.Empty:
                    # 队列为空，等待一下
                    await asyncio.sleep(0.1)
                    continue
                    
            except Exception as e:
                if self.running.is_set():
                    print(f"❌ 数据包处理失败: {e}")
    
    async def _handle_packet(self, packet: Dict):
        """处理数据包"""
        proto_id = packet['proto_id']
        seq = packet['seq']
        payload = packet['payload']
        
        if proto_id in self.handlers:
            try:
                # 调用处理器
                handler = self.handlers[proto_id]
                if asyncio.iscoroutinefunction(handler):
                    await handler(seq, payload)
                else:
                    handler(seq, payload)
            except Exception as e:
                print(f"❌ 处理器执行失败: {e}")
        else:
            print(f"⚠️ 未处理的协议: proto_id={proto_id}")
    
    def stop(self):
        """停止客户端（兼容性方法）"""
        print("🔧 正在停止WebSocket客户端...")
        self.running.clear()
        # 注意：这个方法不能直接关闭 WebSocket，需要在异步环境中调用 disconnect()
        
        # 给一点时间让循环处理停止信号
        import time
        time.sleep(0.1)
        
        print("✅ WebSocket客户端停止信号已发送")
