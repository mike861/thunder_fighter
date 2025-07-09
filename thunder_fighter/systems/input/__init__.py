"""
Thunder Fighter 输入系统

这个包提供了完全重构的输入系统，具有以下特性：
- 完全解耦的架构，核心逻辑不依赖pygame
- 依赖注入支持，便于测试
- 命令模式，解耦输入和游戏逻辑
- 测试友好的设计

向后兼容：
- 保留原有的InputManager, InputHandler等接口
- 新的InputSystem提供更好的测试支持
"""

# 新的输入系统（推荐使用）
from .facade import (
    InputSystem,
    create_for_production,
    create_for_testing,
    InputSystemBuilder
)

# 核心模型
from .core.commands import Command, CommandType
from .core.events import Event, EventType

# 边界接口（供扩展使用）
from .core.boundaries import EventSource, KeyboardState, Clock, Logger

# 适配器（供高级用户使用）
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

# 原有的接口（向后兼容）
from .manager import InputManager
from .handler import InputHandler
from .bindings import KeyBindings
from .events import InputEvent, InputEventType

# 版本信息
__version__ = "2.0.0"
__author__ = "Thunder Fighter Team"

# 主要导出
__all__ = [
    # 新的输入系统
    'InputSystem',
    'create_for_production', 
    'create_for_testing',
    'InputSystemBuilder',
    
    # 核心模型
    'Command',
    'CommandType',
    'Event', 
    'EventType',
    
    # 边界接口
    'EventSource',
    'KeyboardState',
    'Clock',
    'Logger',
    
    # Pygame适配器
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
    'TestScenario',
    
    # 原有接口（向后兼容）
    'InputManager',
    'InputHandler', 
    'KeyBindings',
    'InputEvent',
    'InputEventType'
] 