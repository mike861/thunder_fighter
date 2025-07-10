"""
Thunder Fighter inputsystem

这个包提供了完全重构inputsystem,具有以下特性:
- 完全解耦架构,核心逻辑不依赖pygame
- 依赖注入支持,便于测试
- 命令模式,解耦input和game逻辑
- 测试友好设计

backward compatibility:
- 保留原有InputManager, InputHandler等接口
- 新InputSystem提供更好测试支持
"""

# 新inputsystem(suggesteduse)
from .facade import (
    InputSystem,
    create_for_production,
    create_for_testing,
    InputSystemBuilder
)

# 核心model
from .core.commands import Command, CommandType
from .core.events import Event, EventType

# boundaryinterface(供expanduse)
from .core.boundaries import EventSource, KeyboardState, Clock, Logger

# adapter(供advanceduseruse)
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

# 原有interface(backward compatibility)
from .manager import InputManager
from .handler import InputHandler
from .bindings import KeyBindings
from .events import InputEvent, InputEventType

# versioninformation
__version__ = "2.0.0"
__author__ = "Thunder Fighter Team"

# mainlyexport
__all__ = [
    # 新inputsystem
    'InputSystem',
    'create_for_production', 
    'create_for_testing',
    'InputSystemBuilder',
    
    # 核心model
    'Command',
    'CommandType',
    'Event', 
    'EventType',
    
    # boundaryinterface
    'EventSource',
    'KeyboardState',
    'Clock',
    'Logger',
    
    # Pygameadapter
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
    'TestScenario',
    
    # 原有interface(backward compatibility)
    'InputManager',
    'InputHandler', 
    'KeyBindings',
    'InputEvent',
    'InputEventType'
] 