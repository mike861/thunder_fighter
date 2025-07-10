"""
测试适配器 - 提供完全可控测试环境

这个moduleimplementations了测试用适配器,提供完全可控input环境,
支持精确time控制和state模拟,用于单元测试.

注意:本module中类不是pytest测试类,而是用于单元测试Mockobjects.
"""

from typing import List, Dict, Optional, Set
from ..core.events import Event, EventType
from ..core.boundaries import EventSource, KeyboardState, Clock, Logger

# 告诉 pytest 这个module不Containstestingclass
__test__ = False


class MockEventSourceAdapter(EventSource):
    """testingevent源 - completelycontrollableeventqueue"""
    
    def __init__(self):
        """initializetestingevent源"""
        self.events: List[Event] = []
        self._auto_timestamp = True
        self._current_time = 0.0
    
    def add_event(self, event: Event):
        """
        添加测试event
        
        Args:
            event: 要添加event
        """
        if self._auto_timestamp and event.timestamp == 0.0:
            event.timestamp = self._current_time
        self.events.append(event)
    
    def add_key_down(self, key_code: int, modifiers: Dict[str, bool] = None):
        """
        添加按键按下event便捷方法
        
        Args:
            key_code: 键码
            modifiers: 修饰键state
        """
        self.add_event(Event(
            type=EventType.KEY_DOWN,
            key_code=key_code,
            modifiers=modifiers or {'ctrl': False, 'shift': False, 'alt': False}
        ))
    
    def add_key_up(self, key_code: int, modifiers: Dict[str, bool] = None):
        """
        添加按键释放event便捷方法
        
        Args:
            key_code: 键码
            modifiers: 修饰键state
        """
        self.add_event(Event(
            type=EventType.KEY_UP,
            key_code=key_code,
            modifiers=modifiers or {'ctrl': False, 'shift': False, 'alt': False}
        ))
    
    def add_key_sequence(self, key_code: int, duration: float = 0.1):
        """
        添加按键序列(按下然后释放)
        
        Args:
            key_code: 键码
            duration: 按键持续time
        """
        self.add_key_down(key_code)
        self.advance_time(duration)
        self.add_key_up(key_code)
    
    def poll_events(self) -> List[Event]:
        """
        getall待processevent
        
        Returns:
            event列表(会清空内部队列)
        """
        events = self.events.copy()
        self.events.clear()
        return events
    
    def clear_events(self):
        """cleareventqueue"""
        self.events.clear()
    
    def set_auto_timestamp(self, enabled: bool):
        """settingswhetherautomaticaddtime戳"""
        self._auto_timestamp = enabled
    
    def advance_time(self, seconds: float):
        """推进time(用于time戳spawn)"""
        self._current_time += seconds
    
    def set_time(self, time: float):
        """settingscurrenttime"""
        self._current_time = time
    
    def get_pending_count(self) -> int:
        """get待processeventquantity"""
        return len(self.events)


class MockKeyboardStateAdapter(KeyboardState):
    """testingkey盘state - completelycontrollablekey盘state模拟"""
    
    def __init__(self):
        """initializetestingkey盘state"""
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
        """清除all按keystate"""
        self.pressed_keys.clear()
        self._state_history.clear()
    
    def is_pressed(self, key_code: int) -> bool:
        """
        check指定键whether按下
        
        Args:
            key_code: 键码
            
        Returns:
            True if键被按下,else False
        """
        return key_code in self.pressed_keys
    
    def get_pressed_keys(self) -> List[int]:
        """
        getall按下键
        
        Returns:
            当前按下all键码列表
        """
        return list(self.pressed_keys)
    
    def simulate_key_sequence(self, key_codes: List[int], hold_time: float = 0.1):
        """
        模拟按键序列
        
        Args:
            key_codes: 键码序列
            hold_time: 每个键maintaintime
        """
        for key_code in key_codes:
            self.press_key(key_code)
            # 在实际testing中,这里会配合 TestClock use
            self.release_key(key_code)
    
    def get_state_history(self) -> List[tuple[float, int, bool]]:
        """getstatechangehistory"""
        return self._state_history.copy()


class MockClockAdapter(Clock):
    """testing时钟 - completelycontrollabletime流逝"""
    
    def __init__(self, initial_time: float = 0.0):
        """
        initialize测试时钟
        
        Args:
            initial_time: 初始time
        """
        self.current_time = initial_time
        self._delta = 0.016  # default 60 FPS
        self._last_time = initial_time
        self._time_history: List[float] = [initial_time]
    
    def advance(self, seconds: float):
        """
        推进time
        
        Args:
            seconds: 要推进秒数
        """
        self._last_time = self.current_time
        self.current_time += seconds
        self._delta = seconds
        self._time_history.append(self.current_time)
    
    def advance_frames(self, frames: int, fps: int = 60):
        """
        按帧推进time
        
        Args:
            frames: 要推进帧数
            fps: 帧率
        """
        frame_time = 1.0 / fps
        self.advance(frames * frame_time)
    
    def set_time(self, time: float):
        """
        直接settingstime
        
        Args:
            time: 新time
        """
        self._last_time = self.current_time
        self.current_time = time
        self._delta = time - self._last_time
        self._time_history.append(time)
    
    def now(self) -> float:
        """
        get当前time
        
        Returns:
            当前time戳(秒)
        """
        return self.current_time
    
    def delta_time(self) -> float:
        """
        get帧time间隔
        
        Returns:
            上一帧到这一帧time间隔(秒)
        """
        return self._delta
    
    def reset(self, time: float = 0.0):
        """reset时钟"""
        self.current_time = time
        self._last_time = time
        self._delta = 0.0
        self._time_history = [time]
    
    def get_time_history(self) -> List[float]:
        """gettimechangehistory"""
        return self._time_history.copy()


class MockLoggerAdapter(Logger):
    """testinglog器 - collectlogmessage用于verification"""
    
    def __init__(self, print_logs: bool = False):
        """
        initialize测试日志器
        
        Args:
            print_logs: whether打印日志到控制台
        """
        self.print_logs = print_logs
        self.logs: List[tuple[str, str]] = []  # (level, message)
    
    def debug(self, message: str):
        """recorddebugginginformation"""
        self._log('DEBUG', message)
    
    def info(self, message: str):
        """recordgenerallyinformation"""
        self._log('INFO', message)
    
    def warning(self, message: str):
        """recordwarninginformation"""
        self._log('WARNING', message)
    
    def error(self, message: str):
        """recorderrorinformation"""
        self._log('ERROR', message)
    
    def _log(self, level: str, message: str):
        """insidelogrecordmethod"""
        self.logs.append((level, message))
        if self.print_logs:
            print(f"[{level}] {message}")
    
    def get_logs(self, level: Optional[str] = None) -> List[str]:
        """
        get日志消息
        
        Args:
            level: 过滤日志级别(可选)
            
        Returns:
            日志消息列表
        """
        if level:
            return [msg for lvl, msg in self.logs if lvl == level]
        return [msg for _, msg in self.logs]
    
    def clear_logs(self):
        """clearlog"""
        self.logs.clear()
    
    def has_level(self, level: str) -> bool:
        """checkwhether有指定levellog"""
        return any(lvl == level for lvl, _ in self.logs)
    
    def count_level(self, level: str) -> int:
        """statistics指定levellogquantity"""
        return sum(1 for lvl, _ in self.logs if lvl == level)


def create_test_environment(initial_time: float = 0.0, 
                          print_logs: bool = False) -> tuple[MockEventSourceAdapter, MockKeyboardStateAdapter, MockClockAdapter, MockLoggerAdapter]:
    """
    create完整测试环境
    
    Args:
        initial_time: 初始time
        print_logs: whether打印日志
        
    Returns:
        (event源, 键盘state, 时钟, 日志器) 元组
    """
    event_source = MockEventSourceAdapter()
    keyboard_state = MockKeyboardStateAdapter()
    clock = MockClockAdapter(initial_time)
    logger = MockLoggerAdapter(print_logs)
    
    # synchronizedtime
    event_source.set_time(initial_time)
    
    return event_source, keyboard_state, clock, logger


class MockScenarioBuilder:
    """testingscenariobuild器 - 简化complextestingscenariocreate"""
    
    def __init__(self, event_source: MockEventSourceAdapter, clock: MockClockAdapter, keyboard: MockKeyboardStateAdapter):
        """
        initialize测试场景
        
        Args:
            event_source: 测试event源
            clock: 测试时钟
            keyboard: 测试键盘state
        """
        self.event_source = event_source
        self.clock = clock
        self.keyboard = keyboard
        self._timeline: List[tuple[float, str, dict]] = []
        self._current_time = 0.0
    
    def at_time(self, time: float):
        """settingscurrentoperationtime"""
        self._current_time = time
        return self
    
    def press_key(self, key_code: int, modifiers: Dict[str, bool] = None):
        """在currenttimepressedkey"""
        self.clock.set_time(self._current_time)
        self.event_source.set_time(self._current_time)
        self.event_source.add_key_down(key_code, modifiers)
        self.keyboard.press_key(key_code)
        return self
    
    def release_key(self, key_code: int, modifiers: Dict[str, bool] = None):
        """在currenttimereleasedkey"""
        self.clock.set_time(self._current_time)
        self.event_source.set_time(self._current_time)
        self.event_source.add_key_up(key_code, modifiers)
        self.keyboard.release_key(key_code)
        return self
    
    def wait(self, seconds: float):
        """等待指定time"""
        self._current_time += seconds
        return self
    
    def key_sequence(self, key_code: int, duration: float = 0.1):
        """execute按key序column(pressed-等待-released)"""
        self.press_key(key_code)
        self.wait(duration)
        self.release_key(key_code)
        return self


# 为了backward compatibility,保留旧name
TestEventSource = MockEventSourceAdapter
TestKeyboardState = MockKeyboardStateAdapter  
TestClock = MockClockAdapter
TestLogger = MockLoggerAdapter
TestScenario = MockScenarioBuilder

# publicityAPIuseMock前缀
MockEventSource = MockEventSourceAdapter
MockKeyboardState = MockKeyboardStateAdapter
MockClock = MockClockAdapter
MockLogger = MockLoggerAdapter
MockScenario = MockScenarioBuilder