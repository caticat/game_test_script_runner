# 游戏服登录测试工具 - 使用统一客户端运行器

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from network.clients.tcp_client import SocketClient
from network.protocol.codec import Codec
from utils.client_runner import run_client

# 动态获取proto路径并添加到sys.path
from utils.config_manager import config_manager
proto_path = config_manager.get_proto_path()
sys.path.append(proto_path)
from proto_id_pb2 import ProtoId

_signature = "zZEYq9ag53IzOKmBEbxr1MICaXVjftQR"
_open_id = "q1"
_role_id = 61

# ===================== 请求/应答处理函数 =====================

# 游戏服登录
login_id = ProtoId.C2G_Login

def login_req(client: SocketClient) -> None:
    """🎮 游戏服登录"""
    print("🎮 执行游戏服登录...")
    buff = b''
    buff += Codec.encode_int32(_role_id)
    buff += Codec.encode_string(_open_id)
    buff += Codec.encode_string(_signature)
    buff += Codec.encode_int32(1)  # AreaId
    buff += Codec.encode_string("dev")  # Channel
    buff += Codec.encode_string("windows")  # Platform
    buff += Codec.encode_string("DeviceModel")  # DeviceModel
    buff += Codec.encode_string("DeviceName")  # DeviceName
    buff += Codec.encode_string("DeviceType")  # DeviceType
    buff += Codec.encode_int32(1)  # ProcessorCount
    buff += Codec.encode_int32(1)  # ProcessorFrequency
    buff += Codec.encode_int32(1024*1024*1024*8)  # SystemMemorySize
    buff += Codec.encode_int32(1024*1024*1024*8)  # GraphicsMemorySize
    buff += Codec.encode_string("GraphicsDeviceType")  # GraphicsDeviceType
    buff += Codec.encode_string("GraphicsDeviceName")  # GraphicsDeviceName
    buff += Codec.encode_int32(1024)  # ScreenWidth
    buff += Codec.encode_int32(1024)  # ScreenHeight
    buff += Codec.encode_int32(1)  # WxModelLevel
    buff += Codec.encode_int32(1)  # WxBenchmarkLevel
    buff += Codec.encode_int32(1)  # Language
    buff += Codec.encode_string("localhost")  # ClientIP

    client.send(login_id, buff)

def login_ack(seq: int, payload: bytes) -> None:
    """游戏服登录应答"""
    pos = 0
    resultId, pos = Codec.decode_int16(payload, pos)
    if resultId != 0:
        errMsg, pos = Codec.decode_string(payload, pos)
        print(f"🎮 登录失败: {resultId}, 错误信息: {errMsg}")
        return
    
    roleId, pos = Codec.decode_int32(payload, pos)
    account, pos = Codec.decode_string(payload, pos)
    areaId, pos = Codec.decode_int32(payload, pos)
    timeZone, pos = Codec.decode_int32(payload, pos)
    print(f"🎮 登录成功: 角色ID={roleId}, 账号={account}, 区域ID={areaId}, 时区={timeZone}")

# ===================== 主逻辑 =====================

if __name__ == "__main__":
    # 使用统一的客户端运行器
    run_client(
        module_name="游戏服登录",
        client_type="gate",
        title="🎮 游戏服登录工具"
    )
