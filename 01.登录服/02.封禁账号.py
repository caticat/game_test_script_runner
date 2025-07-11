import sys
import inspect
from utils import time_helper
from utils.tcp_client import SocketClient
from utils.login_poster import load_config
from google.protobuf.json_format import MessageToJson

# 绝对路径
external_path = "Q:/kof/dev/proto_python"
sys.path.append(external_path)
from proto_id_pb2 import ProtoId
import login_pb2

# ===================== 请求/应答处理函数 =====================

# 获取封禁账号列表
get_id = ProtoId.A2L_GetAccountBans

def get_req(client: SocketClient) -> None:
    msg = login_pb2.GetAccountBansReq()
    msg.CurrentPage = 1
    msg.PageSize = 3
    client.send(get_id, msg.SerializeToString())

def get_ack(seq: int, payload: bytes) -> None:
    msg = login_pb2.GetAccountBansAck()
    msg.ParseFromString(payload)
    print(MessageToJson(msg, ensure_ascii=False))

# 封禁账号
ban_id = ProtoId.A2L_BanAccounts

def ban_req(client: SocketClient) -> None:
    msg = login_pb2.BanAccountsReq()
    account = msg.accounts.add()
    account.Channel = "dev"
    account.OpenId = "q1"
    msg.BanEndTime = time_helper.str_to_timestamp("2025-12-31 23:59:59")
    msg.BanReason = "测试封禁"
    client.send(ban_id, msg.SerializeToString())

def ban_ack(seq: int, payload: bytes) -> None:
    msg = login_pb2.BanAccountsAck()
    msg.ParseFromString(payload)
    print(MessageToJson(msg))

# 解封账号
unban_id = ProtoId.A2L_UnbanAccounts

def unban_req(client: SocketClient) -> None:
    msg = login_pb2.UnbanAccountsReq()
    account = msg.accounts.add()
    account.Channel = "dev"
    account.OpenId = "q1"
    client.send(unban_id, msg.SerializeToString())

def unban_ack(seq: int, payload: bytes) -> None:
    msg = login_pb2.UnbanAccountsAck()
    msg.ParseFromString(payload)
    print(MessageToJson(msg))

# ===================== 固定函数 =====================

def quit(client: SocketClient) -> None:
    print("Exit.")
    exit(0)

# ===================== 自动注册机制 =====================

_command_handler = {
    "quit": quit,
}
_ack_handlers = {}

def _auto_register_commands_and_handlers():
    current_module = sys.modules[__name__]
    for name, obj in inspect.getmembers(current_module, inspect.isfunction):
        if name.endswith('_req'):
            key = name[:-4]
            _command_handler[key] = obj
        elif name.endswith('_ack'):
            key = name[:-4]
            id_var_name = f'{key}_id'
            proto_id = getattr(current_module, id_var_name, None)
            if proto_id is not None:
                _ack_handlers[key] = (proto_id, obj)
            else:
                print(f"[警告] 未找到变量 {id_var_name}，无法注册 {name}")

def regist_ack_handler(client: SocketClient) -> None:
    for name, (proto_id, handler_fn) in _ack_handlers.items():
        client.regist_handler(proto_id, handler_fn)

_auto_register_commands_and_handlers()

# ===================== 主逻辑 =====================

def main():
    cfg = load_config()
    host = cfg["login"]["host"]
    port = cfg["login"]["port"]
    
    client = SocketClient(host, port)
    client.dst_gate = False

    try:
        client.connect()
        regist_ack_handler(client)
        while client.running.is_set():
            msg = input("请输入命令: ").strip().lower()
            cmd_fn = _command_handler.get(msg)
            if not cmd_fn:
                print(f"未知命令: {msg}")
                continue
            cmd_fn(client)
    finally:
        client.stop()

if __name__ == "__main__":
    main()
