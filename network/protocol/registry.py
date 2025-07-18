# 协议自动注册工具模块

import inspect
from typing import Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from network.clients.tcp_client import SocketClient


def auto_register_handlers(client: 'SocketClient', current_module: Any) -> int:
    """
    自动注册协议处理函数
    
    Args:
        client: SocketClient 实例
        current_module: 当前模块，通常是 sys.modules[__name__]
        
    Returns:
        int: 注册的处理器数量
    """
    registered_count = 0
    
    # 扫描模块中的所有函数
    for name, obj in inspect.getmembers(current_module, inspect.isfunction):
        if name.endswith('_ack'):
            # 注册应答处理器
            key = name[:-4]  # 去掉 '_ack' 后缀
            id_var_name = f'{key}_id'
            proto_id = getattr(current_module, id_var_name, None)
            if proto_id is not None:
                client.regist_handler(proto_id, obj)
                print(f"🔧 自动注册协议处理函数: {id_var_name}={proto_id} -> {name}")
                registered_count += 1
            else:
                print(f"⚠️ 未找到变量 {id_var_name}，无法注册 {name}")
    
    print(f"✅ 已自动注册 {registered_count} 个协议处理函数")
    return registered_count


def auto_register_commands_and_handlers(client: 'SocketClient', current_module: Any) -> tuple[int, int]:
    """
    自动注册命令和应答处理器 (扩展版本)
    
    Args:
        client: SocketClient 实例
        current_module: 当前模块，通常是 sys.modules[__name__]
        
    Returns:
        tuple[int, int]: (注册的命令数量, 注册的处理器数量)
    """
    command_count = 0
    handler_count = 0
    
    # 扫描模块中的所有函数
    for name, obj in inspect.getmembers(current_module, inspect.isfunction):
        if name.endswith('_req'):
            # 注册请求命令（预留功能）
            key = name[:-4]  # 去掉 '_req' 后缀
            print(f"🔧 发现命令函数: {name} (key: {key})")
            command_count += 1
        elif name.endswith('_ack'):
            # 注册应答处理器
            key = name[:-4]  # 去掉 '_ack' 后缀
            id_var_name = f'{key}_id'
            proto_id = getattr(current_module, id_var_name, None)
            if proto_id is not None:
                client.regist_handler(proto_id, obj)
                print(f"🔧 自动注册协议处理函数: {id_var_name}={proto_id} -> {name}")
                handler_count += 1
            else:
                print(f"⚠️ 未找到变量 {id_var_name}，无法注册 {name}")
    
    print(f"✅ 已自动注册 {command_count} 个命令函数和 {handler_count} 个协议处理函数")
    return command_count, handler_count
