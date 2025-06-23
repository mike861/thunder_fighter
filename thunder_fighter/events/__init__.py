"""
Events Package

This package provides an event system for decoupled communication between
game components in the Thunder Fighter game.
"""

from .event_system import EventSystem, Event, EventType
from .game_events import GameEventType, GameEvent

__all__ = [
    'EventSystem',
    'Event',
    'EventType',
    'GameEventType',
    'GameEvent'
] 