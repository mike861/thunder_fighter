"""
测试适配器 - 提供完全可控的测试环境

这个模块实现了测试用的适配器，提供完全可控的输入环境，
支持精确的时间控制和状态模拟，用于单元测试。

注意：本模块中的类不是pytest测试类，而是用于单元测试的Mock对象。
"""

from typing import List, Dict, Optional, Set
from ..core.events import Event, EventType
from ..core.boundaries import EventSource, KeyboardState, Clock, Logger

# 告诉 pytest 这个模块不包含测试类
__test__ = False


class MockEventSourceAdapter(EventSource):
    """测试事件源 - 完全可控的事件队列"""
    
    def __init__(self):
        """初始化测试事件源"""
        self.events: List[Event] = []
        self._auto_timestamp = True
        self._current_time = 0.0
    
    def add_event(self, event: Event):
        """
        添加测试事件
        
        Args:
            event: 要添加的事件
        """
        if self._auto_timestamp and event.timestamp == 0.0:
            event.timestamp = self._current_time
        self.events.append(event)
    
    def add_key_down(self, key_code: int, modifiers: Dict[str, bool] = None):
        """
        添加按键按下事件的便捷方法
        
        Args:
            key_code: 键码
            modifiers: 修饰键状态
        """
        self.add_event(Event(
            type=EventType.KEY_DOWN,
            key_code=key_code,
            modifiers=modifiers or {'ctrl': False, 'shift': False, 'alt': False}
        ))
    
    def add_key_up(self, key_code: int, modifiers: Dict[str, bool] = None):
        """
        添加按键释放事件的便捷方法
        
        Args:
            key_code: 键码
            modifiers: 修饰键状态
        """
        self.add_event(Event(
            type=EventType.KEY_UP,
            key_code=key_code,
            modifiers=modifiers or {'ctrl': False, 'shift': False, 'alt': False}
        ))
    
    def add_key_sequence(self, key_code: int, duration: float = 0.1):
        """
        添加按键序列（按下然后释放）
        
        Args:
            key_code: 键码
            duration: 按键持续时间
        """
        self.add_key_down(key_code)
        self.advance_time(duration)
        self.add_key_up(key_code)
    
    def poll_events(self) -> List[Event]:
        """
        获取所有待处理事件
        
        Returns:
            事件列表（会清空内部队列）
        """
        events = self.events.copy()
        self.events.clear()
        return events
    
    def clear_events(self):
        """清空事件队列"""
        self.events.clear()
    
    def set_auto_timestamp(self, enabled: bool):
        """设置是否自动添加时间戳"""
        self._auto_timestamp = enabled
    
    def advance_time(self, seconds: float):
        """推进时间（用于时间戳生成）"""
        self._current_time += seconds
    
    def set_time(self, time: float):
        """设置当前时间"""
        self._current_time = time
    
    def get_pending_count(self) -> int:
        """获取待处理事件数量"""
        return len(self.events)


class MockKeyboardStateAdapter(KeyboardState):
    """测试键盘状态 - 完全可控的键盘状态模拟"""
    
    def __init__(self):
        """初始化测试键盘状态"""
        self.pressed_keys: Set[int] = set()
        self._state_history: List[tuple[float, int, bool]] = []  # (time, key, pressed)
    
    def press_key(self, key_code: int):
        """
        模拟按键按下
        
        Args:
            key_code: 键码
        """
        self.pressed_keys.add(key_code)
        self._state_history.append((0.0, key_code, True))
    
    def release_key(self, key_code: int):
        """
        模拟按键释放
        
        Args:
            key_code: 键码
        """
        self.pressed_keys.discard(key_code)
        self._state_history.append((0.0, key_code, False))
    
    def press_keys(self, key_codes: List[int]):
        """
        同时按下多个键
        
        Args:
            key_codes: 键码列表
        """
        for key_code in key_codes:
            self.press_key(key_code)
    
    def release_keys(self, key_codes: List[int]):
        """
        同时释放多个键
        
        Args:
            key_codes: 键码列表
        """
        for key_code in key_codes:
            self.release_key(key_code)
    
    def clear_all(self):
        """清除所有按键状态"""
        self.pressed_keys.clear()
        self._state_history.clear()
    
    def is_pressed(self, key_code: int) -> bool:
        """
        检查指定键是否按下
        
        Args:
            key_code: 键码
            
        Returns:
            True 如果键被按下，否则 False
        """
        return key_code in self.pressed_keys
    
    def get_pressed_keys(self) -> List[int]:
        """
        获取所有按下的键
        
        Returns:
            当前按下的所有键码列表
        """
        return list(self.pressed_keys)
    
    def simulate_key_sequence(self, key_codes: List[int], hold_time: float = 0.1):
        """
        模拟按键序列
        
        Args:
            key_codes: 键码序列
            hold_time: 每个键的保持时间
        """
        for key_code in key_codes:
            self.press_key(key_code)
            # 在实际测试中，这里会配合 TestClock 使用
            self.release_key(key_code)
    
    def get_state_history(self) -> List[tuple[float, int, bool]]:
        """获取状态变更历史"""
        return self._state_history.copy()


class MockClockAdapter(Clock):
    """测试时钟 - 完全可控的时间流逝"""
    
    def __init__(self, initial_time: float = 0.0):
        """
        初始化测试时钟
        
        Args:
            initial_time: 初始时间
        """
        self.current_time = initial_time
        self._delta = 0.016  # 默认 60 FPS
        self._last_time = initial_time
        self._time_history: List[float] = [initial_time]
    
    def advance(self, seconds: float):
        """
        推进时间
        
        Args:
            seconds: 要推进的秒数
        """
        self._last_time = self.current_time
        self.current_time += seconds
        self._delta = seconds
        self._time_history.append(self.current_time)
    
    def advance_frames(self, frames: int, fps: int = 60):
        """
        按帧推进时间
        
        Args:
            frames: 要推进的帧数
            fps: 帧率
        """
        frame_time = 1.0 / fps
        self.advance(frames * frame_time)
    
    def set_time(self, time: float):
        """
        直接设置时间
        
        Args:
            time: 新的时间
        """
        self._last_time = self.current_time
        self.current_time = time
        self._delta = time - self._last_time
        self._time_history.append(time)
    
    def now(self) -> float:
        """
        获取当前时间
        
        Returns:
            当前时间戳（秒）
        """
        return self.current_time
    
    def delta_time(self) -> float:
        """
        获取帧时间间隔
        
        Returns:
            上一帧到这一帧的时间间隔（秒）
        """
        return self._delta
    
    def reset(self, time: float = 0.0):
        """重置时钟"""
        self.current_time = time
        self._last_time = time
        self._delta = 0.0
        self._time_history = [time]
    
    def get_time_history(self) -> List[float]:
        """获取时间变更历史"""
        return self._time_history.copy()


class MockLoggerAdapter(Logger):
    """测试日志器 - 收集日志消息用于验证"""
    
    def __init__(self, print_logs: bool = False):
        """
        初始化测试日志器
        
        Args:
            print_logs: 是否打印日志到控制台
        """
        self.print_logs = print_logs
        self.logs: List[tuple[str, str]] = []  # (level, message)
    
    def debug(self, message: str):
        """记录调试信息"""
        self._log('DEBUG', message)
    
    def info(self, message: str):
        """记录一般信息"""
        self._log('INFO', message)
    
    def warning(self, message: str):
        """记录警告信息"""
        self._log('WARNING', message)
    
    def error(self, message: str):
        """记录错误信息"""
        self._log('ERROR', message)
    
    def _log(self, level: str, message: str):
        """内部日志记录方法"""
        self.logs.append((level, message))
        if self.print_logs:
            print(f"[{level}] {message}")
    
    def get_logs(self, level: Optional[str] = None) -> List[str]:
        """
        获取日志消息
        
        Args:
            level: 过滤的日志级别（可选）
            
        Returns:
            日志消息列表
        """
        if level:
            return [msg for lvl, msg in self.logs if lvl == level]
        return [msg for _, msg in self.logs]
    
    def clear_logs(self):
        """清空日志"""
        self.logs.clear()
    
    def has_level(self, level: str) -> bool:
        """检查是否有指定级别的日志"""
        return any(lvl == level for lvl, _ in self.logs)
    
    def count_level(self, level: str) -> int:
        """统计指定级别的日志数量"""
        return sum(1 for lvl, _ in self.logs if lvl == level)


def create_test_environment(initial_time: float = 0.0, 
                          print_logs: bool = False) -> tuple[MockEventSourceAdapter, MockKeyboardStateAdapter, MockClockAdapter, MockLoggerAdapter]:
    """
    创建完整的测试环境
    
    Args:
        initial_time: 初始时间
        print_logs: 是否打印日志
        
    Returns:
        (事件源, 键盘状态, 时钟, 日志器) 的元组
    """
    event_source = MockEventSourceAdapter()
    keyboard_state = MockKeyboardStateAdapter()
    clock = MockClockAdapter(initial_time)
    logger = MockLoggerAdapter(print_logs)
    
    # 同步时间
    event_source.set_time(initial_time)
    
    return event_source, keyboard_state, clock, logger


class MockScenarioBuilder:
    """测试场景构建器 - 简化复杂测试场景的创建"""
    
    def __init__(self, event_source: MockEventSourceAdapter, clock: MockClockAdapter, keyboard: MockKeyboardStateAdapter):
        """
        初始化测试场景
        
        Args:
            event_source: 测试事件源
            clock: 测试时钟
            keyboard: 测试键盘状态
        """
        self.event_source = event_source
        self.clock = clock
        self.keyboard = keyboard
        self._timeline: List[tuple[float, str, dict]] = []
        self._current_time = 0.0
    
    def at_time(self, time: float):
        """设置当前操作时间"""
        self._current_time = time
        return self
    
    def press_key(self, key_code: int, modifiers: Dict[str, bool] = None):
        """在当前时间按下键"""
        self.clock.set_time(self._current_time)
        self.event_source.set_time(self._current_time)
        self.event_source.add_key_down(key_code, modifiers)
        self.keyboard.press_key(key_code)
        return self
    
    def release_key(self, key_code: int, modifiers: Dict[str, bool] = None):
        """在当前时间释放键"""
        self.clock.set_time(self._current_time)
        self.event_source.set_time(self._current_time)
        self.event_source.add_key_up(key_code, modifiers)
        self.keyboard.release_key(key_code)
        return self
    
    def wait(self, seconds: float):
        """等待指定时间"""
        self._current_time += seconds
        return self
    
    def key_sequence(self, key_code: int, duration: float = 0.1):
        """执行按键序列（按下-等待-释放）"""
        self.press_key(key_code)
        self.wait(duration)
        self.release_key(key_code)
        return self


# 为了向后兼容，保留旧的名称
TestEventSource = MockEventSourceAdapter
TestKeyboardState = MockKeyboardStateAdapter  
TestClock = MockClockAdapter
TestLogger = MockLoggerAdapter
TestScenario = MockScenarioBuilder

# 公开API使用Mock前缀
MockEventSource = MockEventSourceAdapter
MockKeyboardState = MockKeyboardStateAdapter
MockClock = MockClockAdapter
MockLogger = MockLoggerAdapter
MockScenario = MockScenarioBuilder