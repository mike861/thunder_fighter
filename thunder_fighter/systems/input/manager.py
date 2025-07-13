"""
Input Manager

This module provides the main input management interface that coordinates
input handling, event processing, and input system configuration.
"""

from typing import Callable, Dict, List, Optional

import pygame

from thunder_fighter.utils.logger import logger

from .bindings import KeyBindings
from .events import InputEvent, InputEventType
from .handler import InputHandler


class InputManager:
    """
    Main input manager that coordinates all input handling.

    This class provides a high-level interface for input management,
    including event processing, key binding management, and input callbacks.
    """

    def __init__(self, key_bindings: Optional[KeyBindings] = None):
        """
        Initialize the input manager.

        Args:
            key_bindings: Optional KeyBindings instance
        """
        self.key_bindings = key_bindings or KeyBindings()
        self.input_handler = InputHandler(self.key_bindings)

        # Event callbacks
        self._event_callbacks: Dict[InputEventType, List[Callable]] = {}
        self._global_callbacks: List[Callable] = []

        # Input state
        self._enabled = True
        self._paused = False

        logger.info("InputManager initialized")

    def update(self, pygame_events: List[pygame.event.Event]) -> List[InputEvent]:
        """
        Update the input manager with pygame events.

        Args:
            pygame_events: List of pygame events from the current frame

        Returns:
            List of processed InputEvent objects
        """
        if not self._enabled:
            return []

        # Process pygame events into input events
        input_events = self.input_handler.process_pygame_events(pygame_events)

        # Filter events if paused (only allow certain events)
        if self._paused:
            input_events = self._filter_paused_events(input_events)

        # Trigger callbacks for each event
        for event in input_events:
            self._trigger_callbacks(event)

        return input_events

    def _filter_paused_events(self, events: List[InputEvent]) -> List[InputEvent]:
        """
        Filter events when the input is paused.

        Args:
            events: List of input events to filter

        Returns:
            Filtered list of events
        """
        allowed_when_paused = {
            InputEventType.PAUSE,
            InputEventType.RESUME,
            InputEventType.QUIT,
            InputEventType.TOGGLE_MUSIC,
            InputEventType.TOGGLE_SOUND,
            InputEventType.VOLUME_UP,
            InputEventType.VOLUME_DOWN,
            InputEventType.CHANGE_LANGUAGE,
        }

        return [event for event in events if event.event_type in allowed_when_paused]

    def add_event_callback(self, event_type: InputEventType, callback: Callable[[InputEvent], None]):
        """
        Add a callback for a specific event type.

        Args:
            event_type: The input event type to listen for
            callback: Function to call when the event occurs
        """
        if event_type not in self._event_callbacks:
            self._event_callbacks[event_type] = []

        self._event_callbacks[event_type].append(callback)
        logger.debug(f"Added callback for event type: {event_type.value}")

    def remove_event_callback(self, event_type: InputEventType, callback: Callable):
        """
        Remove a callback for a specific event type.

        Args:
            event_type: The input event type
            callback: The callback function to remove
        """
        if event_type in self._event_callbacks:
            try:
                self._event_callbacks[event_type].remove(callback)
                logger.debug(f"Removed callback for event type: {event_type.value}")
            except ValueError:
                logger.warning(f"Callback not found for event type: {event_type.value}")

    def add_global_callback(self, callback: Callable[[InputEvent], None]):
        """
        Add a global callback that receives all input events.

        Args:
            callback: Function to call for all input events
        """
        self._global_callbacks.append(callback)
        logger.debug("Added global input callback")

    def remove_global_callback(self, callback: Callable):
        """
        Remove a global callback.

        Args:
            callback: The callback function to remove
        """
        try:
            self._global_callbacks.remove(callback)
            logger.debug("Removed global input callback")
        except ValueError:
            logger.warning("Global callback not found")

    def _trigger_callbacks(self, event: InputEvent):
        """
        Trigger callbacks for an input event.

        Args:
            event: The input event to process
        """
        # Trigger specific event callbacks
        if event.event_type in self._event_callbacks:
            for callback in self._event_callbacks[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in event callback for {event.event_type.value}: {e}")

        # Trigger global callbacks
        for callback in self._global_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in global input callback: {e}")

    def is_action_active(self, action: str) -> bool:
        """
        Check if an action is currently active.

        Args:
            action: The action name to check

        Returns:
            True if the action is active
        """
        return self.input_handler.is_action_active(action)

    def is_key_pressed(self, key: int) -> bool:
        """
        Check if a key is currently pressed.

        Args:
            key: The key code to check

        Returns:
            True if the key is pressed
        """
        return self.input_handler.is_key_pressed(key)

    def is_key_held(self, key: int) -> bool:
        """
        Check if a key is currently held down.

        Args:
            key: The key code to check

        Returns:
            True if the key is held
        """
        return self.input_handler.is_key_held(key)

    def get_active_actions(self) -> set:
        """
        Get all currently active actions.

        Returns:
            Set of active action names
        """
        return self.input_handler.get_active_actions()

    def enable(self):
        """Enable input processing."""
        self._enabled = True
        logger.debug("Input manager enabled")

    def disable(self):
        """Disable input processing."""
        self._enabled = False
        logger.debug("Input manager disabled")

    def pause(self):
        """Pause input processing (only allow certain events)."""
        self._paused = True
        logger.debug("Input manager paused")

    def resume(self):
        """Resume normal input processing."""
        self._paused = False
        logger.debug("Input manager resumed")

    def is_enabled(self) -> bool:
        """Check if input processing is enabled."""
        return self._enabled

    def is_paused(self) -> bool:
        """Check if input processing is paused."""
        return self._paused

    def clear_state(self):
        """Clear all input state."""
        self.input_handler.clear_state()
        logger.debug("Input manager state cleared")

    def get_key_bindings(self) -> KeyBindings:
        """
        Get the key bindings instance.

        Returns:
            The KeyBindings instance
        """
        return self.key_bindings

    def set_key_bindings(self, key_bindings: KeyBindings):
        """
        Set new key bindings.

        Args:
            key_bindings: The new KeyBindings instance
        """
        self.key_bindings = key_bindings
        self.input_handler.set_key_bindings(key_bindings)
        logger.info("Key bindings updated in input manager")

    def rebind_key(self, action: str, old_key: int, new_key: int) -> bool:
        """
        Rebind a key for an action.

        Args:
            action: The action to rebind
            old_key: The current key
            new_key: The new key

        Returns:
            True if rebinding was successful
        """
        return self.key_bindings.rebind_key(action, old_key, new_key)

    def reset_key_bindings(self):
        """Reset key bindings to defaults."""
        self.key_bindings.reset_to_defaults()
        logger.info("Key bindings reset to defaults")

    def get_binding_info(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get formatted key binding information.

        Returns:
            Dictionary with binding information organized by category
        """
        return self.key_bindings.get_binding_info()

    def create_movement_handler(self, move_callback: Callable[[str, bool], None]) -> Callable:
        """
        Create a movement event handler.

        Args:
            move_callback: Function to call for movement events (direction, pressed)

        Returns:
            Event handler function
        """

        def handle_movement(event: InputEvent):
            if event.event_type in [
                InputEventType.MOVE_UP,
                InputEventType.MOVE_DOWN,
                InputEventType.MOVE_LEFT,
                InputEventType.MOVE_RIGHT,
                InputEventType.STOP_MOVE_UP,
                InputEventType.STOP_MOVE_DOWN,
                InputEventType.STOP_MOVE_LEFT,
                InputEventType.STOP_MOVE_RIGHT,
            ]:
                direction = event.get_data("direction")
                pressed = event.get_data("pressed")
                if direction:
                    move_callback(direction, pressed)

        return handle_movement

    def create_action_handler(self, action_callback: Callable[[str, bool], None]) -> Callable:
        """
        Create an action event handler.

        Args:
            action_callback: Function to call for action events (action, pressed)

        Returns:
            Event handler function
        """

        def handle_action(event: InputEvent):
            if event.event_type in [InputEventType.SHOOT, InputEventType.STOP_SHOOT, InputEventType.LAUNCH_MISSILE]:
                action = event.get_data("action")
                pressed = event.get_data("pressed", True)
                if action:
                    action_callback(action, pressed)

        return handle_action

    def __str__(self):
        return f"InputManager(enabled={self._enabled}, paused={self._paused}, callbacks={len(self._event_callbacks)})"
