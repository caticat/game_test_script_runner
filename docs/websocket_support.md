# WebSocket 支持功能说明

## 🎯 功能概述

协议测试工具现在支持 WebSocket 连接功能，可以通过 `connect_gate` 命令连接到 WebSocket 服务器。

## 🔧 使用方法

### 1. WebSocket 连接

当 `host` 参数以 `ws://` 或 `wss://` 开头时，系统会自动识别为 WebSocket 连接：

```json
{
  "cmd": "connect_gate",
  "host": "wss://127.0.0.1/gateway",
  "comment": "连接到 WebSocket 网关"
}
```

### 2. TCP 连接（原有功能）

普通的 TCP 连接方式保持不变：

```json
{
  "cmd": "connect_gate",
  "host": "127.0.0.1",
  "port": 5001,
  "comment": "连接到 TCP 网关"
}
```

### 3. 自动选择连接方式

`connect_gate` 命令会根据 `host` 参数自动判断连接方式：

- `host` 以 `ws://` 或 `wss://` 开头 → WebSocket 连接
- 其他情况 → TCP 连接

## 📋 返回结果

### WebSocket 连接结果

```json
{
  "connected": true,
  "url": "wss://127.0.0.1/gateway",
  "type": "websocket"
}
```

### TCP 连接结果

```json
{
  "connected": true,
  "host": "127.0.0.1",
  "port": 5001,
  "type": "tcp"
}
```

## 🧪 测试示例

### 完整测试脚本

```json
[
  {
    "cmd": "print",
    "message": "=== WebSocket 连接测试 ===",
    "comment": "开始测试"
  },
  {
    "cmd": "connect_gate",
    "host": "wss://127.0.0.1/gateway",
    "comment": "连接到 WebSocket 网关"
  },
  {
    "cmd": "print",
    "message": "连接状态: ret[\"connect_gate\"][\"connected\"]",
    "comment": "显示连接状态"
  },
  {
    "cmd": "print",
    "message": "连接类型: ret[\"connect_gate\"][\"type\"]",
    "comment": "显示连接类型"
  },
  {
    "cmd": "print",
    "message": "WebSocket URL: ret[\"connect_gate\"][\"url\"]",
    "comment": "显示 WebSocket URL"
  }
]
```

### 混合连接测试

```json
[
  {
    "cmd": "connect_gate",
    "host": "wss://127.0.0.1/gateway",
    "comment": "WebSocket 连接"
  },
  {
    "cmd": "print",
    "message": "WebSocket 连接: ret[\"connect_gate\"][\"type\"]",
    "comment": "显示连接类型"
  },
  {
    "cmd": "connect_gate",
    "host": "127.0.0.1",
    "port": 5001,
    "comment": "TCP 连接"
  },
  {
    "cmd": "print",
    "message": "TCP 连接: ret[\"connect_gate\"][\"type\"]",
    "comment": "显示连接类型"
  }
]
```

## 🛠️ 技术实现

### 1. 自动识别机制

```python
def execute(self, host: str = "", port: int = 0):
    # 判断是否为 WebSocket URL
    if host.startswith(('ws://', 'wss://')):
        return self._connect_websocket(host)
    else:
        return self._connect_tcp(host, port)
```

### 2. WebSocket 客户端

当前实现为模拟版本，支持：
- ✅ 连接状态检测
- ✅ 基本的消息发送接口
- ✅ 处理器注册接口
- ✅ 连接断开功能

### 3. 兼容性保证

- 完全兼容原有的 TCP 连接功能
- 相同的接口和返回格式
- 透明的连接方式切换

## 📦 依赖要求

WebSocket 功能需要安装额外的依赖：

```bash
pip install websockets
```

已添加到 `requirements.txt`：
```
websockets==13.1
```

## 🔄 开发状态

### 当前状态（v1.0）

- ✅ 基本的 WebSocket 连接识别
- ✅ 模拟的 WebSocket 客户端实现
- ✅ 与 TCP 连接的无缝切换
- ✅ 完整的测试用例

### 未来规划（v2.0）

- 🔄 真实的 WebSocket 连接实现
- 🔄 WebSocket 消息的收发功能
- 🔄 WebSocket 心跳检测
- 🔄 WebSocket 重连机制
- 🔄 WebSocket 子协议支持

## 🎯 使用场景

### 1. 游戏服务器连接

```json
{
  "cmd": "connect_gate",
  "host": "wss://game-server.example.com/gateway",
  "comment": "连接到游戏服务器"
}
```

### 2. 开发环境测试

```json
{
  "cmd": "connect_gate",
  "host": "ws://localhost:8080/websocket",
  "comment": "连接到本地开发服务器"
}
```

### 3. 生产环境部署

```json
{
  "cmd": "connect_gate",
  "host": "wss://127.0.0.1/gateway",
  "comment": "连接到生产环境"
}
```

## 📝 注意事项

1. **安全性**：使用 `wss://` 而不是 `ws://` 以确保连接安全
2. **超时处理**：WebSocket 连接会有超时机制
3. **错误处理**：连接失败会返回详细的错误信息
4. **兼容性**：完全兼容原有的 TCP 连接功能

## 🔧 故障排除

### 1. 依赖问题

如果遇到 `ModuleNotFoundError: No module named 'websockets'`：

```bash
pip install websockets
```

### 2. 连接失败

检查 WebSocket URL 是否正确：
- 确保使用正确的协议 (`ws://` 或 `wss://`)
- 确保服务器地址和端口正确
- 检查网络连接状态

### 3. 功能限制

当前版本为模拟实现，如需完整功能请关注后续更新。

## ⚠️ 常见问题和解决方案

### SSL 连接错误

**问题**：`SSL: WRONG_VERSION_NUMBER` 错误
**原因**：使用 `wss://` 连接到不支持SSL的服务器
**解决方案**：
- 对于本地开发服务器，使用 `ws://` 而非 `wss://`
- 确认服务器是否支持SSL连接

**示例**：
```json
// ❌ 错误：本地服务器通常不支持SSL
{
  "cmd": "connect_gate",
  "host": "wss://127.0.0.1:5001"
}

// ✅ 正确：本地服务器使用非加密连接
{
  "cmd": "connect_gate",
  "host": "ws://127.0.0.1:5001"
}
```

### 连接被拒绝错误

**问题**：`Connection refused` 错误
**原因**：目标服务器未运行或端口不正确
**解决方案**：
- 确认服务器正在运行
- 检查端口号是否正确
- 检查防火墙设置

### 主机名解析错误

**问题**：`Name or service not known` 错误
**原因**：无法解析域名或IP地址
**解决方案**：
- 检查URL拼写是否正确
- 确认网络连接正常
- 对于内网服务器，确认DNS设置

## 🔧 协议支持

- **WebSocket**：初步支持，待完善
- **TCP**：完全支持

这个 WebSocket 支持功能大大扩展了协议测试工具的适用范围，使其能够支持现代的 WebSocket 通信协议！
