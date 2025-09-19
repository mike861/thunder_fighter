"""
Input System Facade - Simplified interface for the input system

This module provides the main interface for the input system, hiding the complex internal structure
behind a simple and easy-to-use API.
"""

from typing import Callable, Dict, List, Optional

import pygame

from .adapters.pygame_adapter import create_pygame_adapters
from .adapters.test_adapter import create_test_environment
from .core.boundaries import Clock, EventSource, KeyboardState, Logger
from .core.commands import Command, CommandType
from .core.processor import InputProcessor


class InputSystem:
    """
    Input System Facade

    Provides a simplified interface to use the input system, automatically handling adapter creation and configuration.
    Supports seamless switching between production (pygame) and test environments.
    """

    def __init__(
        self,
        event_source: Optional[EventSource] = None,
        keyboard_state: Optional[KeyboardState] = None,
        clock: Optional[Clock] = None,
        logger: Optional[Logger] = None,
        key_mapping: Optional[Dict[int, CommandType]] = None,
        enable_debug: bool = False,
    ):
        """
        Initializes the input system.

        Args:
            event_source: Event source interface (optional, defaults to pygame).
            keyboard_state: Keyboard state interface (optional, defaults to pygame).
            clock: Clock interface (optional, defaults to pygame).
            logger: Logger interface (optional, defaults to a simple logger).
            key_mapping: Key mapping (optional, uses default mapping).
            enable_debug: Whether to enable debug logging.
        """
        # If dependencies are not provided, use the default pygame adapters
        if not all([event_source, keyboard_state, clock]):
            default_event_source, default_keyboard, default_clock, default_logger = create_pygame_adapters(enable_debug)

            self.event_source = event_source or default_event_source
            self.keyboard_state = keyboard_state or default_keyboard
            self.clock = clock or default_clock
            self.logger = logger or default_logger
        else:
            # These should not be None if we reach this branch
            assert event_source is not None
            assert keyboard_state is not None
            assert clock is not None
            assert logger is not None
            self.event_source = event_source
            self.keyboard_state = keyboard_state
            self.clock = clock
            self.logger = logger

        # Set default key mapping
        if key_mapping is None:
            key_mapping = self._create_default_key_mapping()

        # Create the core processor
        self.processor = InputProcessor(
            event_source=self.event_source,
            keyboard_state=self.keyboard_state,
            clock=self.clock,
            key_mapping=key_mapping,
            logger=self.logger,
        )

        # Command handler registry
        self.command_handlers: Dict[CommandType, List[Callable]] = {}

        # System state
        self.enabled = True
        self.stats = {"total_commands": 0, "last_update_time": 0.0}

    def update(self) -> List[Command]:
        """
        Updates the input system and returns commands.

        Returns:
            A list of generated commands.
        """
        if not self.enabled:
            return []

        try:
            # Process input
            commands = self.processor.process()

            # Execute registered handlers
            for command in commands:
                self._execute_command_handlers(command)

            # Update statistics
            self.stats["total_commands"] += len(commands)
            self.stats["last_update_time"] = self.clock.now()

            return commands

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error in input system update: {e}")
            return []

    def on_command(self, command_type: CommandType, handler: Callable[[Command], None]):
        """
        Registers a command handler.

        Args:
            command_type: The command type.
            handler: The handler function, which accepts a Command object as an argument.
        """
        if command_type not in self.command_handlers:
            self.command_handlers[command_type] = []

        self.command_handlers[command_type].append(handler)

        if self.logger:
            self.logger.debug(f"Registered handler for command {command_type}")

    def remove_command_handler(self, command_type: CommandType, handler: Callable[[Command], None]):
        """
        Removes a command handler.

        Args:
            command_type: The command type.
            handler: The handler function to remove.
        """
        if command_type in self.command_handlers:
            try:
                self.command_handlers[command_type].remove(handler)
                if self.logger:
                    self.logger.debug(f"Removed handler for command {command_type}")
            except ValueError:
                if self.logger:
                    self.logger.warning(f"Handler not found for command {command_type}")

    def clear_handlers(self, command_type: Optional[CommandType] = None):
        """
        Clears command handlers.

        Args:
            command_type: The command type to clear (optional, None clears all).
        """
        if command_type is None:
            self.command_handlers.clear()
            if self.logger:
                self.logger.info("Cleared all command handlers")
        else:
            self.command_handlers.pop(command_type, None)
            if self.logger:
                self.logger.info(f"Cleared handlers for command {command_type}")

    def is_key_pressed(self, key_code: int) -> bool:
        """
        Checks if a key is pressed.

        Args:
            key_code: The key code.

        Returns:
            True if the key is pressed, otherwise False.
        """
        return self.keyboard_state.is_pressed(key_code)

    def is_key_held(self, key_code: int) -> bool:
        """
        Checks if a key is being held down.

        Args:
            key_code: The key code.

        Returns:
            True if the key is being held down, otherwise False.
        """
        return self.processor.is_key_held(key_code)

    def get_held_keys(self) -> List[int]:
        """Gets all keys that are being held down."""
        return self.processor.get_held_keys()

    def reset_state(self):
        """Resets the input system state."""
        self.processor.reset_state()
        if self.logger:
            self.logger.info("Input system state reset")

    def set_key_mapping(self, key_mapping: Dict[int, CommandType]):
        """
        Updates the key mapping.

        Args:
            key_mapping: The new key mapping.
        """
        self.processor.set_key_mapping(key_mapping)
        if self.logger:
            self.logger.info(f"Updated key mapping with {len(key_mapping)} entries")

    def configure_repeat(self, delay: float, rate: float):
        """
        Configures key repeat.

        Args:
            delay: The initial repeat delay in seconds.
            rate: The repeat interval in seconds.
        """
        self.processor.set_repeat_config(delay, rate)

    def configure_cooldown(self, cooldown: float):
        """
        Configures command cooldown.

        Args:
            cooldown: The cooldown time in seconds.
        """
        self.processor.set_cooldown(cooldown)

    def enable(self):
        """Enables the input system."""
        self.enabled = True
        if self.logger:
            self.logger.info("Input system enabled")

    def disable(self):
        """Disables the input system."""
        self.enabled = False
        if self.logger:
            self.logger.info("Input system disabled")

    def get_stats(self) -> Dict:
        """Gets input system statistics."""
        processor_stats = self.processor.get_stats()
        return {
            **self.stats,
            **processor_stats,
            "enabled": self.enabled,
            "handler_count": sum(len(handlers) for handlers in self.command_handlers.values()),
        }

    def _execute_command_handlers(self, command: Command):
        """
        Executes command handlers.

        Args:
            command: The command to process.
        """
        handlers = self.command_handlers.get(command.type, [])
        for handler in handlers:
            try:
                handler(command)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error in command handler for {command.type}: {e}")

    def _create_default_key_mapping(self) -> Dict[int, CommandType]:
        """
        Creates the default key mapping.

        Returns:
            The default key mapping dictionary.
        """
        return {
            # Arrow keys
            pygame.K_UP: CommandType.MOVE_UP,
            pygame.K_DOWN: CommandType.MOVE_DOWN,
            pygame.K_LEFT: CommandType.MOVE_LEFT,
            pygame.K_RIGHT: CommandType.MOVE_RIGHT,
            # WASD
            pygame.K_w: CommandType.MOVE_UP,
            pygame.K_s: CommandType.MOVE_DOWN,
            pygame.K_a: CommandType.MOVE_LEFT,
            pygame.K_d: CommandType.MOVE_RIGHT,
            # Action keys
            pygame.K_SPACE: CommandType.SHOOT,
            pygame.K_x: CommandType.LAUNCH_MISSILE,
            # System keys
            pygame.K_p: CommandType.PAUSE,
            pygame.K_ESCAPE: CommandType.QUIT,
            pygame.K_m: CommandType.TOGGLE_MUSIC,
            pygame.K_l: CommandType.CHANGE_LANGUAGE,
            # Debug keys
            pygame.K_F1: CommandType.RESET_INPUT,
        }


def create_for_production(enable_debug: bool = False) -> InputSystem:
    """
    Creates an input system for the production environment.

    Args:
        enable_debug: Whether to enable debug logging.

    Returns:
        A configured InputSystem instance.
    """
    return InputSystem(enable_debug=enable_debug)


def create_for_testing(
    initial_time: float = 0.0, print_logs: bool = False, key_mapping: Optional[Dict[int, CommandType]] = None
) -> tuple[InputSystem, dict]:
    """
    Creates an input system for the test environment.

    Args:
        initial_time: The initial time.
        print_logs: Whether to print logs.
        key_mapping: The key mapping (optional).

    Returns:
        A tuple of (InputSystem instance, test controllers dictionary).
        The test controllers include: event_source, keyboard_state, clock, logger.
    """
    event_source, keyboard_state, clock, logger = create_test_environment(initial_time, print_logs)

    input_system = InputSystem(
        event_source=event_source, keyboard_state=keyboard_state, clock=clock, logger=logger, key_mapping=key_mapping
    )

    controllers = {"event_source": event_source, "keyboard_state": keyboard_state, "clock": clock, "logger": logger}

    return input_system, controllers


class InputSystemBuilder:
    """Input system builder - provides a fluent configuration API."""

    def __init__(self):
        """Initializes the builder."""
        self._event_source = None
        self._keyboard_state = None
        self._clock = None
        self._logger = None
        self._key_mapping = None
        self._enable_debug = False
        self._repeat_delay = 0.5
        self._repeat_rate = 0.05
        self._cooldown = 0.2

    def with_pygame(self, enable_debug: bool = False):
        """Uses pygame adapters."""
        self._enable_debug = enable_debug
        return self

    def with_test_environment(self, initial_time: float = 0.0, print_logs: bool = False):
        """Uses the test environment."""
        self._event_source, self._keyboard_state, self._clock, self._logger = create_test_environment(
            initial_time, print_logs
        )
        return self

    def with_key_mapping(self, key_mapping: Dict[int, CommandType]):
        """Sets the key mapping."""
        self._key_mapping = key_mapping
        return self

    def with_repeat_config(self, delay: float, rate: float):
        """Sets the repeat configuration."""
        self._repeat_delay = delay
        self._repeat_rate = rate
        return self

    def with_cooldown(self, cooldown: float):
        """Sets the cooldown time."""
        self._cooldown = cooldown
        return self

    def build(self) -> InputSystem:
        """Builds the input system."""
        system = InputSystem(
            event_source=self._event_source,
            keyboard_state=self._keyboard_state,
            clock=self._clock,
            logger=self._logger,
            key_mapping=self._key_mapping,
            enable_debug=self._enable_debug,
        )

        # Apply configurations
        system.configure_repeat(self._repeat_delay, self._repeat_rate)
        system.configure_cooldown(self._cooldown)

        return system
