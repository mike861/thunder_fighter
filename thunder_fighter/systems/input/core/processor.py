"""
Core input processing logic, fully testable.

This module implements the core logic of the input system, independent of any external libraries.
It uses abstract interfaces through dependency injection, making it fully testable.
"""

from typing import Dict, List, Optional, Set

from .boundaries import Clock, EventSource, KeyboardState, Logger
from .commands import Command, CommandType
from .events import Event, EventType


class InputProcessor:
    """
    Pure Input Processor
    
    Core input processing logic, responsible for converting input events into game commands.
    Uses external interfaces through dependency injection, making it fully testable.
    """

    def __init__(self,
                 event_source: EventSource,
                 keyboard_state: KeyboardState,
                 clock: Clock,
                 key_mapping: Dict[int, CommandType],
                 logger: Optional[Logger] = None):
        """
        Initializes the input processor.
        
        Args:
            event_source: Event source interface.
            keyboard_state: Keyboard state interface.  
            clock: Clock interface.
            key_mapping: Mapping from key codes to command types.
            logger: Logger interface (optional).
        """
        self.event_source = event_source
        self.keyboard_state = keyboard_state
        self.clock = clock
        self.key_mapping = key_mapping
        self.logger = logger

        # State tracking
        self.held_keys: Set[int] = set()
        self.last_key_times: Dict[int, float] = {}
        self.last_command_times: Dict[CommandType, float] = {}

        # Configuration parameters
        self.repeat_delay = 0.5  # Delay before the first repeat
        self.repeat_rate = 0.05  # Repeat interval
        self.cooldown_time = 0.2  # Command cooldown time

        # Set of continuous commands (e.g., movement)
        self.continuous_commands = {
            CommandType.MOVE_UP,
            CommandType.MOVE_DOWN,
            CommandType.MOVE_LEFT,
            CommandType.MOVE_RIGHT
        }

        # Statistics
        self.stats = {
            'events_processed': 0,
            'commands_generated': 0,
            'fallback_triggered': 0
        }

    def process(self) -> List[Command]:
        """
        Processes input and returns a list of commands.
        
        Returns:
            A list of generated commands.
        """
        commands = []
        current_time = self.clock.now()

        try:
            # Process events from the event queue
            events = self.event_source.poll_events()
            for event in events:
                event.timestamp = current_time
                if cmd := self._process_event(event):
                    commands.append(cmd)
                self.stats['events_processed'] += 1

            # Process held keys
            for key in self.held_keys.copy():
                if cmd := self._process_held_key(key, current_time):
                    commands.append(cmd)

            # Update statistics
            self.stats['commands_generated'] += len(commands)

            if self.logger:
                if commands:
                    self.logger.debug(f"Generated {len(commands)} commands from {len(events)} events")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error processing input: {e}")
            # Return an empty list on error to avoid crashing
            return []

        return commands

    def _process_event(self, event: Event) -> Optional[Command]:
        """
        Processes a single event.
        
        Args:
            event: The input event.
            
        Returns:
            The generated command (if any).
        """
        if not event.is_key_event():
            return None

        key_code = event.key_code
        if key_code is None:
            return None

        if event.type == EventType.KEY_DOWN:
            return self._handle_key_down(event)
        elif event.type == EventType.KEY_UP:
            return self._handle_key_up(event)

        return None

    def _handle_key_down(self, event: Event) -> Optional[Command]:
        """
        Handles a key down event.
        
        Args:
            event: The key event.
            
        Returns:
            The generated command (if any).
        """
        key_code = event.key_code
        current_time = event.timestamp

        # Add to the set of held keys
        self.held_keys.add(key_code)
        self.last_key_times[key_code] = current_time

        # Check key mapping
        command_type = self.key_mapping.get(key_code)
        if not command_type:
            return None

        # Check command cooldown
        last_command_time = self.last_command_times.get(command_type, -1)  # Initialize to -1 to avoid cooldown issues
        if current_time - last_command_time < self.cooldown_time:
            if self.logger:
                self.logger.debug(f"Command {command_type} on cooldown")
            return None

        # Update command time
        self.last_command_times[command_type] = current_time

        # Create command
        return Command(
            type=command_type,
            timestamp=current_time,
            data={
                'key': key_code,
                'modifiers': event.modifiers.copy(),
                'continuous': False
            }
        )

    def _handle_key_up(self, event: Event) -> Optional[Command]:
        """
        Handles a key up event.
        
        Args:
            event: The key event.
            
        Returns:
            The generated command (if any).
        """
        key_code = event.key_code

        # Remove from the set of held keys
        self.held_keys.discard(key_code)
        self.last_key_times.pop(key_code, None)

        # For some commands, a stop command might be generated on release
        # Not needed for now, but the interface is preserved
        return None

    def _process_held_key(self, key: int, current_time: float) -> Optional[Command]:
        """
        Processes a held key (for continuous actions like movement).
        
        Args:
            key: The key code.
            current_time: The current time.
            
        Returns:
            The generated command (if any).
        """
        command_type = self.key_mapping.get(key)
        if not command_type or command_type not in self.continuous_commands:
            return None

        last_time = self.last_key_times.get(key, current_time)

        # Check if it's time to repeat
        time_since_last = current_time - last_time
        if time_since_last >= self.repeat_rate:
            self.last_key_times[key] = current_time

            return Command(
                type=command_type,
                timestamp=current_time,
                data={
                    'key': key,
                    'continuous': True,
                    'time_held': time_since_last
                }
            )

        return None

    def reset_state(self):
        """Resets the processor state."""
        self.held_keys.clear()
        self.last_key_times.clear()
        self.last_command_times.clear()
        self.event_source.clear_events()

        if self.logger:
            self.logger.info("Input processor state reset")

    def set_key_mapping(self, key_mapping: Dict[int, CommandType]):
        """Updates the key mapping."""
        self.key_mapping = key_mapping
        if self.logger:
            self.logger.info(f"Key mapping updated with {len(key_mapping)} entries")

    def set_repeat_config(self, delay: float, rate: float):
        """
        Sets the key repeat configuration.
        
        Args:
            delay: The delay before the first repeat (in seconds).
            rate: The interval between repeats (in seconds).
        """
        self.repeat_delay = delay
        self.repeat_rate = rate

        if self.logger:
            self.logger.info(f"Repeat config updated: delay={delay}, rate={rate}")

    def set_cooldown(self, cooldown: float):
        """
        Sets the command cooldown time.
        
        Args:
            cooldown: The cooldown time (in seconds).
        """
        self.cooldown_time = cooldown

        if self.logger:
            self.logger.info(f"Cooldown time updated: {cooldown}")

    def get_stats(self) -> Dict[str, int]:
        """Gets processor statistics."""
        return self.stats.copy()

    def is_key_held(self, key_code: int) -> bool:
        """Checks if a specific key is being held down."""
        return key_code in self.held_keys

    def get_held_keys(self) -> List[int]:
        """Gets all keys that are being held down."""
        return list(self.held_keys)
