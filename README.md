# 协议测试工具

## 项目简介

这是一个用于测试游戏服务器协议的工具集合，支持HTTP和TCP协议的测试。

## 🏗️ 项目结构

```
896.协议测试工具/
├── 01.登录服/                    # 登录服务器测试脚本
│   ├── 01.auth.py                # HTTP认证测试
│   ├── 02.封禁账号.py            # 账号封禁管理
│   └── 03.模拟角色数据变更.py     # 角色数据变更测试
├── 03.游戏服/                    # 游戏服务器测试脚本
│   └── 01.game.py                # 游戏服登录测试
├── config/                       # 配置文件
│   └── config.yml                # 服务器配置
├── utils/                        # 工具库
│   ├── base_tcp_client.py        # TCP客户端基础类
│   ├── config_manager.py         # 配置管理器
│   ├── tcp_client.py             # TCP客户端
│   ├── protocol_codec.py         # 协议编解码器
│   ├── formatters.py             # 格式化和文本解码工具
│   ├── http_client.py            # HTTP客户端
│   └── __init__.py               # 包初始化文件
├── test/                         # 测试文件
│   ├── test_auto_register.py     # 自动注册测试
│   ├── test_refactor.py          # 重构测试
│   └── test_game_auto_register.py # 游戏服自动注册测试
├── tools/                        # 构建工具
│   └── gen_proto.sh              # Proto文件生成脚本
├── launcher.py                   # 项目启动器
├── requirements.txt              # Python依赖
└── README.md                     # 项目文档
```

## 🔧 重构说明

### 文件重构对比

| 旧文件名 | 新文件名 | 说明 |
|---------|---------|-----|
| `print_dict.py` | `formatters.py` | 合并格式化相关功能 |
| `decode_dict.py` | `formatters.py` | 合并到格式化模块 |
| `login_poster.py` | `http_client.py` | 重构为通用HTTP客户端 |
| `proto_encode.py` | `protocol_codec.py` | 更符合命名规范 |
| `time_helper.py` | `time_utils.py` | 更符合命名规范 |

### 重构后的结构

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
python 01.登录服/01.auth.py

# 账号封禁管理
python 01.登录服/02.封禁账号.py

# 角色数据变更
python 01.登录服/03.模拟角色数据变更.py

# 游戏服测试
python 03.游戏服/01.game.py
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
