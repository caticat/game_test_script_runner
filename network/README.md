# 网络模块重构说明

## 模块结构

```
network/
├── clients/          # 网络客户端模块
│   ├── __init__.py
│   ├── base_client.py     # 异步客户端基类
│   ├── tcp_client.py      # TCP客户端
│   └── websocket_client.py # WebSocket客户端
├── protocol/         # 协议编解码模块
│   ├── __init__.py
│   └── codec.py           # 协议编解码器
└── __init__.py
```

## 重构内容

### 1. 网络模块拆分
- **从 `utils/` 移动到 `network/`**：将网络相关代码从通用工具模块中分离，提高代码组织性
- **clients/ 目录**：包含所有网络客户端（TCP、WebSocket）
- **protocol/ 目录**：包含协议编解码相关功能

### 2. 异步模型统一
- **纯异步**：所有客户端都使用 `asyncio`，移除了线程和同步包装器
- **统一接口**：`BaseClient` 提供统一的异步接口
- **队列机制**：使用 `asyncio.Queue` 进行异步消息传递

### 3. 命令层保持不变
- **位置不变**：网络连接命令仍在 `src/script_runner/commands/network_commands.py`
- **原因**：命令需要访问脚本执行上下文、结果缓存、配置管理等业务逻辑
- **职责清晰**：底层网络技术在 `network/`，业务命令在 `script_runner/commands/`

## 导入方式

### 推荐的导入方式

```python
# 导入网络客户端
from network.clients import BaseClient, SocketClient, WebSocketClient

# 导入协议编解码器
from network.protocol import Codec

# 或者从顶级包导入
from network import BaseClient, SocketClient, WebSocketClient, Codec
```

### 业务命令
```python
# 网络连接命令仍在原位置
from src.script_runner.commands.network_commands import ConnectGateCommand
```

## 清理内容

### 从 `utils/` 移除的文件
- `base_client.py` → `network/clients/base_client.py`
- `tcp_client.py` → `network/clients/tcp_client.py`
- `websocket_client.py` → `network/clients/websocket_client.py`
- `protocol_codec.py` → `network/protocol/codec.py`
- `async_base_client.py` （已删除，功能合并到 `base_client.py`）

### 保留在 `utils/` 的文件
- `config_manager.py` - 配置管理
- `debug_utils.py` - 调试工具
- `utils.py` - 通用工具函数

## 更新的导入路径

所有使用网络模块的文件都已更新导入路径：
- `src/script_runner/commands/network_commands.py`
- `src/script_runner/commands/game_commands.py`
- `src/gateway/01.登录.py`
- `src/auth_server/02.封禁账号.py`
- `src/auth_server/03.模拟角色数据变更.py`

## 向后兼容性

- `utils/__init__.py` 已移除网络相关类的导出
- 所有导入都指向新的 `network/` 模块
- 不再存在重复的网络代码

## 总结

这次重构的核心目标：
1. **职责分离**：网络技术层（`network/`）与业务逻辑层（`script_runner/commands/`）分离
2. **异步统一**：所有网络操作都使用纯异步模型
3. **消除冗余**：移除重复的网络代码，保持单一来源
4. **结构清晰**：模块职责明确，便于维护和扩展
