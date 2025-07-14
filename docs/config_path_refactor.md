# 配置路径重构

## 修改内容
将硬编码 `external_path = "Q:/kof/dev/proto_python"` 替换为配置读取：

```python
# 修改前
external_path = "Q:/kof/dev/proto_python"
sys.path.append(external_path)

# 修改后
from utils.config_manager import config_manager
proto_path = config_manager.get_proto_path()
sys.path.append(proto_path)
```

## 修改文件
- `11.模拟脚本/script_executor.py`
- `11.模拟脚本/commands/game_commands.py`  
- `02.网关/01.登录.py`
- `01.登录服/03.模拟角色数据变更.py`
- `01.登录服/02.封禁账号.py`

## 结果
✅ 路径统一从 `config/config.yml` 读取
✅ 支持环境变量覆盖 (`PROTO_PYTHON_PATH`)
✅ 所有脚本正常运行
