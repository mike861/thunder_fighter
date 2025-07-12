"""
Pure domain event model, independent of any external libraries.

This module defines the core event model of the input system, completely independent of external dependencies like pygame.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class EventType(Enum):
    """Event Type Enumeration"""

    KEY_DOWN = "key_down"
    KEY_UP = "key_up"
    MOUSE_DOWN = "mouse_down"
    MOUSE_UP = "mouse_up"
    MOUSE_MOVE = "mouse_move"


@dataclass
class Event:
    """
    Pure Event Model

    This class represents an input event in the system, without relying on any external libraries.
    All input events will be converted to this unified format.
    """

    type: EventType
    key_code: Optional[int] = None
    mouse_button: Optional[int] = None
    position: Optional[tuple[int, int]] = None
    modifiers: Dict[str, bool] = None
    timestamp: float = 0.0

    def __post_init__(self):
        """Post-initialization processing to ensure the modifier keys dictionary always exists."""
        if self.modifiers is None:
            self.modifiers = {"ctrl": False, "shift": False, "alt": False}

    def has_modifier(self, modifier: str) -> bool:
        """Checks if a specific modifier key is included."""
        return self.modifiers.get(modifier, False)

    def is_key_event(self) -> bool:
        """Checks if it is a keyboard event."""
        return self.type in (EventType.KEY_DOWN, EventType.KEY_UP)

    def is_mouse_event(self) -> bool:
        """Checks if it is a mouse event."""
        return self.type in (EventType.MOUSE_DOWN, EventType.MOUSE_UP, EventType.MOUSE_MOVE)
