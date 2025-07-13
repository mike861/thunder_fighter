"""
Events Package

This package provides an event system for decoupled communication between
game components in the Thunder Fighter game.
"""

from .event_system import Event, EventSystem, EventType
from .game_events import GameEvent, GameEventType

__all__ = ["EventSystem", "Event", "EventType", "GameEventType", "GameEvent"]
