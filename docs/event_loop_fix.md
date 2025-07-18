# 异步事件循环修复

## 问题描述
协议测试工具在发送请求后出现以下问题：
1. 无法收到服务器返回的消息
2. 屏幕一直刷 "等待写队列中的数据..." 的调试信息
3. 程序卡住，需要手动终止

## 根本原因
1. **事件循环阻塞**：使用同步 `input()` 函数阻塞了异步事件循环
2. **读取循环异常退出**：TCP 接收超时时返回空字节，导致读取循环认为连接关闭
3. **缺少调试信息**：无法准确定位问题位置

## 修复方案

### 1. 事件循环优化
**修改前**：
```python
# 使用同步 input() 阻塞事件循环
while True:
    command = input("请输入命令: ")
    # 处理命令
```

**修改后**：
```python
# 使用 aioconsole 异步输入，不阻塞事件循环
async def handle_input():
    import aioconsole
    while True:
        command = await aioconsole.ainput("请输入命令: ")
        # 处理命令

# 创建异步任务，与读写任务并发运行
input_task = asyncio.create_task(handle_input())
await input_task
```

### 2. TCP 读取循环修复
**修改前**：
```python
async def _async_recv_data(self) -> bytes:
    try:
        return await asyncio.wait_for(
            self.loop.sock_recv(self.socket, 4096), 
            timeout=1.0
        )
    except asyncio.TimeoutError:
        return b""  # 空字节导致读取循环退出
```

**修改后**：
```python
async def _async_recv_data(self) -> bytes:
    try:
        data = await asyncio.wait_for(
            self.loop.sock_recv(self.socket, 4096), 
            timeout=1.0
        )
        if data:
            print(f"🔧 [DEBUG] 接收到数据: {len(data)} 字节")
        return data
    except asyncio.TimeoutError:
        return None  # 返回 None 表示超时，继续等待
```

### 3. 读取循环逻辑优化
**修改前**：
```python
data = await self._async_recv_data()
if not data:  # 空字节和 None 都会导致退出
    print("[INFO] 连接已关闭")
    break
```

**修改后**：
```python
data = await self._async_recv_data()
if data is None:
    # 超时，继续等待
    continue
if not data:  # 只有真正的空字节才表示连接关闭
    print("[INFO] 连接已关闭")
    break
```

### 4. 增强调试信息
- 发送消息时显示协议ID、序列号、数据长度
- 接收数据时显示数据包信息
- 协议处理器调用前后显示状态
- 各个异步循环的启动和结束状态

## 依赖更新
添加了 `aioconsole` 依赖：
```bash
pip install aioconsole
```

更新 `requirements.txt`：
```
aioconsole==0.7.0
```

## 修复效果
1. ✅ 异步事件循环正常运行，不再阻塞
2. ✅ TCP 读取循环持续工作，能正确接收服务器返回
3. ✅ 写队列正常工作，消息能正确发送
4. ✅ 协议处理器能正确调用和执行
5. ✅ 丰富的调试信息便于问题定位

## 使用方法
所有脚本现在都支持异步输入和并发处理：
- `src/auth_server/02.封禁账号.py`
- `src/auth_server/03.模拟角色数据变更.py`
- `src/gateway/01.登录.py`

直接运行脚本即可：
```bash
python src/auth_server/02.封禁账号.py
```

## 后续优化建议
1. 可以添加命令行参数控制调试信息开关
2. 可以增加重连机制，提高连接稳定性
3. 可以添加心跳检测，及时发现连接断开
