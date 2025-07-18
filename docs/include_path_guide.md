# Include 路径规则说明

## 概述

脚本执行器的 include 功能已经进行了重大调整，现在所有的 include 路径都必须基于配置文件中的 `scripts_path` 目录作为根目录。

## 新的路径规则

### 1. 绝对路径基准

所有 include 路径都以 `config.yml` 中配置的 `scripts_path` 为根目录：

```yaml
paths:
  scripts_path: "scripts"  # 配置的脚本根目录
```

### 2. 禁止相对路径

不再支持使用 `../` 这样的相对路径：

```json
// ❌ 错误用法 - 不再支持
{
  "include": "../modules/auth_module.json"
}

// ✅ 正确用法 - 基于scripts目录的路径
{
  "include": "modules/auth_module.json"
}
```

### 3. 路径示例

假设项目结构如下：
```
scripts/
├── examples/
│   ├── login_flow.json
│   └── nested_include.json
├── modules/
│   ├── auth_module.json
│   ├── login_module.json
│   └── post_login.json
└── tests/
    └── test_script.json
```

在任何脚本文件中（无论在哪个子目录下），include 路径都应该这样写：

```json
// 在 examples/login_flow.json 中
{
  "include": "modules/auth_module.json"  // 正确
}

// 在 modules/full_login.json 中  
{
  "include": "modules/login_module.json"  // 正确
}

// 在 tests/test_script.json 中
{
  "include": "modules/auth_module.json"  // 正确
}
```

## 安全性改进

### 1. 路径验证

- 禁止使用 `../` 开头的相对路径
- 验证绝对路径必须在 scripts 目录范围内
- 防止路径遍历攻击

### 2. 错误提示

当使用不正确的路径时，会显示清晰的错误信息：

```
❌ 禁止使用相对路径: ../modules/auth_module.json
💡 请使用相对于scripts目录的路径，如: modules/auth_module.json
```

## 迁移指南

### 旧脚本更新

如果你有使用旧相对路径的脚本，需要按以下规则更新：

1. 移除所有 `../` 前缀
2. 确保路径相对于 `scripts` 目录

例如：
```json
// 旧格式
{
  "include": "../modules/auth_module.json"
}

// 新格式  
{
  "include": "modules/auth_module.json"
}
```

### 批量更新

项目中的以下文件已经更新：
- `scripts/examples/include_login_flow.json`
- `scripts/examples/nested_include.json`
- `scripts/examples/modular_login.json`
- `scripts/examples/mixed_include.json`
- `scripts/modules/full_login.json`

## 技术实现

### 路径解析逻辑

1. 获取配置的 `scripts_path`
2. 将其与项目根目录组合得到绝对的 scripts 根目录
3. 所有 include 路径都基于这个根目录解析
4. 递归处理嵌套的 include，保持一致的根目录

### 向后兼容性

- `set_script_base_dir()` 方法保留但不再使用
- 旧的脚本会显示错误提示，指导用户正确更新

## 优势

1. **一致性**: 所有脚本使用统一的路径规则
2. **安全性**: 防止路径遍历，确保文件在合法范围内
3. **可维护性**: 路径规则简单明确，易于理解
4. **可配置性**: 可通过配置文件调整 scripts 根目录
