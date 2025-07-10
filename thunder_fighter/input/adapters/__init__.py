"""
inputsystem适配器module

这个包Contains各种适配器implementations,用于连接核心逻辑和外部system.
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
    # Pygame adapter
    'PygameEventSource',
    'PygameKeyboardState',
    'PygameClock',
    'PygameLogger',
    'create_pygame_adapters',
    
    # testingadapter
    'TestEventSource',
    'TestKeyboardState',
    'TestClock',
    'TestLogger',
    'create_test_environment',
    'TestScenario'
]