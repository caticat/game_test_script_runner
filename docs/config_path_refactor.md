# 配置路径重构

## 修改内容
将硬编码路径替换为配置读取：

```python
# 修改前
external_path = "Q:/kof/dev/proto_python"
sys.path.append(external_path)

# 修改后
from utils.config_manager import config_manager
proto_path = config_manager.get_proto_path()
sys.path.append(proto_path)
```

## 新增配置
添加脚本文件夹路径配置：

```python
# 脚本路径配置
scripts_path = config_manager.get_scripts_path()
```

## 修改文件
- `config/config.yml` - 添加 `scripts_path` 配置
- `utils/config_manager.py` - 添加 `get_scripts_path()` 方法
- `11.模拟脚本/script_executor.py` - 使用配置proto_path
- `11.模拟脚本/commands/game_commands.py` - 使用配置proto_path
- `11.模拟脚本/quick_runner.py` - 使用配置scripts_path
- `02.网关/01.登录.py` - 使用配置proto_path
- `01.登录服/03.模拟角色数据变更.py` - 使用配置proto_path
- `01.登录服/02.封禁账号.py` - 使用配置proto_path

## 结果
✅ proto_path统一从 `config/config.yml` 读取
✅ scripts_path可配置，默认为 `scripts`
✅ 支持环境变量覆盖 (`PROTO_PYTHON_PATH`, `SCRIPTS_PATH`)
✅ 所有脚本正常运行
