"""
Input Handler

This module processes raw pygame events and converts them into structured
input events using the key bindings system.
"""

import pygame
from typing import List, Set, Optional, Callable
from .events import InputEvent, InputEventFactory, InputEventType
from .bindings import KeyBindings
from thunder_fighter.utils.logger import logger


class InputHandler:
    """
    Handles raw input events and converts them to structured input events.
    
    This class processes pygame events, applies key bindings, and generates
    InputEvent objects that can be consumed by game logic.
    """
    
    def __init__(self, key_bindings: Optional[KeyBindings] = None):
        """
        Initialize the input handler.
        
        Args:
            key_bindings: Optional KeyBindings instance. If None, creates default.
        """
        self.key_bindings = key_bindings or KeyBindings()
        self._pressed_keys: Set[int] = set()
        self._held_keys: Set[int] = set()
        self._event_queue: List[InputEvent] = []
        
        # Track continuous actions (like movement and shooting)
        self._continuous_actions = {
            'move_up', 'move_down', 'move_left', 'move_right', 'shoot'
        }
        self._active_continuous_actions: Set[str] = set()
        
        # macOS screenshot function interference detection
        self._last_activity_time = pygame.time.get_ticks() if hasattr(pygame, 'time') else 0
        self._focus_lost_recovery_needed = False
        
        logger.info("InputHandler initialized")
    
    def process_pygame_events(self, pygame_events: List[pygame.event.Event]) -> List[InputEvent]:
        """
        Process pygame events and convert them to input events.
        Uses hybrid processing with fallback for macOS screenshot interference.
        
        Args:
            pygame_events: List of pygame events to process
            
        Returns:
            List of InputEvent objects
        """
        input_events = []
        
        # Note: Automatic focus detection disabled due to false positives
        # Use F1 key to manually reset input state if needed after macOS screenshot
        # self._detect_focus_issues(pygame_events)
        
        for event in pygame_events:
            processed_events = self._process_single_event_with_fallback(event)
            input_events.extend(processed_events)
        
        # Add continuous action events for held keys
        input_events.extend(self._generate_continuous_events())
        
        return input_events
    
    def _process_single_event_with_fallback(self, event: pygame.event.Event) -> List[InputEvent]:
        """
        Process a single pygame event with fallback for macOS screenshot interference.
        
        Args:
            event: The pygame event to process
            
        Returns:
            List of InputEvent objects generated from the event
        """
        try:
            # First try normal processing
            events = self._process_single_event(event)
            
            # Check if critical events (P, L) might have been lost
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_p, pygame.K_l]:
                # If normal processing didn't generate expected events, use fallback
                expected_events = self._get_expected_events_for_key(event.key)
                actual_events = [str(e.event_type) for e in events]
                
                # If we didn't get the expected event types, use fallback
                if not any(expected in actual for expected in expected_events for actual in actual_events):
                    logger.warning(f"Input processing failed for key {pygame.key.name(event.key)}, using fallback")
                    fallback_events = self._create_fallback_events(event)
                    if fallback_events:
                        return fallback_events
            
            return events
            
        except Exception as e:
            logger.error(f"Event processing failed: {e}, using fallback")
            # If processing fails completely, use fallback
            return self._create_fallback_events(event)
    
    def _get_expected_events_for_key(self, key: int) -> List[str]:
        """Get expected event types for a given key."""
        if key == pygame.K_p:
            return ["PAUSE"]
        elif key == pygame.K_l:
            return ["CHANGE_LANGUAGE"]
        return []
    
    def _create_fallback_events(self, event: pygame.event.Event) -> List[InputEvent]:
        """Create fallback events for critical keys that failed normal processing."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                logger.info("Fallback: Creating PAUSE event for P key")
                return [InputEventFactory.create_game_control_event('pause')]
            elif event.key == pygame.K_l:
                logger.info("Fallback: Creating CHANGE_LANGUAGE event for L key")
                return [InputEventFactory.create_ui_event('change_language')]
        return []
    
    def _process_single_event(self, event: pygame.event.Event) -> List[InputEvent]:
        """
        Process a single pygame event.
        
        Args:
            event: The pygame event to process
            
        Returns:
            List of InputEvent objects generated from the event
        """
        events = []
        
        if event.type == pygame.QUIT:
            events.append(InputEventFactory.create_game_control_event('quit'))
        
        elif event.type == pygame.KEYDOWN:
            events.extend(self._handle_keydown(event))
        
        elif event.type == pygame.KEYUP:
            events.extend(self._handle_keyup(event))
        
        # Add other event types as needed (mouse, joystick, etc.)
        
        return events
    
    def _handle_keydown(self, event: pygame.event.Event) -> List[InputEvent]:
        """
        Handle keydown events.
        
        Args:
            event: The pygame keydown event
            
        Returns:
            List of InputEvent objects
        """
        events = []
        key = event.key
        modifiers = self._get_modifiers()
        
        # Track pressed keys
        self._pressed_keys.add(key)
        self._held_keys.add(key)
        
        # Get action from key bindings
        action = self.key_bindings.get_action(key, modifiers)
        
        if action:
            if action in ['move_up', 'move_down', 'move_left', 'move_right']:
                # Movement actions
                direction = action.replace('move_', '')
                events.append(InputEventFactory.create_movement_event(direction, True))
                self._active_continuous_actions.add(action)
                
            elif action == 'shoot':
                # Shooting action (continuous)
                events.append(InputEventFactory.create_action_event('shoot', True))
                self._active_continuous_actions.add(action)
                
            elif action == 'launch_missile':
                # Missile action (single press)
                events.append(InputEventFactory.create_action_event('missile', True))
                
            elif action in ['pause', 'quit', 'restart', 'skip_animation']:
                # Game control actions
                control_map = {
                    'pause': 'pause',
                    'quit': 'quit', 
                    'restart': 'restart',
                    'skip_animation': 'skip'
                }
                events.append(InputEventFactory.create_game_control_event(control_map[action]))
                
            elif action in ['toggle_music', 'toggle_sound', 'volume_up', 'volume_down']:
                # Audio actions
                events.append(InputEventFactory.create_audio_event(action))
                
            elif action in ['change_language', 'toggle_dev_mode']:
                # UI actions
                events.append(InputEventFactory.create_ui_event(action))
                
            elif action == 'reset_input_state':
                # Debug action - immediately reset input state
                logger.info("Manual input state reset triggered (F1 key)")
                self.force_key_state_validation()
                # Don't generate an event for this, it's handled internally
        
        return events
    
    def _handle_keyup(self, event: pygame.event.Event) -> List[InputEvent]:
        """
        Handle keyup events.
        
        Args:
            event: The pygame keyup event
            
        Returns:
            List of InputEvent objects
        """
        events = []
        key = event.key
        modifiers = self._get_modifiers()
        
        # Remove from pressed and held keys
        self._pressed_keys.discard(key)
        self._held_keys.discard(key)
        
        # Get action from key bindings
        action = self.key_bindings.get_action(key, modifiers)
        
        if action:
            if action in ['move_up', 'move_down', 'move_left', 'move_right']:
                # Stop movement
                direction = action.replace('move_', '')
                events.append(InputEventFactory.create_movement_event(direction, False))
                self._active_continuous_actions.discard(action)
                
            elif action == 'shoot':
                # Stop shooting
                events.append(InputEventFactory.create_action_event('shoot', False))
                self._active_continuous_actions.discard(action)
        
        return events
    
    def _generate_continuous_events(self) -> List[InputEvent]:
        """
        Generate events for continuous actions (held keys).
        
        Returns:
            List of InputEvent objects for continuous actions
        """
        events = []
        
        # Only generate continuous events if we have active continuous actions
        # This prevents spam when no keys are held
        if not self._active_continuous_actions:
            return events
        
        for action in self._active_continuous_actions:
            if action in ['move_up', 'move_down', 'move_left', 'move_right']:
                direction = action.replace('move_', '')
                event = InputEventFactory.create_movement_event(direction, True)
                event.set_data('continuous', True)
                events.append(event)
                
            elif action == 'shoot':
                event = InputEventFactory.create_action_event('shoot', True)
                event.set_data('continuous', True)
                events.append(event)
        
        return events
    
    def _get_modifiers(self) -> Set[int]:
        """
        Get currently pressed modifier keys.
        
        Returns:
            Set of modifier key codes
        """
        modifiers = set()
        
        try:
            keys = pygame.key.get_pressed()
            
            if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                modifiers.add(pygame.K_LCTRL)
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                modifiers.add(pygame.K_LSHIFT)
            if keys[pygame.K_LALT] or keys[pygame.K_RALT]:
                modifiers.add(pygame.K_LALT)
        except pygame.error:
            # pygame not initialized or no video system available
            # Return empty set for testing environments
            pass
        
        return modifiers
    
    def is_key_pressed(self, key: int) -> bool:
        """
        Check if a key is currently pressed.
        
        Args:
            key: The key code to check
            
        Returns:
            True if the key is pressed
        """
        return key in self._pressed_keys
    
    def is_key_held(self, key: int) -> bool:
        """
        Check if a key is currently held down.
        
        Args:
            key: The key code to check
            
        Returns:
            True if the key is held
        """
        return key in self._held_keys
    
    def is_action_active(self, action: str) -> bool:
        """
        Check if an action is currently active (for continuous actions).
        
        Args:
            action: The action name to check
            
        Returns:
            True if the action is active
        """
        return action in self._active_continuous_actions
    
    def get_active_actions(self) -> Set[str]:
        """
        Get all currently active continuous actions.
        
        Returns:
            Set of active action names
        """
        return self._active_continuous_actions.copy()
    
    def clear_state(self):
        """Clear all input state."""
        self._pressed_keys.clear()
        self._held_keys.clear()
        self._active_continuous_actions.clear()
        logger.debug("Input handler state cleared")
    
    def _detect_focus_issues(self, pygame_events: List[pygame.event.Event]):
        """
        Detect potential focus loss issues that can occur with macOS screenshot function.
        
        Args:
            pygame_events: List of pygame events to analyze
        """
        import platform
        
        # Only apply this fix on macOS
        if platform.system() != 'Darwin':
            return
            
        current_time = pygame.time.get_ticks() if hasattr(pygame, 'time') else 0
        
        # Check for specific focus-related events that indicate real focus loss
        has_actual_focus_events = False
        for event in pygame_events:
            # Look for window focus events that indicate actual focus loss/gain
            if hasattr(pygame, 'WINDOWEVENT') and event.type == pygame.WINDOWEVENT:
                if hasattr(event, 'event') and event.event in [
                    pygame.WINDOWEVENT_FOCUS_LOST, 
                    pygame.WINDOWEVENT_FOCUS_GAINED
                ]:
                    has_actual_focus_events = True
                    logger.debug(f"Detected actual window focus event: {event.event}")
                    break
            elif hasattr(pygame, 'ACTIVEEVENT') and event.type == pygame.ACTIVEEVENT:
                # Older pygame versions
                if hasattr(event, 'state') and event.state & pygame.APPINPUTFOCUS:
                    has_actual_focus_events = True
                    logger.debug("Detected legacy focus event")
                    break
        
        # Only perform recovery for actual focus events, not gaps
        # Gaps are too unreliable and cause false positives
        if has_actual_focus_events:
            logger.info("Detected real focus change - performing recovery")
            self._recover_from_focus_loss()
        else:
            # Update activity time but don't trigger recovery on gaps
            if pygame_events:
                self._last_activity_time = current_time
    
    def _recover_from_focus_loss(self):
        """
        Recover from potential focus loss by validating key states.
        This addresses the macOS screenshot function interference issue.
        """
        logger.debug("Performing focus recovery - validating key states")
        
        # Get current actual key states from pygame
        try:
            current_pressed = pygame.key.get_pressed()
            
            # Validate our tracked key states against actual pygame state
            keys_to_remove = []
            for key in self._pressed_keys:
                if not current_pressed[key]:
                    keys_to_remove.append(key)
                    logger.debug(f"Key {key} no longer pressed - removing from tracked state")
            
            for key in keys_to_remove:
                self._pressed_keys.discard(key)
                self._held_keys.discard(key)
            
            # Clear actions for keys that are no longer pressed
            actions_to_remove = []
            for action in self._active_continuous_actions:
                # Get the key for this action
                key = self.key_bindings.get_key_for_action(action)
                if key is not None and not current_pressed[key]:
                    actions_to_remove.append(action)
                    logger.debug(f"Action {action} no longer active - removing")
            
            for action in actions_to_remove:
                self._active_continuous_actions.discard(action)
                
        except (AttributeError, IndexError) as e:
            logger.warning(f"Could not validate key states during recovery: {e}")
            # If we can't validate, just clear everything to be safe
            self.clear_state()
        
        self._focus_lost_recovery_needed = False
        logger.debug("Focus recovery completed")
    
    def force_key_state_validation(self):
        """
        Force a validation of all tracked key states against actual pygame state.
        This can be called externally when input issues are detected.
        """
        logger.debug("Force validating key states due to external request")
        self._focus_lost_recovery_needed = True
        self._recover_from_focus_loss()
    
    def get_key_bindings(self) -> KeyBindings:
        """
        Get the key bindings instance.
        
        Returns:
            The KeyBindings instance
        """
        return self.key_bindings
    
    def set_key_bindings(self, key_bindings: KeyBindings):
        """
        Set a new key bindings instance.
        
        Args:
            key_bindings: The new KeyBindings instance
        """
        self.key_bindings = key_bindings
        logger.info("Key bindings updated")
    
    def __str__(self):
        return (f"InputHandler(pressed_keys={len(self._pressed_keys)}, "
                f"active_actions={len(self._active_continuous_actions)})") 