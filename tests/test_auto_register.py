# 测试自动注册功能

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.base_tcp_client import BaseTCPClient
from utils.tcp_client import SocketClient

def get_req(client: SocketClient) -> None:
    print("执行 get_req 命令")

def get_ack(seq: int, payload: bytes) -> None:
    print("执行 get_ack 处理")

def ban_req(client: SocketClient) -> None:
    print("执行 ban_req 命令")

def ban_ack(seq: int, payload: bytes) -> None:
    print("执行 ban_ack 处理")

get_id = 100
ban_id = 200

def test_auto_register():
    current_module = sys.modules[__name__]
    client = BaseTCPClient("login", current_module)
    
    print(f"注册的命令: {list(client.command_handlers.keys())}")
    print(f"注册的处理器: {list(client.ack_handlers.keys())}")
    
    if 'get' in client.command_handlers:
        client.command_handlers['get'](None)
    
    if 'ban' in client.command_handlers:
        client.command_handlers['ban'](None)
    
    if 'get' in client.ack_handlers:
        proto_id, handler = client.ack_handlers['get']
        handler(0, b'test')
    
    if 'ban' in client.ack_handlers:
        proto_id, handler = client.ack_handlers['ban']
        handler(0, b'test')

if __name__ == "__main__":
    test_auto_register()
