"""
输入系统核心模块

这个包包含输入系统的核心逻辑，完全独立于外部依赖。
"""

from .commands import Command, CommandType
from .events import Event, EventType
from .boundaries import EventSource, KeyboardState, Clock, Logger
from .processor import InputProcessor

__all__ = [
    'Command',
    'CommandType', 
    'Event',
    'EventType',
    'EventSource',
    'KeyboardState',
    'Clock',
    'Logger',
    'InputProcessor'
]