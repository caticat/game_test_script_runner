# 脚本示例说明

这个目录包含了核心的脚本执行示例和模块化脚本功能。

## 📋 基础示例

### 1. `login_flow.json` - 完整登录流程
完整的游戏登录流程，包括：
- HTTP认证获取OpenId和LoginToken
- 选择游戏区服获取网关信息和签名
- 连接游戏网关
- 发送登录请求
- 显示登录结果

**适用场景：** 正常的游戏登录流程测试

### 2. `auth_only.json` - 仅认证测试
只执行HTTP认证和选服步骤，不进行TCP连接和游戏登录：
- HTTP认证获取OpenId和LoginToken
- 选择游戏区服获取网关信息
- 显示认证结果

**适用场景：** 测试HTTP认证服务器和选服逻辑

### 3. `direct_login.json` - 直接登录
跳过HTTP认证步骤，直接使用预设的签名和角色ID进行登录：
- 直接连接网关
- 使用预设参数登录
- 显示登录结果

**适用场景：** 测试游戏服登录逻辑，或当已知登录参数时快速登录

## 🔧 模块化脚本功能

### Include 功能
支持通过`include`字段包含其他脚本文件，实现模块化和代码复用：

```json
{
  "include": [
    "modules/auth_module.json",
    "modules/login_module.json"
  ],
  "comment": "包含认证和登录模块"
}
```

### 4. `modular_login.json` - 纯模块化登录
完全使用include的方式组织登录流程：
```json
[
  {
    "include": [
      "modules/auth_module.json",
      "modules/login_module.json", 
      "modules/post_login.json"
    ],
    "comment": "包含完整的登录流程模块"
  }
]
```

### 5. `mixed_include.json` - 混合使用示例
展示include与普通命令的混合使用：
- 可以在include前后添加普通命令
- 支持单个文件或文件数组的include
- 支持嵌套include（包含的文件内部也可以include其他文件）

### 6. `nested_include.json` - 嵌套包含示例
展示递归include的使用方式

## 📁 模块目录结构

```
modules/
├── auth_module.json     # 认证模块
├── login_module.json    # 登录模块
├── post_login.json      # 登录后处理
└── full_login.json      # 完整登录流程（内部包含其他模块）
```

## 🚀 使用方法

```python
# 在script_executor.py中运行
python script_executor.py

# 或者通过quick_runner.py运行
python quick_runner.py examples/login_flow.json
python quick_runner.py examples/modular_login.json
```

## 🔄 Include 功能特点

1. **路径解析**：支持相对路径（相对于当前脚本文件）
2. **递归包含**：支持包含的文件内部再包含其他文件
3. **数组或单个文件**：`"include": "file.json"` 或 `"include": ["a.json", "b.json"]`
4. **执行顺序**：严格按照include数组的顺序执行
5. **错误处理**：包含文件不存在或格式错误时会提示但不中断执行
6. **注释支持**：include指令也支持comment字段

## 📤 返回值使用

所有示例都展示了如何使用返回值引用：
- `ret["auth"]["OpenId"]` - 认证返回的OpenId
- `ret["login"]["role_id"]` - 登录返回的角色ID  
- `ret["login"]["success"]` - 登录是否成功

## 💬 注释功能

所有示例都使用了`comment`字段来说明每个步骤的作用，这些注释会在执行时显示但不会传递给命令函数。
