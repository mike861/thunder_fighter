"""
纯领域事件模型，不依赖任何外部库

这个模块定义了输入系统的核心事件模型，完全独立于pygame等外部依赖。
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any


class EventType(Enum):
    """事件类型枚举"""
    KEY_DOWN = "key_down"
    KEY_UP = "key_up" 
    MOUSE_DOWN = "mouse_down"
    MOUSE_UP = "mouse_up"
    MOUSE_MOVE = "mouse_move"


@dataclass
class Event:
    """
    纯净的事件模型
    
    这个类表示系统中的一个输入事件，不依赖任何外部库。
    所有的输入事件都会被转换为这种统一的格式。
    """
    type: EventType
    key_code: Optional[int] = None
    mouse_button: Optional[int] = None
    position: Optional[tuple[int, int]] = None
    modifiers: Dict[str, bool] = None
    timestamp: float = 0.0
    
    def __post_init__(self):
        """初始化后处理，确保修饰键字典总是存在"""
        if self.modifiers is None:
            self.modifiers = {'ctrl': False, 'shift': False, 'alt': False}
    
    def has_modifier(self, modifier: str) -> bool:
        """检查是否包含特定修饰键"""
        return self.modifiers.get(modifier, False)
    
    def is_key_event(self) -> bool:
        """检查是否为键盘事件"""
        return self.type in (EventType.KEY_DOWN, EventType.KEY_UP)
    
    def is_mouse_event(self) -> bool:
        """检查是否为鼠标事件"""
        return self.type in (EventType.MOUSE_DOWN, EventType.MOUSE_UP, EventType.MOUSE_MOVE)