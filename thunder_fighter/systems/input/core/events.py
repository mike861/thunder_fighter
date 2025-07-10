"""
纯领域event模型,不依赖任何外部库

这个moduledefinitions了inputsystem核心event模型,完全独立于pygame等外部依赖.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any


class EventType(Enum):
    """eventtypeenumeration"""
    KEY_DOWN = "key_down"
    KEY_UP = "key_up" 
    MOUSE_DOWN = "mouse_down"
    MOUSE_UP = "mouse_up"
    MOUSE_MOVE = "mouse_move"


@dataclass
class Event:
    """
    纯净event模型
    
    这个类表示system中一个inputevent,不依赖任何外部库.
    allinputevent都会被转换为这种统一格式.
    """
    type: EventType
    key_code: Optional[int] = None
    mouse_button: Optional[int] = None
    position: Optional[tuple[int, int]] = None
    modifiers: Dict[str, bool] = None
    timestamp: float = 0.0
    
    def __post_init__(self):
        """initialize后process,确保修饰keydictionaryalwaysexists"""
        if self.modifiers is None:
            self.modifiers = {'ctrl': False, 'shift': False, 'alt': False}
    
    def has_modifier(self, modifier: str) -> bool:
        """checkwhetherContainsspecific修饰key"""
        return self.modifiers.get(modifier, False)
    
    def is_key_event(self) -> bool:
        """checkwhether为key盘event"""
        return self.type in (EventType.KEY_DOWN, EventType.KEY_UP)
    
    def is_mouse_event(self) -> bool:
        """checkwhether为鼠标event"""
        return self.type in (EventType.MOUSE_DOWN, EventType.MOUSE_UP, EventType.MOUSE_MOVE)