# 模拟角色数据变更测试工具 - 使用统一客户端运行器

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from network.clients.tcp_client import SocketClient
from utils.client_runner import run_client
from google.protobuf.json_format import MessageToJson

# 动态获取proto路径并添加到sys.path
from utils.config_manager import config_manager
proto_path = config_manager.get_proto_path()
sys.path.append(proto_path)
from proto_id_pb2 import ProtoId
import login_pb2

# ===================== 请求/应答处理函数 =====================

# 角色状态变更
status_id = ProtoId.G2L_PlayerStatus

def status_req(client: SocketClient) -> None:
    """📊 发送角色状态变更通知"""
    print("📊 发送角色状态变更通知...")
    msg = login_pb2.PlayerStatusNtf()
    msg.User.RoleId = 903
    msg.User.RoleLevel = 4
    client.send(status_id, msg.SerializeToString())

def status_ack(seq: int, payload: bytes) -> None:
    """角色状态变更应答"""
    print("✅ 角色状态变更通知发送完成")

# ===================== 主逻辑 =====================

if __name__ == "__main__":
    # 使用统一的客户端运行器
    run_client(
        module_name="角色数据变更",
        client_type="login",
        title="📊 角色数据变更测试工具"
    )