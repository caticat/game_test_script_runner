# 封禁账号测试工具

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.base_tcp_client import BaseTCPClient
from utils.tcp_client import SocketClient
from utils.utils import Utils
from google.protobuf.json_format import MessageToJson

external_path = "Q:/kof/dev/proto_python"
sys.path.append(external_path)
from proto_id_pb2 import ProtoId
import login_pb2

# ===================== 请求/应答处理函数 =====================

# 获取封禁账号列表
get_id = ProtoId.A2L_GetAccountBans

def get_req(client: SocketClient) -> None:
    """获取封禁账号列表请求"""
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
    """封禁账号请求"""
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
    """解封账号请求"""
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

def main():
    """主函数"""
    print("=== 🔧 账号封禁管理工具 ===")
    print("📝 可用命令:")
    print("  get   - 📋 获取封禁账号列表")
    print("  ban   - 🚫 封禁账号")
    print("  unban - ✅ 解封账号")
    print("  quit  - 🚪 退出程序")
    print()
    
    # 使用基础TCP客户端
    current_module = sys.modules[__name__]
    client = BaseTCPClient("login", current_module)
    client.connect_and_run()

if __name__ == "__main__":
    main()
