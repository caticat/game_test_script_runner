from utils.proto_encode import Codec
from utils.tcp_client import SocketClient
from utils.login_poster import load_config

_signature = "3/VySUzR7X6w6xPfzpT0HDNdCif0HBbn" # 登录签名

def login(client: SocketClient) -> None:
        proto_id = 1 # C2G_Login

        buff = b''
        buff += Codec.encode_int32(903) # RoleId
        buff += Codec.encode_string("q1") # Account
        buff += Codec.encode_string(_signature) # Signature
        buff += Codec.encode_int32(1) # AreaId
        buff += Codec.encode_string("dev") # Channel
        buff += Codec.encode_string("windows") # Platform
        buff += Codec.encode_string("DeviceModel") # DeviceModel
        buff += Codec.encode_string("DeviceName") # DeviceName
        buff += Codec.encode_string("DeviceType") # DeviceType
        buff += Codec.encode_int32(1) # ProcessorCount
        buff += Codec.encode_int32(1) # ProcessorFrequency
        buff += Codec.encode_int32(1024*1024*1024*8) # SystemMemorySize
        buff += Codec.encode_int32(1024*1024*1024*8) # GraphicsMemorySize
        buff += Codec.encode_string("GraphicsDeviceType") # GraphicsDeviceType
        buff += Codec.encode_string("GraphicsDeviceName") # GraphicsDeviceName
        buff += Codec.encode_int32(1024) # ScreenWidth
        buff += Codec.encode_int32(1024) # ScreenHeight
        buff += Codec.encode_int32(1) # WxModelLevel
        buff += Codec.encode_int32(1) # WxBenchmarkLevel
        buff += Codec.encode_int32(1) # Language
        buff += Codec.encode_string("localhost") # ClientIP

        client.send(proto_id, buff)

def login_ack(seq: int, payload: bytes) -> None:
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
    # 其他字段可以根据需要继续解码

def quit(client: SocketClient) -> None:
    print("Exit.")
    exit(0)

def regist_ack_handler(client: SocketClient) -> None:
    client.regist_handler(1, login_ack)

_command_handler = {
    "quit": quit,
    "login": login,
}

def main():
    cfg = load_config()
    host = cfg["gate"]["host"]
    port = cfg["gate"]["port"]
    
    client = SocketClient(host, port)
    try:
        client.connect()
        regist_ack_handler(client)
        while client.running.is_set():
            msg = input("请输入命令: ")
            cmd = msg.strip().lower()
            if cmd not in _command_handler:
                print(f"未知命令(请在_command_handler中注册): {cmd}")
                continue
            _command_handler[cmd](client)
    finally:
        client.stop()

if __name__ == "__main__":
    main()
