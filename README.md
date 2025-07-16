# 协议测试工具

## 项目简介

这是一个用于测试游戏服务器协议的工具集合，支持HTTP和TCP协议的测试。

## 🏗️ 项目结构

```
896.协议测试工具/
├── src/                          # 源代码目录
│   ├── auth_server/              # 认证服务器测试
│   │   ├── 01.http_auth.py       # HTTP认证测试
│   │   ├── 02.封禁账号.py        # 账号封禁管理
│   │   └── 03.模拟角色数据变更.py # 角色数据变更测试
│   ├── gateway/                  # 网关服务器测试
│   │   └── 01.登录.py            # 网关登录测试
│   ├── game_server/              # 游戏服务器测试
│   │   └── [预留]                # 游戏服相关测试
│   └── script_runner/            # 脚本运行器
│       ├── main.py               # 主程序
│       ├── quick_runner.py       # 快速运行器
│       ├── script_editor.py      # 脚本编辑器
│       ├── script_executor.py    # 脚本执行器
│       └── commands/             # 命令实现
│           ├── __init__.py
│           ├── base.py           # 基础命令类
│           ├── login.py          # 登录命令
│           ├── send.py           # 发送命令
│           ├── wait.py           # 等待命令
│           └── assert_cmd.py     # 断言命令
├── scripts/                      # 测试脚本
│   ├── async_demo.json
│   ├── auth_only.json
│   ├── auto_params.json
│   ├── batch_test.json
│   ├── direct_login.json
│   └── login_flow.json
├── tests/                        # 测试文件
│   ├── run_tests.py
│   ├── test_async_simple.py
│   ├── test_auto_params.py
│   ├── test_forced_sync.py
│   ├── test_new_command.py
│   ├── test_script.py
│   └── test_wait_logic.py
├── config/                       # 配置文件
│   └── config.yml                # 服务器配置
├── utils/                        # 工具库
│   ├── base_tcp_client.py        # TCP客户端基础类
│   ├── config_manager.py         # 配置管理器
│   ├── tcp_client.py             # TCP客户端
│   ├── protocol_codec.py         # 协议编解码器
│   ├── utils.py                  # 通用工具
│   └── __init__.py               # 包初始化文件
├── tools/                        # 构建工具
│   └── gen_proto.sh              # Proto文件生成脚本
├── docs/                         # 项目文档
│   ├── project_structure.md      # 项目结构说明
│   ├── refactor_modernization.md # 重构现代化说明
│   └── exit_command_unification.md # 退出命令统一说明
├── launcher.py                   # 项目启动器
├── requirements.txt              # Python依赖
└── README.md                     # 项目文档
```

## 🔧 重构说明

### 主要重构内容

1. **目录结构重组**
   - 将测试脚本按功能分类到 `src/` 目录
   - 创建 `scripts/` 目录存放测试脚本
   - 统一测试文件到 `tests/` 目录
   - 添加 `docs/` 目录存放项目文档

2. **模块化改进**
   - 脚本运行器模块化，分离命令实现
   - 使用配置驱动的路径管理
   - 动态命令发现和加载机制

3. **用户体验优化**
   - 统一所有退出命令：支持 `0`、`q`、`quit`
   - 改进菜单显示和交互提示
   - 优化错误处理和异常管理

### 现代化特点

1. **配置驱动**：使用结构化配置文件管理路径和设置
2. **动态发现**：自动发现和注册命令及处理器
3. **模块化设计**：清晰的模块边界和职责分离
4. **用户友好**：统一的交互界面和退出机制
5. **文档完整**：详细的项目文档和使用说明

| 模块 | 功能 | 说明 |
|-------|-------|-----|
| `utils.py` | 统一工具类 | 整合所有常用功能 |
| `protocol_codec.py` | 协议编解码 | 仅包含Codec类 |
| `tcp_client.py` | TCP客户端 | 网络通信功能 |
| `base_tcp_client.py` | 基础TCP客户端 | 高层抽象 |
| `config_manager.py` | 配置管理 | 配置文件读取 |

### 优化特点

1. **去除冗余**：删除重复功能的文件
2. **功能统一**：合并相似功能到单一模块
3. **代码简洁**：不保留兼容性代码，直接更新使用方式
4. **结构清晰**：每个模块职责单一明确
5. **便于维护**：减少文件数量，降低维护成本

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置服务器

编辑 `config/config.yml` 文件：

```yaml
login:
  url: "http://127.0.0.1:8000"
  host: "127.0.0.1"
  port: 8031
gate:
  host: "127.0.0.1"
  port: 5001
proto_path: "Q:/kof/dev/proto_python"
```

### 3. 使用启动器

```bash
python launcher.py
```

或者直接运行具体的测试脚本：

```bash
# HTTP认证测试
python src/auth_server/01.http_auth.py

# 账号封禁管理
python src/auth_server/02.封禁账号.py

# 角色数据变更
python src/auth_server/03.模拟角色数据变更.py

# 网关登录测试
python src/gateway/01.登录.py

# 脚本运行器
python src/script_runner/main.py
```

## ️ 开发指南

### 添加新的测试工具

1. 继承或使用 `BaseTCPClient` 类：

```python
from utils.base_tcp_client import BaseTCPClient

def main():
    current_module = sys.modules[__name__]
    client = BaseTCPClient("login", current_module)  # 或 "gate"
    client.connect_and_run()
```

2. 实现请求/应答处理函数：

```python
def my_test_req(client: SocketClient) -> None:
    # 发送请求
    pass

def my_test_ack(seq: int, payload: bytes) -> None:
    # 处理应答
    pass

# 协议ID变量
my_test_id = ProtoId.MY_TEST_PROTOCOL
```

### 自动注册机制

- **命令函数**: `{command}_req` → 自动注册为 `{command}` 命令
- **处理器函数**: `{command}_ack` → 自动注册为处理器
- **协议ID变量**: `{command}_id` → 自动关联到处理器

## 🐛 故障排除

### 常见问题

1. **Proto文件导入失败**
   - 检查 `config.yml` 中的 `proto_path` 配置
   - 确保Proto文件已正确生成
   - 运行 `./tools/gen_proto.sh` 生成Proto文件

2. **连接服务器失败**
   - 检查服务器地址和端口配置
   - 确保目标服务器正在运行

3. **依赖包缺失**
   - 运行 `pip install -r requirements.txt`

### 调试技巧

1. 使用启动器统一管理测试工具
2. 查看终端输出的错误信息
3. 检查配置文件格式是否正确
4. 查看"已注册X个命令和X个处理器"的提示信息

## 📝 待办事项

- [ ] 添加单元测试
- [ ] 支持更多协议类型
- [ ] 添加性能测试功能
- [ ] 支持批量测试
- [ ] 添加测试报告生成

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 📄 许可证

此项目使用MIT许可证。
