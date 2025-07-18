"""
统一的异步客户端基类 - TCP和WebSocket统一为异步模型
"""
import asyncio
import struct
from abc import ABC, abstractmethod
from typing import Dict, Callable, Optional, Any, Union
from utils.debug_utils import debug_print, packet_debug_print


class Packet:
    """统一的数据包编解码类"""
    
    # 登录服协议头部大小
    HEADER_SIZE_LOGIN = 18
    
    # 网关协议头部大小
    HEADER_SIZE_GATE = 10
    
    @staticmethod
    def encode_login(role_id: int, proto_id: int, seq: int, server_id: int, server_type: int, payload: bytes) -> bytes:
        """编码登录服数据包"""
        total_len = Packet.HEADER_SIZE_LOGIN + len(payload)
        return struct.pack('<IIhIhh', total_len, role_id, proto_id, seq, server_id, server_type) + payload
    
    @staticmethod
    def decode_login(stream: bytes):
        """解码登录服数据包"""
        HEADER_FORMAT = '<IIhIhh'
        HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # 18

        if len(stream) < HEADER_SIZE:
            return None, stream  # 头部数据不足

        total_len, role_id, proto_id, seq, server_id, server_type = struct.unpack(HEADER_FORMAT, stream[:HEADER_SIZE])
        if len(stream) < total_len:
            return None, stream  # 数据包不完整

        payload = stream[HEADER_SIZE:total_len]
        rest = stream[total_len:]
        return {
            'total_len': total_len,
            'role_id': role_id,
            'proto_id': proto_id,
            'seq': seq,
            'server_id': server_id,
            'server_type': server_type,
            'payload': payload
        }, rest

    @staticmethod
    def encode_gate(proto_id: int, seq: int, payload: bytes) -> bytes:
        """编码网关数据包"""
        total_len = Packet.HEADER_SIZE_GATE + len(payload)
        return struct.pack('<IHI', total_len, proto_id, seq) + payload

    @staticmethod
    def decode_gate(stream: bytes):
        """解码网关数据包"""
        if len(stream) < Packet.HEADER_SIZE_GATE:
            return None, stream  # 头部数据不足

        total_len, = struct.unpack('<I', stream[:4])
        if len(stream) < total_len:
            return None, stream  # 数据包不完整

        proto_id, seq = struct.unpack('<HI', stream[4:10])
        payload = stream[10:total_len]
        rest = stream[total_len:]
        return {'proto_id': proto_id, 'seq': seq, 'payload': payload}, rest


class BaseClient(ABC):
    """统一的异步客户端基类"""
    
    def __init__(self, connection_info: Union[str, tuple]):
        """
        初始化异步客户端
        
        Args:
            connection_info: 连接信息，TCP为(host, port)，WebSocket为url字符串
        """
        self.connection_info = connection_info
        self.read_queue = asyncio.Queue()
        self.write_queue = asyncio.Queue()
        self.running = asyncio.Event()
        self.running.set()
        self.seq = 0
        self.handlers: Dict[int, Callable] = {}
        self.dst_gate = True  # 默认使用网关协议
        
        # 连接相关
        self.connection = None
        self.recv_buffer = b""
        
        # 异步任务管理
        self.tasks = []
        self.loop = None
    
    @abstractmethod
    async def connect(self):
        """异步连接到服务器（需要子类实现）"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """异步断开连接（需要子类实现）"""
        pass
    
    def send(self, proto_id: int, payload: bytes):
        """发送消息"""
        self.seq += 1
        if self.dst_gate:
            packet = Packet.encode_gate(proto_id, self.seq, payload)
        else:
            packet = Packet.encode_login(0, proto_id, self.seq, 0, 0, payload)
        
        debug_print(f"🔧 [DEBUG] 发送消息: proto_id={proto_id}, seq={self.seq}, payload_len={len(payload)}")
        
        # 异步放入队列
        try:
            self.write_queue.put_nowait(packet)
            debug_print(f"🔧 [DEBUG] 消息已放入写队列, 当前队列大小: {self.write_queue.qsize()}")
        except asyncio.QueueFull:
            print("⚠️ 写队列已满，丢弃数据包")
    
    def regist_handler(self, proto_id: int, handler: Callable):
        """注册协议处理器"""
        self.handlers[proto_id] = handler
    
    async def stop(self):
        """停止客户端"""
        print("🔧 正在停止异步客户端...")
        self.running.clear()
        
        # 取消所有任务
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # 等待任务完成
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        await self.disconnect()
        debug_print("✅ 异步客户端已停止")
    
    async def _async_read_loop(self):
        """异步读取循环（公共逻辑）"""
        decode_fun = Packet.decode_gate if self.dst_gate else Packet.decode_login
        debug_print("🔧 [DEBUG] _async_read_loop 开始运行")
        
        while self.running.is_set():
            try:
                # 子类实现具体的数据接收逻辑
                data = await self._async_recv_data()
                if data is None:
                    # 超时，继续等待
                    continue
                if not data:
                    print("[INFO] 连接已关闭")
                    break
                    
                self.recv_buffer += data
                
                # 解析数据包
                while True:
                    pkt, self.recv_buffer = decode_fun(self.recv_buffer)
                    if pkt is None:
                        break
                    packet_debug_print(f"🔧 [DEBUG] 解析到数据包: proto_id={pkt['proto_id']}, seq={pkt['seq']}")
                    await self.read_queue.put(pkt)
                    
            except Exception as e:
                if self.running.is_set():
                    print(f"❌ 异步读取失败: {e}")
                break
        debug_print("🔧 [DEBUG] _async_read_loop 结束运行")
    
    async def _async_write_loop(self):
        """异步写入循环（公共逻辑）"""
        debug_print("🔧 [DEBUG] _async_write_loop 开始运行")
        while self.running.is_set():
            try:
                # 从写队列获取数据
                try:
                    debug_print("🔧 [DEBUG] 等待写队列中的数据...")
                    data = await asyncio.wait_for(self.write_queue.get(), timeout=0.1)
                    debug_print(f"🔧 [DEBUG] 从写队列获取数据: {len(data)} 字节")
                    # 子类实现具体的数据发送逻辑
                    await self._async_send_data(data)
                    debug_print("🔧 [DEBUG] 数据发送完成")
                except asyncio.TimeoutError:
                    continue
                    
            except Exception as e:
                if self.running.is_set():
                    print(f"❌ 异步写入失败: {e}")
                break
        debug_print("🔧 [DEBUG] _async_write_loop 结束运行")
    
    async def _async_logic_loop(self):
        """异步逻辑处理循环（公共逻辑）"""
        debug_print("🔧 [DEBUG] _async_logic_loop 开始运行")
        while self.running.is_set():
            try:
                # 从读队列获取数据包
                try:
                    packet = await asyncio.wait_for(self.read_queue.get(), timeout=0.1)
                    debug_print(f"🔧 [DEBUG] 从读队列获取数据包: proto_id={packet['proto_id']}")
                    await self._async_handle_packet(packet)
                except asyncio.TimeoutError:
                    continue
                    
            except Exception as e:
                if self.running.is_set():
                    print(f"❌ 异步逻辑处理失败: {e}")
        debug_print("🔧 [DEBUG] _async_logic_loop 结束运行")
    
    async def _async_handle_packet(self, packet: Dict[str, Any]):
        """异步处理数据包（公共逻辑）"""
        proto_id = packet['proto_id']
        seq = packet['seq']
        payload = packet['payload']
        
        packet_debug_print(f"🔧 [DEBUG] 处理数据包: proto_id={proto_id}, seq={seq}, payload_len={len(payload)}")
        
        if proto_id not in self.handlers:
            print(f"⚠️ 未处理的协议: proto_id={proto_id}")
            return
            
        try:
            handler = self.handlers[proto_id]
            debug_print(f"🔧 [DEBUG] 调用处理器: {handler.__name__}")
            if asyncio.iscoroutinefunction(handler):
                await handler(seq, payload)
            else:
                handler(seq, payload)
            debug_print(f"🔧 [DEBUG] 处理器执行完成: {handler.__name__}")
        except Exception as e:
            print(f"❌ 处理器执行失败 proto_id={proto_id}: {e}")
            import traceback
            traceback.print_exc()
    
    @abstractmethod
    async def _async_recv_data(self) -> bytes:
        """异步接收数据（需要子类实现）"""
        pass
    
    @abstractmethod
    async def _async_send_data(self, data: bytes):
        """异步发送数据（需要子类实现）"""
        pass
