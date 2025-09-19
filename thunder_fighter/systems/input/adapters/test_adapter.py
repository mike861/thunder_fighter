"""
Test Adapter - Provides a fully controllable test environment

This module implements test adapters, providing a fully controllable input environment
that supports precise time control and state simulation for unit testing.

Note: The classes in this module are not pytest test classes, but Mock objects for unit testing.
"""

from typing import Dict, List, Optional, Set

from ..core.boundaries import Clock, EventSource, KeyboardState, Logger
from ..core.events import Event, EventType

# Tell pytest that this module does not contain test classes
__test__ = False


class MockEventSourceAdapter(EventSource):
    """Test Event Source - Fully controllable event queue"""

    __test__ = False  # Tell pytest this is not a test class

    def __init__(self):
        """Initializes the test event source."""
        self.events: List[Event] = []
        self._auto_timestamp = True
        self._current_time = 0.0

    def add_event(self, event: Event):
        """
        Adds a test event.

        Args:
            event: The event to add.
        """
        if self._auto_timestamp and event.timestamp == 0.0:
            event.timestamp = self._current_time
        self.events.append(event)

    def add_key_down(self, key_code: int, modifiers: Optional[Dict[str, bool]] = None):
        """
        Convenience method to add a key down event.

        Args:
            key_code: The key code.
            modifiers: The modifier key state.
        """
        self.add_event(
            Event(
                type=EventType.KEY_DOWN,
                key_code=key_code,
                modifiers=modifiers or {"ctrl": False, "shift": False, "alt": False},
            )
        )

    def add_key_up(self, key_code: int, modifiers: Optional[Dict[str, bool]] = None):
        """
        Convenience method to add a key up event.

        Args:
            key_code: The key code.
            modifiers: The modifier key state.
        """
        self.add_event(
            Event(
                type=EventType.KEY_UP,
                key_code=key_code,
                modifiers=modifiers or {"ctrl": False, "shift": False, "alt": False},
            )
        )

    def add_key_sequence(self, key_code: int, duration: float = 0.1):
        """
        Adds a key sequence (press then release).

        Args:
            key_code: The key code.
            duration: The key hold duration.
        """
        self.add_key_down(key_code)
        self.advance_time(duration)
        self.add_key_up(key_code)

    def poll_events(self) -> List[Event]:
        """
        Gets all pending events.

        Returns:
            A list of events (clears the internal queue).
        """
        events = self.events.copy()
        self.events.clear()
        return events

    def clear_events(self):
        """Clears the event queue."""
        self.events.clear()

    def set_auto_timestamp(self, enabled: bool):
        """Sets whether to automatically add timestamps."""
        self._auto_timestamp = enabled

    def advance_time(self, seconds: float):
        """Advances time (for timestamp generation)."""
        self._current_time += seconds

    def set_time(self, time: float):
        """Sets the current time."""
        self._current_time = time

    def get_pending_count(self) -> int:
        """Gets the number of pending events."""
        return len(self.events)


class MockKeyboardStateAdapter(KeyboardState):
    """Test Keyboard State - Fully controllable keyboard state simulation"""

    __test__ = False  # Tell pytest this is not a test class

    def __init__(self):
        """Initializes the test keyboard state."""
        self.pressed_keys: Set[int] = set()
        self._state_history: List[tuple[float, int, bool]] = []  # (time, key, pressed)

    def press_key(self, key_code: int):
        """
        Simulates a key press.

        Args:
            key_code: The key code.
        """
        self.pressed_keys.add(key_code)
        self._state_history.append((0.0, key_code, True))

    def release_key(self, key_code: int):
        """
        Simulates a key release.

        Args:
            key_code: The key code.
        """
        self.pressed_keys.discard(key_code)
        self._state_history.append((0.0, key_code, False))

    def press_keys(self, key_codes: List[int]):
        """
        Presses multiple keys simultaneously.

        Args:
            key_codes: A list of key codes.
        """
        for key_code in key_codes:
            self.press_key(key_code)

    def release_keys(self, key_codes: List[int]):
        """
        Releases multiple keys simultaneously.

        Args:
            key_codes: A list of key codes.
        """
        for key_code in key_codes:
            self.release_key(key_code)

    def clear_all(self):
        """Clears all key states."""
        self.pressed_keys.clear()
        self._state_history.clear()

    def is_pressed(self, key_code: int) -> bool:
        """
        Checks if a specific key is pressed.

        Args:
            key_code: The key code.

        Returns:
            True if the key is pressed, False otherwise.
        """
        return key_code in self.pressed_keys

    def get_pressed_keys(self) -> List[int]:
        """
        Gets all pressed keys.

        Returns:
            A list of all currently pressed key codes.
        """
        return list(self.pressed_keys)

    def simulate_key_sequence(self, key_codes: List[int], hold_time: float = 0.1):
        """
        Simulates a key sequence.

        Args:
            key_codes: The key code sequence.
            hold_time: The hold time for each key.
        """
        for key_code in key_codes:
            self.press_key(key_code)
            # In actual tests, this would be used with TestClock
            self.release_key(key_code)

    def get_state_history(self) -> List[tuple[float, int, bool]]:
        """Gets the state change history."""
        return self._state_history.copy()


class MockClockAdapter(Clock):
    """Test Clock - Fully controllable time flow"""

    __test__ = False  # Tell pytest this is not a test class

    def __init__(self, initial_time: float = 0.0):
        """
        Initializes the test clock.

        Args:
            initial_time: The initial time.
        """
        self.current_time = initial_time
        self._delta = 0.016  # Default 60 FPS
        self._last_time = initial_time
        self._time_history: List[float] = [initial_time]

    def advance(self, seconds: float):
        """
        Advances time.

        Args:
            seconds: The number of seconds to advance.
        """
        self._last_time = self.current_time
        self.current_time += seconds
        self._delta = seconds
        self._time_history.append(self.current_time)

    def advance_frames(self, frames: int, fps: int = 60):
        """
        Advances time by frames.

        Args:
            frames: The number of frames to advance.
            fps: The frame rate.
        """
        frame_time = 1.0 / fps
        self.advance(frames * frame_time)

    def set_time(self, time: float):
        """
        Sets the time directly.

        Args:
            time: The new time.
        """
        self._last_time = self.current_time
        self.current_time = time
        self._delta = time - self._last_time
        self._time_history.append(time)

    def now(self) -> float:
        """
        Gets the current time.

        Returns:
            The current timestamp (in seconds).
        """
        return self.current_time

    def delta_time(self) -> float:
        """
        Gets the frame time interval.

        Returns:
            The time interval from the last frame to this one (in seconds).
        """
        return self._delta

    def reset(self, time: float = 0.0):
        """Resets the clock."""
        self.current_time = time
        self._last_time = time
        self._delta = 0.0
        self._time_history = [time]

    def get_time_history(self) -> List[float]:
        """Gets the time change history."""
        return self._time_history.copy()


class MockLoggerAdapter(Logger):
    """Test Logger - Collects log messages for validation"""

    __test__ = False  # Tell pytest this is not a test class

    def __init__(self, print_logs: bool = False):
        """
        Initializes the test logger.

        Args:
            print_logs: Whether to print logs to the console.
        """
        self.print_logs = print_logs
        self.logs: List[tuple[str, str]] = []  # (level, message)

    def debug(self, message: str):
        """Logs a debug message."""
        self._log("DEBUG", message)

    def info(self, message: str):
        """Logs a general information message."""
        self._log("INFO", message)

    def warning(self, message: str):
        """Logs a warning message."""
        self._log("WARNING", message)

    def error(self, message: str):
        """Logs an error message."""
        self._log("ERROR", message)

    def _log(self, level: str, message: str):
        """Internal logging method."""
        self.logs.append((level, message))
        if self.print_logs:
            print(f"[{level}] {message}")

    def get_logs(self, level: Optional[str] = None) -> List[str]:
        """
        Gets log messages.

        Args:
            level: The log level to filter by (optional).

        Returns:
            A list of log messages.
        """
        if level:
            return [msg for lvl, msg in self.logs if lvl == level]
        return [msg for _, msg in self.logs]

    def clear_logs(self):
        """Clears the logs."""
        self.logs.clear()

    def has_level(self, level: str) -> bool:
        """Checks if there are logs of a specific level."""
        return any(lvl == level for lvl, _ in self.logs)

    def count_level(self, level: str) -> int:
        """Counts the number of logs of a specific level."""
        return sum(1 for lvl, _ in self.logs if lvl == level)


def create_test_environment(
    initial_time: float = 0.0, print_logs: bool = False
) -> tuple[MockEventSourceAdapter, MockKeyboardStateAdapter, MockClockAdapter, MockLoggerAdapter]:
    """
    Creates a complete test environment.

    Args:
        initial_time: The initial time.
        print_logs: Whether to print logs.

    Returns:
        A tuple of (event source, keyboard state, clock, logger).
    """
    event_source = MockEventSourceAdapter()
    keyboard_state = MockKeyboardStateAdapter()
    clock = MockClockAdapter(initial_time)
    logger = MockLoggerAdapter(print_logs)

    # Synchronize time
    event_source.set_time(initial_time)

    return event_source, keyboard_state, clock, logger


class MockScenarioBuilder:
    """Test Scenario Builder - Simplifies the creation of complex test scenarios"""

    __test__ = False  # Tell pytest this is not a test class

    def __init__(
        self, event_source: MockEventSourceAdapter, clock: MockClockAdapter, keyboard: MockKeyboardStateAdapter
    ):
        """
        Initializes the test scenario.

        Args:
            event_source: The test event source.
            clock: The test clock.
            keyboard: The test keyboard state.
        """
        self.event_source = event_source
        self.clock = clock
        self.keyboard = keyboard
        self._timeline: List[tuple[float, str, dict]] = []
        self._current_time = 0.0

    def at_time(self, time: float):
        """Sets the current operation time."""
        self._current_time = time
        return self

    def press_key(self, key_code: int, modifiers: Optional[Dict[str, bool]] = None):
        """Presses a key at the current time."""
        self.clock.set_time(self._current_time)
        self.event_source.set_time(self._current_time)
        self.event_source.add_key_down(key_code, modifiers)
        self.keyboard.press_key(key_code)
        return self

    def release_key(self, key_code: int, modifiers: Optional[Dict[str, bool]] = None):
        """Releases a key at the current time."""
        self.clock.set_time(self._current_time)
        self.event_source.set_time(self._current_time)
        self.event_source.add_key_up(key_code, modifiers)
        self.keyboard.release_key(key_code)
        return self

    def wait(self, seconds: float):
        """Waits for a specified time."""
        self._current_time += seconds
        return self

    def key_sequence(self, key_code: int, duration: float = 0.1):
        """Executes a key sequence (press-wait-release)."""
        self.press_key(key_code)
        self.wait(duration)
        self.release_key(key_code)
        return self


# For backward compatibility, keep the old names
TestEventSource = MockEventSourceAdapter
TestKeyboardState = MockKeyboardStateAdapter
TestClock = MockClockAdapter
TestLogger = MockLoggerAdapter
TestScenario = MockScenarioBuilder

# Use Mock prefix for public API
MockEventSource = MockEventSourceAdapter
MockKeyboardState = MockKeyboardStateAdapter
MockClock = MockClockAdapter
MockLogger = MockLoggerAdapter
MockScenario = MockScenarioBuilder
