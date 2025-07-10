"""
Pygame 适配器 - 隔离 pygame 依赖

这个moduleimplementations了 pygame related适配器,将 pygame event和state
转换为标准接口,隔离外部依赖.
"""

import pygame
import time
from typing import List, Optional, Dict
from ..core.events import Event, EventType
from ..core.boundaries import EventSource, KeyboardState, Clock, Logger


class PygameEventSource(EventSource):
    """Pygame event源adapter"""
    
    def __init__(self, logger: Optional[Logger] = None):
        """
        initialize Pygame event源
        
        Args:
            logger: 日志接口(可选)
        """
        self.logger = logger
        self._event_queue = []
        
    def poll_events(self) -> List[Event]:
        """
        getall待processevent
        
        Returns:
            转换后 Event objects列表
        """
        events = []
        try:
            # get pygame event
            pygame_events = pygame.event.get()
            
            for pg_event in pygame_events:
                if event := self._convert_event(pg_event):
                    events.append(event)
                    
            if self.logger and events:
                self.logger.debug(f"Polled {len(events)} events from pygame")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error polling pygame events: {e}")
            
        return events
    
    def clear_events(self):
        """cleareventqueue"""
        try:
            pygame.event.clear()
            if self.logger:
                self.logger.debug("Pygame event queue cleared")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error clearing pygame events: {e}")
    
    def _convert_event(self, pg_event) -> Optional[Event]:
        """
        转换 pygame event为标准event
        
        Args:
            pg_event: pygame eventobjects
            
        Returns:
            转换后 Event objects,或 None
        """
        try:
            if pg_event.type == pygame.KEYDOWN:
                return Event(
                    type=EventType.KEY_DOWN,
                    key_code=pg_event.key,
                    modifiers=self._get_modifiers()
                )
            elif pg_event.type == pygame.KEYUP:
                return Event(
                    type=EventType.KEY_UP,
                    key_code=pg_event.key,
                    modifiers=self._get_modifiers()
                )
            elif pg_event.type == pygame.MOUSEBUTTONDOWN:
                return Event(
                    type=EventType.MOUSE_DOWN,
                    mouse_button=pg_event.button,
                    position=pg_event.pos
                )
            elif pg_event.type == pygame.MOUSEBUTTONUP:
                return Event(
                    type=EventType.MOUSE_UP,
                    mouse_button=pg_event.button,
                    position=pg_event.pos
                )
            elif pg_event.type == pygame.MOUSEMOTION:
                return Event(
                    type=EventType.MOUSE_MOVE,
                    position=pg_event.pos
                )
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error converting pygame event: {e}")
                
        return None
    
    def _get_modifiers(self) -> Dict[str, bool]:
        """
        get修饰键state
        
        Returns:
            修饰键state字典
        """
        try:
            mods = pygame.key.get_mods()
            return {
                'ctrl': bool(mods & pygame.KMOD_CTRL),
                'shift': bool(mods & pygame.KMOD_SHIFT),
                'alt': bool(mods & pygame.KMOD_ALT)
            }
        except Exception:
            return {'ctrl': False, 'shift': False, 'alt': False}


class PygameKeyboardState(KeyboardState):
    """Pygame key盘stateadapter"""
    
    def __init__(self, logger: Optional[Logger] = None):
        """
        initialize Pygame 键盘state
        
        Args:
            logger: 日志接口(可选)
        """
        self.logger = logger
    
    def is_pressed(self, key_code: int) -> bool:
        """
        check指定键whether按下
        
        Args:
            key_code: 键码
            
        Returns:
            True if键被按下,else False
        """
        try:
            if not pygame.get_init():
                return False
                
            keys = pygame.key.get_pressed()
            return bool(keys[key_code]) if 0 <= key_code < len(keys) else False
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking key state: {e}")
            return False
    
    def get_pressed_keys(self) -> List[int]:
        """
        getall按下键
        
        Returns:
            当前按下all键码列表
        """
        try:
            if not pygame.get_init():
                return []
                
            keys = pygame.key.get_pressed()
            return [i for i in range(len(keys)) if keys[i]]
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting pressed keys: {e}")
            return []


class PygameClock(Clock):
    """Pygame 时钟adapter"""
    
    def __init__(self, logger: Optional[Logger] = None):
        """
        initialize Pygame 时钟
        
        Args:
            logger: 日志接口(可选)
        """
        self.logger = logger
        self.clock = pygame.time.Clock() if pygame.get_init() else None
        self._last_time = self._get_pygame_time()
        self._delta = 0.016  # default 60 FPS
        
    def now(self) -> float:
        """
        get当前time
        
        Returns:
            当前time戳(秒)
        """
        return self._get_pygame_time()
    
    def delta_time(self) -> float:
        """
        get帧time间隔
        
        Returns:
            上一帧到这一帧time间隔(秒)
        """
        current = self.now()
        if self._last_time > 0:
            self._delta = current - self._last_time
        self._last_time = current
        return self._delta
    
    def _get_pygame_time(self) -> float:
        """get pygame time或systemtime作为后备"""
        try:
            if pygame.get_init():
                return pygame.time.get_ticks() / 1000.0
            else:
                return time.time()
        except Exception:
            return time.time()
    
    def tick(self, fps: int = 60) -> int:
        """
        控制帧率(if使用 pygame 时钟)
        
        Args:
            fps: 目标帧率
            
        Returns:
            实际经过毫秒数
        """
        try:
            if self.clock:
                return self.clock.tick(fps)
            else:
                # simpletimecontrol
                target_delta = 1.0 / fps
                current_time = time.time()
                elapsed = current_time - self._last_time
                if elapsed < target_delta:
                    time.sleep(target_delta - elapsed)
                return int((time.time() - current_time) * 1000)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error in clock tick: {e}")
            return 16  # default 60 FPS


class PygameLogger(Logger):
    """simple Pygame compatiblelogimplementations"""
    
    def __init__(self, enable_debug: bool = False):
        """
        initialize日志器
        
        Args:
            enable_debug: whether启用调试output
        """
        self.enable_debug = enable_debug
    
    def debug(self, message: str):
        """recorddebugginginformation"""
        if self.enable_debug:
            print(f"[DEBUG] {message}")
    
    def info(self, message: str):
        """recordgenerallyinformation"""
        print(f"[INFO] {message}")
    
    def warning(self, message: str):
        """recordwarninginformation"""
        print(f"[WARNING] {message}")
    
    def error(self, message: str):
        """recorderrorinformation"""
        print(f"[ERROR] {message}")


def create_pygame_adapters(enable_debug: bool = False) -> tuple[PygameEventSource, PygameKeyboardState, PygameClock, PygameLogger]:
    """
    create完整 Pygame 适配器集合
    
    Args:
        enable_debug: whether启用调试日志
        
    Returns:
        (event源, 键盘state, 时钟, 日志器) 元组
    """
    logger = PygameLogger(enable_debug)
    event_source = PygameEventSource(logger)
    keyboard_state = PygameKeyboardState(logger)
    clock = PygameClock(logger)
    
    return event_source, keyboard_state, clock, logger