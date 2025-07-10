"""
inputsystem门面 - 简化inputsystem接口

这个module提供了inputsystem主要接口,将复杂内部结构
隐藏在简单易用API后面.
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
    inputsystem门面
    
    提供简化接口来使用inputsystem,自动process适配器create和configuration.
    支持生产环境(pygame)和测试环境无缝切换.
    """
    
    def __init__(self,
                 event_source: Optional[EventSource] = None,
                 keyboard_state: Optional[KeyboardState] = None,
                 clock: Optional[Clock] = None,
                 logger: Optional[Logger] = None,
                 key_mapping: Optional[Dict[int, CommandType]] = None,
                 enable_debug: bool = False):
        """
        initializeinputsystem
        
        Args:
            event_source: event源接口(可选,默认使用pygame)
            keyboard_state: 键盘state接口(可选,默认使用pygame)
            clock: 时钟接口(可选,默认使用pygame)
            logger: 日志接口(可选,默认create简单日志器)
            key_mapping: 键位映射(可选,使用默认映射)
            enable_debug: whether启用调试日志
        """
        # if没有providedependency,usedefaultpygameadapter
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
        
        # settingsdefaultkey位mapping
        if key_mapping is None:
            key_mapping = self._create_default_key_mapping()
        
        # create核心process器
        self.processor = InputProcessor(
            event_source=self.event_source,
            keyboard_state=self.keyboard_state,
            clock=self.clock,
            key_mapping=key_mapping,
            logger=self.logger
        )
        
        # commandprocess器registrationtable
        self.command_handlers: Dict[CommandType, List[Callable]] = {}
        
        # systemstate
        self.enabled = True
        self.stats = {
            'total_commands': 0,
            'last_update_time': 0.0
        }
    
    def update(self) -> List[Command]:
        """
        updateinputsystem并return命令
        
        Returns:
            spawn命令列表
        """
        if not self.enabled:
            return []
        
        try:
            # processinput
            commands = self.processor.process()
            
            # executeregistrationprocess器
            for command in commands:
                self._execute_command_handlers(command)
            
            # updatestatistics
            self.stats['total_commands'] += len(commands)
            self.stats['last_update_time'] = self.clock.now()
            
            return commands
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error in input system update: {e}")
            return []
    
    def on_command(self, command_type: CommandType, handler: Callable[[Command], None]):
        """
        注册命令process器
        
        Args:
            command_type: 命令类型
            handler: process函数,接收Commandobjects作为parameters
        """
        if command_type not in self.command_handlers:
            self.command_handlers[command_type] = []
        
        self.command_handlers[command_type].append(handler)
        
        if self.logger:
            self.logger.debug(f"Registered handler for command {command_type}")
    
    def remove_command_handler(self, command_type: CommandType, handler: Callable[[Command], None]):
        """
        移除命令process器
        
        Args:
            command_type: 命令类型
            handler: 要移除process函数
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
        清除命令process器
        
        Args:
            command_type: 要清除命令类型(可选,None表示清除all)
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
        check键whether按下
        
        Args:
            key_code: 键码
            
        Returns:
            Trueif键被按下,elseFalse
        """
        return self.keyboard_state.is_pressed(key_code)
    
    def is_key_held(self, key_code: int) -> bool:
        """
        check键whether正在被长按
        
        Args:
            key_code: 键码
            
        Returns:
            Trueif键正在被长按,elseFalse
        """
        return self.processor.is_key_held(key_code)
    
    def get_held_keys(self) -> List[int]:
        """getall正在被长按key"""
        return self.processor.get_held_keys()
    
    def reset_state(self):
        """resetinputsystemstate"""
        self.processor.reset_state()
        if self.logger:
            self.logger.info("Input system state reset")
    
    def set_key_mapping(self, key_mapping: Dict[int, CommandType]):
        """
        update键位映射
        
        Args:
            key_mapping: 新键位映射
        """
        self.processor.set_key_mapping(key_mapping)
        if self.logger:
            self.logger.info(f"Updated key mapping with {len(key_mapping)} entries")
    
    def configure_repeat(self, delay: float, rate: float):
        """
        configuration按键重复
        
        Args:
            delay: 首次重复delayed(秒)
            rate: 重复间隔(秒)
        """
        self.processor.set_repeat_config(delay, rate)
    
    def configure_cooldown(self, cooldown: float):
        """
        configuration命令冷却time
        
        Args:
            cooldown: 冷却time(秒)
        """
        self.processor.set_cooldown(cooldown)
    
    def enable(self):
        """enabledinputsystem"""
        self.enabled = True
        if self.logger:
            self.logger.info("Input system enabled")
    
    def disable(self):
        """disabledinputsystem"""
        self.enabled = False
        if self.logger:
            self.logger.info("Input system disabled")
    
    def get_stats(self) -> Dict:
        """getinputsystemstatisticsinformation"""
        processor_stats = self.processor.get_stats()
        return {
            **self.stats,
            **processor_stats,
            'enabled': self.enabled,
            'handler_count': sum(len(handlers) for handlers in self.command_handlers.values())
        }
    
    def _execute_command_handlers(self, command: Command):
        """
        execute命令process器
        
        Args:
            command: 要process命令
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
        create默认键位映射
        
        Returns:
            默认键位映射字典
        """
        return {
            # directionkey
            pygame.K_UP: CommandType.MOVE_UP,
            pygame.K_DOWN: CommandType.MOVE_DOWN,
            pygame.K_LEFT: CommandType.MOVE_LEFT,
            pygame.K_RIGHT: CommandType.MOVE_RIGHT,
            
            # WASD
            pygame.K_w: CommandType.MOVE_UP,
            pygame.K_s: CommandType.MOVE_DOWN,
            pygame.K_a: CommandType.MOVE_LEFT,
            pygame.K_d: CommandType.MOVE_RIGHT,
            
            # actionkey
            pygame.K_SPACE: CommandType.SHOOT,
            pygame.K_x: CommandType.LAUNCH_MISSILE,
            
            # systemkey
            pygame.K_p: CommandType.PAUSE,
            pygame.K_ESCAPE: CommandType.QUIT,
            pygame.K_m: CommandType.TOGGLE_MUSIC,
            pygame.K_l: CommandType.CHANGE_LANGUAGE,
            
            # debuggingkey
            pygame.K_F1: CommandType.RESET_INPUT,
        }


def create_for_production(enable_debug: bool = False) -> InputSystem:
    """
    create生产环境inputsystem
    
    Args:
        enable_debug: whether启用调试日志
        
    Returns:
        configuration好InputSystem实例
    """
    return InputSystem(enable_debug=enable_debug)


def create_for_testing(initial_time: float = 0.0, 
                      print_logs: bool = False,
                      key_mapping: Optional[Dict[int, CommandType]] = None) -> tuple[InputSystem, dict]:
    """
    create测试环境inputsystem
    
    Args:
        initial_time: 初始time
        print_logs: whether打印日志
        key_mapping: 键位映射(可选)
        
    Returns:
        (InputSystem实例, 测试控制器字典) 元组
        测试控制器Contains: event_source, keyboard_state, clock, logger
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
    """inputsystembuild器 - provide流畅configurationAPI"""
    
    def __init__(self):
        """initializebuild器"""
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
        """usepygameadapter"""
        self._enable_debug = enable_debug
        return self
    
    def with_test_environment(self, initial_time: float = 0.0, print_logs: bool = False):
        """usetestingenvironment"""
        self._event_source, self._keyboard_state, self._clock, self._logger = create_test_environment(initial_time, print_logs)
        return self
    
    def with_key_mapping(self, key_mapping: Dict[int, CommandType]):
        """settingskey位mapping"""
        self._key_mapping = key_mapping
        return self
    
    def with_repeat_config(self, delay: float, rate: float):
        """settingsrepetitionconfiguration"""
        self._repeat_delay = delay
        self._repeat_rate = rate
        return self
    
    def with_cooldown(self, cooldown: float):
        """settings冷却time"""
        self._cooldown = cooldown
        return self
    
    def build(self) -> InputSystem:
        """buildinputsystem"""
        system = InputSystem(
            event_source=self._event_source,
            keyboard_state=self._keyboard_state,
            clock=self._clock,
            logger=self._logger,
            key_mapping=self._key_mapping,
            enable_debug=self._enable_debug
        )
        
        # applyconfiguration
        system.configure_repeat(self._repeat_delay, self._repeat_rate)
        system.configure_cooldown(self._cooldown)
        
        return system