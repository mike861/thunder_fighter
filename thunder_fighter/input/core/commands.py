"""
命令模式implementations - 解耦input和game逻辑

这个moduledefinitions了game命令system,将inputevent转换为game命令,
implementationsinputsystem和game逻辑完全解耦.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict


class CommandType(Enum):
    """gamecommandtypeenumeration"""
    
    # movementcommand
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    
    # actioncommand
    SHOOT = "shoot"
    LAUNCH_MISSILE = "launch_missile"
    
    # systemcommand
    PAUSE = "pause"
    QUIT = "quit"
    TOGGLE_MUSIC = "toggle_music"
    TOGGLE_SOUND = "toggle_sound"
    CHANGE_LANGUAGE = "change_language"
    
    # debuggingcommand
    TOGGLE_DEBUG = "toggle_debug"
    RESET_INPUT = "reset_input"


@dataclass
class Command:
    """
    game命令
    
    表示一个具体game命令,Contains命令类型、time戳和relateddata.
    这是inputsystem和game逻辑之间接口.
    """
    type: CommandType
    timestamp: float
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        """initialize后process,确保datadictionaryalwaysexists"""
        if self.data is None:
            self.data = {}
    
    def get_data(self, key: str, default=None):
        """securitygetcommanddata"""
        return self.data.get(key, default)
    
    def set_data(self, key: str, value: Any):
        """settingscommanddata"""
        self.data[key] = value
    
    def is_movement_command(self) -> bool:
        """checkwhether为movementcommand"""
        return self.type in (
            CommandType.MOVE_UP, 
            CommandType.MOVE_DOWN, 
            CommandType.MOVE_LEFT, 
            CommandType.MOVE_RIGHT
        )
    
    def is_action_command(self) -> bool:
        """checkwhether为actioncommand"""
        return self.type in (
            CommandType.SHOOT, 
            CommandType.LAUNCH_MISSILE
        )
    
    def is_system_command(self) -> bool:
        """checkwhether为systemcommand"""
        return self.type in (
            CommandType.PAUSE,
            CommandType.QUIT,
            CommandType.TOGGLE_MUSIC,
            CommandType.TOGGLE_SOUND,
            CommandType.CHANGE_LANGUAGE,
            CommandType.TOGGLE_DEBUG,
            CommandType.RESET_INPUT
        )