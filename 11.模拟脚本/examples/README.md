# 脚本示例说明

这个目录包含了三个核心的脚本执行示例：

## 1. `login_flow.json` - 完整登录流程
完整的游戏登录流程，包括：
- HTTP认证获取OpenId和LoginToken
- 选择游戏区服获取网关信息和签名
- 连接游戏网关
- 发送登录请求
- 显示登录结果

**适用场景：** 正常的游戏登录流程测试

## 2. `auth_only.json` - 仅认证测试
只执行HTTP认证和选服步骤，不进行TCP连接和游戏登录：
- HTTP认证获取OpenId和LoginToken
- 选择游戏区服获取网关信息
- 显示认证结果

**适用场景：** 测试HTTP认证服务器和选服逻辑

## 3. `direct_login.json` - 直接登录
跳过HTTP认证步骤，直接使用预设的签名和角色ID进行登录：
- 直接连接网关
- 使用预设参数登录
- 显示登录结果

**适用场景：** 测试游戏服登录逻辑，或当已知登录参数时快速登录

## 使用方法

```python
# 在script_executor.py中运行
python script_executor.py

# 或者通过quick_runner.py运行
python quick_runner.py examples/login_flow.json
```

## 返回值使用

所有示例都展示了如何使用返回值引用：
- `ret["auth"]["OpenId"]` - 认证返回的OpenId
- `ret["login"]["role_id"]` - 登录返回的角色ID  
- `ret["login"]["success"]` - 登录是否成功

## 注释功能

所有示例都使用了`comment`字段来说明每个步骤的作用，这些注释会在执行时显示但不会传递给命令函数。
