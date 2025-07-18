import asyncio
import socket
from ..protocol.codec import Codec
from .base_client import BaseClient, Packet
from utils.debug_utils import debug_print


class SocketClient(BaseClient):
    """异步TCP客户端"""
    
    def __init__(self, host: str, port: int):
        super().__init__((host, port))
        self.host = host
        self.port = port
        self.socket = None

    async def connect(self):
        """异步连接到TCP服务器"""
        try:
            # 创建socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setblocking(False)  # 设置为非阻塞
            
            # 获取事件循环
            self.loop = asyncio.get_event_loop()
            
            # 异步连接
            await self.loop.sock_connect(self.socket, (self.host, self.port))
            self.connection = self.socket
            
            print(f"✅ TCP已连接: {self.host}:{self.port}")
            
            # 创建异步任务
            read_task = asyncio.create_task(self._async_read_loop())
            write_task = asyncio.create_task(self._async_write_loop())
            logic_task = asyncio.create_task(self._async_logic_loop())
            
            self.tasks = [read_task, write_task, logic_task]
            
            return True
            
        except Exception as e:
            print(f"❌ TCP连接失败: {e}")
            return False

    async def disconnect(self):
        """异步断开TCP连接"""
        if self.socket:
            self.socket.close()
            self.socket = None
            self.connection = None
            
        print("✅ TCP已断开连接")

    async def _async_recv_data(self) -> bytes:
        """异步接收TCP数据"""
        if not self.socket:
            return b""
        try:
            data = await asyncio.wait_for(
                self.loop.sock_recv(self.socket, 4096), 
                timeout=1.0
            )
            if data:
                debug_print(f"🔧 [DEBUG] 接收到数据: {len(data)} 字节")
            return data
        except asyncio.TimeoutError:
            # 超时不是错误，继续等待
            return None
        except Exception as e:
            print(f"❌ TCP接收数据失败: {e}")
            return b""

    async def _async_send_data(self, data: bytes):
        """异步发送TCP数据"""
        if not self.socket:
            raise Exception("Socket not connected")
        await self.loop.sock_sendall(self.socket, data)


# ✅ 示例：异步连接并交互
async def main():
    client = SocketClient("127.0.0.1", 5001)
    try:
        await client.connect()
        
        # 发送登录数据
        buff = b''
        buff += Codec.encode_int32(1) # RoleId
        buff += Codec.encode_string("q1") # Account
        buff += Codec.encode_string("dQwWCnVsIbP8VRB20GJV9rFuGthn5ZpRScrZJnyMe2b/wF4BbfeG+w==") # Signature
        buff += Codec.encode_int32(1) # AreaId
        buff += Codec.encode_string("dev") # Channel
        buff += Codec.encode_string("windows") # Platform
        buff += Codec.encode_string("DeviceModel") # DeviceModel
        buff += Codec.encode_string("DeviceName") # DeviceName
        buff += Codec.encode_string("DeviceType") # DeviceType
        buff += Codec.encode_int32(1) # ProcessorCount
        buff += Codec.encode_int32(1) # ProcessorFrequency
        buff += Codec.encode_int32(1024*1024*1024*8) # SystemMemorySize
        buff += Codec.encode_int32(1024*1024*1024*8) # GraphicsMemorySize
        buff += Codec.encode_string("GraphicsDeviceType") # GraphicsDeviceType
        buff += Codec.encode_string("GraphicsDeviceName") # GraphicsDeviceName
        buff += Codec.encode_int32(1024) # ScreenWidth
        buff += Codec.encode_int32(1024) # ScreenHeight
        buff += Codec.encode_int32(1) # WxModelLevel
        buff += Codec.encode_int32(1) # WxBenchmarkLevel
        buff += Codec.encode_int32(1) # Language
        buff += Codec.encode_string("localhost") # ClientIP
        client.send(1, buff) # C2G_Login
        
        # 等待一段时间让任务运行
        await asyncio.sleep(5)
        
    finally:
        await client.stop()

if __name__ == "__main__":
    asyncio.run(main())
