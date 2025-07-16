# CommandManager 自动发现优化

## 优化内容
将硬编码的命令注册改为自动发现和注册机制：

### 1. 自动发现命令类
- 递归搜索 `commands/` 目录中的所有 Python 文件
- 自动发现继承自 `BaseCommand` 的类
- 过滤掉 `BaseCommand` 本身和不以 `Command` 结尾的类

### 2. 自动生成命令名称
- 从类名中去掉 `Command` 后缀
- 将驼峰命名转换为蛇形命名
- 例如：`AuthCommand` → `auth`，`SelectAreaCommand` → `select_area`

### 3. 自动获取命令描述
- 使用类的文档字符串（`__doc__`）作为命令描述
- 如果没有文档字符串，使用默认格式

## 优化前后对比

### 优化前
```python
def _register_commands(self):
    """注册所有可用的命令"""
    self.commands["auth"] = AuthCommand(self.executor)
    self.commands["select_area"] = SelectAreaCommand(self.executor)
    # ... 需要手动添加每个命令

def get_available_commands(self) -> Dict[str, str]:
    return {
        "auth": "HTTP认证获取OpenId和LoginToken",
        "select_area": "选择游戏区服，获取网关信息和签名",
        # ... 需要手动维护描述
    }
```

### 优化后
```python
def _register_commands(self):
    """注册所有可用的命令"""
    discovered_commands = self._discover_commands()
    for command_name, command_info in discovered_commands.items():
        command_instance = command_info['class'](self.executor)
        self.commands[command_name] = command_instance

def get_available_commands(self) -> Dict[str, str]:
    """自动获取命令描述"""
    discovered_commands = self._discover_commands()
    return {name: info['description'] for name, info in discovered_commands.items()}
```

## 优势

1. **自动化**：新增命令类后无需手动注册
2. **一致性**：命令名称生成规则统一
3. **可维护性**：减少重复代码和手动维护
4. **扩展性**：易于添加新命令

## 新增功能

- `_snake_case()` - 驼峰命名转蛇形命名
- `_discover_commands()` - 自动发现命令类
- 自动从类文档字符串获取描述

## 测试结果
✅ 自动发现 7 个命令
✅ 命令名称正确转换（auth, select_area, connect_gate, connect_login, login, print, sleep）
✅ 描述自动从类文档字符串获取
✅ 新增命令可自动发现和注册
✅ 原有功能完全兼容
