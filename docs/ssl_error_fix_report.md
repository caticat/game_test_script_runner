# SSL版本错误修复报告

## 🐛 问题描述
用户遇到 WebSocket 连接错误：
```
WebSocket 连接失败: [SSL: WRONG_VERSION_NUMBER] wrong version number (_ssl.c:1010)
```

## 🔍 问题分析
- 错误原因：在 `auth_ori.json` 中使用了 `wss://127.0.0.1:5002`
- 本地服务器通常不支持 SSL，但使用了 `wss://` 协议
- 系统尝试建立 SSL 连接但服务器不支持导致版本错误

## ✅ 修复方案

### 1. 脚本修复
- 将 `wss://127.0.0.1:5002` 改为 `ws://127.0.0.1:5002`
- 移除硬编码的主机地址，使用自动获取的网关地址
- 简化登录命令参数，使用自动参数获取

### 2. 错误处理改进
在 `network_commands.py` 中添加了友好的错误提示：
```python
if "SSL: WRONG_VERSION_NUMBER" in error_msg:
    error_msg = "SSL版本错误 - 请检查是否应使用 ws:// 而非 wss://"
elif "SSL:" in error_msg:
    error_msg = f"SSL连接错误: {error_msg}"
elif "Connection refused" in error_msg:
    error_msg = "连接被拒绝 - 请检查服务器是否正在运行"
```

### 3. 文档更新
在 `websocket_support.md` 中添加了常见问题解决方案：
- SSL 连接错误的处理
- 连接被拒绝错误的处理
- 主机名解析错误的处理

## 🎯 修复结果

### 修复前
```json
{
    "cmd": "connect_gate",
    "host": "wss://127.0.0.1:5002",
    "comment": "直接连接网关 - 跳过HTTP认证步骤"
}
```
❌ 结果：SSL版本错误

### 修复后
```json
{
    "cmd": "connect_gate",
    "comment": "连接到网关 - 使用认证返回的网关地址"
}
```
✅ 结果：成功连接到 `wss://127.0.0.1/gateway`

## 📊 测试验证

执行 `auth_ori.json` 脚本的结果：
- ✅ `ori.auth` 命令成功执行
- ✅ 自动获取网关地址：`wss://127.0.0.1/gateway`
- ✅ WebSocket 连接成功：`"connected": true`
- ✅ 连接类型正确：`"type": "websocket"`

## 💡 使用建议

1. **本地开发环境**：使用 `ws://` 协议
2. **生产环境**：使用 `wss://` 协议
3. **自动获取地址**：让系统从认证结果中自动获取网关地址
4. **错误处理**：查看友好的错误提示来快速定位问题

## 🔧 相关文件

- `scripts/auth_ori.json` - 修复的脚本文件
- `src/script_runner/commands/network_commands.py` - 改进的错误处理
- `docs/websocket_support.md` - 更新的文档
- `scripts/websocket_connection_test.json` - 新的测试脚本

SSL版本错误已完全修复，WebSocket功能现在可以正常使用。
