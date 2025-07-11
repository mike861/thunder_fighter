"""
Input System Adapters Module

This package contains various adapter implementations for connecting core logic with external systems.
"""

from .pygame_adapter import (
    PygameEventSource,
    PygameKeyboardState,
    PygameClock,
    PygameLogger,
    create_pygame_adapters
)

from .test_adapter import (
    TestEventSource,
    TestKeyboardState,
    TestClock,
    TestLogger,
    create_test_environment,
    TestScenario
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
