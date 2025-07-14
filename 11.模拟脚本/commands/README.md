# Commands 架构说明

## 📁 目录结构

```
commands/
├── __init__.py              # 包初始化
├── base_command.py          # 命令基类
├── command_manager.py       # 命令管理器
├── auth_commands.py         # HTTP认证相关命令
├── network_commands.py      # 网络连接相关命令
├── game_commands.py         # 游戏服相关命令
├── utility_commands.py      # 工具类命令
└── README.md               # 本说明文件
```

## 🎯 设计理念

### 1. **模块化设计**
- 每个命令类别独立成文件
- 便于维护和扩展
- 职责分离，代码清晰

### 2. **统一接口**
- 所有命令都继承自`BaseCommand`
- 统一的`execute()`方法接口
- 统一的错误处理和结果返回

### 3. **集中管理**
- `CommandManager`负责命令注册和调度
- 支持动态获取可用命令列表
- 便于添加新命令类型

## 🔧 如何添加新命令

### 步骤1: 创建命令类

```python
# 例如：新增一个数据库命令文件 database_commands.py
from typing import Dict, Any
from .base_command import BaseCommand

class QueryCommand(BaseCommand):
    def execute(self, sql: str, **kwargs) -> Dict[str, Any]:
        # 实现查询逻辑
        result = {"data": [...], "rows": 10}
        return result
```

### 步骤2: 在CommandManager中注册

```python
# 在 command_manager.py 中
from .database_commands import QueryCommand

class CommandManager:
    def _register_commands(self):
        # ...existing commands...
        
        # 数据库相关
        self.commands["query"] = QueryCommand(self.executor)
```

### 步骤3: 更新命令描述

```python
# 在 command_manager.py 的 get_available_commands() 方法中
def get_available_commands(self) -> Dict[str, str]:
    return {
        # ...existing commands...
        "query": "执行数据库查询",
    }
```

## 📝 命令分类

### 🔐 认证相关 (auth_commands.py)
- `AuthCommand`: HTTP认证获取OpenId和LoginToken
- `SelectAreaCommand`: 选择游戏区服，获取网关信息和签名

### 🌐 网络相关 (network_commands.py)
- `ConnectGateCommand`: 连接到游戏网关
- `ConnectLoginCommand`: 连接到登录服

### 🎮 游戏相关 (game_commands.py)
- `LoginCommand`: 游戏服登录
- *未来可扩展*：角色操作、战斗指令等

### 🛠️ 工具相关 (utility_commands.py)
- `SleepCommand`: 睡眠指定时间
- `PrintCommand`: 打印消息（支持返回值引用）
- *未来可扩展*：文件操作、数据处理等

## 🔗 基类功能

### BaseCommand提供的功能：

1. **执行器引用**: 通过`self.executor`访问主执行器
2. **结果访问**: 通过`self.results`访问所有命令结果
3. **客户端管理**: 通过`self.current_client`管理网络连接
4. **命令完成**: 通过`self.complete_command()`标记异步命令完成
5. **配置访问**: 通过`self.get_config()`获取系统配置

## 🚀 优势

1. **可扩展性强**: 新增命令只需创建新的命令类
2. **维护简单**: 每个功能模块独立，便于调试和修改
3. **代码清晰**: 职责分离，逻辑清晰
4. **复用性好**: 命令类可以在不同场景下复用
5. **测试友好**: 每个命令类都可以独立测试

## 📚 最佳实践

1. **命令命名**: 使用清晰的动词，如`LoginCommand`、`ConnectCommand`
2. **参数验证**: 在`execute()`方法中进行参数验证
3. **错误处理**: 使用try-catch处理异常，返回标准格式的错误信息
4. **文档注释**: 为每个命令类和方法添加清晰的文档字符串
5. **日志输出**: 使用统一的日志格式，便于调试和监控
