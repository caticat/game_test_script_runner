# 封禁账号测试工具 - 使用统一客户端运行器

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from network.clients.tcp_client import SocketClient
from utils.utils import Utils
from utils.client_runner import run_client
from google.protobuf.json_format import MessageToJson

# 动态获取proto路径并添加到sys.path
from utils.config_manager import config_manager
proto_path = config_manager.get_proto_path()
sys.path.append(proto_path)
from proto_id_pb2 import ProtoId
import login_pb2

# ===================== 请求/应答处理函数 =====================

# 获取封禁账号列表
get_id = ProtoId.A2L_GetAccountBans

def get_req(client: SocketClient) -> None:
    """📋 获取封禁账号列表"""
    print("📋 获取封禁账号列表...")
    msg = login_pb2.GetAccountBansReq()
    msg.CurrentPage = 1
    msg.PageSize = 3
    client.send(get_id, msg.SerializeToString())

def get_ack(seq: int, payload: bytes) -> None:
    """获取封禁账号列表应答"""
    msg = login_pb2.GetAccountBansAck()
    msg.ParseFromString(payload)
    print("📋 封禁账号列表:")
    print(MessageToJson(msg, ensure_ascii=False))

# 封禁账号
ban_id = ProtoId.A2L_BanAccounts

def ban_req(client: SocketClient) -> None:
    """🚫 封禁账号"""
    print("🚫 执行封禁账号...")
    msg = login_pb2.BanAccountsReq()
    account = msg.Accounts.add()
    account.Channel = "dev"
    account.OpenId = "q1"
    msg.BanEndTime = Utils.str_to_timestamp("2025-12-31 23:59:59")
    msg.BanReason = "测试封禁"
    client.send(ban_id, msg.SerializeToString())

def ban_ack(seq: int, payload: bytes) -> None:
    """封禁账号应答"""
    msg = login_pb2.BanAccountsAck()
    msg.ParseFromString(payload)
    print("🚫 封禁账号结果:")
    print(MessageToJson(msg, ensure_ascii=False))

# 解封账号
unban_id = ProtoId.A2L_UnbanAccounts

def unban_req(client: SocketClient) -> None:
    """✅ 解封账号"""
    print("✅ 执行解封账号...")
    msg = login_pb2.UnbanAccountsReq()
    account = msg.Accounts.add()
    account.Channel = "dev"
    account.OpenId = "q1"
    client.send(unban_id, msg.SerializeToString())

def unban_ack(seq: int, payload: bytes) -> None:
    """解封账号应答"""
    msg = login_pb2.UnbanAccountsAck()
    msg.ParseFromString(payload)
    print("✅ 解封账号结果:")
    print(MessageToJson(msg, ensure_ascii=False))

# ===================== 主逻辑 =====================

if __name__ == "__main__":
    # 使用统一的客户端运行器
    run_client(
        module_name="账号封禁管理",
        client_type="login",
        title="🔧 账号封禁管理工具"
    )