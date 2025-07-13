# 输入系统清洁设计方案（无兼容性包袱版）

## 设计理念

既然项目处于测试阶段，我们可以采用最理想的设计，避免技术债务：

1. **完全解耦**：彻底分离 pygame 依赖
2. **纯净接口**：不保留任何向后兼容的冗余设计
3. **测试优先**：接口设计完全以可测试性为导向

## 一、核心架构重设计

### 1.1 领域模型分离

```python
# thunder_fighter/input/core/events.py
"""纯领域事件，不依赖任何外部库"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any

class EventType(Enum):
    """事件类型枚举"""
    KEY_DOWN = "key_down"
    KEY_UP = "key_up"
    MOUSE_DOWN = "mouse_down"
    MOUSE_UP = "mouse_up"
    MOUSE_MOVE = "mouse_move"

@dataclass
class Event:
    """纯净的事件模型"""
    type: EventType
    key_code: Optional[int] = None
    mouse_button: Optional[int] = None
    position: Optional[tuple[int, int]] = None
    modifiers: Dict[str, bool] = None
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.modifiers is None:
            self.modifiers = {'ctrl': False, 'shift': False, 'alt': False}
```

### 1.2 抽象边界接口

```python
# thunder_fighter/input/core/boundaries.py
"""系统边界接口定义"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
from .events import Event

class EventSource(ABC):
    """事件源抽象 - 隔离 pygame"""
    
    @abstractmethod
    def poll_events(self) -> List[Event]:
        """获取所有待处理事件"""
        pass
    
    @abstractmethod
    def clear_events(self):
        """清空事件队列"""
        pass

class KeyboardState(ABC):
    """键盘状态抽象"""
    
    @abstractmethod
    def is_pressed(self, key_code: int) -> bool:
        """检查键是否按下"""
        pass
    
    @abstractmethod
    def get_pressed_keys(self) -> List[int]:
        """获取所有按下的键"""
        pass

class Clock(ABC):
    """时钟抽象"""
    
    @abstractmethod
    def now(self) -> float:
        """获取当前时间（秒）"""
        pass
    
    @abstractmethod
    def delta_time(self) -> float:
        """获取帧时间间隔"""
        pass
```

### 1.3 核心输入处理器（无外部依赖）

```python
# thunder_fighter/input/core/processor.py
"""核心输入处理逻辑，完全可测试"""

from typing import List, Dict, Callable, Optional
from .events import Event, EventType
from .boundaries import EventSource, KeyboardState, Clock
from .commands import Command, CommandType

class InputProcessor:
    """纯净的输入处理器"""
    
    def __init__(self,
                 event_source: EventSource,
                 keyboard_state: KeyboardState,
                 clock: Clock,
                 key_mapping: Dict[int, CommandType]):
        self.event_source = event_source
        self.keyboard_state = keyboard_state
        self.clock = clock
        self.key_mapping = key_mapping
        self.command_handlers: Dict[CommandType, List[Callable]] = {}
        
        # 状态跟踪
        self.held_keys: set[int] = set()
        self.last_key_times: Dict[int, float] = {}
        self.repeat_delay = 0.5
        self.repeat_rate = 0.05
    
    def process(self) -> List[Command]:
        """处理输入并返回命令列表"""
        commands = []
        current_time = self.clock.now()
        
        # 处理事件
        for event in self.event_source.poll_events():
            event.timestamp = current_time
            if cmd := self._process_event(event):
                commands.append(cmd)
        
        # 处理持续按键
        for key in self.held_keys:
            if cmd := self._process_held_key(key, current_time):
                commands.append(cmd)
        
        return commands
    
    def _process_event(self, event: Event) -> Optional[Command]:
        """处理单个事件"""
        if event.type == EventType.KEY_DOWN:
            self.held_keys.add(event.key_code)
            self.last_key_times[event.key_code] = event.timestamp
            
            if cmd_type := self.key_mapping.get(event.key_code):
                return Command(
                    type=cmd_type,
                    timestamp=event.timestamp,
                    data={'key': event.key_code, 'modifiers': event.modifiers}
                )
        
        elif event.type == EventType.KEY_UP:
            self.held_keys.discard(event.key_code)
            self.last_key_times.pop(event.key_code, None)
        
        return None
    
    def _process_held_key(self, key: int, current_time: float) -> Optional[Command]:
        """处理持续按键（用于移动等）"""
        last_time = self.last_key_times.get(key, current_time)
        
        # 检查是否应该重复
        if current_time - last_time >= self.repeat_rate:
            self.last_key_times[key] = current_time
            
            if cmd_type := self.key_mapping.get(key):
                if cmd_type in [CommandType.MOVE_UP, CommandType.MOVE_DOWN,
                               CommandType.MOVE_LEFT, CommandType.MOVE_RIGHT]:
                    return Command(
                        type=cmd_type,
                        timestamp=current_time,
                        data={'continuous': True}
                    )
        
        return None
```

### 1.4 命令模式实现

```python
# thunder_fighter/input/core/commands.py
"""命令模式 - 解耦输入和游戏逻辑"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict

class CommandType(Enum):
    """游戏命令类型"""
    # 移动
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    
    # 动作
    SHOOT = "shoot"
    LAUNCH_MISSILE = "launch_missile"
    
    # 系统
    PAUSE = "pause"
    QUIT = "quit"
    TOGGLE_MUSIC = "toggle_music"
    TOGGLE_SOUND = "toggle_sound"
    CHANGE_LANGUAGE = "change_language"

@dataclass
class Command:
    """游戏命令"""
    type: CommandType
    timestamp: float
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
```

## 二、适配器层设计

### 2.1 Pygame 适配器

```python
# thunder_fighter/input/adapters/pygame_adapter.py
"""Pygame 适配器 - 隔离在这一层"""

import pygame
from typing import List
from ..core.events import Event, EventType
from ..core.boundaries import EventSource, KeyboardState, Clock

class PygameEventSource(EventSource):
    """Pygame 事件源适配器"""
    
    def poll_events(self) -> List[Event]:
        events = []
        for pg_event in pygame.event.get():
            if event := self._convert_event(pg_event):
                events.append(event)
        return events
    
    def _convert_event(self, pg_event) -> Optional[Event]:
        """转换 pygame 事件为领域事件"""
        if pg_event.type == pygame.KEYDOWN:
            return Event(
                type=EventType.KEY_DOWN,
                key_code=pg_event.key,
                modifiers=self._get_modifiers()
            )
        elif pg_event.type == pygame.KEYUP:
            return Event(
                type=EventType.KEY_UP,
                key_code=pg_event.key,
                modifiers=self._get_modifiers()
            )
        # ... 其他事件类型
        return None
    
    def _get_modifiers(self) -> Dict[str, bool]:
        """获取修饰键状态"""
        mods = pygame.key.get_mods()
        return {
            'ctrl': bool(mods & pygame.KMOD_CTRL),
            'shift': bool(mods & pygame.KMOD_SHIFT),
            'alt': bool(mods & pygame.KMOD_ALT)
        }
    
    def clear_events(self):
        pygame.event.clear()

class PygameKeyboardState(KeyboardState):
    """Pygame 键盘状态适配器"""
    
    def is_pressed(self, key_code: int) -> bool:
        keys = pygame.key.get_pressed()
        return bool(keys[key_code]) if 0 <= key_code < len(keys) else False
    
    def get_pressed_keys(self) -> List[int]:
        keys = pygame.key.get_pressed()
        return [i for i in range(len(keys)) if keys[i]]

class PygameClock(Clock):
    """Pygame 时钟适配器"""
    
    def __init__(self):
        self.clock = pygame.time.Clock()
        self._last_time = pygame.time.get_ticks() / 1000.0
    
    def now(self) -> float:
        return pygame.time.get_ticks() / 1000.0
    
    def delta_time(self) -> float:
        current = self.now()
        delta = current - self._last_time
        self._last_time = current
        return delta
```

### 2.2 测试适配器

```python
# thunder_fighter/input/adapters/test_adapter.py
"""测试用适配器"""

from typing import List, Dict
from ..core.events import Event, EventType
from ..core.boundaries import EventSource, KeyboardState, Clock

class TestEventSource(EventSource):
    """测试事件源"""
    
    def __init__(self):
        self.events: List[Event] = []
    
    def add_event(self, event: Event):
        """添加测试事件"""
        self.events.append(event)
    
    def poll_events(self) -> List[Event]:
        events = self.events.copy()
        self.events.clear()
        return events
    
    def clear_events(self):
        self.events.clear()

class TestKeyboardState(KeyboardState):
    """测试键盘状态"""
    
    def __init__(self):
        self.pressed_keys: set[int] = set()
    
    def press_key(self, key_code: int):
        self.pressed_keys.add(key_code)
    
    def release_key(self, key_code: int):
        self.pressed_keys.discard(key_code)
    
    def is_pressed(self, key_code: int) -> bool:
        return key_code in self.pressed_keys
    
    def get_pressed_keys(self) -> List[int]:
        return list(self.pressed_keys)

class TestClock(Clock):
    """测试时钟"""
    
    def __init__(self, initial_time: float = 0.0):
        self.current_time = initial_time
        self._delta = 0.016  # 默认60 FPS
    
    def advance(self, seconds: float):
        """推进时间"""
        self.current_time += seconds
        self._delta = seconds
    
    def now(self) -> float:
        return self.current_time
    
    def delta_time(self) -> float:
        return self._delta
```

## 三、简化的使用接口

### 3.1 输入系统门面

```python
# thunder_fighter/input/input_system.py
"""简化的输入系统接口"""

from typing import Dict, Callable, Optional
from .core.processor import InputProcessor
from .core.commands import Command, CommandType
from .core.boundaries import EventSource, KeyboardState, Clock
from .adapters.pygame_adapter import PygameEventSource, PygameKeyboardState, PygameClock

class InputSystem:
    """输入系统门面"""
    
    def __init__(self,
                 event_source: Optional[EventSource] = None,
                 keyboard_state: Optional[KeyboardState] = None,
                 clock: Optional[Clock] = None,
                 key_mapping: Optional[Dict[int, CommandType]] = None):
        
        # 使用提供的或默认的实现
        self.event_source = event_source or PygameEventSource()
        self.keyboard_state = keyboard_state or PygameKeyboardState()
        self.clock = clock or PygameClock()
        
        # 默认键位映射
        if key_mapping is None:
            import pygame
            key_mapping = {
                pygame.K_UP: CommandType.MOVE_UP,
                pygame.K_DOWN: CommandType.MOVE_DOWN,
                pygame.K_LEFT: CommandType.MOVE_LEFT,
                pygame.K_RIGHT: CommandType.MOVE_RIGHT,
                pygame.K_w: CommandType.MOVE_UP,
                pygame.K_s: CommandType.MOVE_DOWN,
                pygame.K_a: CommandType.MOVE_LEFT,
                pygame.K_d: CommandType.MOVE_RIGHT,
                pygame.K_SPACE: CommandType.SHOOT,
                pygame.K_x: CommandType.LAUNCH_MISSILE,
                pygame.K_p: CommandType.PAUSE,
                pygame.K_ESCAPE: CommandType.QUIT,
                pygame.K_m: CommandType.TOGGLE_MUSIC,
                pygame.K_l: CommandType.CHANGE_LANGUAGE,
            }
        
        self.processor = InputProcessor(
            self.event_source,
            self.keyboard_state,
            self.clock,
            key_mapping
        )
        
        self.command_handlers: Dict[CommandType, Callable] = {}
    
    def update(self) -> List[Command]:
        """更新输入系统并返回命令"""
        commands = self.processor.process()
        
        # 执行注册的处理器
        for command in commands:
            if handler := self.command_handlers.get(command.type):
                handler(command)
        
        return commands
    
    def on_command(self, command_type: CommandType, handler: Callable):
        """注册命令处理器"""
        self.command_handlers[command_type] = handler
    
    def is_key_pressed(self, key_code: int) -> bool:
        """检查键是否按下"""
        return self.keyboard_state.is_pressed(key_code)
```

## 四、测试示例

### 4.1 单元测试示例

```python
# tests/unit/test_input_processor.py

import pytest
from thunder_fighter.input.core.processor import InputProcessor
from thunder_fighter.input.core.commands import CommandType
from thunder_fighter.input.core.events import Event, EventType
from thunder_fighter.input.adapters.test_adapter import TestEventSource, TestKeyboardState, TestClock

class TestInputProcessor:
    """输入处理器单元测试"""
    
    def test_simple_key_press(self):
        """测试简单按键"""
        # 设置测试环境
        event_source = TestEventSource()
        keyboard = TestKeyboardState()
        clock = TestClock(1000.0)
        
        processor = InputProcessor(
            event_source=event_source,
            keyboard_state=keyboard,
            clock=clock,
            key_mapping={32: CommandType.SHOOT}  # 空格键
        )
        
        # 添加按键事件
        event_source.add_event(Event(
            type=EventType.KEY_DOWN,
            key_code=32
        ))
        
        # 处理输入
        commands = processor.process()
        
        # 验证
        assert len(commands) == 1
        assert commands[0].type == CommandType.SHOOT
        assert commands[0].timestamp == 1000.0
    
    def test_continuous_movement(self):
        """测试持续移动"""
        event_source = TestEventSource()
        keyboard = TestKeyboardState()
        clock = TestClock(0.0)
        
        processor = InputProcessor(
            event_source=event_source,
            keyboard_state=keyboard,
            clock=clock,
            key_mapping={87: CommandType.MOVE_UP}  # W键
        )
        
        # 按下 W 键
        event_source.add_event(Event(
            type=EventType.KEY_DOWN,
            key_code=87
        ))
        
        # 第一次处理
        commands = processor.process()
        assert len(commands) == 1
        assert commands[0].type == CommandType.MOVE_UP
        
        # 模拟时间流逝
        clock.advance(0.1)
        
        # 持续按键应该产生新命令
        commands = processor.process()
        assert len(commands) == 1
        assert commands[0].data['continuous'] is True
    
    def test_modifier_keys(self):
        """测试修饰键"""
        event_source = TestEventSource()
        keyboard = TestKeyboardState()
        clock = TestClock()
        
        processor = InputProcessor(
            event_source=event_source,
            keyboard_state=keyboard,
            clock=clock,
            key_mapping={83: CommandType.TOGGLE_SOUND}  # S键
        )
        
        # 添加带修饰键的事件
        event_source.add_event(Event(
            type=EventType.KEY_DOWN,
            key_code=83,
            modifiers={'ctrl': True, 'shift': False, 'alt': False}
        ))
        
        commands = processor.process()
        assert len(commands) == 1
        assert commands[0].data['modifiers']['ctrl'] is True
```

### 4.2 集成测试示例

```python
# tests/integration/test_input_system.py

class TestInputSystemIntegration:
    """输入系统集成测试"""
    
    def test_game_pause_flow(self):
        """测试完整的暂停流程"""
        # 使用测试适配器
        event_source = TestEventSource()
        keyboard = TestKeyboardState()
        clock = TestClock()
        
        input_system = InputSystem(
            event_source=event_source,
            keyboard_state=keyboard,
            clock=clock
        )
        
        # 注册暂停处理器
        paused = False
        def on_pause(cmd):
            nonlocal paused
            paused = not paused
        
        input_system.on_command(CommandType.PAUSE, on_pause)
        
        # 模拟 P 键按下
        event_source.add_event(Event(
            type=EventType.KEY_DOWN,
            key_code=80  # P键
        ))
        
        # 更新系统
        input_system.update()
        
        # 验证暂停状态
        assert paused is True
```

## 五、迁移策略

### 5.1 Game 类集成

```python
# thunder_fighter/game.py 的修改

class RefactoredGame:
    def __init__(self):
        # ... 其他初始化
        
        # 创建输入系统
        self.input_system = InputSystem()
        
        # 注册命令处理器
        self._setup_command_handlers()
    
    def _setup_command_handlers(self):
        """设置命令处理器"""
        # 移动命令
        self.input_system.on_command(CommandType.MOVE_UP, 
            lambda cmd: self._handle_move(cmd, 'up'))
        self.input_system.on_command(CommandType.MOVE_DOWN,
            lambda cmd: self._handle_move(cmd, 'down'))
        
        # 动作命令
        self.input_system.on_command(CommandType.SHOOT,
            lambda cmd: self.player.shoot())
        
        # 系统命令
        self.input_system.on_command(CommandType.PAUSE,
            lambda cmd: self.pause_manager.toggle_pause())
    
    def handle_events(self):
        """处理游戏事件"""
        # 简化的事件处理
        self.input_system.update()
        
        # 处理其他 pygame 事件（如窗口关闭）
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
```

## 六、优势总结

1. **完全解耦**：核心逻辑不依赖 pygame
2. **易于测试**：可以完全控制所有输入
3. **清晰分层**：领域层、适配器层、应用层分明
4. **扩展性强**：易于添加新的输入源（手柄、网络等）
5. **无技术债**：没有为兼容性做的妥协

这个设计完全以可测试性和清晰度为目标，充分利用了项目还在测试阶段的优势。