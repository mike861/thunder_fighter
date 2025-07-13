# Input System Interface Testability Improvements

## 问题分析

Thunder Fighter 的输入系统虽然在功能分离方面做得很好，但在接口可测试性方面存在以下关键问题：

### 1. 硬编码依赖问题

**当前问题：**
```python
# InputHandler._get_modifiers() - 硬编码 pygame 依赖
def _get_modifiers(self) -> Dict[str, bool]:
    keys = pygame.key.get_pressed()  # 无法模拟测试
    return {
        'ctrl': keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL],
        'shift': keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT],
        'alt': keys[pygame.K_LALT] or keys[pygame.K_RALT]
    }
```

**改进建议：**
```python
# 1. 创建键盘状态提供者接口
from abc import ABC, abstractmethod
from typing import Dict, Any

class KeyboardStateProvider(ABC):
    @abstractmethod
    def get_pressed_keys(self) -> Dict[int, bool]:
        """获取当前按下的键状态"""
        pass
    
    @abstractmethod
    def is_key_pressed(self, key: int) -> bool:
        """检查特定键是否被按下"""
        pass

class PygameKeyboardStateProvider(KeyboardStateProvider):
    def get_pressed_keys(self) -> Dict[int, bool]:
        keys = pygame.key.get_pressed()
        return {i: keys[i] for i in range(len(keys))}
    
    def is_key_pressed(self, key: int) -> bool:
        return pygame.key.get_pressed()[key]

class MemoryKeyboardStateProvider(KeyboardStateProvider):
    def __init__(self, pressed_keys: Dict[int, bool] = None):
        self.pressed_keys = pressed_keys or {}
    
    def get_pressed_keys(self) -> Dict[int, bool]:
        return self.pressed_keys.copy()
    
    def is_key_pressed(self, key: int) -> bool:
        return self.pressed_keys.get(key, False)
    
    def set_key_pressed(self, key: int, pressed: bool):
        """测试辅助方法"""
        self.pressed_keys[key] = pressed

# 2. 修改 InputHandler 以支持依赖注入
class InputHandler:
    def __init__(self, 
                 key_bindings: Optional[KeyBindings] = None,
                 keyboard_provider: Optional[KeyboardStateProvider] = None,
                 time_provider: Optional[TimeProvider] = None):
        self.key_bindings = key_bindings or KeyBindings()
        self.keyboard_provider = keyboard_provider or PygameKeyboardStateProvider()
        self.time_provider = time_provider or SystemTimeProvider()
    
    def _get_modifiers(self) -> Dict[str, bool]:
        # 使用注入的键盘状态提供者
        return {
            'ctrl': (self.keyboard_provider.is_key_pressed(pygame.K_LCTRL) or 
                    self.keyboard_provider.is_key_pressed(pygame.K_RCTRL)),
            'shift': (self.keyboard_provider.is_key_pressed(pygame.K_LSHIFT) or 
                     self.keyboard_provider.is_key_pressed(pygame.K_RSHIFT)),
            'alt': (self.keyboard_provider.is_key_pressed(pygame.K_LALT) or 
                   self.keyboard_provider.is_key_pressed(pygame.K_RALT))
        }
```

### 2. 时间依赖抽象

**当前问题：**
```python
# InputEvent.__post_init__() - 直接时间耦合
if self.timestamp == 0.0:
    import time
    self.timestamp = time.time()  # 无法控制测试时间
```

**改进建议：**
```python
# 1. 创建时间提供者接口
class TimeProvider(ABC):
    @abstractmethod
    def get_time(self) -> float:
        """获取当前时间戳"""
        pass
    
    @abstractmethod
    def get_ticks(self) -> int:
        """获取毫秒计时器"""
        pass

class SystemTimeProvider(TimeProvider):
    def get_time(self) -> float:
        return time.time()
    
    def get_ticks(self) -> int:
        return pygame.time.get_ticks()

class MockTimeProvider(TimeProvider):
    def __init__(self, initial_time: float = 1000.0):
        self.current_time = initial_time
        self.current_ticks = int(initial_time * 1000)
    
    def get_time(self) -> float:
        return self.current_time
    
    def get_ticks(self) -> int:
        return self.current_ticks
    
    def advance_time(self, seconds: float):
        """测试辅助方法"""
        self.current_time += seconds
        self.current_ticks += int(seconds * 1000)

# 2. 修改 InputEvent 以支持时间注入
@dataclass
class InputEvent:
    event_type: InputEventType
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
    _time_provider: Optional[TimeProvider] = None
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            if self._time_provider:
                self.timestamp = self._time_provider.get_time()
            else:
                import time
                self.timestamp = time.time()

# 3. 创建带时间提供者的工厂方法
class InputEventFactory:
    def __init__(self, time_provider: Optional[TimeProvider] = None):
        self.time_provider = time_provider or SystemTimeProvider()
    
    def create_event(self, event_type: InputEventType, data: Dict[str, Any] = None) -> InputEvent:
        return InputEvent(
            event_type=event_type,
            data=data or {},
            _time_provider=self.time_provider
        )
```

### 3. 依赖注入重构

**当前问题：**
```python
# InputManager.__init__() - 内部创建依赖
class InputManager:
    def __init__(self):
        self.key_bindings = KeyBindings()
        self.input_handler = InputHandler(self.key_bindings)  # 硬编码依赖
```

**改进建议：**
```python
class InputManager:
    def __init__(self, 
                 key_bindings: Optional[KeyBindings] = None,
                 input_handler: Optional[InputHandler] = None,
                 event_factory: Optional[InputEventFactory] = None,
                 time_provider: Optional[TimeProvider] = None):
        
        # 使用依赖注入，提供默认实现
        self.time_provider = time_provider or SystemTimeProvider()
        self.key_bindings = key_bindings or KeyBindings()
        self.event_factory = event_factory or InputEventFactory(self.time_provider)
        self.input_handler = input_handler or InputHandler(
            key_bindings=self.key_bindings,
            time_provider=self.time_provider
        )
        
        # 其他初始化代码...
```

### 4. 事件处理抽象

**当前问题：**
```python
# InputHandler.process_pygame_events() - 直接处理 pygame 事件
def process_pygame_events(self, pygame_events: List[pygame.event.Event]) -> List[InputEvent]:
    # 紧耦合 pygame.event.Event 结构
```

**改进建议：**
```python
# 1. 创建通用事件接口
@dataclass
class GenericEvent:
    event_type: int
    key: Optional[int] = None
    button: Optional[int] = None
    pos: Optional[Tuple[int, int]] = None
    unicode: Optional[str] = None

class EventAdapter(ABC):
    @abstractmethod
    def adapt_events(self, raw_events: List[Any]) -> List[GenericEvent]:
        """将原始事件转换为通用事件格式"""
        pass

class PygameEventAdapter(EventAdapter):
    def adapt_events(self, pygame_events: List[pygame.event.Event]) -> List[GenericEvent]:
        generic_events = []
        for event in pygame_events:
            generic_event = GenericEvent(
                event_type=event.type,
                key=getattr(event, 'key', None),
                button=getattr(event, 'button', None),
                pos=getattr(event, 'pos', None),
                unicode=getattr(event, 'unicode', None)
            )
            generic_events.append(generic_event)
        return generic_events

class MockEventAdapter(EventAdapter):
    def __init__(self, mock_events: List[GenericEvent] = None):
        self.mock_events = mock_events or []
    
    def adapt_events(self, raw_events: List[Any]) -> List[GenericEvent]:
        return self.mock_events.copy()
    
    def add_mock_event(self, event: GenericEvent):
        """测试辅助方法"""
        self.mock_events.append(event)

# 2. 修改 InputHandler 以使用事件适配器
class InputHandler:
    def __init__(self, 
                 key_bindings: Optional[KeyBindings] = None,
                 keyboard_provider: Optional[KeyboardStateProvider] = None,
                 time_provider: Optional[TimeProvider] = None,
                 event_adapter: Optional[EventAdapter] = None):
        
        self.key_bindings = key_bindings or KeyBindings()
        self.keyboard_provider = keyboard_provider or PygameKeyboardStateProvider()
        self.time_provider = time_provider or SystemTimeProvider()
        self.event_adapter = event_adapter or PygameEventAdapter()
    
    def process_events(self, raw_events: List[Any]) -> List[InputEvent]:
        """处理通用事件而不是特定的 pygame 事件"""
        generic_events = self.event_adapter.adapt_events(raw_events)
        input_events = []
        
        for event in generic_events:
            # 使用通用事件结构处理
            input_event = self._process_generic_event(event)
            if input_event:
                input_events.append(input_event)
        
        return input_events
```

## 测试示例

应用这些改进后，单元测试将变得简单而可靠：

```python
class TestInputHandlerImproved:
    def test_modifier_detection_with_mock_keyboard(self):
        """测试修饰键检测 - 使用模拟键盘状态"""
        # 设置模拟键盘状态
        mock_keyboard = MemoryKeyboardStateProvider()
        mock_keyboard.set_key_pressed(pygame.K_LCTRL, True)
        mock_keyboard.set_key_pressed(pygame.K_LSHIFT, True)
        
        # 创建测试用的 InputHandler
        handler = InputHandler(keyboard_provider=mock_keyboard)
        
        # 测试修饰键检测
        modifiers = handler._get_modifiers()
        assert modifiers['ctrl'] is True
        assert modifiers['shift'] is True
        assert modifiers['alt'] is False
    
    def test_event_processing_with_controlled_time(self):
        """测试事件处理 - 使用可控时间"""
        mock_time = MockTimeProvider(1000.0)
        mock_events = MockEventAdapter([
            GenericEvent(event_type=pygame.KEYDOWN, key=pygame.K_SPACE)
        ])
        
        handler = InputHandler(
            time_provider=mock_time,
            event_adapter=mock_events
        )
        
        # 处理事件
        input_events = handler.process_events([])
        
        # 验证时间戳
        assert len(input_events) == 1
        assert input_events[0].timestamp == 1000.0
        
        # 推进时间并测试
        mock_time.advance_time(5.0)
        # 继续测试...
    
    def test_input_manager_integration(self):
        """测试 InputManager 集成 - 完全模拟环境"""
        mock_time = MockTimeProvider(1000.0)
        mock_keyboard = MemoryKeyboardStateProvider()
        mock_events = MockEventAdapter()
        
        # 创建完全可测试的 InputManager
        manager = InputManager(
            input_handler=InputHandler(
                keyboard_provider=mock_keyboard,
                time_provider=mock_time,
                event_adapter=mock_events
            ),
            time_provider=mock_time
        )
        
        # 模拟按键事件
        mock_events.add_mock_event(
            GenericEvent(event_type=pygame.KEYDOWN, key=pygame.K_p)
        )
        
        # 测试输入处理
        events = manager.update([])
        
        # 验证结果
        assert len(events) > 0
        assert events[0].event_type == InputEventType.PAUSE
```

## 实施优先级

**高优先级：**
1. 时间提供者抽象 - 影响所有时间相关测试
2. 键盘状态提供者 - 最常用的输入测试场景

**中优先级：**
3. InputManager 依赖注入重构
4. 事件适配器模式

**低优先级：**
5. 完整的事件处理抽象层

## 兼容性保证

所有改进都通过依赖注入实现，默认使用原有的 pygame 实现，确保：
- 现有代码无需修改
- 生产环境行为不变
- 测试环境可以使用模拟实现
- 渐进式重构可行

这些改进将显著提高输入系统的可测试性，同时保持代码的清晰度和可维护性。