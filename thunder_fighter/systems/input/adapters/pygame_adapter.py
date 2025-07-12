"""
Pygame Adapter - Isolates pygame dependencies

This module implements pygame-related adapters, converting pygame events and states
into standard interfaces to isolate external dependencies.
"""

import time
from typing import Dict, List, Optional

import pygame

from ..core.boundaries import Clock, EventSource, KeyboardState, Logger
from ..core.events import Event, EventType


class PygameEventSource(EventSource):
    """Pygame Event Source Adapter"""

    def __init__(self, logger: Optional[Logger] = None):
        """
        Initializes the Pygame event source.
        
        Args:
            logger: Logger interface (optional).
        """
        self.logger = logger
        self._event_queue = []

    def poll_events(self) -> List[Event]:
        """
        Gets all pending events.
        
        Returns:
            A list of converted Event objects.
        """
        events = []
        try:
            # Get pygame events
            pygame_events = pygame.event.get()

            for pg_event in pygame_events:
                if event := self._convert_event(pg_event):
                    events.append(event)

            if self.logger and events:
                self.logger.debug(f"Polled {len(events)} events from pygame")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error polling pygame events: {e}")

        return events

    def clear_events(self):
        """Clears the event queue."""
        try:
            pygame.event.clear()
            if self.logger:
                self.logger.debug("Pygame event queue cleared")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error clearing pygame events: {e}")

    def _convert_event(self, pg_event) -> Optional[Event]:
        """
        Converts a pygame event to a standard event.
        
        Args:
            pg_event: The pygame event object.
            
        Returns:
            The converted Event object, or None.
        """
        try:
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
            elif pg_event.type == pygame.MOUSEBUTTONDOWN:
                return Event(
                    type=EventType.MOUSE_DOWN,
                    mouse_button=pg_event.button,
                    position=pg_event.pos
                )
            elif pg_event.type == pygame.MOUSEBUTTONUP:
                return Event(
                    type=EventType.MOUSE_UP,
                    mouse_button=pg_event.button,
                    position=pg_event.pos
                )
            elif pg_event.type == pygame.MOUSEMOTION:
                return Event(
                    type=EventType.MOUSE_MOVE,
                    position=pg_event.pos
                )

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error converting pygame event: {e}")

        return None

    def _get_modifiers(self) -> Dict[str, bool]:
        """
        Gets the state of modifier keys.
        
        Returns:
            A dictionary of modifier key states.
        """
        try:
            mods = pygame.key.get_mods()
            return {
                'ctrl': bool(mods & pygame.KMOD_CTRL),
                'shift': bool(mods & pygame.KMOD_SHIFT),
                'alt': bool(mods & pygame.KMOD_ALT)
            }
        except Exception:
            return {'ctrl': False, 'shift': False, 'alt': False}


class PygameKeyboardState(KeyboardState):
    """Pygame Keyboard State Adapter"""

    def __init__(self, logger: Optional[Logger] = None):
        """
        Initializes the Pygame keyboard state.
        
        Args:
            logger: Logger interface (optional).
        """
        self.logger = logger

    def is_pressed(self, key_code: int) -> bool:
        """
        Checks if a specific key is pressed.
        
        Args:
            key_code: The key code.
            
        Returns:
            True if the key is pressed, False otherwise.
        """
        try:
            if not pygame.get_init():
                return False

            keys = pygame.key.get_pressed()
            return bool(keys[key_code]) if 0 <= key_code < len(keys) else False

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking key state: {e}")
            return False

    def get_pressed_keys(self) -> List[int]:
        """
        Gets all pressed keys.
        
        Returns:
            A list of all currently pressed key codes.
        """
        try:
            if not pygame.get_init():
                return []

            keys = pygame.key.get_pressed()
            return [i for i in range(len(keys)) if keys[i]]

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting pressed keys: {e}")
            return []


class PygameClock(Clock):
    """Pygame Clock Adapter"""

    def __init__(self, logger: Optional[Logger] = None):
        """
        Initializes the Pygame clock.
        
        Args:
            logger: Logger interface (optional).
        """
        self.logger = logger
        self.clock = pygame.time.Clock() if pygame.get_init() else None
        self._last_time = self._get_pygame_time()
        self._delta = 0.016  # Default 60 FPS

    def now(self) -> float:
        """
        Gets the current time.
        
        Returns:
            The current timestamp (in seconds).
        """
        return self._get_pygame_time()

    def delta_time(self) -> float:
        """
        Gets the frame time interval.
        
        Returns:
            The time interval from the last frame to this one (in seconds).
        """
        current = self.now()
        if self._last_time > 0:
            self._delta = current - self._last_time
        self._last_time = current
        return self._delta

    def _get_pygame_time(self) -> float:
        """Gets the pygame time or system time as a fallback."""
        try:
            if pygame.get_init():
                return pygame.time.get_ticks() / 1000.0
            else:
                return time.time()
        except Exception:
            return time.time()

    def tick(self, fps: int = 60) -> int:
        """
        Controls the frame rate (if using the pygame clock).
        
        Args:
            fps: The target frame rate.
            
        Returns:
            The actual milliseconds passed.
        """
        try:
            if self.clock:
                return self.clock.tick(fps)
            else:
                # Simple time control
                target_delta = 1.0 / fps
                current_time = time.time()
                elapsed = current_time - self._last_time
                if elapsed < target_delta:
                    time.sleep(target_delta - elapsed)
                return int((time.time() - current_time) * 1000)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error in clock tick: {e}")
            return 16  # Default 60 FPS


class PygameLogger(Logger):
    """Simple Pygame-compatible logging implementation."""

    def __init__(self, enable_debug: bool = False):
        """
        Initializes the logger.
        
        Args:
            enable_debug: Whether to enable debug output.
        """
        self.enable_debug = enable_debug

    def debug(self, message: str):
        """Logs a debug message."""
        if self.enable_debug:
            print(f"[DEBUG] {message}")

    def info(self, message: str):
        """Logs a general information message."""
        print(f"[INFO] {message}")

    def warning(self, message: str):
        """Logs a warning message."""
        print(f"[WARNING] {message}")

    def error(self, message: str):
        """Logs an error message."""
        print(f"[ERROR] {message}")


def create_pygame_adapters(enable_debug: bool = False) -> tuple[PygameEventSource, PygameKeyboardState, PygameClock, PygameLogger]:
    """
    Creates a complete set of Pygame adapters.
    
    Args:
        enable_debug: Whether to enable debug logging.
        
    Returns:
        A tuple of (event source, keyboard state, clock, logger).
    """
    logger = PygameLogger(enable_debug)
    event_source = PygameEventSource(logger)
    keyboard_state = PygameKeyboardState(logger)
    clock = PygameClock(logger)

    return event_source, keyboard_state, clock, logger
