"""
输入系统适配器模块

这个包包含各种适配器实现，用于连接核心逻辑和外部系统。
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
    # Pygame 适配器
    'PygameEventSource',
    'PygameKeyboardState',
    'PygameClock',
    'PygameLogger',
    'create_pygame_adapters',
    
    # 测试适配器
    'TestEventSource',
    'TestKeyboardState',
    'TestClock',
    'TestLogger',
    'create_test_environment',
    'TestScenario'
]