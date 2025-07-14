# 游戏服测试工具

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.base_tcp_client import BaseTCPClient
from utils.tcp_client import SocketClient
from utils.protocol_codec import Codec
from utils.config_manager import config_manager

# 动态获取proto路径并添加到sys.path
proto_path = config_manager.get_proto_path()
sys.path.append(proto_path)
from proto_id_pb2 import ProtoId

_signature = "SSdRaix1HD0YnB1XnhXp88W5Rr90qj9y7XldlcDtQzg="

login_id = ProtoId.C2G_Login

def login_req(client: SocketClient) -> None:
    buff = b''
    buff += Codec.encode_int32(903)
    buff += Codec.encode_string("q1")
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
    print("发送游戏服登录请求")

def login_ack(seq: int, payload: bytes) -> None:
    """游戏服登录应答"""
    pos = 0
    resultId, pos = Codec.decode_int16(payload, pos)
    if resultId != 0:
        errMsg, pos = Codec.decode_string(payload, pos)
        print(f"登录失败: {resultId}, 错误信息: {errMsg}")
        return
    
    roleId, pos = Codec.decode_int32(payload, pos)
    account, pos = Codec.decode_string(payload, pos)
    areaId, pos = Codec.decode_int32(payload, pos)
    timeZone, pos = Codec.decode_int32(payload, pos)
    print(f"登录成功: 角色ID={roleId}, 账号={account}, 区域ID={areaId}, 时区={timeZone}")

# ===================== 主逻辑 =====================

def main():
    """主函数"""
    print("=== 游戏服测试工具 ===")
    print("可用命令:")
    print("  login - 游戏服登录")
    print("  quit  - 退出程序")
    print()
    
    # 使用基础TCP客户端
    current_module = sys.modules[__name__]
    client = BaseTCPClient("gate", current_module)
    client.connect_and_run()

if __name__ == "__main__":
    main()
