"""
Concrete Game State Implementations

This module contains the concrete implementations of different game states
such as playing, paused, game over, victory, etc.
"""

import time
from typing import Optional

import pygame

from thunder_fighter.utils.logger import logger

from .state_machine import State


class MenuState(State):
    """State for the main menu (not currently used but ready for future)."""

    def __init__(self):
        super().__init__("menu")

    def enter(self, previous_state: Optional[State] = None):
        """Enter the menu state."""
        logger.info("Entered menu state")

    def exit(self, next_state: Optional[State] = None):
        """Exit the menu state."""
        logger.info("Exiting menu state")

    def update(self, dt: float):
        """Update menu state."""
        pass

    def handle_event(self, event):
        """Handle menu events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Start the game
                if self._context:
                    self._context.transition_to("playing")

    def can_transition_to(self, state_name: str) -> bool:
        """Menu can transition to playing state."""
        return state_name in ["playing"]


class PlayingState(State):
    """State for active gameplay."""

    def __init__(self, game_instance=None):
        super().__init__("playing")
        self.game = game_instance
        self.last_enemy_spawn = time.time()
        self.last_item_spawn = time.time()

    def enter(self, previous_state: Optional[State] = None):
        """Enter the playing state."""
        logger.info("Entered playing state")

        # If coming from pause, resume music
        if previous_state and previous_state.name == "paused":
            if self.game and hasattr(self.game, 'sound_manager'):
                self.game.sound_manager.set_music_volume(
                    min(1.0, self.game.sound_manager.music_volume * 2)
                )

    def exit(self, next_state: Optional[State] = None):
        """Exit the playing state."""
        logger.info("Exiting playing state")

        # If going to pause, lower music volume
        if next_state and next_state.name == "paused":
            if self.game and hasattr(self.game, 'sound_manager'):
                self.game.sound_manager.set_music_volume(
                    max(0.1, self.game.sound_manager.music_volume / 2)
                )

    def update(self, dt: float):
        """Update playing state logic."""
        if not self.game:
            return

        # Update game time
        current_time = time.time()

        # Enemy spawning logic
        if (len(self.game.enemies) < self.game.target_enemy_count and
            current_time - self.last_enemy_spawn > 2.0):
            game_time = (current_time - self.game.game_start_time) / 60.0
            self.game.spawn_enemy(game_time, self.game.game_level)
            self.last_enemy_spawn = current_time

        # Boss spawning logic
        if (self.game.game_level > 1 and
            current_time - self.game.boss_spawn_timer > self.game.BOSS_SPAWN_INTERVAL):
            if not self.game.boss or not self.game.boss.alive():
                self.game.spawn_boss()

        # Item spawning logic
        if current_time - self.last_item_spawn > self.game.item_spawn_interval:
            game_time = (current_time - self.game.game_start_time) / 60.0
            self.game.spawn_random_item(game_time)
            self.last_item_spawn = current_time

        # Check for level progression
        if (self.game.game_level <= 1 and
            self.game.score.value // self.game.SCORE_THRESHOLD >= self.game.game_level):
            self.game.level_up()

        # Check for game over conditions
        if self.game.player.health <= 0:
            if self._context:
                self._context.transition_to("game_over")

        # Check for victory conditions
        if self.game.game_won:
            if self._context:
                self._context.transition_to("victory")

    def handle_event(self, event):
        """Handle playing state events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                # Pause the game
                if self._context:
                    self._context.transition_to("paused")
            elif event.key == pygame.K_ESCAPE:
                # Exit game
                if self.game:
                    self.game.running = False

    def can_transition_to(self, state_name: str) -> bool:
        """Playing state can transition to paused, game_over, or victory."""
        return state_name in ["paused", "game_over", "victory", "level_transition"]


class PausedState(State):
    """State for when the game is paused."""

    def __init__(self, game_instance=None):
        super().__init__("paused")
        self.game = game_instance

    def enter(self, previous_state: Optional[State] = None):
        """Enter the paused state."""
        logger.info("Entered paused state")
        if self.game:
            self.game.paused = True

    def exit(self, next_state: Optional[State] = None):
        """Exit the paused state."""
        logger.info("Exiting paused state")
        if self.game:
            self.game.paused = False

    def update(self, dt: float):
        """Update paused state (minimal updates)."""
        pass

    def handle_event(self, event):
        """Handle paused state events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                # Resume the game
                if self._context:
                    self._context.transition_to("playing")
            elif event.key == pygame.K_ESCAPE:
                # Exit game
                if self.game:
                    self.game.running = False

    def can_transition_to(self, state_name: str) -> bool:
        """Paused state can only transition back to playing."""
        return state_name in ["playing"]


class GameOverState(State):
    """State for game over screen."""

    def __init__(self, game_instance=None):
        super().__init__("game_over")
        self.game = game_instance
        self.enter_time = 0

    def enter(self, previous_state: Optional[State] = None):
        """Enter the game over state."""
        logger.info("Entered game over state")
        self.enter_time = time.time()

        if self.game:
            # Stop music and play game over sound
            if hasattr(self.game, 'sound_manager'):
                self.game.sound_manager.fadeout_music(2000)
                # Could play game over sound here if we had one

    def exit(self, next_state: Optional[State] = None):
        """Exit the game over state."""
        logger.info("Exiting game over state")

    def update(self, dt: float):
        """Update game over state."""
        # Auto-exit after some time or wait for user input
        pass

    def handle_event(self, event):
        """Handle game over state events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Exit game
                if self.game:
                    self.game.running = False
            elif event.key == pygame.K_r:
                # Restart game (if we implement this feature)
                if self._context:
                    self._context.transition_to("playing")

    def can_transition_to(self, state_name: str) -> bool:
        """Game over can transition to playing (restart) or menu."""
        return state_name in ["playing", "menu"]


class VictoryState(State):
    """State for victory screen."""

    def __init__(self, game_instance=None):
        super().__init__("victory")
        self.game = game_instance
        self.enter_time = 0

    def enter(self, previous_state: Optional[State] = None):
        """Enter the victory state."""
        logger.info("Entered victory state")
        self.enter_time = time.time()

        if self.game:
            # Play victory music/sound
            if hasattr(self.game, 'sound_manager'):
                self.game.sound_manager.fadeout_music(3000)
                # Could play victory sound here

    def exit(self, next_state: Optional[State] = None):
        """Exit the victory state."""
        logger.info("Exiting victory state")

    def update(self, dt: float):
        """Update victory state."""
        pass

    def handle_event(self, event):
        """Handle victory state events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Exit game
                if self.game:
                    self.game.running = False
            elif event.key == pygame.K_r:
                # Restart game (if we implement this feature)
                if self._context:
                    self._context.transition_to("playing")

    def can_transition_to(self, state_name: str) -> bool:
        """Victory can transition to playing (restart) or menu."""
        return state_name in ["playing", "menu"]


class LevelTransitionState(State):
    """State for level transition animations."""

    def __init__(self, game_instance=None):
        super().__init__("level_transition")
        self.game = game_instance
        self.transition_start_time = 0
        self.transition_duration = 3.0  # 3 seconds

    def enter(self, previous_state: Optional[State] = None):
        """Enter the level transition state."""
        logger.info("Entered level transition state")
        self.transition_start_time = time.time()

    def exit(self, next_state: Optional[State] = None):
        """Exit the level transition state."""
        logger.info("Exiting level transition state")

    def update(self, dt: float):
        """Update level transition state."""
        # Check if transition is complete
        elapsed = time.time() - self.transition_start_time
        if elapsed >= self.transition_duration:
            # Transition back to playing
            if self._context:
                self._context.transition_to("playing")

    def handle_event(self, event):
        """Handle level transition events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Allow exiting during transition
                if self.game:
                    self.game.running = False
            elif event.key == pygame.K_SPACE:
                # Skip transition animation
                if self._context:
                    self._context.transition_to("playing")

    def can_transition_to(self, state_name: str) -> bool:
        """Level transition can go back to playing or to game over/victory."""
        return state_name in ["playing", "game_over", "victory"]


class StateFactory:
    """Factory for creating game states."""

    @staticmethod
    def create_state(state_name: str, game_instance=None) -> Optional[State]:
        """
        Create a state by name.
        
        Args:
            state_name: The name of the state to create
            game_instance: The game instance to pass to the state
            
        Returns:
            The created state or None if unknown state name
        """
        state_map = {
            "menu": MenuState,
            "playing": PlayingState,
            "paused": PausedState,
            "game_over": GameOverState,
            "victory": VictoryState,
            "level_transition": LevelTransitionState
        }

        state_class = state_map.get(state_name)
        if state_class:
            if state_name == "menu":
                return state_class()
            else:
                return state_class(game_instance)

        logger.error(f"Unknown state name: {state_name}")
        return None

    @staticmethod
    def create_all_states(game_instance=None) -> list:
        """
        Create all game states.
        
        Args:
            game_instance: The game instance to pass to states
            
        Returns:
            List of all created states
        """
        state_names = ["menu", "playing", "paused", "game_over", "victory", "level_transition"]
        states = []

        for name in state_names:
            state = StateFactory.create_state(name, game_instance)
            if state:
                states.append(state)

        return states
