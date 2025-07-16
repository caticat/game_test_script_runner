# 模拟角色数据变更测试工具

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.base_tcp_client import BaseTCPClient
from utils.tcp_client import SocketClient
from utils.config_manager import config_manager

# 动态获取proto路径并添加到sys.path
proto_path = config_manager.get_proto_path()
sys.path.append(proto_path)
from proto_id_pb2 import ProtoId
import login_pb2

status_id = ProtoId.G2L_PlayerStatus

def status_req(client: SocketClient) -> None:
    """发送角色状态变更请求"""
    print("📊 发送角色状态变更通知...")
    msg = login_pb2.PlayerStatusNtf()
    msg.User.RoleId = 903
    msg.User.RoleLevel = 4
    client.send(status_id, msg.SerializeToString())

def status_ack(seq: int, payload: bytes) -> None:
    """角色状态变更应答"""
    print("✅ 角色状态变更通知发送完成")

def main():
    """主函数"""
    print("=== 📊 角色数据变更模拟工具 ===")
    print("📝 可用命令:")
    print("  status - 📊 发送角色状态变更通知")
    print("  quit   - 🚪 退出程序 (可输入 quit/q/0)")
    print()
    
    current_module = sys.modules[__name__]
    client = BaseTCPClient("login", current_module)
    client.connect_and_run()

if __name__ == "__main__":
    main()
