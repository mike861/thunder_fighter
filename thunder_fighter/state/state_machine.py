"""
State Machine Framework

This module provides a generic state machine framework for managing
state transitions and behaviors in the Thunder Fighter game.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
from thunder_fighter.utils.logger import logger


class State(ABC):
    """
    Abstract base class for game states.
    
    Each state represents a distinct mode of the game (playing, paused, etc.)
    and defines the behavior for that mode.
    """
    
    def __init__(self, name: str):
        """
        Initialize the state.
        
        Args:
            name: The name of this state
        """
        self.name = name
        self._context = None
    
    def set_context(self, context):
        """
        Set the state machine context.
        
        Args:
            context: The state machine that owns this state
        """
        self._context = context
    
    @abstractmethod
    def enter(self, previous_state: Optional['State'] = None):
        """
        Called when entering this state.
        
        Args:
            previous_state: The state we're transitioning from
        """
        pass
    
    @abstractmethod
    def exit(self, next_state: Optional['State'] = None):
        """
        Called when exiting this state.
        
        Args:
            next_state: The state we're transitioning to
        """
        pass
    
    @abstractmethod
    def update(self, dt: float):
        """
        Update the state logic.
        
        Args:
            dt: Delta time since last update
        """
        pass
    
    @abstractmethod
    def handle_event(self, event):
        """
        Handle an event in this state.
        
        Args:
            event: The event to handle
        """
        pass
    
    def can_transition_to(self, state_name: str) -> bool:
        """
        Check if this state can transition to another state.
        
        Args:
            state_name: The target state name
            
        Returns:
            True if transition is allowed
        """
        return True  # Default: allow all transitions
    
    def __str__(self):
        return f"State({self.name})"


class StateMachine:
    """
    Generic state machine for managing game states.
    
    This class manages state transitions, validates them, and ensures
    proper enter/exit handling for each state.
    """
    
    def __init__(self, initial_state: Optional[State] = None):
        """
        Initialize the state machine.
        
        Args:
            initial_state: The initial state to start with
        """
        self._states: Dict[str, State] = {}
        self._current_state: Optional[State] = None
        self._previous_state: Optional[State] = None
        self._transition_callbacks: Dict[str, list] = {}
        self._global_callbacks: list = []
        
        if initial_state:
            self.add_state(initial_state)
            self.set_current_state(initial_state.name)
        
        logger.info("StateMachine initialized")
    
    def add_state(self, state: State):
        """
        Add a state to the state machine.
        
        Args:
            state: The state to add
        """
        state.set_context(self)
        self._states[state.name] = state
        logger.debug(f"Added state: {state.name}")
    
    def remove_state(self, state_name: str):
        """
        Remove a state from the state machine.
        
        Args:
            state_name: The name of the state to remove
        """
        if state_name in self._states:
            if self._current_state and self._current_state.name == state_name:
                logger.warning(f"Cannot remove current state: {state_name}")
                return
            
            del self._states[state_name]
            logger.debug(f"Removed state: {state_name}")
    
    def get_state(self, state_name: str) -> Optional[State]:
        """
        Get a state by name.
        
        Args:
            state_name: The name of the state to get
            
        Returns:
            The state object or None if not found
        """
        return self._states.get(state_name)
    
    def get_current_state(self) -> Optional[State]:
        """Get the current active state."""
        return self._current_state
    
    def get_previous_state(self) -> Optional[State]:
        """Get the previous state."""
        return self._previous_state
    
    def set_current_state(self, state_name: str, force: bool = False):
        """
        Set the current state.
        
        Args:
            state_name: The name of the state to set as current
            force: Whether to force the transition even if not allowed
        """
        if state_name not in self._states:
            logger.error(f"State not found: {state_name}")
            return False
        
        new_state = self._states[state_name]
        
        # Check if transition is allowed
        if (self._current_state and 
            not force and 
            not self._current_state.can_transition_to(state_name)):
            logger.warning(f"Transition not allowed from {self._current_state.name} to {state_name}")
            return False
        
        # Perform the transition
        old_state = self._current_state
        
        # Exit current state
        if self._current_state:
            self._current_state.exit(new_state)
        
        # Update state references
        self._previous_state = self._current_state
        self._current_state = new_state
        
        # Enter new state
        self._current_state.enter(old_state)
        
        # Notify callbacks
        self._notify_transition(old_state, new_state)
        
        logger.info(f"State transition: {old_state.name if old_state else 'None'} -> {new_state.name}")
        return True
    
    def transition_to(self, state_name: str, force: bool = False) -> bool:
        """
        Transition to a new state.
        
        Args:
            state_name: The name of the state to transition to
            force: Whether to force the transition
            
        Returns:
            True if transition was successful
        """
        return self.set_current_state(state_name, force)
    
    def update(self, dt: float):
        """
        Update the current state.
        
        Args:
            dt: Delta time since last update
        """
        if self._current_state:
            self._current_state.update(dt)
    
    def handle_event(self, event):
        """
        Handle an event in the current state.
        
        Args:
            event: The event to handle
        """
        if self._current_state:
            self._current_state.handle_event(event)
    
    def add_transition_callback(self, state_name: str, callback: Callable):
        """
        Add a callback for when transitioning to a specific state.
        
        Args:
            state_name: The state name to listen for
            callback: The callback function
        """
        if state_name not in self._transition_callbacks:
            self._transition_callbacks[state_name] = []
        self._transition_callbacks[state_name].append(callback)
    
    def add_global_callback(self, callback: Callable):
        """
        Add a global callback for all state transitions.
        
        Args:
            callback: The callback function
        """
        self._global_callbacks.append(callback)
    
    def remove_transition_callback(self, state_name: str, callback: Callable):
        """
        Remove a transition callback.
        
        Args:
            state_name: The state name
            callback: The callback to remove
        """
        if state_name in self._transition_callbacks:
            try:
                self._transition_callbacks[state_name].remove(callback)
            except ValueError:
                pass
    
    def remove_global_callback(self, callback: Callable):
        """
        Remove a global callback.
        
        Args:
            callback: The callback to remove
        """
        try:
            self._global_callbacks.remove(callback)
        except ValueError:
            pass
    
    def _notify_transition(self, old_state: Optional[State], new_state: State):
        """
        Notify callbacks of state transitions.
        
        Args:
            old_state: The previous state
            new_state: The new state
        """
        # Notify global callbacks
        for callback in self._global_callbacks:
            try:
                callback(old_state, new_state)
            except Exception as e:
                logger.error(f"Error in global transition callback: {e}", exc_info=True)
        
        # Notify specific state callbacks
        if new_state.name in self._transition_callbacks:
            for callback in self._transition_callbacks[new_state.name]:
                try:
                    callback(old_state, new_state)
                except Exception as e:
                    logger.error(f"Error in transition callback for {new_state.name}: {e}", exc_info=True)
    
    def get_state_names(self) -> list:
        """Get a list of all state names."""
        return list(self._states.keys())
    
    def has_state(self, state_name: str) -> bool:
        """
        Check if a state exists.
        
        Args:
            state_name: The state name to check
            
        Returns:
            True if the state exists
        """
        return state_name in self._states
    
    def get_current_state_name(self) -> Optional[str]:
        """Get the name of the current state."""
        return self._current_state.name if self._current_state else None
    
    def get_previous_state_name(self) -> Optional[str]:
        """Get the name of the previous state."""
        return self._previous_state.name if self._previous_state else None
    
    def __str__(self):
        current_name = self.get_current_state_name()
        return f"StateMachine(current={current_name}, states={len(self._states)})" 