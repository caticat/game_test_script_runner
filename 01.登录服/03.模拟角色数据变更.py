import sys
import inspect
from utils.proto_encode import Codec
from utils.tcp_client import SocketClient
from utils.login_poster import load_config
from google.protobuf.json_format import MessageToJson

# 绝对路径
external_path = "Q:/kof/dev/proto_python"
sys.path.append(external_path)
from proto_id_pb2 import ProtoId
import login_pb2

# ===================== 请求/应答处理函数 =====================

# 模拟角色数据变更
status_id = ProtoId.G2L_PlayerStatus

def status_req(client: SocketClient) -> None:
    msg = login_pb2.PlayerStatusNtf()
    msg.User.RoleId = 1
    msg.User.RoleLevel = 1
    client.send(status_id, msg.SerializeToString())

def status_ack(seq: int, payload: bytes) -> None:
    print("没有ack")
    # msg = login_pb2.PlayerStatusNtf()
    # msg.ParseFromString(payload)
    # print(MessageToJson(msg, ensure_ascii=False))

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
