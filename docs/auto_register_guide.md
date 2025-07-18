# 协议自动注册机制

## 概述

为了简化协议处理函数的注册过程，我们实现了自动注册机制。该机制会自动扫描模块中的协议处理函数，并将它们注册到客户端中。

## 工作原理

自动注册机制通过以下步骤工作：

1. **扫描模块函数**：扫描当前模块中所有以 `_ack` 结尾的函数
2. **查找协议ID**：对于每个 `*_ack` 函数，查找对应的 `*_id` 变量
3. **自动注册**：如果找到对应的协议ID，自动调用 `client.regist_handler(proto_id, handler_func)`

## 使用方法

### 1. 导入自动注册工具

```python
from network.protocol.registry import auto_register_handlers
```

### 2. 定义协议处理函数

按照命名约定定义协议ID和处理函数：

```python
# 协议ID定义
login_id = ProtoId.C2G_Login
ban_id = ProtoId.A2L_BanAccount

# 协议处理函数定义
def login_ack(seq: int, payload: bytes) -> None:
    """登录应答处理"""
    print("登录成功")

def ban_ack(seq: int, payload: bytes) -> None:
    """封禁应答处理"""
    print("封禁完成")
```

### 3. 调用自动注册

在客户端连接成功后，调用自动注册函数：

```python
# 创建客户端并连接
client = SocketClient(host, port)
await client.connect()

# 自动注册协议处理函数
current_module = sys.modules[__name__]
auto_register_handlers(client, current_module)
```

## 命名约定

- **协议ID变量**：`*_id` 格式，例如 `login_id`、`ban_id`
- **处理函数**：`*_ack` 格式，例如 `login_ack`、`ban_ack`
- **请求函数**：`*_req` 格式，例如 `login_req`、`ban_req`（当前仅用于命令发现）

## 示例

```python
# 完整示例
import sys
from network.clients.tcp_client import SocketClient
from network.protocol.registry import auto_register_handlers
from proto_id_pb2 import ProtoId

# 定义协议ID
login_id = ProtoId.C2G_Login

# 定义处理函数
def login_ack(seq: int, payload: bytes) -> None:
    print("登录成功")

async def main():
    client = SocketClient("localhost", 8080)
    await client.connect()
    
    # 自动注册所有 *_ack 函数
    current_module = sys.modules[__name__]
    auto_register_handlers(client, current_module)
    
    # 现在可以正常使用客户端
    # 当收到 login_id 协议时，会自动调用 login_ack 函数
```

## 优势

1. **减少重复代码**：无需在每个文件中重复实现注册逻辑
2. **自动化**：无需手动调用 `client.regist_handler`
3. **统一管理**：所有注册逻辑集中在 `network.protocol.registry` 模块中
4. **易于维护**：只需按照命名约定定义函数即可

## 注意事项

- 确保协议ID变量和处理函数的命名遵循约定
- 如果找不到对应的协议ID变量，会输出警告信息
- 自动注册仅适用于 `*_ack` 应答处理函数
- 请求函数 `*_req` 仅用于命令发现，不会自动注册
