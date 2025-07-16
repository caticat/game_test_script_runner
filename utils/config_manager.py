# 配置管理工具 - 统一配置加载

import os
import yaml
from typing import Dict, Any

class ConfigManager:
    """配置管理类，单例模式"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        config_path = os.path.join(os.path.dirname(__file__), "../config/config.yml")
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                self._config = yaml.safe_load(file)
        except FileNotFoundError:
            print(f"配置文件未找到: {config_path}")
            self._config = self._get_default_config()
        except yaml.YAMLError as e:
            print(f"配置文件格式错误: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "login": {
                "url": "http://127.0.0.1:8000",
                "host": "127.0.0.1",
                "port": 8031
            },
            "gate": {
                "host": "127.0.0.1",
                "port": 5001
            }
        }
    
    def get_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self._config
    
    def get_login_config(self) -> Dict[str, Any]:
        """获取登录服务器配置"""
        return self._config.get("login", {})
    
    def get_gate_config(self) -> Dict[str, Any]:
        """获取网关服务器配置"""
        return self._config.get("gate", {})
    
    def get_proto_path(self) -> str:
        """获取Proto文件路径"""
        # 优先使用新的路径配置
        paths = self._config.get("paths", {})
        proto_path = paths.get("proto_path")
        if proto_path:
            return proto_path
        
        # 向后兼容旧配置
        return self._config.get("proto_path", 
                               os.getenv("PROTO_PYTHON_PATH", "Q:/kof/dev/proto_python"))
    
    def get_scripts_path(self) -> str:
        """获取脚本文件夹路径"""
        # 优先使用新的路径配置
        paths = self._config.get("paths", {})
        scripts_path = paths.get("scripts_path")
        if scripts_path:
            return scripts_path
        
        # 向后兼容旧配置
        return self._config.get("scripts_path", 
                               os.getenv("SCRIPTS_PATH", "scripts"))
    
    def get_tests_path(self) -> str:
        """获取测试文件夹路径"""
        paths = self._config.get("paths", {})
        return paths.get("tests_path", "tests")
    
    def get_docs_path(self) -> str:
        """获取文档文件夹路径"""
        paths = self._config.get("paths", {})
        return paths.get("docs_path", "docs")
    
    def reload_config(self):
        """重新加载配置"""
        self._config = None
        self._load_config()

# 全局配置管理器实例
config_manager = ConfigManager()

# 兼容性函数，保持向后兼容
def load_config() -> Dict[str, Any]:
    """加载配置文件（兼容旧版本API）"""
    return config_manager.get_config()
