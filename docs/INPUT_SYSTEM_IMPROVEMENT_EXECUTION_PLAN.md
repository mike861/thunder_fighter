# 输入系统可测试性改进执行计划

## 一、执行概述

基于评估文档的分析，输入系统存在以下核心问题：
1. 硬编码 pygame 依赖（评分：3/10）
2. 缺乏依赖注入机制
3. 时间耦合问题
4. 事件处理紧耦合

目标：将输入系统可测试性从 3/10 提升到 8/10

## 二、分阶段执行步骤

### 第一阶段：创建抽象接口层（第1-2天）

#### 步骤 1.1：创建时间提供者接口
**文件**: `thunder_fighter/input/providers/time_provider.py`

```python
from abc import ABC, abstractmethod
import time
import pygame

class TimeProvider(ABC):
    """时间服务抽象接口"""
    
    @abstractmethod
    def get_time(self) -> float:
        """获取当前时间戳（秒）"""
        pass
    
    @abstractmethod
    def get_ticks(self) -> int:
        """获取毫秒计时器"""
        pass

class SystemTimeProvider(TimeProvider):
    """生产环境的系统时间提供者"""
    
    def get_time(self) -> float:
        return time.time()
    
    def get_ticks(self) -> int:
        return pygame.time.get_ticks() if pygame.get_init() else int(time.time() * 1000)

class MockTimeProvider(TimeProvider):
    """测试用的可控时间提供者"""
    
    def __init__(self, initial_time: float = 1000.0):
        self.current_time = initial_time
        self.current_ticks = int(initial_time * 1000)
    
    def get_time(self) -> float:
        return self.current_time
    
    def get_ticks(self) -> int:
        return self.current_ticks
    
    def advance_time(self, seconds: float):
        """推进时间（测试辅助）"""
        self.current_time += seconds
        self.current_ticks += int(seconds * 1000)
```

**验收标准**：
- [ ] TimeProvider 接口定义完整
- [ ] SystemTimeProvider 正确实现系统时间
- [ ] MockTimeProvider 支持时间控制
- [ ] 单元测试覆盖所有方法

#### 步骤 1.2：创建键盘状态提供者接口
**文件**: `thunder_fighter/input/providers/keyboard_provider.py`

```python
from abc import ABC, abstractmethod
from typing import Dict
import pygame

class KeyboardStateProvider(ABC):
    """键盘状态抽象接口"""
    
    @abstractmethod
    def get_pressed_keys(self) -> Dict[int, bool]:
        """获取所有按键状态"""
        pass
    
    @abstractmethod
    def is_key_pressed(self, key: int) -> bool:
        """检查特定键是否按下"""
        pass

class PygameKeyboardStateProvider(KeyboardStateProvider):
    """生产环境的 pygame 键盘状态提供者"""
    
    def get_pressed_keys(self) -> Dict[int, bool]:
        if not pygame.get_init():
            return {}
        keys = pygame.key.get_pressed()
        return {i: bool(keys[i]) for i in range(len(keys))}
    
    def is_key_pressed(self, key: int) -> bool:
        if not pygame.get_init():
            return False
        keys = pygame.key.get_pressed()
        return bool(keys[key]) if 0 <= key < len(keys) else False

class MemoryKeyboardStateProvider(KeyboardStateProvider):
    """测试用的内存键盘状态提供者"""
    
    def __init__(self, pressed_keys: Dict[int, bool] = None):
        self.pressed_keys = pressed_keys or {}
    
    def get_pressed_keys(self) -> Dict[int, bool]:
        return self.pressed_keys.copy()
    
    def is_key_pressed(self, key: int) -> bool:
        return self.pressed_keys.get(key, False)
    
    def set_key_pressed(self, key: int, pressed: bool):
        """设置按键状态（测试辅助）"""
        self.pressed_keys[key] = pressed
    
    def clear_all(self):
        """清除所有按键状态（测试辅助）"""
        self.pressed_keys.clear()
```

**验收标准**：
- [ ] KeyboardStateProvider 接口定义完整
- [ ] PygameKeyboardStateProvider 正确封装 pygame
- [ ] MemoryKeyboardStateProvider 支持状态控制
- [ ] 错误处理完善（pygame 未初始化等）

### 第二阶段：重构 InputEvent 支持时间注入（第2天）

#### 步骤 2.1：创建 InputEventFactory
**文件**: `thunder_fighter/input/event_factory.py`

```python
from typing import Dict, Any, Optional
from thunder_fighter.input.input_events import InputEvent, InputEventType
from thunder_fighter.input.providers.time_provider import TimeProvider, SystemTimeProvider

class InputEventFactory:
    """输入事件工厂，支持时间注入"""
    
    def __init__(self, time_provider: Optional[TimeProvider] = None):
        self.time_provider = time_provider or SystemTimeProvider()
    
    def create_event(self, 
                    event_type: InputEventType, 
                    data: Dict[str, Any] = None,
                    timestamp: float = 0.0) -> InputEvent:
        """创建带时间戳的输入事件"""
        if timestamp == 0.0:
            timestamp = self.time_provider.get_time()
        
        return InputEvent(
            event_type=event_type,
            data=data or {},
            timestamp=timestamp
        )
    
    def create_movement_event(self, direction: str, pressed: bool = True) -> InputEvent:
        """创建移动事件的便捷方法"""
        event_type_map = {
            'up': InputEventType.MOVE_UP,
            'down': InputEventType.MOVE_DOWN,
            'left': InputEventType.MOVE_LEFT,
            'right': InputEventType.MOVE_RIGHT
        }
        
        return self.create_event(
            event_type_map.get(direction, InputEventType.MOVE_UP),
            {'direction': direction, 'pressed': pressed}
        )
    
    def create_action_event(self, action: str) -> InputEvent:
        """创建动作事件的便捷方法"""
        action_map = {
            'shoot': InputEventType.SHOOT,
            'missile': InputEventType.LAUNCH_MISSILE,
            'pause': InputEventType.PAUSE,
            'quit': InputEventType.QUIT
        }
        
        return self.create_event(
            action_map.get(action, InputEventType.SHOOT),
            {'action': action}
        )
```

**验收标准**：
- [ ] InputEventFactory 支持时间注入
- [ ] 便捷方法覆盖常用事件类型
- [ ] 时间戳正确生成
- [ ] 单元测试验证工厂功能

#### 步骤 2.2：修改 InputEvent 支持依赖注入
**修改文件**: `thunder_fighter/input/input_events.py`

在 InputEvent 类中添加：
```python
def set_timestamp_if_empty(self, time_provider: TimeProvider):
    """使用时间提供者设置时间戳（如果未设置）"""
    if self.timestamp == 0.0:
        self.timestamp = time_provider.get_time()
```

### 第三阶段：重构 InputHandler 支持依赖注入（第3-4天）

#### 步骤 3.1：修改 InputHandler 构造函数
**修改文件**: `thunder_fighter/input/input_handler.py`

```python
from typing import Optional
from thunder_fighter.input.providers.time_provider import TimeProvider, SystemTimeProvider
from thunder_fighter.input.providers.keyboard_provider import KeyboardStateProvider, PygameKeyboardStateProvider
from thunder_fighter.input.event_factory import InputEventFactory

class InputHandler:
    def __init__(self, 
                 key_bindings: Optional[KeyBindings] = None,
                 keyboard_provider: Optional[KeyboardStateProvider] = None,
                 time_provider: Optional[TimeProvider] = None,
                 event_factory: Optional[InputEventFactory] = None):
        """
        初始化输入处理器，支持依赖注入
        
        Args:
            key_bindings: 键位绑定配置
            keyboard_provider: 键盘状态提供者
            time_provider: 时间提供者
            event_factory: 事件工厂
        """
        self.key_bindings = key_bindings or KeyBindings()
        self.keyboard_provider = keyboard_provider or PygameKeyboardStateProvider()
        self.time_provider = time_provider or SystemTimeProvider()
        self.event_factory = event_factory or InputEventFactory(self.time_provider)
        
        # 保留原有初始化逻辑
        self.pressed_keys = set()
        self.continuous_actions = set()
        self._last_activity_time = self.time_provider.get_ticks()
        # ... 其他初始化
```

#### 步骤 3.2：重构 _get_modifiers 方法
```python
def _get_modifiers(self) -> Dict[str, bool]:
    """获取修饰键状态 - 使用注入的键盘提供者"""
    return {
        'ctrl': (self.keyboard_provider.is_key_pressed(pygame.K_LCTRL) or 
                self.keyboard_provider.is_key_pressed(pygame.K_RCTRL)),
        'shift': (self.keyboard_provider.is_key_pressed(pygame.K_LSHIFT) or 
                 self.keyboard_provider.is_key_pressed(pygame.K_RSHIFT)),
        'alt': (self.keyboard_provider.is_key_pressed(pygame.K_LALT) or 
               self.keyboard_provider.is_key_pressed(pygame.K_RALT))
    }
```

**验收标准**：
- [ ] InputHandler 支持所有依赖注入
- [ ] 保持向后兼容（默认参数）
- [ ] 所有时间相关调用使用 time_provider
- [ ] 所有键盘状态调用使用 keyboard_provider

### 第四阶段：重构 InputManager 支持依赖注入（第4天）

#### 步骤 4.1：修改 InputManager 构造函数
**修改文件**: `thunder_fighter/input/input_manager.py`

```python
class InputManager:
    def __init__(self, 
                 key_bindings: Optional[KeyBindings] = None,
                 input_handler: Optional[InputHandler] = None,
                 event_factory: Optional[InputEventFactory] = None,
                 time_provider: Optional[TimeProvider] = None):
        """
        初始化输入管理器，支持依赖注入
        """
        # 创建共享的依赖
        self.time_provider = time_provider or SystemTimeProvider()
        self.event_factory = event_factory or InputEventFactory(self.time_provider)
        self.key_bindings = key_bindings or KeyBindings()
        
        # 如果没有提供 input_handler，创建一个
        if input_handler is None:
            self.input_handler = InputHandler(
                key_bindings=self.key_bindings,
                time_provider=self.time_provider,
                event_factory=self.event_factory
            )
        else:
            self.input_handler = input_handler
        
        # 其他初始化
        self.event_callbacks = {}
        self._is_paused = False
```

**验收标准**：
- [ ] InputManager 支持完整依赖注入
- [ ] 依赖共享正确（time_provider 等）
- [ ] 保持现有功能不变

### 第五阶段：创建综合测试套件（第5天）

#### 步骤 5.1：创建输入系统单元测试
**文件**: `tests/unit/test_input_system_improved.py`

```python
import pytest
from unittest.mock import Mock, patch
import pygame

from thunder_fighter.input import InputHandler, InputManager, InputEventType
from thunder_fighter.input.providers.time_provider import MockTimeProvider
from thunder_fighter.input.providers.keyboard_provider import MemoryKeyboardStateProvider
from thunder_fighter.input.event_factory import InputEventFactory

class TestInputHandlerWithDI:
    """测试改进后的 InputHandler"""
    
    def test_modifier_detection_without_pygame(self):
        """测试修饰键检测 - 无需 pygame"""
        # 设置测试环境
        mock_keyboard = MemoryKeyboardStateProvider()
        mock_keyboard.set_key_pressed(pygame.K_LCTRL, True)
        mock_keyboard.set_key_pressed(pygame.K_LSHIFT, False)
        
        handler = InputHandler(keyboard_provider=mock_keyboard)
        
        # 测试修饰键
        modifiers = handler._get_modifiers()
        assert modifiers['ctrl'] is True
        assert modifiers['shift'] is False
        assert modifiers['alt'] is False
    
    def test_event_timing_control(self):
        """测试事件时间控制"""
        mock_time = MockTimeProvider(1000.0)
        factory = InputEventFactory(mock_time)
        handler = InputHandler(time_provider=mock_time, event_factory=factory)
        
        # 创建事件并验证时间戳
        event = factory.create_event(InputEventType.PAUSE)
        assert event.timestamp == 1000.0
        
        # 推进时间
        mock_time.advance_time(5.0)
        event2 = factory.create_event(InputEventType.SHOOT)
        assert event2.timestamp == 1005.0
    
    def test_fallback_mechanism_isolation(self):
        """测试 fallback 机制 - 隔离测试"""
        mock_keyboard = MemoryKeyboardStateProvider()
        mock_time = MockTimeProvider(1000.0)
        
        handler = InputHandler(
            keyboard_provider=mock_keyboard,
            time_provider=mock_time
        )
        
        # 模拟 P 键按下但正常处理失败的场景
        mock_keyboard.set_key_pressed(pygame.K_p, True)
        
        # 创建模拟的 pygame 事件
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_p
        
        # 测试 fallback 处理
        events = handler._create_fallback_events(mock_event)
        assert len(events) > 0
        assert any(e.event_type == InputEventType.PAUSE for e in events)

class TestInputManagerWithDI:
    """测试改进后的 InputManager"""
    
    def test_full_integration_with_mocks(self):
        """完整集成测试 - 使用所有 mock"""
        mock_time = MockTimeProvider(1000.0)
        mock_keyboard = MemoryKeyboardStateProvider()
        
        # 创建完全可控的 InputManager
        manager = InputManager(
            time_provider=mock_time,
            input_handler=InputHandler(
                keyboard_provider=mock_keyboard,
                time_provider=mock_time
            )
        )
        
        # 注册回调
        pause_called = False
        def on_pause(event):
            nonlocal pause_called
            pause_called = True
        
        manager.add_event_callback(InputEventType.PAUSE, on_pause)
        
        # 模拟按键
        mock_keyboard.set_key_pressed(pygame.K_p, True)
        
        # 创建并处理事件
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_p
        
        # 通过某种方式触发事件处理
        # ... 测试逻辑
    
    def test_pause_cooldown_with_controlled_time(self):
        """测试暂停冷却 - 精确时间控制"""
        mock_time = MockTimeProvider(1000.0)
        manager = InputManager(time_provider=mock_time)
        
        # 第一次暂停
        manager.pause()
        assert manager.is_paused()
        
        # 立即尝试恢复（应该被冷却阻止）
        mock_time.advance_time(0.1)  # 100ms
        result = manager.resume()
        assert result is False  # 冷却中
        
        # 超过冷却时间后
        mock_time.advance_time(0.3)  # 再过300ms，总共400ms
        result = manager.resume()
        assert result is True
        assert not manager.is_paused()
```

**验收标准**：
- [ ] 所有核心功能都有对应的单元测试
- [ ] 测试不依赖 pygame 初始化
- [ ] 测试执行速度快（< 0.1秒/测试）
- [ ] 测试相互独立，无副作用

### 第六阶段：集成测试和回归验证（第5-6天）

#### 步骤 6.1：创建集成测试
**文件**: `tests/integration/test_input_system_integration.py`

```python
class TestInputSystemIntegration:
    """输入系统集成测试"""
    
    @pytest.fixture
    def game_with_mock_input(self):
        """创建带 mock 输入系统的游戏实例"""
        mock_time = MockTimeProvider(1000.0)
        mock_keyboard = MemoryKeyboardStateProvider()
        
        # 创建游戏实例，注入 mock 输入系统
        # ... 配置代码
        
    def test_game_pause_with_mock_input(self, game_with_mock_input):
        """测试游戏暂停功能"""
        game, mock_keyboard, mock_time = game_with_mock_input
        
        # 模拟 P 键按下
        mock_keyboard.set_key_pressed(pygame.K_p, True)
        
        # 处理输入
        game.handle_events()
        
        # 验证游戏已暂停
        assert game.paused is True
```

#### 步骤 6.2：运行回归测试
```bash
# 运行所有现有测试，确保改动不破坏功能
python -m pytest tests/ -v

# 运行特定的输入相关测试
python -m pytest tests/ -k "input" -v
```

**验收标准**：
- [ ] 所有现有测试通过（310+ 个）
- [ ] 新增测试覆盖所有新接口
- [ ] 集成测试验证实际游戏场景
- [ ] 性能测试确认无性能退化

## 三、验收标准总结

### 功能验收
1. **依赖注入**
   - [ ] InputHandler 支持注入所有依赖
   - [ ] InputManager 支持注入所有依赖
   - [ ] 默认行为与原代码完全一致

2. **测试能力**
   - [ ] 可以在不初始化 pygame 的情况下测试
   - [ ] 可以精确控制时间流逝
   - [ ] 可以模拟任意键盘状态
   - [ ] 测试执行速度提升 10 倍以上

3. **代码质量**
   - [ ] 无需访问私有方法进行测试
   - [ ] 测试代码清晰易懂
   - [ ] Mock 使用最小化

### 性能验收
- [ ] 游戏运行性能无明显变化（FPS 稳定）
- [ ] 内存使用无明显增加（< 1MB）
- [ ] 启动时间无明显延长（< 100ms）

### 兼容性验收
- [ ] 现有游戏功能完全正常
- [ ] 配置文件兼容
- [ ] 存档文件兼容（如有）

## 四、风险缓解措施

1. **分支策略**
   - 在独立分支 `feature/input-testability` 上开发
   - 每个阶段完成后创建检查点提交
   - 保留回滚能力

2. **测试策略**
   - 每个步骤完成后立即运行回归测试
   - 使用 `--lf` 选项快速重跑失败测试
   - 保持测试覆盖率监控

3. **代码审查**
   - 每个阶段完成后进行代码审查
   - 特别关注接口设计和向后兼容性
   - 文档同步更新

## 五、时间估算

- 第一阶段：1-2 天（创建抽象接口）
- 第二阶段：0.5 天（InputEvent 重构）
- 第三阶段：1-1.5 天（InputHandler 重构）
- 第四阶段：0.5 天（InputManager 重构）
- 第五阶段：1 天（测试套件）
- 第六阶段：0.5-1 天（集成和验收）

**总计：4.5-6 天**

## 六、成功标准

改进完成后，输入系统应该：
1. 可测试性评分达到 8/10
2. 新增 50+ 个高质量单元测试
3. 测试执行时间 < 5 秒（全部输入测试）
4. 测试覆盖率 > 90%
5. 无需 pygame 初始化即可测试核心逻辑

通过这个执行计划，我们可以系统地改进输入系统的可测试性，同时确保现有功能的稳定性。