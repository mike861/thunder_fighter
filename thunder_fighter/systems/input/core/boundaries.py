"""
System Boundary Interface Definitions

This module defines the abstract interfaces for the input system to interact with the outside world,
implementing the dependency inversion principle so that the core logic does not depend on specific implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List

from .events import Event


class EventSource(ABC):
    """
    Abstract interface for an event source.
    
    Defines the abstract interface for getting input events, isolating specific implementations like pygame.
    Implementing classes are responsible for converting external input events into standard Event objects.
    """

    @abstractmethod
    def poll_events(self) -> List[Event]:
        """
        Gets all pending events.
        
        Returns:
            A list of Event objects, containing all pending input events.
        """
        pass

    @abstractmethod
    def clear_events(self):
        """Clears the event queue."""
        pass


class KeyboardState(ABC):
    """
    Abstract interface for keyboard state.
    
    Defines the abstract interface for querying keyboard state, supporting real-time querying of key states.
    """

    @abstractmethod
    def is_pressed(self, key_code: int) -> bool:
        """
        Checks if a specific key is pressed.
        
        Args:
            key_code: The key code.
            
        Returns:
            True if the key is pressed, False otherwise.
        """
        pass

    @abstractmethod
    def get_pressed_keys(self) -> List[int]:
        """
        Gets all pressed keys.
        
        Returns:
            A list of all currently pressed key codes.
        """
        pass


class Clock(ABC):
    """
    Abstract interface for a clock.
    
    Defines the abstract interface for time-related functions, supporting controllable time flow.
    """

    @abstractmethod
    def now(self) -> float:
        """
        Gets the current time.
        
        Returns:
            The current timestamp (in seconds).
        """
        pass

    @abstractmethod
    def delta_time(self) -> float:
        """
        Gets the frame time interval.
        
        Returns:
            The time interval from the last frame to this one (in seconds).
        """
        pass


class InputConfiguration(ABC):
    """
    Abstract interface for input configuration.
    
    Defines the abstract interface for input configuration, supporting key mapping and input behavior configuration.
    """

    @abstractmethod
    def get_key_mapping(self) -> Dict[int, str]:
        """
        Gets the key mapping.
        
        Returns:
            A dictionary mapping key codes to command types.
        """
        pass

    @abstractmethod
    def get_repeat_delay(self) -> float:
        """
        Gets the key repeat delay.
        
        Returns:
            The delay time before the first repeat (in seconds).
        """
        pass

    @abstractmethod
    def get_repeat_rate(self) -> float:
        """
        Gets the key repeat rate.
        
        Returns:
            The interval time for repeated keys (in seconds).
        """
        pass

    @abstractmethod
    def is_continuous_key(self, key_code: int) -> bool:
        """
        Checks if a specific key supports continuous triggering.
        
        Args:
            key_code: The key code.
            
        Returns:
            True if the key supports continuous triggering (e.g., movement keys), False otherwise.
        """
        pass


class Logger(ABC):
    """
    Abstract interface for a logger.
    
    Defines the abstract interface for logging, supporting different levels of log output.
    """

    @abstractmethod
    def debug(self, message: str):
        """Logs a debug message."""
        pass

    @abstractmethod
    def info(self, message: str):
        """Logs a general information message."""
        pass

    @abstractmethod
    def warning(self, message: str):
        """Logs a warning message."""
        pass

    @abstractmethod
    def error(self, message: str):
        """Logs an error message."""
        pass
