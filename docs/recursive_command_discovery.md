# 递归命令发现功能说明

## 🎯 功能概述

协议测试工具现在支持递归命令发现功能，允许在 `commands` 目录的子文件夹中组织命令，并使用层级命名来执行命令。

## 📁 目录结构示例

```
src/script_runner/commands/
├── __init__.py
├── base_command.py
├── command_manager.py
├── auth_commands.py           # 基础命令：auth
├── game_commands.py           # 基础命令：login
├── network_commands.py        # 基础命令：connect_gate, connect_login
├── utility_commands.py        # 基础命令：print, sleep
└── custom/                    # 自定义子文件夹示例
    ├── __init__.py
    ├── special_commands.py    # 命令：custom.special_test
    └── advanced/              # 嵌套子文件夹示例
        ├── __init__.py
        └── features.py        # 命令：custom.advanced.feature_test
```

## 🔧 命令命名规则

### 1. 基础命令（根目录）
- **文件**：`auth_commands.py`
- **类**：`AuthCommand`
- **命令名**：`auth`

### 2. 一级子目录命令
- **文件**：`custom/special_commands.py`
- **类**：`SpecialTestCommand`
- **命令名**：`custom.special_test`

### 3. 多级嵌套命令
- **文件**：`custom/advanced/features.py`
- **类**：`FeatureTestCommand`
- **命令名**：`custom.advanced.feature_test`

## 💡 实现原理

### 1. 递归扫描
```python
def scan_directory(directory: str, prefix: str = ""):
    for item in os.listdir(directory):
        if os.path.isfile(item_path) and item.endswith('.py'):
            # 处理Python文件
            process_python_file(item, prefix)
        elif os.path.isdir(item_path):
            # 递归扫描子目录
            scan_directory(item_path, f"{prefix}.{item}")
```

### 2. 命令名称生成
```python
# 基础命令名：去掉Command后缀，转换为蛇形命名
base_command_name = snake_case(class_name[:-7])

# 最终命令名：添加目录前缀
command_name = f"{prefix}.{base_command_name}"
```

### 3. 自动创建__init__.py
系统会自动为缺少 `__init__.py` 文件的子目录创建该文件，确保Python能正确导入模块。

## 🧪 使用示例

### 1. 创建命令类
```python
# custom/special_commands.py
from ..base_command import BaseCommand

class SpecialTestCommand(BaseCommand):
    """特殊测试命令"""
    
    def execute(self, message: str = "Hello!") -> Dict[str, Any]:
        print(f"🎯 特殊测试命令执行: {message}")
        return {"success": True, "message": message}
```

### 2. 在脚本中使用
```json
[
  {
    "cmd": "custom.special_test",
    "message": "来自脚本的测试消息",
    "comment": "测试递归命令：custom.special_test"
  },
  {
    "cmd": "custom.advanced.feature_test",
    "feature": "高级功能测试",
    "comment": "测试深度嵌套命令"
  }
]
```

### 3. 查看可用命令
运行脚本运行器后，可以查看所有可用命令：
```
📋 发现了 8 个命令:
  • auth                      - HTTP认证命令
  • connect_gate              - 连接网关命令
  • connect_login             - 连接登录服命令
  • custom.special_test       - 特殊测试命令
  • custom.advanced.feature_test - 高级功能测试命令
  • login                     - 游戏服登录命令
  • print                     - 打印命令
  • select_area               - 选择区服命令
  • sleep                     - 睡眠命令
```

## ✅ 功能特点

1. **递归扫描**：自动发现所有子目录中的命令
2. **层级命名**：使用点号分隔的层级命名系统
3. **自动导入**：自动创建必要的 `__init__.py` 文件
4. **向后兼容**：不影响现有的基础命令
5. **错误处理**：对导入失败的模块提供清晰的错误信息

## 🎯 实际应用

### 1. 按功能组织
```
commands/
├── auth/          # 认证相关命令
├── game/          # 游戏相关命令
├── network/       # 网络相关命令
└── utility/       # 工具类命令
```

### 2. 按服务器类型组织
```
commands/
├── login_server/  # 登录服命令
├── gate_server/   # 网关服命令
└── game_server/   # 游戏服命令
```

### 3. 按协议模块组织
```
commands/
├── user/          # 用户相关协议
├── item/          # 物品相关协议
├── battle/        # 战斗相关协议
└── social/        # 社交相关协议
```

## 🔧 扩展建议

1. **命名规范**：建议使用有意义的目录名和文件名
2. **文档完善**：为每个命令类添加详细的文档字符串
3. **测试覆盖**：为新增的递归命令创建测试用例
4. **性能优化**：对于大量命令，可考虑添加缓存机制

这个递归命令发现功能大大提升了项目的可扩展性和组织性，使得大型项目中的命令管理更加高效和清晰。
