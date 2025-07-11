"""
Thunder Fighter Input System

This package provides a completely refactored input system with the following features:
- Fully decoupled architecture, core logic does not depend on pygame
- Dependency injection support for easy testing
- Command pattern to decouple input from game logic
- Test-friendly design

Backward Compatibility:
- Retains original interfaces like InputManager, InputHandler, etc.
- The new InputSystem provides better testing support
"""

# New input system (recommended)
from .input_system import (
    InputSystem,
    create_for_production,
    create_for_testing,
    InputSystemBuilder
)

# Core models
from .core.commands import Command, CommandType
from .core.events import Event, EventType

# Boundary interfaces (for extension)
from .core.boundaries import EventSource, KeyboardState, Clock, Logger

# Adapters (for advanced users)
from .adapters.pygame_adapter import (
    PygameEventSource,
    PygameKeyboardState, 
    PygameClock,
    PygameLogger,
    create_pygame_adapters
)

from .adapters.test_adapter import (
    TestEventSource,
    TestKeyboardState,
    TestClock,
    TestLogger,
    create_test_environment,
    TestScenario
)

# Original interfaces (for backward compatibility)
from .input_manager import InputManager
from .input_handler import InputHandler
from .key_bindings import KeyBindings
from .input_events import InputEvent, InputEventType

# Version information
__version__ = "2.0.0"
__author__ = "Thunder Fighter Team"

# Main exports
__all__ = [
    # New input system
    'InputSystem',
    'create_for_production', 
    'create_for_testing',
    'InputSystemBuilder',
    
    # Core models
    'Command',
    'CommandType',
    'Event', 
    'EventType',
    
    # Boundary interfaces
    'EventSource',
    'KeyboardState',
    'Clock',
    'Logger',
    
    # Pygame adapters
    'PygameEventSource',
    'PygameKeyboardState',
    'PygameClock', 
    'PygameLogger',
    'create_pygame_adapters',
    
    # Test adapters
    'TestEventSource',
    'TestKeyboardState',
    'TestClock',
    'TestLogger',
    'create_test_environment',
    'TestScenario',
    
    # Original interfaces (for backward compatibility)
    'InputManager',
    'InputHandler', 
    'KeyBindings',
    'InputEvent',
    'InputEventType'
]