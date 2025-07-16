# 项目结构重组文档

## 重组概述
对整个项目进行了结构重组，使文件组织更加清晰和符合现代项目标准。

## 重组前后对比

### 重组前结构
```
896.协议测试工具/
├── 01.登录服/
├── 02.网关/
├── 03.游戏服/
├── 11.模拟脚本/
│   ├── examples/       # 空目录
│   ├── scripts/        # 脚本文件
│   ├── test/           # 测试文件
│   └── ...
├── test/               # 测试文件
├── config/
├── utils/
├── tools/
└── docs/
```

### 重组后结构
```
896.协议测试工具/
├── src/                # 源代码目录
│   ├── auth_server/    # 登录服相关代码
│   ├── gateway/        # 网关相关代码
│   ├── game_server/    # 游戏服相关代码
│   └── script_runner/  # 脚本运行器
│       ├── commands/   # 命令模块
│       ├── main.py
│       ├── script_executor.py
│       ├── script_editor.py
│       └── ...
├── scripts/            # 脚本文件（从src/script_runner/scripts移动）
│   ├── auth_only.json
│   ├── login_flow.json
│   ├── modules/
│   └── ...
├── tests/              # 统一的测试目录
│   ├── run_tests.py
│   ├── test_auto_params.py
│   ├── test_script.py
│   └── ...
├── config/             # 配置文件
├── utils/              # 工具函数
├── tools/              # 构建工具
├── docs/               # 文档
├── launcher.py         # 主启动器
├── README.md
└── requirements.txt
```

## 重组内容详细说明

### 1. 源代码组织 (src/)
- **auth_server/**: 原"01.登录服"，重命名为更清晰的英文名称
- **gateway/**: 原"02.网关"，包含网关相关的所有代码
- **game_server/**: 原"03.游戏服"，游戏服务器相关代码
- **script_runner/**: 原"11.模拟脚本"，脚本运行器核心代码

### 2. 脚本文件统一管理 (scripts/)
- 将所有脚本文件从 `src/script_runner/scripts/` 移动到顶级 `scripts/` 目录
- 便于用户访问和管理脚本文件
- 与配置文件中的 `scripts_path` 设置保持一致

### 3. 测试文件整合 (tests/)
- 合并原来分散的测试文件
  - `test/` 目录下的文件
  - `11.模拟脚本/test/` 目录下的文件
- 统一的测试入口和管理

### 4. 清理的临时文件
- 删除了所有临时测试文件：
  - `test_refactor.py`
  - `test_editor.py`
  - `commands/test_commands.py`
- 删除了空的 `examples/` 目录
- 清理了所有 `__pycache__/` 目录

## 配置文件更新

### config/config.yml
```yaml
# 脚本文件夹路径配置
scripts_path: "scripts"  # 指向新的顶级scripts目录
```

## 文件路径影响

### 需要更新的引用
1. **script_runner中的相对路径**:
   - 脚本文件现在在 `../../scripts/` 而不是 `./scripts/`
   - 配置文件引用需要相应调整

2. **launcher.py中的模块引用**:
   - 需要更新import路径以适应新的src结构

3. **测试文件的引用**:
   - 测试文件现在在统一的tests目录中

## 优势

### 1. 更清晰的项目结构
- 源代码集中在src目录
- 脚本文件有专门的目录
- 测试文件统一管理

### 2. 符合现代项目标准
- 使用英文目录名称
- 采用标准的src/tests/docs结构
- 便于CI/CD集成

### 3. 更好的可维护性
- 减少文件散乱
- 清晰的职责分离
- 便于新人理解项目结构

### 4. 更好的扩展性
- 新功能可以在src下添加对应目录
- 脚本文件独立管理
- 测试文件集中维护

## 迁移注意事项

### 1. 路径更新
- 检查所有硬编码的文件路径
- 更新相对路径引用
- 确保配置文件路径正确

### 2. 导入语句
- 更新Python模块的import路径
- 检查sys.path设置
- 确保模块能正确找到

### 3. 脚本引用
- 更新脚本文件的引用路径
- 确保script_runner能找到scripts目录
- 测试脚本加载功能

## 验证清单

- [x] 源代码目录结构正确
- [x] 脚本文件移动完成
- [x] 测试文件整合完成
- [x] 临时文件清理完成
- [x] 配置文件更新
- [ ] 路径引用更新（需要后续验证）
- [ ] 功能测试（需要后续验证）

这次重组让项目结构更加清晰和专业，为后续的维护和扩展打下了良好的基础。
