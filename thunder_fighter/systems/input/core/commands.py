"""
Command Pattern Implementation - Decouples input from game logic

This module defines the game command system, converting input events into game commands,
-achieving complete decoupling between the input system and game logic.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict


class CommandType(Enum):
    """Game Command Type Enumeration"""
    
    # Movement commands
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    
    # Action commands
    SHOOT = "shoot"
    LAUNCH_MISSILE = "launch_missile"
    
    # System commands
    PAUSE = "pause"
    QUIT = "quit"
    TOGGLE_MUSIC = "toggle_music"
    TOGGLE_SOUND = "toggle_sound"
    CHANGE_LANGUAGE = "change_language"
    
    # Debug commands
    TOGGLE_DEBUG = "toggle_debug"
    RESET_INPUT = "reset_input"


@dataclass
class Command:
    """
    Game Command
    
    Represents a specific game command, including the command type, timestamp, and related data.
    This is the interface between the input system and the game logic.
    """
    type: CommandType
    timestamp: float
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        """Post-initialization processing to ensure the data dictionary always exists."""
        if self.data is None:
            self.data = {}
    
    def get_data(self, key: str, default=None):
        """Safely gets command data."""
        return self.data.get(key, default)
    
    def set_data(self, key: str, value: Any):
        """Sets command data."""
        self.data[key] = value
    
    def is_movement_command(self) -> bool:
        """Checks if it is a movement command."""
        return self.type in (
            CommandType.MOVE_UP, 
            CommandType.MOVE_DOWN, 
            CommandType.MOVE_LEFT, 
            CommandType.MOVE_RIGHT
        )
    
    def is_action_command(self) -> bool:
        """Checks if it is an action command."""
        return self.type in (
            CommandType.SHOOT, 
            CommandType.LAUNCH_MISSILE
        )
    
    def is_system_command(self) -> bool:
        """Checks if it is a system command."""
        return self.type in (
            CommandType.PAUSE,
            CommandType.QUIT,
            CommandType.TOGGLE_MUSIC,
            CommandType.TOGGLE_SOUND,
            CommandType.CHANGE_LANGUAGE,
            CommandType.TOGGLE_DEBUG,
            CommandType.RESET_INPUT
        )