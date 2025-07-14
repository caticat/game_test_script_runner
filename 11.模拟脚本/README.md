# 模拟脚本工具

## 🎯 功能简介

模拟脚本工具允许您按顺序执行测试命令，支持参数的动态引用和异步等待。非常适合自动化测试游戏服务器的登录流程。

## 📁 文件结构

```
11.模拟脚本/
├── main.py                # 主入口文件
├── script_editor.py       # 交互式脚本编辑器
├── script_executor.py     # 脚本执行引擎
├── quick_runner.py        # 快速运行器
├── examples/              # 示例脚本目录
│   ├── login_flow.json    # 完整登录流程
│   ├── auth_only.json     # 仅认证和选服
│   └── direct_login.json  # 直接登录
└── README.md              # 说明文档
```

## 🚀 快速开始

### 1. 运行主程序

```bash
python main.py
```

### 2. 使用快速运行器

```bash
python quick_runner.py
```

### 3. 直接运行脚本文件

```bash
python quick_runner.py login_flow.json
```

## 🔧 可用命令

| 命令 | 描述 | 参数 | 自动获取 |
|------|------|------|----------|
| `auth` | HTTP认证登录 | user_name, channel | - |
| `select_area` | 选择游戏区域 | open_id, area_id, login_token | - |
| `connect_gate` | 连接游戏网关 | 无 | 自动从select_area获取GateHost和GateTcpPort |
| `connect_login` | 连接登录服务器 | 无 | 使用配置文件 |
| `login` | 游戏服登录 | signature, role_id, user_name, area_id, channel, platform | signature从select_area获取，role_id从select_area获取，user_name从auth获取 |
| `sleep` | 等待指定时间 | seconds | - |
| `print` | 输出调试信息 | message | - |

## 🎯 自动参数获取功能

### connect_gate 命令
- 自动从 `select_area` 返回值中获取 `GateHost` 和 `GateTcpPort`
- 如果没有 `select_area` 结果，使用配置文件中的默认值

### login 命令
- **signature**: 自动从 `select_area` 返回值的 `Signature` 字段获取
- **role_id**: 自动从 `select_area` 返回值的 `RoleId` 字段获取  
- **user_name**: 自动从 `auth` 返回值的 `OpenId` 字段获取
- 如果脚本中提供了这些参数，将优先使用提供的值

## 📋 脚本格式

脚本使用JSON格式，每个命令包含以下字段：

```json
{
  "cmd": "命令名",
  "参数名": "参数值",
  "timeout": 30
}
```

### 示例脚本

#### 简化版本（使用自动参数获取）
```json
[
  {
    "cmd": "auth",
    "user_name": "q1",
    "channel": "dev"
  },
  {
    "cmd": "select_area",
    "open_id": "ret[\"auth\"][\"OpenId\"]",
    "area_id": 1,
    "login_token": "ret[\"auth\"][\"LoginToken\"]"
  },
  {
    "cmd": "connect_gate"
  },
  {
    "cmd": "login"
  }
]
```

#### 完整版本（手动指定参数）
```json
[
  {
    "cmd": "auth",
    "user_name": "q1",
    "channel": "dev"
  },
  {
    "cmd": "select_area",
    "open_id": "ret[\"auth\"][\"OpenId\"]",
    "area_id": 1,
    "login_token": "ret[\"auth\"][\"LoginToken\"]"
  },
  {
    "cmd": "connect_gate"
  },
  {
    "cmd": "login",
    "signature": "ret[\"select_area\"][\"Signature\"]",
    "role_id": "ret[\"select_area\"][\"RoleId\"]",
    "user_name": "ret[\"auth\"][\"OpenId\"]"
  }
]
```

## 💡 参数引用

支持两种参数引用方式：

1. **字段引用**: `ret["命令名"]["字段名"]`
   - 例: `ret["auth"]["OpenId"]` 获取认证返回的OpenId

2. **完整引用**: `ret["命令名"]`
   - 例: `ret["auth"]` 获取认证的完整返回结果

## 🎮 使用场景

### 1. 完整登录流程测试
```json
auth → select_area → connect_gate → login
```

### 2. 仅HTTP认证测试
```json
auth → select_area
```

### 3. 直接登录测试
```json
connect_gate → login (使用预设signature)
```

## 🔧 工具使用

### 脚本编辑器
- 交互式创建和编辑脚本
- 支持参数提示和验证
- 可以保存/加载脚本文件

### 快速运行器
- 快速运行示例脚本
- 支持查看脚本内容
- 支持命令行参数

## ⚡ 高级功能

### 1. 异步执行
脚本支持异步执行，会等待每个命令完成后再执行下一个。

### 2. 超时控制
每个命令都可以设置超时时间：

```json
{
  "cmd": "login",
  "signature": "...",
  "timeout": 60
}
```

### 3. 错误处理
- 自动捕获和显示执行错误
- 支持继续执行或停止脚本

### 4. 结果存储
- 每个命令的返回结果都会被保存
- 后续命令可以引用之前的结果

## 📊 执行示例

```
🚀 开始执行脚本...
📋 共有 4 个命令
==================================================
🔄 [1/4] 执行命令: auth
📝 参数: {'user_name': 'q1', 'channel': 'dev'}
✅ 命令 auth 执行完成
📤 返回结果: {'OpenId': '12345', 'LoginToken': 'abc123'}
------------------------------
🔄 [2/4] 执行命令: select_area
📝 参数: {'open_id': '12345', 'area_id': 1, 'login_token': 'abc123'}
✅ 命令 select_area 执行完成
📤 返回结果: {'Signature': 'xyz789'}
------------------------------
🎉 脚本执行完成!
```

## 🐛 故障排除

### 1. 连接失败
- 检查 `config/config.yml` 中的服务器配置
- 确保目标服务器正在运行

### 2. 参数引用错误
- 检查参数引用格式是否正确
- 确保被引用的命令已经执行并返回结果

### 3. 超时错误
- 增加命令的超时时间
- 检查网络连接是否正常

### 4. 协议错误
- 确保proto文件路径配置正确
- 检查协议ID是否匹配

## 💻 开发说明

### 扩展新命令

1. 在 `ScriptExecutor` 类中添加命令函数：

```python
def _new_command(self, param1: str, param2: int = 0) -> Dict[str, Any]:
    """新命令实现"""
    # 执行逻辑
    result = {"success": True}
    self._complete_command("new_command", result)
    return result
```

2. 在 `_register_commands` 方法中注册：

```python
self.command_functions["new_command"] = self._new_command
```

### 自定义参数解析

可以扩展 `_resolve_value` 方法来支持更复杂的参数引用格式。

## 📝 更新日志

### v1.0.0
- 初始版本
- 支持基本的命令执行和参数引用
- 提供交互式编辑器和快速运行器
- 包含完整的示例脚本
