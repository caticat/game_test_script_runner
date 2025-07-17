"""
调试工具模块
"""
from utils.config_manager import config_manager

def debug_print(message: str):
    """
    调试输出函数
    
    Args:
        message: 要输出的调试信息
    """
    # 每次调用时重新检查配置，确保实时生效
    if config_manager.is_debug_enabled():
        print(message)

def packet_debug_print(message: str):
    """
    数据包调试输出函数
    
    Args:
        message: 要输出的数据包调试信息
    """
    # 只有在开启数据包详情时才显示
    if config_manager.is_debug_enabled() and config_manager.is_packet_details_enabled():
        print(message)
