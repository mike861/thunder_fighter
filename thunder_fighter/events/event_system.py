"""
Event System Core

This module provides the core event system for decoupled communication
between game components.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

from thunder_fighter.utils.logger import logger


class EventType(Enum):
    """Base event types. Empty base class for type hierarchy."""

    pass


@dataclass
class Event:
    """
    Base event class for the event system.

    This class represents an event that can be dispatched through
    the event system to decouple component communication.
    """

    event_type: EventType
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    source: str = "unknown"
    handled: bool = False

    def get_data(self, key: str, default: Any = None) -> Any:
        """
        Get data from the event.

        Args:
            key: Data key to retrieve
            default: Default value if key not found

        Returns:
            The data value or default
        """
        return self.data.get(key, default)

    def set_data(self, key: str, value: Any):
        """
        Set data in the event.

        Args:
            key: Data key to set
            value: Value to set
        """
        self.data[key] = value

    def mark_handled(self):
        """Mark this event as handled."""
        self.handled = True

    def is_handled(self) -> bool:
        """Check if this event has been handled."""
        return self.handled

    def __str__(self):
        return f"Event({self.event_type.value}, source={self.source}, handled={self.handled})"


class EventListener(ABC):
    """
    Abstract base class for event listeners.

    Components that want to receive events should inherit from this class
    and implement the handle_event method.
    """

    @abstractmethod
    def handle_event(self, event: Event) -> bool:
        """
        Handle an event.

        Args:
            event: The event to handle

        Returns:
            True if the event was handled and should not be passed to other listeners
        """
        pass

    def get_listened_events(self) -> Set[EventType]:
        """
        Get the set of event types this listener is interested in.

        Returns:
            Set of EventType values this listener wants to receive
        """
        return set()  # Override in subclasses to specify event types


class FunctionListener(EventListener):
    """
    Wrapper class that adapts callable functions to EventListener interface.

    This allows backward compatibility for code that passes functions directly
    to register_listener instead of EventListener objects.
    """

    def __init__(self, func):
        """
        Initialize with a callable function.

        Args:
            func: The function to wrap (should accept an Event parameter)
        """
        self.func = func

    def handle_event(self, event: Event) -> bool:
        """
        Handle an event by calling the wrapped function.

        Args:
            event: The event to handle

        Returns:
            False (functions don't stop event propagation by default)
        """
        self.func(event)
        return False


class EventSystem:
    """
    Central event system for managing event dispatch and handling.

    This system provides decoupled communication between game components
    through an event-driven architecture.
    """

    def __init__(self):
        """Initialize the event system."""
        self._listeners: Dict[EventType, List[EventListener]] = {}
        self._global_listeners: List[EventListener] = []
        self._event_queue: List[Event] = []
        self._processing_events = False
        self._events_processed = 0

        logger.info("EventSystem initialized")

    def register_listener(
        self, event_type: EventType, listener: Union[EventListener, Callable[[Event], None], Callable[[Any], None]]
    ):
        """
        Register a listener for a specific event type.

        Args:
            event_type: The event type to listen for
            listener: The listener to register (EventListener object or callable function)
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []

        # Wrap callable functions with FunctionListener for backward compatibility
        # but don't wrap objects that already have handle_event method (like Mock objects)
        if callable(listener) and not isinstance(listener, EventListener) and not hasattr(listener, "handle_event"):
            listener = FunctionListener(listener)

        # Ensure listener is treated as EventListener after wrapping
        listener_obj: EventListener = listener  # type: ignore
        if listener_obj not in self._listeners[event_type]:
            self._listeners[event_type].append(listener_obj)
            logger.debug(f"Registered listener for event type: {event_type.value}")

    def unregister_listener(self, event_type: EventType, listener: EventListener):
        """
        Unregister a listener for a specific event type.

        Args:
            event_type: The event type
            listener: The listener to unregister
        """
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(listener)
                logger.debug(f"Unregistered listener for event type: {event_type.value}")
            except ValueError:
                logger.warning(f"Listener not found for event type: {event_type.value}")

    def register_global_listener(self, listener: EventListener):
        """
        Register a global listener that receives all events.

        Args:
            listener: The listener to register
        """
        if listener not in self._global_listeners:
            self._global_listeners.append(listener)
            logger.debug("Registered global event listener")

    def unregister_global_listener(self, listener: EventListener):
        """
        Unregister a global listener.

        Args:
            listener: The listener to unregister
        """
        try:
            self._global_listeners.remove(listener)
            logger.debug("Unregistered global event listener")
        except ValueError:
            logger.warning("Global listener not found")

    def dispatch_event(self, event: Event, immediate: bool = False):
        """
        Dispatch an event to registered listeners.

        Args:
            event: The event to dispatch
            immediate: If True, process the event immediately. Otherwise, queue it.
        """
        if immediate:
            self._process_event(event)
        else:
            self._event_queue.append(event)
            logger.debug(f"Queued event: {event.event_type.value}")

    def process_events(self):
        """Process all queued events."""
        if self._processing_events:
            logger.warning("Already processing events, skipping to avoid recursion")
            return

        self._processing_events = True

        try:
            events_to_process = self._event_queue.copy()
            self._event_queue.clear()

            for event in events_to_process:
                self._process_event(event)
                self._events_processed += 1

        finally:
            self._processing_events = False

    def _process_event(self, event: Event):
        """
        Process a single event.

        Args:
            event: The event to process
        """
        logger.debug(f"Processing event: {event.event_type.value}")

        # Send to global listeners first
        for listener in self._global_listeners:
            try:
                # Support both function and object listeners
                if hasattr(listener, "handle_event"):
                    # Object with handle_event method
                    if listener.handle_event(event):
                        event.mark_handled()
                        return
                elif callable(listener):
                    # Function listener
                    if listener(event):
                        event.mark_handled()
                        return
            except Exception as e:
                logger.error(f"Error in global event listener: {e}", exc_info=True)

        # Send to specific event type listeners
        if event.event_type in self._listeners:
            for listener in self._listeners[event.event_type]:
                try:
                    # Support both function and object listeners
                    if hasattr(listener, "handle_event"):
                        # Object with handle_event method
                        if listener.handle_event(event):
                            event.mark_handled()
                            return
                    elif callable(listener):
                        # Function listener
                        if listener(event):
                            event.mark_handled()
                            return
                except Exception as e:
                    logger.error(f"Error in event listener for {event.event_type.value}: {e}", exc_info=True)

    def create_event(self, event_type: EventType, source: str = "unknown", **data) -> Event:
        """
        Create an event with the given type and data.

        Args:
            event_type: The type of event to create
            source: The source component creating the event
            **data: Event data as keyword arguments

        Returns:
            Created Event instance
        """
        return Event(event_type=event_type, data=data, source=source)

    def emit_event(self, event_type: EventType, source: str = "unknown", immediate: bool = False, **data):
        """
        Create and dispatch an event in one call.

        Args:
            event_type: The type of event to emit
            source: The source component emitting the event
            immediate: Whether to process the event immediately
            **data: Event data as keyword arguments
        """
        event = self.create_event(event_type, source, **data)
        self.dispatch_event(event, immediate)

    def clear_event_queue(self):
        """Clear all queued events."""
        cleared_count = len(self._event_queue)
        self._event_queue.clear()
        logger.debug(f"Cleared {cleared_count} queued events")

    def get_queue_size(self) -> int:
        """
        Get the number of queued events.

        Returns:
            Number of events in the queue
        """
        return len(self._event_queue)

    def get_listener_count(self, event_type: Optional[EventType] = None) -> int:
        """
        Get the number of listeners for an event type.

        Args:
            event_type: Event type to count listeners for. If None, count all listeners.

        Returns:
            Number of listeners
        """
        if event_type is None:
            total = len(self._global_listeners)
            for listeners in self._listeners.values():
                total += len(listeners)
            return total
        else:
            return len(self._listeners.get(event_type, []))

    def get_events_processed(self) -> int:
        """
        Get the total number of events processed.

        Returns:
            Number of events processed since initialization
        """
        return self._events_processed

    def reset_statistics(self):
        """Reset event processing statistics."""
        self._events_processed = 0
        logger.debug("Event system statistics reset")

    def __str__(self):
        return (
            f"EventSystem(listeners={len(self._listeners)}, "
            f"queue_size={len(self._event_queue)}, "
            f"processed={self._events_processed})"
        )
