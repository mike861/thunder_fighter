"""
Input Event System

This module defines input events and event types for decoupled communication
between input handling and game logic.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, Optional
import pygame


class InputEventType(Enum):
    """Types of input events."""
    
    # Movement events
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    STOP_MOVE_UP = "stop_move_up"
    STOP_MOVE_DOWN = "stop_move_down"
    STOP_MOVE_LEFT = "stop_move_left"
    STOP_MOVE_RIGHT = "stop_move_right"
    
    # Action events
    SHOOT = "shoot"
    STOP_SHOOT = "stop_shoot"
    LAUNCH_MISSILE = "launch_missile"
    
    # Game control events
    PAUSE = "pause"
    RESUME = "resume"
    QUIT = "quit"
    
    # Audio events
    TOGGLE_MUSIC = "toggle_music"
    TOGGLE_SOUND = "toggle_sound"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    
    # UI events
    CHANGE_LANGUAGE = "change_language"
    TOGGLE_DEV_MODE = "toggle_dev_mode"
    
    # Special events
    SKIP_ANIMATION = "skip_animation"
    RESTART_GAME = "restart_game"


@dataclass
class InputEvent:
    """
    Represents an input event with associated data.
    
    This class encapsulates input events in a way that decouples
    input handling from game logic processing.
    """
    
    event_type: InputEventType
    data: Dict[str, Any] = None
    timestamp: float = 0.0
    source: str = "unknown"
    
    def __post_init__(self):
        """Initialize default values after creation."""
        if self.data is None:
            self.data = {}
        
        if self.timestamp == 0.0:
            import time
            self.timestamp = time.time()
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """
        Get data from the event.
        
        Args:
            key: The data key to retrieve
            default: Default value if key not found
            
        Returns:
            The data value or default
        """
        return self.data.get(key, default)
    
    def set_data(self, key: str, value: Any):
        """
        Set data in the event.
        
        Args:
            key: The data key to set
            value: The value to set
        """
        self.data[key] = value
    
    def __str__(self):
        return f"InputEvent({self.event_type.value}, data={self.data})"


class InputEventFactory:
    """Factory for creating common input events."""
    
    @staticmethod
    def create_movement_event(direction: str, pressed: bool = True) -> InputEvent:
        """
        Create a movement event.
        
        Args:
            direction: Direction of movement (up, down, left, right)
            pressed: Whether the key is pressed or released
            
        Returns:
            InputEvent for movement
        """
        if pressed:
            event_type = {
                'up': InputEventType.MOVE_UP,
                'down': InputEventType.MOVE_DOWN,
                'left': InputEventType.MOVE_LEFT,
                'right': InputEventType.MOVE_RIGHT
            }.get(direction)
        else:
            event_type = {
                'up': InputEventType.STOP_MOVE_UP,
                'down': InputEventType.STOP_MOVE_DOWN,
                'left': InputEventType.STOP_MOVE_LEFT,
                'right': InputEventType.STOP_MOVE_RIGHT
            }.get(direction)
        
        return InputEvent(
            event_type=event_type,
            data={'direction': direction, 'pressed': pressed},
            source='keyboard'
        )
    
    @staticmethod
    def create_action_event(action: str, pressed: bool = True) -> InputEvent:
        """
        Create an action event.
        
        Args:
            action: Action type (shoot, missile)
            pressed: Whether the key is pressed or released
            
        Returns:
            InputEvent for action
        """
        if action == 'shoot':
            event_type = InputEventType.SHOOT if pressed else InputEventType.STOP_SHOOT
        elif action == 'missile':
            event_type = InputEventType.LAUNCH_MISSILE
        else:
            raise ValueError(f"Unknown action: {action}")
        
        return InputEvent(
            event_type=event_type,
            data={'action': action, 'pressed': pressed},
            source='keyboard'
        )
    
    @staticmethod
    def create_game_control_event(control: str) -> InputEvent:
        """
        Create a game control event.
        
        Args:
            control: Control type (pause, quit, etc.)
            
        Returns:
            InputEvent for game control
        """
        event_type_map = {
            'pause': InputEventType.PAUSE,
            'resume': InputEventType.RESUME,
            'quit': InputEventType.QUIT,
            'restart': InputEventType.RESTART_GAME,
            'skip': InputEventType.SKIP_ANIMATION
        }
        
        event_type = event_type_map.get(control)
        if not event_type:
            raise ValueError(f"Unknown control: {control}")
        
        return InputEvent(
            event_type=event_type,
            data={'control': control},
            source='keyboard'
        )
    
    @staticmethod
    def create_audio_event(audio_action: str) -> InputEvent:
        """
        Create an audio event.
        
        Args:
            audio_action: Audio action (toggle_music, volume_up, etc.)
            
        Returns:
            InputEvent for audio control
        """
        event_type_map = {
            'toggle_music': InputEventType.TOGGLE_MUSIC,
            'toggle_sound': InputEventType.TOGGLE_SOUND,
            'volume_up': InputEventType.VOLUME_UP,
            'volume_down': InputEventType.VOLUME_DOWN
        }
        
        event_type = event_type_map.get(audio_action)
        if not event_type:
            raise ValueError(f"Unknown audio action: {audio_action}")
        
        return InputEvent(
            event_type=event_type,
            data={'audio_action': audio_action},
            source='keyboard'
        )
    
    @staticmethod
    def create_ui_event(ui_action: str) -> InputEvent:
        """
        Create a UI event.
        
        Args:
            ui_action: UI action (change_language, toggle_dev_mode)
            
        Returns:
            InputEvent for UI control
        """
        event_type_map = {
            'change_language': InputEventType.CHANGE_LANGUAGE,
            'toggle_dev_mode': InputEventType.TOGGLE_DEV_MODE
        }
        
        event_type = event_type_map.get(ui_action)
        if not event_type:
            raise ValueError(f"Unknown UI action: {ui_action}")
        
        return InputEvent(
            event_type=event_type,
            data={'ui_action': ui_action},
            source='keyboard'
        ) 