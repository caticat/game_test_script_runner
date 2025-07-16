#!/usr/bin/env python3
"""
验证退出命令统一性
"""
import os
import re

def check_exit_commands():
    """检查所有文件中的退出命令统一性"""
    print("🔍 检查退出命令统一性")
    print("=" * 50)
    
    # 需要检查的文件
    files_to_check = [
        "launcher.py",
        "src/script_runner/main.py",
        "src/script_runner/script_editor.py", 
        "src/script_runner/quick_runner.py",
        "src/auth_server/02.封禁账号.py",
        "src/auth_server/03.模拟角色数据变更.py",
        "src/gateway/01.登录.py",
        "utils/base_tcp_client.py",
        "utils/tcp_client.py"
    ]
    
    patterns = [
        r'quit.*退出|退出.*quit',
        r'choice.*==.*["\']0["\']',
        r'choice.*==.*["\']quit["\']',
        r'choice.*==.*["\']q["\']',
        r'输入.*0.*退出|输入.*q.*退出|输入.*quit.*退出',
        r'可输入.*0.*quit|可输入.*q.*quit'
    ]
    
    issues = []
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            continue
            
        print(f"\n📂 检查文件: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            for i, line in enumerate(lines, 1):
                # 检查是否包含退出相关的文本
                if any(keyword in line.lower() for keyword in ['quit', '退出', 'choice == "0"']):
                    print(f"  第{i}行: {line.strip()}")
                    
                    # 检查是否符合统一标准
                    if '退出' in line and '可输入' not in line and 'quit' in line:
                        if not re.search(r'可输入.*0.*quit|可输入.*q.*quit', line):
                            issues.append(f"{file_path}:{i} - 退出提示不够清晰")
                    
                    # 检查条件判断是否包含所有退出方式
                    if 'choice ==' in line and '"0"' in line:
                        if not ('quit' in line and 'q' in line):
                            issues.append(f"{file_path}:{i} - 退出条件判断不完整")
                            
        except Exception as e:
            print(f"  ❌ 读取文件失败: {e}")
    
    print(f"\n📊 检查结果:")
    if issues:
        print(f"❌ 发现 {len(issues)} 个问题:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ 所有退出命令已统一")
    
    print("\n📝 统一标准:")
    print("  1. 菜单显示: '0. quit - 退出 (可输入 0/q/quit)'")
    print("  2. 条件判断: choice == '0' or choice.lower() == 'quit' or choice.lower() == 'q'")
    print("  3. 命令处理器: 支持 '0', 'q', 'quit' 三种方式")

if __name__ == "__main__":
    check_exit_commands()
