# 调试输出控制

## 概述
协议测试工具现在支持通过配置文件控制调试信息的显示，避免在生产环境中产生过多的调试输出。

## 配置文件
在 `config/config.yml` 中添加了调试控制配置：

```yaml
# 调试配置
debug:
  enabled: true # 是否启用调试模式
  show_packet_details: false # 是否显示数据包详细信息
```

## 调试级别

### 1. 基础调试信息 (`debug.enabled`)
当 `debug.enabled: true` 时，显示以下信息：
- 异步循环的启动和停止状态
- 消息发送和接收的基本信息
- 协议处理器的调用状态
- 写队列的状态信息

示例输出：
```
🔧 [DEBUG] _async_write_loop 开始运行
🔧 [DEBUG] 发送消息: proto_id=1001, seq=1, payload_len=25
🔧 [DEBUG] 消息已放入写队列, 当前队列大小: 1
🔧 [DEBUG] 等待写队列中的数据...
🔧 [DEBUG] 从写队列获取数据: 43 字节
🔧 [DEBUG] 数据发送完成
🔧 [DEBUG] 调用处理器: ban_ack
🔧 [DEBUG] 处理器执行完成: ban_ack
```

### 2. 数据包详细信息 (`show_packet_details`)
当 `show_packet_details: true` 时，额外显示：
- 接收到的原始数据包大小
- 解析后的数据包详细信息
- 协议处理的详细参数

示例输出：
```
🔧 [DEBUG] 接收到数据: 45 字节
🔧 [DEBUG] 解析到数据包: proto_id=1002, seq=1
🔧 [DEBUG] 处理数据包: proto_id=1002, seq=1, payload_len=25
```

## 使用方法

### 1. 关闭所有调试信息
```yaml
debug:
  enabled: false
  show_packet_details: false
```

### 2. 只显示基础调试信息
```yaml
debug:
  enabled: true
  show_packet_details: false
```

### 3. 显示全部调试信息
```yaml
debug:
  enabled: true
  show_packet_details: true
```

## 调试函数

### `debug_print(message)`
用于输出基础调试信息，受 `debug.enabled` 控制。

### `packet_debug_print(message)`
用于输出数据包详细信息，受 `debug.enabled` 和 `show_packet_details` 双重控制。

## 实时配置
配置更改会立即生效，无需重启程序。每次调用调试函数时都会重新检查配置。

## 推荐设置

### 开发环境
```yaml
debug:
  enabled: true
  show_packet_details: true
```

### 生产环境
```yaml
debug:
  enabled: false
  show_packet_details: false
```

### 问题诊断
```yaml
debug:
  enabled: true
  show_packet_details: true
```

这样既能在需要时提供详细的调试信息，又能在不需要时保持输出的简洁性。
