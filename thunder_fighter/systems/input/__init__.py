"""
Thunder Fighter Input System

This package provides a completely refactored input system with the following features:
- Fully decoupled architecture, with core logic independent of pygame
- Dependency injection support for easy testing
- Command pattern to decouple input from game logic
- Test-friendly design

Backward Compatibility:
- Retains the original InputManager, InputHandler, etc. interfaces
- The new InputSystem provides better testing support
"""

# New input system (recommended)
# Adapters (for advanced users)
from .adapters.pygame_adapter import (
    PygameClock,
    PygameEventSource,
    PygameKeyboardState,
    PygameLogger,
    create_pygame_adapters,
)
from .adapters.test_adapter import (
    TestClock,
    TestEventSource,
    TestKeyboardState,
    TestLogger,
    TestScenario,
    create_test_environment,
)
from .bindings import KeyBindings

# Boundary interfaces (for extension)
from .core.boundaries import Clock, EventSource, KeyboardState, Logger

# Core models
from .core.commands import Command, CommandType
from .core.events import Event, EventType
from .events import InputEvent, InputEventType
from .facade import InputSystem, InputSystemBuilder, create_for_production, create_for_testing
from .handler import InputHandler

# Original interfaces (for backward compatibility)
from .manager import InputManager

# Version information
__version__ = "2.0.0"
__author__ = "Thunder Fighter Team"

# Main exports
__all__ = [
    # New input system
    "InputSystem",
    "create_for_production",
    "create_for_testing",
    "InputSystemBuilder",
    # Core models
    "Command",
    "CommandType",
    "Event",
    "EventType",
    # Boundary interfaces
    "EventSource",
    "KeyboardState",
    "Clock",
    "Logger",
    # Pygame adapters
    "PygameEventSource",
    "PygameKeyboardState",
    "PygameClock",
    "PygameLogger",
    "create_pygame_adapters",
    # Test adapters
    "TestEventSource",
    "TestKeyboardState",
    "TestClock",
    "TestLogger",
    "create_test_environment",
    "TestScenario",
    # Original interfaces (for backward compatibility)
    "InputManager",
    "InputHandler",
    "KeyBindings",
    "InputEvent",
    "InputEventType",
]
