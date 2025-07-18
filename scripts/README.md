# 脚本示例说明

这个目录包含了协议测试工具的核心脚本执行示例和模块化脚本功能。

## � 目录结构

```
scripts/
├── README.md                    # 本说明文件
├── login_flow_ori.json         # 原始登录流程
├── login_flow_step.json        # 分步登录流程
├── examples/                   # 示例脚本
│   ├── auth_only.json          # 仅认证测试
│   ├── direct_login.json       # 直接登录
│   ├── include_login_flow.json # 使用include的登录流程
│   ├── mixed_include.json      # 混合include示例
│   ├── modular_login.json      # 纯模块化登录
│   ├── nested_include.json     # 嵌套include示例
│   ├── test_include_paths.json # include路径测试
│   └── websocket_demo.json     # WebSocket功能演示
├── modules/                    # 可复用模块
│   ├── auth_module.json        # 认证模块
│   ├── login_module.json       # 登录模块
│   ├── post_login.json         # 登录后处理
│   └── full_login.json         # 完整登录流程
└── tests/                      # 测试脚本
    ├── websocket_connection_test.json
    └── websocket_test.json
```

## 📋 根目录脚本

### 1. `login_flow_ori.json` - 原始登录流程
使用原始认证命令的登录流程：
- 使用 `ori.auth` 命令进行HTTP认证
- 连接WebSocket网关
- 发送登录请求

**适用场景：** 使用原始认证接口的测试

### 2. `login_flow_step.json` - 分步登录流程
标准的分步登录流程：
- HTTP认证获取OpenId和LoginToken
- 选择游戏区服获取网关信息和签名
- 连接游戏网关
- 发送登录请求
- 显示登录结果

**适用场景：** 标准的游戏登录流程测试

## 📝 examples/ 示例脚本

### 3. `auth_only.json` - 仅认证测试
只执行HTTP认证和选服步骤，不进行网关连接：
- HTTP认证获取OpenId和LoginToken
- 选择游戏区服获取网关信息
- 显示认证结果

**适用场景：** 测试HTTP认证服务器和选服逻辑

### 4. `direct_login.json` - 直接登录
跳过HTTP认证步骤，直接使用预设参数进行登录：
- 直接连接网关
- 使用预设参数登录
- 显示登录结果

**适用场景：** 测试游戏服登录逻辑，或当已知登录参数时快速登录

### 5. `websocket_demo.json` - WebSocket功能演示
演示WebSocket连接功能：
- 连接到公共WebSocket测试服务器
- 测试WebSocket连接状态
- 展示WebSocket通信能力

**适用场景：** 测试WebSocket连接和通信功能

## 🔧 模块化脚本功能 (examples/include_*.json)

### Include 功能
支持通过`include`字段包含其他脚本文件，实现模块化和代码复用。

**重要：** 从2025年7月开始，include路径规则已更新：
- ✅ 所有路径都基于 `scripts` 目录作为根目录
- ✅ 使用如 `modules/auth_module.json` 的路径格式
- ❌ 禁止使用 `../modules/auth_module.json` 的相对路径

### 6. `include_login_flow.json` - 使用include的登录流程
展示如何使用include功能组织登录流程：
```json
{
  "include": "modules/auth_module.json",
  "comment": "包含认证模块"
}
```

### 7. `modular_login.json` - 纯模块化登录
完全使用include数组的方式组织登录流程：
```json
{
  "include": [
    "modules/auth_module.json",
    "modules/login_module.json", 
    "modules/post_login.json"
  ],
  "comment": "包含完整的登录流程模块"
}
```

### 8. `mixed_include.json` - 混合使用示例
展示include与普通命令的混合使用：
- 可以在include前后添加普通命令
- 支持单个文件或文件数组的include
- 展示灵活的脚本组织方式

### 9. `nested_include.json` - 嵌套包含示例
展示递归include的使用方式：
- 包含的模块内部还可以include其他模块
- 支持多层嵌套

### 10. `test_include_paths.json` - Include路径测试
用于测试新的include路径逻辑的示例脚本

## � modules/ 可复用模块

### `auth_module.json` - 认证模块
包含HTTP认证和选服的通用步骤：
- HTTP认证获取OpenId和LoginToken
- 选择游戏区服获取网关信息和签名

### `login_module.json` - 登录模块
包含网关连接和登录的步骤：
- 连接游戏网关
- 发送登录请求

### `post_login.json` - 登录后处理
包含登录后的通用处理：
- 等待和显示结果

### `full_login.json` - 完整登录流程
通过include组合其他模块实现完整登录流程（展示嵌套include）

## 🧪 tests/ 测试脚本

### `websocket_connection_test.json` 和 `websocket_test.json`
专门用于测试WebSocket连接功能的脚本

## 🚀 使用方法

### 通过脚本运行器使用
```bash
# 启动主程序
python src/script_runner/main.py

# 选择 "快速运行器" 然后选择脚本文件
```

### 直接运行脚本
```bash
# 使用快速运行器运行特定脚本
python src/script_runner/quick_runner.py
```

## 🔄 Include 功能特点

1. **统一路径规则**：所有include路径都基于scripts目录作为根目录
2. **安全性**：禁止使用 `../` 相对路径，防止路径遍历
3. **递归包含**：支持包含的文件内部再包含其他文件
4. **灵活格式**：支持单个文件或文件数组
   - `"include": "modules/auth_module.json"`
   - `"include": ["modules/auth_module.json", "modules/login_module.json"]`
5. **执行顺序**：严格按照include数组的顺序执行
6. **错误处理**：包含文件不存在时会显示清晰的错误提示
7. **注释支持**：include指令也支持comment字段

## 📤 返回值使用

所有脚本都展示了如何使用返回值引用：
- `ret["auth"]["OpenId"]` - 认证返回的OpenId
- `ret["auth"]["LoginToken"]` - 认证返回的LoginToken
- `ret["select_area"]["Signature"]` - 选服返回的签名
- `ret["select_area"]["GateHost"]` - 选服返回的网关地址
- `ret["login"]["success"]` - 登录是否成功

## 💬 注释功能

所有脚本都使用了`comment`字段来说明每个步骤的作用，这些注释会在执行时显示但不会传递给命令函数。

## ⚙️ 配置

脚本路径通过 `config/config.yml` 中的 `paths.scripts_path` 配置项控制，默认为 `"scripts"`。
