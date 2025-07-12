"""
Game State Management

This module provides the core game state data structures and management functionality.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict

from thunder_fighter.utils.logger import logger


@dataclass
class GameState:
    """
    Core game state data structure.
    
    This class holds all the essential game state information in a centralized manner.
    """
    # Basic game control
    running: bool = True
    paused: bool = False
    current_state: str = "menu"  # menu, playing, paused, game_over, victory, level_transition

    # Game progression
    level: int = 1
    score: int = 0
    game_time: float = 0.0
    game_start_time: float = field(default_factory=time.time)

    # Player state
    player_health: int = 100
    player_max_health: int = 100
    player_bullet_paths: int = 1
    player_bullet_speed: int = 7
    player_speed: int = 5
    player_wingmen: int = 0

    # Boss state
    boss_active: bool = False
    boss_health: int = 0
    boss_max_health: int = 0
    boss_level: int = 1
    boss_mode: str = "normal"

    # Game mechanics
    enemy_count: int = 0
    target_enemy_count: int = 5
    last_score_checkpoint: int = 0

    # Victory/defeat flags
    game_won: bool = False
    game_over: bool = False

    # Timing state
    enemy_spawn_timer: float = field(default_factory=time.time)
    boss_spawn_timer: float = field(default_factory=time.time)
    item_spawn_timer: float = field(default_factory=time.time)

    # UI state
    victory_screen_shown: bool = False
    defeat_screen_shown: bool = False
    level_change_active: bool = False
    level_change_timer: float = 0.0

    # Configuration state
    item_spawn_interval: int = 30

    def update_game_time(self):
        """Update the game time based on current time."""
        if not self.paused and self.current_state == "playing":
            self.game_time = (time.time() - self.game_start_time) / 60.0

    def reset_for_new_game(self):
        """Reset state for a new game."""
        self.running = True
        self.paused = False
        self.current_state = "playing"

        self.level = 1
        self.score = 0
        self.game_time = 0.0
        self.game_start_time = time.time()

        self.player_health = 100
        self.player_max_health = 100
        self.player_bullet_paths = 1
        self.player_bullet_speed = 7
        self.player_speed = 5
        self.player_wingmen = 0

        self.boss_active = False
        self.boss_health = 0
        self.boss_max_health = 0
        self.boss_level = 1
        self.boss_mode = "normal"

        self.enemy_count = 0
        self.target_enemy_count = 5
        self.last_score_checkpoint = 0

        self.game_won = False
        self.game_over = False

        current_time = time.time()
        self.enemy_spawn_timer = current_time
        self.boss_spawn_timer = current_time
        self.item_spawn_timer = current_time

        self.victory_screen_shown = False
        self.defeat_screen_shown = False
        self.level_change_active = False
        self.level_change_timer = 0.0

        self.item_spawn_interval = 30

        logger.info("Game state reset for new game")


class GameStateManager:
    """
    Centralized game state manager.
    
    This class provides a centralized interface for managing game state,
    including state transitions, validation, and event handling.
    """

    def __init__(self):
        """Initialize the game state manager."""
        self.state = GameState()
        self._state_listeners = {}
        self._previous_state = None

        logger.info("GameStateManager initialized")

    def get_state(self) -> GameState:
        """Get the current game state."""
        return self.state

    def set_current_state(self, new_state: str):
        """
        Set the current game state.
        
        Args:
            new_state: The new state name
        """
        if new_state != self.state.current_state:
            old_state = self.state.current_state
            self.state.current_state = new_state
            self._notify_state_change(old_state, new_state)
            logger.info(f"State changed from {old_state} to {new_state}")

    def pause_game(self):
        """Pause the game."""
        if self.state.current_state == "playing":
            self._previous_state = self.state.current_state
            self.state.paused = True
            self.set_current_state("paused")

    def resume_game(self):
        """Resume the game."""
        if self.state.current_state == "paused":
            self.state.paused = False
            self.set_current_state(self._previous_state or "playing")
            self._previous_state = None

    def start_game(self):
        """Start a new game."""
        self.state.reset_for_new_game()
        self.set_current_state("playing")

    def end_game(self, victory: bool = False):
        """
        End the current game.
        
        Args:
            victory: Whether the game ended in victory
        """
        if victory:
            self.state.game_won = True
            self.set_current_state("victory")
        else:
            self.state.game_over = True
            self.set_current_state("game_over")

    def level_up(self, new_level: int):
        """
        Level up the game.
        
        Args:
            new_level: The new level number
        """
        if new_level > self.state.level:
            old_level = self.state.level
            self.state.level = new_level
            self.state.level_change_active = True
            self.state.level_change_timer = time.time()
            self.set_current_state("level_transition")
            logger.info(f"Level up from {old_level} to {new_level}")

    def update_player_stats(self, **kwargs):
        """
        Update player statistics.
        
        Args:
            **kwargs: Player stat updates (health, bullet_paths, etc.)
        """
        for key, value in kwargs.items():
            if hasattr(self.state, f"player_{key}"):
                setattr(self.state, f"player_{key}", value)

    def update_boss_stats(self, **kwargs):
        """
        Update boss statistics.
        
        Args:
            **kwargs: Boss stat updates (active, health, level, mode, etc.)
        """
        for key, value in kwargs.items():
            if hasattr(self.state, f"boss_{key}"):
                setattr(self.state, f"boss_{key}", value)

    def update_score(self, new_score: int):
        """
        Update the game score.
        
        Args:
            new_score: The new score value
        """
        self.state.score = new_score

    def update_enemy_count(self, count: int, target: int = None):
        """
        Update enemy count information.
        
        Args:
            count: Current enemy count
            target: Target enemy count (optional)
        """
        self.state.enemy_count = count
        if target is not None:
            self.state.target_enemy_count = target

    def is_playing(self) -> bool:
        """Check if the game is currently in playing state."""
        return self.state.current_state == "playing"

    def is_paused(self) -> bool:
        """Check if the game is paused."""
        return self.state.current_state == "paused"

    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self.state.current_state == "game_over"

    def is_victory(self) -> bool:
        """Check if the game ended in victory."""
        return self.state.current_state == "victory"

    def should_update_game_logic(self) -> bool:
        """Check if game logic should be updated."""
        return self.state.current_state in ["playing", "level_transition"]

    def should_spawn_enemies(self) -> bool:
        """Check if enemies should be spawned."""
        return self.is_playing() and not self.state.game_won

    def should_spawn_items(self) -> bool:
        """Check if items should be spawned."""
        return self.is_playing() and not self.state.game_won

    def add_state_listener(self, state_name: str, callback):
        """
        Add a listener for state changes.
        
        Args:
            state_name: The state to listen for
            callback: Function to call when state changes
        """
        if state_name not in self._state_listeners:
            self._state_listeners[state_name] = []
        self._state_listeners[state_name].append(callback)

    def remove_state_listener(self, state_name: str, callback):
        """
        Remove a state listener.
        
        Args:
            state_name: The state name
            callback: The callback to remove
        """
        if state_name in self._state_listeners:
            try:
                self._state_listeners[state_name].remove(callback)
            except ValueError:
                pass

    def _notify_state_change(self, old_state: str, new_state: str):
        """
        Notify listeners of state changes.
        
        Args:
            old_state: The previous state
            new_state: The new state
        """
        for state_name, listeners in self._state_listeners.items():
            if state_name == new_state:
                for callback in listeners:
                    try:
                        callback(old_state, new_state)
                    except Exception as e:
                        logger.error(f"Error in state listener callback: {e}", exc_info=True)

    def update(self):
        """Update the game state manager."""
        self.state.update_game_time()

        # Handle level transition timeout
        if (self.state.current_state == "level_transition" and
            self.state.level_change_active and
            time.time() - self.state.level_change_timer > 3.0):
            self.state.level_change_active = False
            self.set_current_state("playing")

    def get_state_info(self) -> Dict[str, Any]:
        """
        Get a dictionary of current state information.
        
        Returns:
            Dictionary containing current state information
        """
        return {
            'current_state': self.state.current_state,
            'running': self.state.running,
            'paused': self.state.paused,
            'level': self.state.level,
            'score': self.state.score,
            'game_time': self.state.game_time,
            'player_health': self.state.player_health,
            'boss_active': self.state.boss_active,
            'game_won': self.state.game_won,
            'game_over': self.state.game_over
        }
