"""
命令管理器
"""
import os
import importlib
import inspect
from typing import Dict, Callable
from .base_command import BaseCommand

class CommandManager:
    """命令管理器"""
    
    def __init__(self, executor_ref):
        """
        初始化命令管理器
        
        Args:
            executor_ref: ScriptExecutor实例的引用
        """
        self.executor = executor_ref
        self.commands = {}
        self._register_commands()
    
    def _snake_case(self, name: str) -> str:
        """将驼峰命名转换为蛇形命名"""
        import re
        # 在大写字母前插入下划线，然后转换为小写
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _discover_commands(self):
        """自动发现命令类（支持递归搜索子文件夹）"""
        commands = {}
        
        # 获取当前模块所在的目录
        current_dir = os.path.dirname(__file__)
        
        # 递归搜索所有Python文件
        def scan_directory(directory: str, prefix: str = ""):
            """
            递归扫描目录
            
            Args:
                directory: 要扫描的目录
                prefix: 命令前缀（用于子文件夹）
            """
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                
                if os.path.isfile(item_path) and item.endswith('.py'):
                    # 跳过特殊文件
                    if item in ['__init__.py', 'command_manager.py', 'base_command.py']:
                        continue
                    
                    module_name = item[:-3]  # 去掉.py后缀
                    
                    try:
                        # 构建完整的模块路径
                        if prefix:
                            full_module_name = f'.{prefix}.{module_name}'
                            command_prefix = f"{prefix}."
                        else:
                            full_module_name = f'.{module_name}'
                            command_prefix = ""
                        
                        # 导入模块
                        module = importlib.import_module(full_module_name, package=__package__)
                        
                        # 检查模块中的所有类
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            # 检查是否继承自BaseCommand且不是BaseCommand本身
                            if (issubclass(obj, BaseCommand) and 
                                obj is not BaseCommand and 
                                name.endswith('Command')):
                                
                                # 生成命令名称：去掉Command后缀，转换为蛇形命名
                                base_command_name = self._snake_case(name[:-7])  # 去掉Command后缀
                                command_name = f"{command_prefix}{base_command_name}"
                                
                                # 获取类的文档字符串作为描述
                                description = obj.__doc__.strip() if obj.__doc__ else f"{name}命令"
                                
                                commands[command_name] = {
                                    'class': obj,
                                    'description': description,
                                    'module_path': full_module_name,
                                    'class_name': name
                                }
                                
                    except Exception as e:
                        print(f"⚠️  导入模块 {full_module_name} 失败: {e}")
                
                elif os.path.isdir(item_path) and not item.startswith('__'):
                    # 递归搜索子文件夹
                    sub_prefix = f"{prefix}.{item}" if prefix else item
                    
                    # 检查子文件夹是否有__init__.py文件，如果没有则创建
                    init_file = os.path.join(item_path, '__init__.py')
                    if not os.path.exists(init_file):
                        try:
                            with open(init_file, 'w', encoding='utf-8') as f:
                                f.write(f'"""\n{item}命令包\n"""\n')
                            print(f"📝 创建了 {init_file}")
                        except Exception as e:
                            print(f"⚠️  创建 {init_file} 失败: {e}")
                    
                    scan_directory(item_path, sub_prefix)
        
        # 从根目录开始扫描
        scan_directory(current_dir)
        
        return commands
    
    def _register_commands(self):
        """注册所有可用的命令"""
        discovered_commands = self._discover_commands()
        
        for command_name, command_info in discovered_commands.items():
            try:
                # 实例化命令类
                command_instance = command_info['class'](self.executor)
                self.commands[command_name] = command_instance
                
            except Exception as e:
                print(f"⚠️  注册命令 {command_name} 失败: {e}")
        
        # 只在调试模式或需要时显示
        # print(f"✅ 已注册 {len(self.commands)} 个命令: {list(self.commands.keys())}")
    
    def get_command(self, cmd_name: str):
        """
        获取命令实例
        
        Args:
            cmd_name: 命令名称
            
        Returns:
            BaseCommand: 命令实例
            
        Raises:
            ValueError: 如果命令不存在
        """
        if cmd_name not in self.commands:
            raise ValueError(f"未知命令: {cmd_name}")
        return self.commands[cmd_name]
    
    def execute_command(self, cmd_name: str, **kwargs):
        """
        执行命令
        
        Args:
            cmd_name: 命令名称
            **kwargs: 命令参数
            
        Returns:
            Any: 命令执行结果
        """
        command = self.get_command(cmd_name)
        return command.execute(**kwargs)
    
    def get_available_commands(self) -> Dict[str, str]:
        """
        获取所有可用命令的列表
        
        Returns:
            Dict[str, str]: 命令名称和描述的映射
        """
        discovered_commands = self._discover_commands()
        return {name: info['description'] for name, info in discovered_commands.items()}
