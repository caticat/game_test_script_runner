# TCP客户端错误处理优化

## 问题描述
脚本执行完成后出现错误：
```
[ERROR] Read failed: [WinError 10038] 在一个非套接字上尝试了一个操作。
```

## 原因分析
1. 线程设置为 `daemon=True`，程序退出时线程被强制终止
2. 套接字在程序结束时没有正确关闭
3. 读取循环在套接字关闭后仍尝试操作

## 解决方案

### 1. 线程管理优化
- 移除 `daemon=True` 设置
- 添加线程跟踪：`self.threads = []`
- 在 `stop()` 方法中等待线程结束

### 2. 套接字关闭优化
```python
def stop(self):
    self.running.clear()
    if self.socket:
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            self.socket.close()
        except:
            pass
        self.socket = None
    
    # 等待所有线程结束
    for thread in self.threads:
        if thread.is_alive():
            thread.join(timeout=2.0)
```

### 3. 错误处理优化
- 读取循环中添加 `if not self.socket: break`
- 区分 `OSError` 和其他异常
- 只在连接仍活跃时才打印错误信息

## 测试结果
✅ 不再出现 `[ERROR] Read failed: [WinError 10038]` 错误
✅ 脚本正常执行完成并退出
✅ TCP连接正确关闭

## 修改文件
- `utils/tcp_client.py` - 优化TCP客户端错误处理
