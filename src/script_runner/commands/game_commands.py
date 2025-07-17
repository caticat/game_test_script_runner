"""
游戏服相关命令
"""
from typing import Dict, Any
from .base_command import BaseCommand
from utils.protocol_codec import Codec
from utils.debug_utils import debug_print
import sys
import os

# 动态获取proto路径并添加到sys.path
from utils.config_manager import config_manager
proto_path = config_manager.get_proto_path()
sys.path.append(proto_path)

class LoginCommand(BaseCommand):
    """游戏服登录命令"""
    
    def execute(self, signature: str = "", role_id: int = 0, user_name: str = "", 
                area_id: int = 1, channel: str = "dev", platform: str = "windows") -> Dict[str, Any]:
        """
        执行游戏服登录
        
        Args:
            signature: 登录签名
            role_id: 角色ID
            user_name: 用户名
            area_id: 区域ID
            channel: 渠道
            platform: 平台
            
        Returns:
            Dict[str, Any]: 登录结果（None，等待异步应答）
        """
        if not self.current_client:
            raise ValueError("未连接到服务器，请先执行 connect_gate 或 connect_login")
        
        # 如果参数未提供，尝试从之前的命令结果中获取
        if not signature or not role_id or not user_name:
            select_area_result = self.results.get("select_area")
            auth_result = self.results.get("auth")
            
            if not signature and select_area_result and "Signature" in select_area_result:
                signature = select_area_result["Signature"]
                
            if not role_id and select_area_result and "RoleId" in select_area_result:
                role_id = select_area_result["RoleId"]
                
            if not user_name and auth_result and "OpenId" in auth_result:
                user_name = auth_result["OpenId"]
        
        # 检查必要参数
        if not signature:
            raise ValueError("缺少signature参数，请提供或确保select_area命令已执行")
        if not role_id:
            raise ValueError("缺少role_id参数，请提供或确保select_area命令已执行")
        if not user_name:
            raise ValueError("缺少user_name参数，请提供或确保auth命令已执行")
        
        # 导入协议ID
        try:
            from proto_id_pb2 import ProtoId
            login_id = ProtoId.C2G_Login
        except ImportError:
            debug_print("⚠️  无法导入协议ID，使用默认值")
            login_id = 1  # 默认登录协议ID
        
        # 构建登录数据包
        buff = self._build_login_packet(role_id, user_name, signature, area_id, channel, platform)
        
        debug_print(f"🔧 [Login] 构建登录数据包: 长度={len(buff)} bytes")
        debug_print(f"🔧 [Login] 数据包头部: {buff[:20].hex()}")
        
        # 注册登录应答处理器
        self.current_client.regist_handler(login_id, self._login_ack_handler)
        
        debug_print(f"🔧 [Login] 注册处理器: proto_id={login_id}")
        
        # 发送登录请求
        self.current_client.send(login_id, buff)
        print(f"📤 发送登录请求: proto_id={login_id}, role_id={role_id}, user_name={user_name}")
        
        # 不返回临时结果，等待登录应答处理器设置真正的结果
        return None
    
    def _build_login_packet(self, role_id: int, user_name: str, signature: str, 
                           area_id: int, channel: str, platform: str) -> bytes:
        """构建登录数据包"""
        buff = b''
        buff += Codec.encode_int32(role_id)
        buff += Codec.encode_string(user_name)
        buff += Codec.encode_string(signature)
        buff += Codec.encode_int32(area_id)
        buff += Codec.encode_string(channel)
        buff += Codec.encode_string(platform)
        buff += Codec.encode_string("DeviceModel")
        buff += Codec.encode_string("DeviceName")
        buff += Codec.encode_string("DeviceType")
        buff += Codec.encode_int32(1)  # ProcessorCount
        buff += Codec.encode_int32(1)  # ProcessorFrequency
        buff += Codec.encode_int32(1024*1024*1024*8)  # SystemMemorySize
        buff += Codec.encode_int32(1024*1024*1024*8)  # GraphicsMemorySize
        buff += Codec.encode_string("GraphicsDeviceType")
        buff += Codec.encode_string("GraphicsDeviceName")
        buff += Codec.encode_int32(1024)  # ScreenWidth
        buff += Codec.encode_int32(1024)  # ScreenHeight
        buff += Codec.encode_int32(1)  # WxModelLevel
        buff += Codec.encode_int32(1)  # WxBenchmarkLevel
        buff += Codec.encode_int32(1)  # Language
        buff += Codec.encode_string("localhost")  # ClientIP
        return buff
    
    def _login_ack_handler(self, seq: int, payload: bytes):
        """登录应答处理器"""
        try:
            pos = 0
            result_id, pos = Codec.decode_int16(payload, pos)
            
            if result_id != 0:
                err_msg, pos = Codec.decode_string(payload, pos)
                result = {"success": False, "result_id": result_id, "error": err_msg}
                print(f"❌ 登录失败: {result_id}, 错误: {err_msg}")
            else:
                role_id, pos = Codec.decode_int32(payload, pos)
                account, pos = Codec.decode_string(payload, pos)
                area_id, pos = Codec.decode_int32(payload, pos)
                time_zone, pos = Codec.decode_int32(payload, pos)
                
                result = {
                    "success": True,
                    "role_id": role_id,
                    "account": account,
                    "area_id": area_id,
                    "time_zone": time_zone
                }
                print(f"✅ 登录成功: role_id={role_id}, account={account}")
            
            self.complete_command("login", result)
            
        except Exception as e:
            print(f"❌ 解析登录应答失败: {e}")
            self.complete_command("login", {"success": False, "error": str(e)})
