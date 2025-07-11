# 统一工具模块 - 整合所有常用功能

import json
import re
import urllib.parse
import requests
from datetime import datetime, timezone
from typing import Any, Dict, List, Union, Optional


class Utils:
    """统一工具类 - 包含所有常用功能，无兼容性代码"""
    
    # ========== 格式化相关 ==========
    @staticmethod
    def print_dict(data: dict, prefix: str = ""):
        """美化打印字典"""
        if prefix:
            print(prefix)
        print(json.dumps(data, indent=4, ensure_ascii=False))
    
    @staticmethod
    def dict_to_json(data: dict, indent: int = 4) -> str:
        """将字典转换为格式化的JSON字符串"""
        return json.dumps(data, indent=indent, ensure_ascii=False)
    
    @staticmethod
    def decode_text(data: Any) -> Any:
        """递归解码字典中的文本"""
        if isinstance(data, dict):
            return {k: Utils.decode_text(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [Utils.decode_text(item) for item in data]
        elif isinstance(data, str):
            # 尝试修复URL编码
            if re.search(r'%[0-9A-Fa-f]{2}', data):
                try:
                    data = urllib.parse.unquote(data)
                except Exception:
                    pass
            
            # 尝试修复误编码的UTF-8
            try:
                decoded = data.encode('latin1').decode('utf-8')
                if any('\u4e00' <= ch <= '\u9fff' for ch in decoded):
                    data = decoded
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass
            
            return data
        else:
            return data
    
    # ========== 时间相关 ==========
    @staticmethod
    def str_to_timestamp(time_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> int:
        """将时间字符串转换为Unix时间戳"""
        dt = datetime.strptime(time_str, format_str)
        return int(dt.timestamp())
    
    @staticmethod
    def timestamp_to_str(timestamp: Union[int, float], 
                        format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """将Unix时间戳转换为时间字符串"""
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime(format_str)
    
    @staticmethod
    def now_timestamp() -> int:
        """获取当前Unix时间戳"""
        return int(datetime.now().timestamp())
    
    @staticmethod
    def now_str(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """获取当前时间字符串"""
        return datetime.now().strftime(format_str)
    
    @staticmethod
    def utc_now_timestamp() -> int:
        """获取当前UTC时间戳"""
        return int(datetime.now(timezone.utc).timestamp())
    
    @staticmethod
    def utc_now_str(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """获取当前UTC时间字符串"""
        return datetime.now(timezone.utc).strftime(format_str)
    
    # ========== HTTP相关 ==========
    @staticmethod
    def post_json(url: str, data: Union[Dict, Any], timeout: int = 3) -> Dict[str, Any]:
        """发送JSON POST请求"""
        headers = {"Content-Type": "application/json"}
        
        # 序列化数据
        json_str = json.dumps(data, separators=(',', ':'))
        
        try:
            response = requests.post(
                url, 
                data=json_str.encode('utf-8'), 
                headers=headers, 
                timeout=timeout
            )
            
            # 解析响应
            response_data = response.json()
            return Utils.decode_text(response_data)
            
        except requests.exceptions.Timeout:
            return {"error": "请求超时"}
        except requests.exceptions.RequestException as e:
            return {"error": f"请求失败: {str(e)}"}
        except json.JSONDecodeError:
            return {"error": "响应不是有效的JSON", "response": response.text}
    
    @staticmethod
    def get_json(url: str, params: Optional[Dict] = None, timeout: int = 3) -> Dict[str, Any]:
        """发送GET请求并返回JSON"""
        try:
            response = requests.get(url, params=params, timeout=timeout)
            response_data = response.json()
            return Utils.decode_text(response_data)
        except requests.exceptions.Timeout:
            return {"error": "请求超时"}
        except requests.exceptions.RequestException as e:
            return {"error": f"请求失败: {str(e)}"}
        except json.JSONDecodeError:
            return {"error": "响应不是有效的JSON", "response": response.text}
    
    @staticmethod
    def send_to_login(action: str, data: dict) -> dict:
        """发送数据到登录服务器"""
        from .config_manager import config_manager
        
        config = config_manager.get_config()
        base_url = config.get("login", {}).get("url", "")
        if not base_url:
            return {"error": "登录服务器URL未配置"}
        
        # 构建完整的URL
        full_url = f"{base_url.rstrip('/')}/{action}"
        return Utils.post_json(full_url, data)
