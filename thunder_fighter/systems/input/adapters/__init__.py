"""
Input System Adapters Module

This package contains various adapter implementations for connecting core logic with external systems.
"""

from .pygame_adapter import PygameClock, PygameEventSource, PygameKeyboardState, PygameLogger, create_pygame_adapters
from .test_adapter import (
    TestClock,
    TestEventSource,
    TestKeyboardState,
    TestLogger,
    TestScenario,
    create_test_environment,
)

__all__ = [
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
    'TestScenario'
]
