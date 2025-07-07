"""
输入系统门面 - 简化的输入系统接口

这个模块提供了输入系统的主要接口，将复杂的内部结构
隐藏在简单易用的API后面。
"""

import pygame
from typing import Dict, Callable, Optional, List
from .core.processor import InputProcessor
from .core.commands import Command, CommandType
from .core.boundaries import EventSource, KeyboardState, Clock, Logger
from .adapters.pygame_adapter import create_pygame_adapters
from .adapters.test_adapter import create_test_environment


class InputSystem:
    """
    输入系统门面
    
    提供简化的接口来使用输入系统，自动处理适配器的创建和配置。
    支持生产环境（pygame）和测试环境的无缝切换。
    """
    
    def __init__(self,
                 event_source: Optional[EventSource] = None,
                 keyboard_state: Optional[KeyboardState] = None,
                 clock: Optional[Clock] = None,
                 logger: Optional[Logger] = None,
                 key_mapping: Optional[Dict[int, CommandType]] = None,
                 enable_debug: bool = False):
        """
        初始化输入系统
        
        Args:
            event_source: 事件源接口（可选，默认使用pygame）
            keyboard_state: 键盘状态接口（可选，默认使用pygame）
            clock: 时钟接口（可选，默认使用pygame）
            logger: 日志接口（可选，默认创建简单日志器）
            key_mapping: 键位映射（可选，使用默认映射）
            enable_debug: 是否启用调试日志
        """
        # 如果没有提供依赖，使用默认的pygame适配器
        if not all([event_source, keyboard_state, clock]):
            default_event_source, default_keyboard, default_clock, default_logger = create_pygame_adapters(enable_debug)
            
            self.event_source = event_source or default_event_source
            self.keyboard_state = keyboard_state or default_keyboard
            self.clock = clock or default_clock
            self.logger = logger or default_logger
        else:
            self.event_source = event_source
            self.keyboard_state = keyboard_state
            self.clock = clock
            self.logger = logger
        
        # 设置默认键位映射
        if key_mapping is None:
            key_mapping = self._create_default_key_mapping()
        
        # 创建核心处理器
        self.processor = InputProcessor(
            event_source=self.event_source,
            keyboard_state=self.keyboard_state,
            clock=self.clock,
            key_mapping=key_mapping,
            logger=self.logger
        )
        
        # 命令处理器注册表
        self.command_handlers: Dict[CommandType, List[Callable]] = {}
        
        # 系统状态
        self.enabled = True
        self.stats = {
            'total_commands': 0,
            'last_update_time': 0.0
        }
    
    def update(self) -> List[Command]:
        """
        更新输入系统并返回命令
        
        Returns:
            生成的命令列表
        """
        if not self.enabled:
            return []
        
        try:
            # 处理输入
            commands = self.processor.process()
            
            # 执行注册的处理器
            for command in commands:
                self._execute_command_handlers(command)
            
            # 更新统计
            self.stats['total_commands'] += len(commands)
            self.stats['last_update_time'] = self.clock.now()
            
            return commands
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error in input system update: {e}")
            return []
    
    def on_command(self, command_type: CommandType, handler: Callable[[Command], None]):
        """
        注册命令处理器
        
        Args:
            command_type: 命令类型
            handler: 处理函数，接收Command对象作为参数
        """
        if command_type not in self.command_handlers:
            self.command_handlers[command_type] = []
        
        self.command_handlers[command_type].append(handler)
        
        if self.logger:
            self.logger.debug(f"Registered handler for command {command_type}")
    
    def remove_command_handler(self, command_type: CommandType, handler: Callable[[Command], None]):
        """
        移除命令处理器
        
        Args:
            command_type: 命令类型
            handler: 要移除的处理函数
        """
        if command_type in self.command_handlers:
            try:
                self.command_handlers[command_type].remove(handler)
                if self.logger:
                    self.logger.debug(f"Removed handler for command {command_type}")
            except ValueError:
                if self.logger:
                    self.logger.warning(f"Handler not found for command {command_type}")
    
    def clear_handlers(self, command_type: Optional[CommandType] = None):
        """
        清除命令处理器
        
        Args:
            command_type: 要清除的命令类型（可选，None表示清除所有）
        """
        if command_type is None:
            self.command_handlers.clear()
            if self.logger:
                self.logger.info("Cleared all command handlers")
        else:
            self.command_handlers.pop(command_type, None)
            if self.logger:
                self.logger.info(f"Cleared handlers for command {command_type}")
    
    def is_key_pressed(self, key_code: int) -> bool:
        """
        检查键是否按下
        
        Args:
            key_code: 键码
            
        Returns:
            True如果键被按下，否则False
        """
        return self.keyboard_state.is_pressed(key_code)
    
    def is_key_held(self, key_code: int) -> bool:
        """
        检查键是否正在被长按
        
        Args:
            key_code: 键码
            
        Returns:
            True如果键正在被长按，否则False
        """
        return self.processor.is_key_held(key_code)
    
    def get_held_keys(self) -> List[int]:
        """获取所有正在被长按的键"""
        return self.processor.get_held_keys()
    
    def reset_state(self):
        """重置输入系统状态"""
        self.processor.reset_state()
        if self.logger:
            self.logger.info("Input system state reset")
    
    def set_key_mapping(self, key_mapping: Dict[int, CommandType]):
        """
        更新键位映射
        
        Args:
            key_mapping: 新的键位映射
        """
        self.processor.set_key_mapping(key_mapping)
        if self.logger:
            self.logger.info(f"Updated key mapping with {len(key_mapping)} entries")
    
    def configure_repeat(self, delay: float, rate: float):
        """
        配置按键重复
        
        Args:
            delay: 首次重复延迟（秒）
            rate: 重复间隔（秒）
        """
        self.processor.set_repeat_config(delay, rate)
    
    def configure_cooldown(self, cooldown: float):
        """
        配置命令冷却时间
        
        Args:
            cooldown: 冷却时间（秒）
        """
        self.processor.set_cooldown(cooldown)
    
    def enable(self):
        """启用输入系统"""
        self.enabled = True
        if self.logger:
            self.logger.info("Input system enabled")
    
    def disable(self):
        """禁用输入系统"""
        self.enabled = False
        if self.logger:
            self.logger.info("Input system disabled")
    
    def get_stats(self) -> Dict:
        """获取输入系统统计信息"""
        processor_stats = self.processor.get_stats()
        return {
            **self.stats,
            **processor_stats,
            'enabled': self.enabled,
            'handler_count': sum(len(handlers) for handlers in self.command_handlers.values())
        }
    
    def _execute_command_handlers(self, command: Command):
        """
        执行命令处理器
        
        Args:
            command: 要处理的命令
        """
        handlers = self.command_handlers.get(command.type, [])
        for handler in handlers:
            try:
                handler(command)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error in command handler for {command.type}: {e}")
    
    def _create_default_key_mapping(self) -> Dict[int, CommandType]:
        """
        创建默认键位映射
        
        Returns:
            默认的键位映射字典
        """
        return {
            # 方向键
            pygame.K_UP: CommandType.MOVE_UP,
            pygame.K_DOWN: CommandType.MOVE_DOWN,
            pygame.K_LEFT: CommandType.MOVE_LEFT,
            pygame.K_RIGHT: CommandType.MOVE_RIGHT,
            
            # WASD
            pygame.K_w: CommandType.MOVE_UP,
            pygame.K_s: CommandType.MOVE_DOWN,
            pygame.K_a: CommandType.MOVE_LEFT,
            pygame.K_d: CommandType.MOVE_RIGHT,
            
            # 动作键
            pygame.K_SPACE: CommandType.SHOOT,
            pygame.K_x: CommandType.LAUNCH_MISSILE,
            
            # 系统键
            pygame.K_p: CommandType.PAUSE,
            pygame.K_ESCAPE: CommandType.QUIT,
            pygame.K_m: CommandType.TOGGLE_MUSIC,
            pygame.K_l: CommandType.CHANGE_LANGUAGE,
            
            # 调试键
            pygame.K_F1: CommandType.RESET_INPUT,
        }


def create_for_production(enable_debug: bool = False) -> InputSystem:
    """
    创建生产环境的输入系统
    
    Args:
        enable_debug: 是否启用调试日志
        
    Returns:
        配置好的InputSystem实例
    """
    return InputSystem(enable_debug=enable_debug)


def create_for_testing(initial_time: float = 0.0, 
                      print_logs: bool = False,
                      key_mapping: Optional[Dict[int, CommandType]] = None) -> tuple[InputSystem, dict]:
    """
    创建测试环境的输入系统
    
    Args:
        initial_time: 初始时间
        print_logs: 是否打印日志
        key_mapping: 键位映射（可选）
        
    Returns:
        (InputSystem实例, 测试控制器字典) 的元组
        测试控制器包含: event_source, keyboard_state, clock, logger
    """
    event_source, keyboard_state, clock, logger = create_test_environment(initial_time, print_logs)
    
    input_system = InputSystem(
        event_source=event_source,
        keyboard_state=keyboard_state,
        clock=clock,
        logger=logger,
        key_mapping=key_mapping
    )
    
    controllers = {
        'event_source': event_source,
        'keyboard_state': keyboard_state,
        'clock': clock,
        'logger': logger
    }
    
    return input_system, controllers


class InputSystemBuilder:
    """输入系统构建器 - 提供流畅的配置API"""
    
    def __init__(self):
        """初始化构建器"""
        self._event_source = None
        self._keyboard_state = None
        self._clock = None
        self._logger = None
        self._key_mapping = None
        self._enable_debug = False
        self._repeat_delay = 0.5
        self._repeat_rate = 0.05
        self._cooldown = 0.2
    
    def with_pygame(self, enable_debug: bool = False):
        """使用pygame适配器"""
        self._enable_debug = enable_debug
        return self
    
    def with_test_environment(self, initial_time: float = 0.0, print_logs: bool = False):
        """使用测试环境"""
        self._event_source, self._keyboard_state, self._clock, self._logger = create_test_environment(initial_time, print_logs)
        return self
    
    def with_key_mapping(self, key_mapping: Dict[int, CommandType]):
        """设置键位映射"""
        self._key_mapping = key_mapping
        return self
    
    def with_repeat_config(self, delay: float, rate: float):
        """设置重复配置"""
        self._repeat_delay = delay
        self._repeat_rate = rate
        return self
    
    def with_cooldown(self, cooldown: float):
        """设置冷却时间"""
        self._cooldown = cooldown
        return self
    
    def build(self) -> InputSystem:
        """构建输入系统"""
        system = InputSystem(
            event_source=self._event_source,
            keyboard_state=self._keyboard_state,
            clock=self._clock,
            logger=self._logger,
            key_mapping=self._key_mapping,
            enable_debug=self._enable_debug
        )
        
        # 应用配置
        system.configure_repeat(self._repeat_delay, self._repeat_rate)
        system.configure_cooldown(self._cooldown)
        
        return system