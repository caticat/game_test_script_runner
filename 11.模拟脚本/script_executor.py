# 模拟脚本执行器

import sys
import os
import asyncio
import threading
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.utils import Utils
from utils.base_tcp_client import BaseTCPClient
from utils.tcp_client import SocketClient
from utils.protocol_codec import Codec

external_path = "Q:/kof/dev/proto_python"
sys.path.append(external_path)

@dataclass
class ScriptCommand:
    """脚本命令数据类"""
    cmd: str
    params: Dict[str, Any]
    timeout: int = 30  # 默认超时时间30秒

class ScriptExecutor:
    """脚本执行器"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {}  # 存储每个命令的返回结果
        self.command_functions: Dict[str, Callable] = {}  # 命令函数映射
        self.waiting_commands: Dict[str, threading.Event] = {}  # 等待命令完成的事件
        self.current_client: Optional[SocketClient] = None
        self.executor = ThreadPoolExecutor(max_workers=1)
        
        # 注册可用的命令函数
        self._register_commands()
    
    def _register_commands(self):
        """注册可用的命令函数"""
        # HTTP认证相关
        self.command_functions["auth"] = self._auth_command
        self.command_functions["select_area"] = self._select_area_command
        
        # TCP连接相关
        self.command_functions["connect_gate"] = self._connect_gate_command
        self.command_functions["connect_login"] = self._connect_login_command
        
        # 游戏服相关
        self.command_functions["login"] = self._login_command
        
        # 工具函数
        self.command_functions["sleep"] = self._sleep_command
        self.command_functions["print"] = self._print_command
    
    def _resolve_value(self, value: Any) -> Any:
        """解析参数值，支持从之前的返回结果中获取"""
        if isinstance(value, str) and value.startswith("ret["):
            # 格式: ret["command"]["field"]
            try:
                # 移除 ret[ 前缀和最后的 ]
                content = value[4:-1]  # 去掉 "ret[" 和 "]"
                
                # 分割路径，支持多级访问
                parts = []
                current = ""
                in_quotes = False
                quote_char = None
                
                i = 0
                while i < len(content):
                    char = content[i]
                    
                    if char in ['"', "'"] and (i == 0 or content[i-1] != '\\'):
                        if not in_quotes:
                            in_quotes = True
                            quote_char = char
                        elif char == quote_char:
                            in_quotes = False
                            quote_char = None
                    elif char == '[' and not in_quotes:
                        if current:
                            parts.append(current.strip('"\''))
                            current = ""
                    elif char == ']' and not in_quotes:
                        if current:
                            parts.append(current.strip('"\''))
                            current = ""
                    elif char != '[' and char != ']':
                        current += char
                    
                    i += 1
                
                if current:
                    parts.append(current.strip('"\''))
                
                # 获取值
                if len(parts) >= 1:
                    cmd_name = parts[0]
                    result = self.results.get(cmd_name)
                    
                    if result is None:
                        print(f"⚠️  命令 '{cmd_name}' 的结果不存在")
                        return None
                    
                    # 如果有字段名，则获取字段
                    if len(parts) >= 2:
                        field_name = parts[1]
                        if isinstance(result, dict):
                            return result.get(field_name)
                        else:
                            print(f"⚠️  命令 '{cmd_name}' 的结果不是字典类型")
                            return None
                    else:
                        return result
                        
            except Exception as e:
                print(f"⚠️  解析返回值失败: {value}, 错误: {e}")
                return value
        return value
    
    def _resolve_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """解析所有参数"""
        resolved = {}
        for key, value in params.items():
            resolved[key] = self._resolve_value(value)
        return resolved
    
    async def execute_script(self, scripts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """执行脚本"""
        print("🚀 开始执行脚本...")
        print(f"📋 共有 {len(scripts)} 个命令")
        print("=" * 50)
        
        for i, script_dict in enumerate(scripts, 1):
            try:
                # 解析命令
                cmd = script_dict["cmd"]
                params = script_dict.copy()
                del params["cmd"]
                timeout = params.pop("timeout", 30)
                comment = params.pop("comment", None)  # 提取注释字段，不传递给命令
                
                command = ScriptCommand(cmd=cmd, params=params, timeout=timeout)
                
                # 显示注释（如果有）
                if comment:
                    print(f"💬 {comment}")
                
                print(f"🔄 [{i}/{len(scripts)}] 执行命令: {cmd}")
                
                # 解析参数
                resolved_params = self._resolve_params(command.params)
                print(f"📝 参数: {resolved_params}")
                
                # 执行命令
                result = await self._execute_command(command, resolved_params)
                
                # 对于需要等待应答的命令，使用应答处理器设置的结果
                if command.cmd in ["auth", "select_area", "login"]:
                    final_result = self.results.get(command.cmd)
                    if final_result is not None:
                        result = final_result
                
                # 保存结果
                self.results[cmd] = result
                print(f"✅ 命令 {cmd} 执行完成")
                
                if result:
                    print(f"📤 返回结果: {result}")
                
                print("-" * 30)
                
            except Exception as e:
                print(f"❌ 命令 {cmd} 执行失败: {e}")
                print("-" * 30)
                # 根据需要决定是否继续执行
                # break  # 如果需要在出错时停止，取消注释这行
        
        print("🎉 脚本执行完成!")
        return self.results
    
    async def _execute_command(self, command: ScriptCommand, params: Dict[str, Any]) -> Any:
        """执行单个命令"""
        if command.cmd not in self.command_functions:
            raise ValueError(f"未知命令: {command.cmd}")
        
        func = self.command_functions[command.cmd]
        
        # 创建等待事件
        event = threading.Event()
        self.waiting_commands[command.cmd] = event
        
        try:
            # 在线程池中执行命令
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, 
                self._execute_command_sync, 
                func, 
                params
            )
            
            # 等待命令完成（如果需要）
            if command.cmd in ["auth", "select_area", "login"]:
                await asyncio.wait_for(
                    asyncio.to_thread(event.wait),
                    timeout=command.timeout
                )
            
            return result
            
        finally:
            # 清理等待事件
            if command.cmd in self.waiting_commands:
                del self.waiting_commands[command.cmd]
    
    def _execute_command_sync(self, func: Callable, params: Dict[str, Any]) -> Any:
        """同步执行命令"""
        return func(**params)
    
    def _complete_command(self, cmd: str, result: Any = None):
        """标记命令完成"""
        if result is not None:
            self.results[cmd] = result
        
        if cmd in self.waiting_commands:
            self.waiting_commands[cmd].set()
    
    # ========== 命令实现 ==========
    
    def _auth_command(self, user_name: str = "q1", channel: str = "dev") -> Dict[str, Any]:
        """HTTP认证命令"""
        payload = {
            "Channel": channel,
            "Code": user_name,
        }
        result = Utils.send_to_login("auth_step", payload)
        self._complete_command("auth", result)
        return result
    
    def _select_area_command(self, open_id: str, area_id: int = 1, login_token: str = "") -> Dict[str, Any]:
        """选服命令"""
        payload = {
            "OpenId": open_id,
            "AreaId": area_id,
            "LoginToken": login_token,
        }
        result = Utils.send_to_login("select_area", payload)
        self._complete_command("select_area", result)
        return result
    
    def _connect_gate_command(self, **kwargs) -> Dict[str, Any]:
        """连接网关"""
        # 优先从select_area返回值中获取网关信息
        select_area_result = self.results.get("select_area")
        if select_area_result and "GateHost" in select_area_result and "GateTcpPort" in select_area_result:
            host = select_area_result["GateHost"]
            port = select_area_result["GateTcpPort"]
        else:
            # 如果没有select_area结果，使用配置文件中的默认值
            print("⚠️  未找到select_area返回的网关信息，使用配置文件默认值")
            from utils.config_manager import config_manager
            cfg = config_manager.get_config()
            host = cfg["gate"]["host"]
            port = cfg["gate"]["port"]
        
        self.current_client = SocketClient(host, port)
        self.current_client.dst_gate = True
        self.current_client.connect()
        
        print(f"✅ 已连接到网关: {host}:{port}")
        return {"connected": True, "host": host, "port": port}
    
    def _connect_login_command(self, **kwargs) -> Dict[str, Any]:
        """连接登录服"""
        from utils.config_manager import config_manager
        cfg = config_manager.get_config()
        
        host = cfg["login"]["host"]
        port = cfg["login"]["port"]
        
        self.current_client = SocketClient(host, port)
        self.current_client.dst_gate = False
        self.current_client.connect()
        
        print(f"✅ 已连接到登录服: {host}:{port}")
        return {"connected": True, "host": host, "port": port}
    
    def _login_command(self, signature: str = "", role_id: int = 0, user_name: str = "", 
                      area_id: int = 1, channel: str = "dev", platform: str = "windows") -> Dict[str, Any]:
        """游戏服登录命令"""
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
            print("⚠️  无法导入协议ID，使用默认值")
            login_id = 1  # 默认登录协议ID
        
        # 构建登录数据包
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
        
        # 注册登录应答处理器
        self.current_client.regist_handler(login_id, self._login_ack_handler)
        
        # 发送登录请求
        self.current_client.send(login_id, buff)
        print(f"📤 发送登录请求: role_id={role_id}, user_name={user_name}")
        
        # 不返回临时结果，等待登录应答处理器设置真正的结果
        return None
    
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
            
            self._complete_command("login", result)
            
        except Exception as e:
            print(f"❌ 解析登录应答失败: {e}")
            self._complete_command("login", {"success": False, "error": str(e)})
    
    def _sleep_command(self, seconds: float = 1.0) -> Dict[str, Any]:
        """睡眠命令"""
        print(f"😴 睡眠 {seconds} 秒...")
        time.sleep(seconds)
        return {"slept": seconds}
    
    def _print_command(self, message: str = "", **kwargs) -> Dict[str, Any]:
        """打印命令"""
        # 解析message中的返回值引用
        resolved_message = self._resolve_message_content(message)
        print(f"📢 {resolved_message}")
        return {"printed": resolved_message}
    
    def _resolve_message_content(self, message: str) -> str:
        """解析字符串中的返回值引用"""
        import re
        
        # 使用正则表达式找到所有的 ret["xxx"]["yyy"] 模式
        pattern = r'ret\["([^"]+)"\]\["([^"]+)"\]'
        
        def replace_func(match):
            cmd_name = match.group(1)
            field_name = match.group(2)
            
            result = self.results.get(cmd_name)
            if result is None:
                return f"[命令'{cmd_name}'结果不存在]"
            
            if isinstance(result, dict):
                value = result.get(field_name)
                if value is None:
                    return f"[字段'{field_name}'不存在]"
                return str(value)
            else:
                return f"[命令'{cmd_name}'结果不是字典]"
        
        # 替换所有匹配的部分
        resolved = re.sub(pattern, replace_func, message)
        
        # 也处理简单的 ret["xxx"] 模式（只有命令名，没有字段）
        simple_pattern = r'ret\["([^"]+)"\](?!\[)'
        
        def simple_replace_func(match):
            cmd_name = match.group(1)
            result = self.results.get(cmd_name)
            if result is None:
                return f"[命令'{cmd_name}'结果不存在]"
            return str(result)
        
        resolved = re.sub(simple_pattern, simple_replace_func, resolved)
        
        return resolved

    def close(self):
        """关闭连接"""
        if self.current_client:
            self.current_client.stop()
            self.current_client = None
        
        self.executor.shutdown(wait=True)

# 使用示例
async def main():
    """主函数示例"""
    executor = ScriptExecutor()
    
    # 示例脚本
    scripts = [
        {"cmd": "auth", "user_name": "q1", "channel": "dev"},
        {"cmd": "select_area", "open_id": "ret[\"auth\"][\"OpenId\"]", "area_id": 1, "login_token": "ret[\"auth\"][\"LoginToken\"]"},
        {"cmd": "connect_gate"},
        {"cmd": "login", "signature": "ret[\"select_area\"][\"Signature\"]", "role_id": 903, "user_name": "q1"},
        {"cmd": "sleep", "seconds": 2.0},
        {"cmd": "print", "message": "脚本执行完成!"}
    ]
    
    try:
        results = await executor.execute_script(scripts)
        print("\n🎯 最终结果:")
        Utils.print_dict(results)
    finally:
        executor.close()

if __name__ == "__main__":
    asyncio.run(main())
