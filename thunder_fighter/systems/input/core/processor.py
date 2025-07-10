"""
核心inputprocess逻辑,完全可测试

这个moduleimplementations了inputsystem核心逻辑,不依赖任何外部库,
通过依赖注入方式使用抽象接口,implementations完全可测试性.
"""

from typing import List, Dict, Callable, Optional, Set
from .events import Event, EventType
from .commands import Command, CommandType
from .boundaries import EventSource, KeyboardState, Clock, Logger


class InputProcessor:
    """
    纯净inputprocess器
    
    核心inputprocess逻辑,负责将inputevent转换为game命令.
    通过依赖注入使用外部接口,完全可测试.
    """
    
    def __init__(self,
                 event_source: EventSource,
                 keyboard_state: KeyboardState,
                 clock: Clock,
                 key_mapping: Dict[int, CommandType],
                 logger: Optional[Logger] = None):
        """
        initializeinputprocess器
        
        Args:
            event_source: event源接口
            keyboard_state: 键盘state接口  
            clock: 时钟接口
            key_mapping: 键码到命令类型映射
            logger: 日志接口(可选)
        """
        self.event_source = event_source
        self.keyboard_state = keyboard_state
        self.clock = clock
        self.key_mapping = key_mapping
        self.logger = logger
        
        # state跟踪
        self.held_keys: Set[int] = set()
        self.last_key_times: Dict[int, float] = {}
        self.last_command_times: Dict[CommandType, float] = {}
        
        # configurationparameters
        self.repeat_delay = 0.5  # 首次repetition前delayed
        self.repeat_rate = 0.05  # repetitioninterval
        self.cooldown_time = 0.2  # command冷却time
        
        # persistcommandset(如movement)
        self.continuous_commands = {
            CommandType.MOVE_UP,
            CommandType.MOVE_DOWN,
            CommandType.MOVE_LEFT,
            CommandType.MOVE_RIGHT
        }
        
        # statisticsinformation
        self.stats = {
            'events_processed': 0,
            'commands_generated': 0,
            'fallback_triggered': 0
        }
    
    def process(self) -> List[Command]:
        """
        processinput并return命令列表
        
        Returns:
            spawn命令列表
        """
        commands = []
        current_time = self.clock.now()
        
        try:
            # processeventqueue中event
            events = self.event_source.poll_events()
            for event in events:
                event.timestamp = current_time
                if cmd := self._process_event(event):
                    commands.append(cmd)
                self.stats['events_processed'] += 1
            
            # processpersist按key
            for key in self.held_keys.copy():
                if cmd := self._process_held_key(key, current_time):
                    commands.append(cmd)
            
            # updatestatistics
            self.stats['commands_generated'] += len(commands)
            
            if self.logger:
                if commands:
                    self.logger.debug(f"Generated {len(commands)} commands from {len(events)} events")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error processing input: {e}")
            # 在发生error时returnnulllist,avoid崩溃
            return []
        
        return commands
    
    def _process_event(self, event: Event) -> Optional[Command]:
        """
        process单个event
        
        Args:
            event: inputevent
            
        Returns:
            spawn命令(if有)
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
        process按键按下event
        
        Args:
            event: 按键event
            
        Returns:
            spawn命令(if有)
        """
        key_code = event.key_code
        current_time = event.timestamp
        
        # add到persist按keyset
        self.held_keys.add(key_code)
        self.last_key_times[key_code] = current_time
        
        # checkkey位mapping
        command_type = self.key_mapping.get(key_code)
        if not command_type:
            return None
        
        # checkcommand冷却
        last_command_time = self.last_command_times.get(command_type, -1)  # initialize为-1avoid冷却problem
        if current_time - last_command_time < self.cooldown_time:
            if self.logger:
                self.logger.debug(f"Command {command_type} on cooldown")
            return None
        
        # updatecommandtime
        self.last_command_times[command_type] = current_time
        
        # createcommand
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
        process按键释放event
        
        Args:
            event: 按键event
            
        Returns:
            spawn命令(if有)
        """
        key_code = event.key_code
        
        # 从persist按keyset中remove
        self.held_keys.discard(key_code)
        self.last_key_times.pop(key_code, None)
        
        # pair于某些command,可能需要在released时spawnstopcommand
        # 目前不需要,但保留interface
        return None
    
    def _process_held_key(self, key: int, current_time: float) -> Optional[Command]:
        """
        process持续按键(用于movement等连续动作)
        
        Args:
            key: 按键码
            current_time: 当前time
            
        Returns:
            spawn命令(if有)
        """
        command_type = self.key_mapping.get(key)
        if not command_type or command_type not in self.continuous_commands:
            return None
        
        last_time = self.last_key_times.get(key, current_time)
        
        # checkwhethertime forrepetitiontime
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
        """resetprocess器state"""
        self.held_keys.clear()
        self.last_key_times.clear()
        self.last_command_times.clear()
        self.event_source.clear_events()
        
        if self.logger:
            self.logger.info("Input processor state reset")
    
    def set_key_mapping(self, key_mapping: Dict[int, CommandType]):
        """updatekey位mapping"""
        self.key_mapping = key_mapping
        if self.logger:
            self.logger.info(f"Key mapping updated with {len(key_mapping)} entries")
    
    def set_repeat_config(self, delay: float, rate: float):
        """
        settings按键重复configuration
        
        Args:
            delay: 首次重复delayed(秒)
            rate: 重复间隔(秒)
        """
        self.repeat_delay = delay
        self.repeat_rate = rate
        
        if self.logger:
            self.logger.info(f"Repeat config updated: delay={delay}, rate={rate}")
    
    def set_cooldown(self, cooldown: float):
        """
        settings命令冷却time
        
        Args:
            cooldown: 冷却time(秒)
        """
        self.cooldown_time = cooldown
        
        if self.logger:
            self.logger.info(f"Cooldown time updated: {cooldown}")
    
    def get_stats(self) -> Dict[str, int]:
        """getprocess器statisticsinformation"""
        return self.stats.copy()
    
    def is_key_held(self, key_code: int) -> bool:
        """check指定keywhether正在被按住"""
        return key_code in self.held_keys
    
    def get_held_keys(self) -> List[int]:
        """getall正在被按住key"""
        return list(self.held_keys)