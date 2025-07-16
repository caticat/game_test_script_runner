# 测试游戏服自动注册功能

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.base_tcp_client import BaseTCPClient
from utils.tcp_client import SocketClient
from utils.protocol_codec import Codec

class MockProtoId:
    C2G_Login = 1

ProtoId = MockProtoId

_signature = "test_signature"

login_id = ProtoId.C2G_Login

def login_req(client: SocketClient) -> None:
    print("🎮 执行游戏服登录请求...")
    
    if client is None:
        print("   Mock模式：构建登录数据包")
        return
        
    buff = b''
    buff += Codec.encode_int32(903)
    buff += Codec.encode_string("q1")
    buff += Codec.encode_string(_signature)
    buff += Codec.encode_int32(1)
    buff += Codec.encode_string("dev")
    client.send(login_id, buff)

def login_ack(seq: int, payload: bytes) -> None:
    print("✅ 收到游戏服登录应答")
    print(f"   序列号: {seq}")
    print(f"   数据长度: {len(payload)}")

def test_game_client():
    current_module = sys.modules[__name__]
    client = BaseTCPClient("gate", current_module)
    
    print(f"注册的命令: {list(client.command_handlers.keys())}")
    print(f"注册的处理器: {list(client.ack_handlers.keys())}")
    
    if 'login' in client.command_handlers:
        client.command_handlers['login'](None)
    
    if 'login' in client.ack_handlers:
        proto_id, handler = client.ack_handlers['login']
        print(f"协议ID: {proto_id}")
        handler(123, b'test_payload')

if __name__ == "__main__":
    test_game_client()
