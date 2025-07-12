"""
核心输入处理逻辑，完全可测试

这个模块实现了输入系统的核心逻辑，不依赖任何外部库，
通过依赖注入的方式使用抽象接口，实现完全的可测试性。
"""

from typing import List, Dict, Callable, Optional, Set
from .events import Event, EventType
from .commands import Command, CommandType
from .boundaries import EventSource, KeyboardState, Clock, Logger


class InputProcessor:
    """
    纯净的输入处理器
    
    核心输入处理逻辑，负责将输入事件转换为游戏命令。
    通过依赖注入使用外部接口，完全可测试。
    """
    
    def __init__(self,
                 event_source: EventSource,
                 keyboard_state: KeyboardState,
                 clock: Clock,
                 key_mapping: Dict[int, CommandType],
                 logger: Optional[Logger] = None):
        """
        初始化输入处理器
        
        Args:
            event_source: 事件源接口
            keyboard_state: 键盘状态接口  
            clock: 时钟接口
            key_mapping: 键码到命令类型的映射
            logger: 日志接口（可选）
        """
        self.event_source = event_source
        self.keyboard_state = keyboard_state
        self.clock = clock
        self.key_mapping = key_mapping
        self.logger = logger
        
        # 状态跟踪
        self.held_keys: Set[int] = set()
        self.last_key_times: Dict[int, float] = {}
        self.last_command_times: Dict[CommandType, float] = {}
        
        # 配置参数
        self.repeat_delay = 0.5  # 首次重复前的延迟
        self.repeat_rate = 0.05  # 重复间隔
        self.cooldown_time = 0.2  # 命令冷却时间
        
        # 持续命令集合（如移动）
        self.continuous_commands = {
            CommandType.MOVE_UP,
            CommandType.MOVE_DOWN,
            CommandType.MOVE_LEFT,
            CommandType.MOVE_RIGHT
        }
        
        # 统计信息
        self.stats = {
            'events_processed': 0,
            'commands_generated': 0,
            'fallback_triggered': 0
        }
    
    def process(self) -> List[Command]:
        """
        处理输入并返回命令列表
        
        Returns:
            生成的命令列表
        """
        commands = []
        current_time = self.clock.now()
        
        try:
            # 处理事件队列中的事件
            events = self.event_source.poll_events()
            for event in events:
                event.timestamp = current_time
                if cmd := self._process_event(event):
                    commands.append(cmd)
                self.stats['events_processed'] += 1
            
            # 处理持续按键
            for key in self.held_keys.copy():
                if cmd := self._process_held_key(key, current_time):
                    commands.append(cmd)
            
            # 更新统计
            self.stats['commands_generated'] += len(commands)
            
            if self.logger:
                if commands:
                    self.logger.debug(f"Generated {len(commands)} commands from {len(events)} events")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error processing input: {e}")
            # 在发生错误时返回空列表，避免崩溃
            return []
        
        return commands
    
    def _process_event(self, event: Event) -> Optional[Command]:
        """
        处理单个事件
        
        Args:
            event: 输入事件
            
        Returns:
            生成的命令（如果有）
        """
        if not event.is_key_event():
            return None
        
        key_code = event.key_code
        if key_code is None:
            return None
        
        if event.type == EventType.KEY_DOWN:
            return self._handle_key_down(event)
        elif event.type == EventType.KEY_UP:
            return self._handle_key_up(event)
        
        return None
    
    def _handle_key_down(self, event: Event) -> Optional[Command]:
        """
        处理按键按下事件
        
        Args:
            event: 按键事件
            
        Returns:
            生成的命令（如果有）
        """
        key_code = event.key_code
        current_time = event.timestamp
        
        # 添加到持续按键集合
        self.held_keys.add(key_code)
        self.last_key_times[key_code] = current_time
        
        # 检查键位映射
        command_type = self.key_mapping.get(key_code)
        if not command_type:
            return None
        
        # 检查命令冷却
        last_command_time = self.last_command_times.get(command_type, -1)  # 初始化为-1避免冷却问题
        if current_time - last_command_time < self.cooldown_time:
            if self.logger:
                self.logger.debug(f"Command {command_type} on cooldown")
            return None
        
        # 更新命令时间
        self.last_command_times[command_type] = current_time
        
        # 创建命令
        return Command(
            type=command_type,
            timestamp=current_time,
            data={
                'key': key_code,
                'modifiers': event.modifiers.copy(),
                'continuous': False
            }
        )
    
    def _handle_key_up(self, event: Event) -> Optional[Command]:
        """
        处理按键释放事件
        
        Args:
            event: 按键事件
            
        Returns:
            生成的命令（如果有）
        """
        key_code = event.key_code
        
        # 从持续按键集合中移除
        self.held_keys.discard(key_code)
        self.last_key_times.pop(key_code, None)
        
        # 对于某些命令，可能需要在释放时生成停止命令
        # 目前不需要，但保留接口
        return None
    
    def _process_held_key(self, key: int, current_time: float) -> Optional[Command]:
        """
        处理持续按键（用于移动等连续动作）
        
        Args:
            key: 按键码
            current_time: 当前时间
            
        Returns:
            生成的命令（如果有）
        """
        command_type = self.key_mapping.get(key)
        if not command_type or command_type not in self.continuous_commands:
            return None
        
        last_time = self.last_key_times.get(key, current_time)
        
        # 检查是否到了重复时间
        time_since_last = current_time - last_time
        if time_since_last >= self.repeat_rate:
            self.last_key_times[key] = current_time
            
            return Command(
                type=command_type,
                timestamp=current_time,
                data={
                    'key': key,
                    'continuous': True,
                    'time_held': time_since_last
                }
            )
        
        return None
    
    def reset_state(self):
        """重置处理器状态"""
        self.held_keys.clear()
        self.last_key_times.clear()
        self.last_command_times.clear()
        self.event_source.clear_events()
        
        if self.logger:
            self.logger.info("Input processor state reset")
    
    def set_key_mapping(self, key_mapping: Dict[int, CommandType]):
        """更新键位映射"""
        self.key_mapping = key_mapping
        if self.logger:
            self.logger.info(f"Key mapping updated with {len(key_mapping)} entries")
    
    def set_repeat_config(self, delay: float, rate: float):
        """
        设置按键重复配置
        
        Args:
            delay: 首次重复延迟（秒）
            rate: 重复间隔（秒）
        """
        self.repeat_delay = delay
        self.repeat_rate = rate
        
        if self.logger:
            self.logger.info(f"Repeat config updated: delay={delay}, rate={rate}")
    
    def set_cooldown(self, cooldown: float):
        """
        设置命令冷却时间
        
        Args:
            cooldown: 冷却时间（秒）
        """
        self.cooldown_time = cooldown
        
        if self.logger:
            self.logger.info(f"Cooldown time updated: {cooldown}")
    
    def get_stats(self) -> Dict[str, int]:
        """获取处理器统计信息"""
        return self.stats.copy()
    
    def is_key_held(self, key_code: int) -> bool:
        """检查指定键是否正在被按住"""
        return key_code in self.held_keys
    
    def get_held_keys(self) -> List[int]:
        """获取所有正在被按住的键"""
        return list(self.held_keys)