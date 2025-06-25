"""
Input Management Package

This package provides centralized input handling for the Thunder Fighter game.
It separates input processing from game logic and provides a clean interface
for handling keyboard, mouse, and other input events.
"""

from .input_manager import InputManager
from .input_handler import InputHandler
from .key_bindings import KeyBindings
from .input_events import InputEvent, InputEventType

__all__ = [
    'InputManager',
    'InputHandler', 
    'KeyBindings',
    'InputEvent',
    'InputEventType'
] 