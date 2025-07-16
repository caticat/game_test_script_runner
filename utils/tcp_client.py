import socket
import threading
import queue
import struct
import time

from utils.protocol_codec import Codec

class Packet:

    HEADER_SIZE_LOGIN = 18
    @staticmethod
    def encode_login(role_id: int, proto_id: int, seq: int, server_id: int, server_type: int, payload: bytes) -> bytes:
        total_len = Packet.HEADER_SIZE_LOGIN + len(payload)
        # '<' 表示小端序
        # I = uint32, Q = uint64, h = int16, H = uint16
        return struct.pack('<IIhIhh', total_len, role_id, proto_id, seq, server_id, server_type) + payload
    
    @staticmethod
    def decode_login(stream: bytes):
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

    HEADER_SIZE = 10
    @staticmethod
    def encode_gate(proto_id: int, seq: int, payload: bytes) -> bytes:
        total_len = Packet.HEADER_SIZE + len(payload)
        # '<' = little-endian, I=uint32, H=uint16
        return struct.pack('<IHI', total_len, proto_id, seq) + payload

    @staticmethod
    def decode_gate(stream: bytes):
        if len(stream) < Packet.HEADER_SIZE:
            return None, stream  # Not enough for header

        total_len, = struct.unpack('<I', stream[:4])
        if len(stream) < total_len:
            return None, stream  # Not enough for full packet

        proto_id, seq = struct.unpack('<HI', stream[4:10])
        payload = stream[10:total_len]
        rest = stream[total_len:]
        return {'proto_id': proto_id, 'seq': seq, 'payload': payload}, rest


class SocketClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = None
        self.read_queue = queue.Queue()
        self.write_queue = queue.Queue()
        self.running = threading.Event()
        self.running.set()
        self.lock = threading.Lock()
        self.seq = 0
        self.recv_buffer = b""
        self.handlers = {}
        self.dst_gate = True
        self.threads = []

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.socket.settimeout(1.0)
        
        # 创建线程但不设置为daemon
        read_thread = threading.Thread(target=self._read_loop)
        write_thread = threading.Thread(target=self._write_loop)
        logic_thread = threading.Thread(target=self._logic_loop)
        
        self.threads = [read_thread, write_thread, logic_thread]
        
        for thread in self.threads:
            thread.start()

    def stop(self):
        self.running.clear()
        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        # 等待所有线程结束
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=2.0)  # 最多等待2秒

    def send(self, proto_id: int, payload: bytes):
        self.seq += 1
        if self.dst_gate:
            packet = Packet.encode_gate(proto_id, self.seq, payload)
        else:
            packet = Packet.encode_login(0, proto_id, self.seq, 0, 0, payload)
        self.write_queue.put(packet)

    def regist_handler(self, proto_id, handler):
        self.handlers[proto_id] = handler

    def _read_loop(self):
        decode_fun = Packet.decode_gate if self.dst_gate else Packet.decode_login

        while self.running.is_set():
            try:
                if not self.socket:
                    break
                data = self.socket.recv(4096)
                if not data:
                    print("[INFO] Connection closed by remote.")
                    break
                self.recv_buffer += data
                while True:
                    pkt, self.recv_buffer = decode_fun(self.recv_buffer)
                    if pkt is None:
                        break
                    self.read_queue.put(pkt)
            except socket.timeout:
                continue
            except OSError as e:
                if self.running.is_set():
                    print(f"[ERROR] Read failed: {e}")
                break
            except Exception as e:
                if self.running.is_set():
                    print(f"[ERROR] Read failed: {e}")
                break

    def _write_loop(self):
        while self.running.is_set():
            try:
                data = self.write_queue.get(timeout=1)
                if not self.socket:
                    break
                with self.lock:
                    self.socket.sendall(data)
            except queue.Empty:
                continue
            except OSError as e:
                if self.running.is_set():
                    print(f"[ERROR] Write failed: {e}")
                break
            except Exception as e:
                if self.running.is_set():
                    print(f"[ERROR] Write failed: {e}")
                break

    def _logic_loop(self):
        while self.running.is_set():
            try:
                pkt = self.read_queue.get(timeout=1)
                self._handle_packet(pkt)
            except queue.Empty:
                continue

    def _handle_packet(self, pkt):
        proto_id = pkt['proto_id']
        seq = pkt['seq']
        payload = pkt['payload']
        if proto_id not in self.handlers:
            print(f"未处理的协议: proto_id={proto_id}")
            return
        self.handlers[proto_id](seq, payload)
        # print(f"[RECV] proto_id={pkt['proto_id']}, seq={pkt['seq']}, data={pkt['payload']}")


# ✅ 示例：连接并交互
if __name__ == "__main__":
    client = SocketClient("127.0.0.1", 5001)
    try:
        client.connect()
        while client.running.is_set():
            msg = input("Enter message: ")
            if msg.strip().lower() in ["quit", "q", "0"]:
                break

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
    finally:
        client.stop()
