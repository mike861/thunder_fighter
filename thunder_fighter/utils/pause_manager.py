"""
Pause Manager

A dedicated component for managing game pause state and pause-aware timing.
This module provides a testable interface for pause functionality.
"""

import time
from dataclasses import dataclass
from typing import Optional

from thunder_fighter.utils.logger import logger


@dataclass
class PauseStats:
    """Statistics about pause state and timing."""

    is_paused: bool
    total_pause_duration: float
    current_pause_duration: float
    pause_count: int
    last_toggle_time: float

    def __str__(self) -> str:
        return (
            f"PauseStats(paused={self.is_paused}, "
            f"total_duration={self.total_pause_duration:.2f}s, "
            f"pause_count={self.pause_count})"
        )


class PauseManager:
    """
    Manages game pause state and pause-aware timing calculations.

    This class provides a clean, testable interface for pause functionality,
    separating it from the main game logic.
    """

    def __init__(self, cooldown_ms: int = 300):
        """
        Initialize the pause manager.

        Args:
            cooldown_ms: Minimum milliseconds between pause toggles
        """
        self.cooldown_seconds = cooldown_ms / 1000.0

        # Pause state
        self._is_paused = False
        self._pause_start_time: Optional[float] = None
        self._total_paused_time = 0.0
        self._pause_count = 0
        self._last_toggle_time = 0.0

        logger.info(f"PauseManager initialized with {cooldown_ms}ms cooldown")

    @property
    def is_paused(self) -> bool:
        """Check if the game is currently paused."""
        return self._is_paused

    def toggle_pause(self, current_time: Optional[float] = None) -> bool:
        """
        Toggle the pause state.

        Args:
            current_time: Current time in seconds. If None, uses time.time()

        Returns:
            True if pause state was toggled, False if blocked by cooldown
        """
        if current_time is None:
            current_time = time.time()

        # Check cooldown
        if current_time - self._last_toggle_time < self.cooldown_seconds:
            time_since_toggle = current_time - self._last_toggle_time
            logger.debug(f"Pause toggle blocked by cooldown: {time_since_toggle:.3f}s < {self.cooldown_seconds}s")
            return False

        self._last_toggle_time = current_time

        if self._is_paused:
            # Resume game
            if self._pause_start_time is not None:
                pause_duration = current_time - self._pause_start_time
                self._total_paused_time += pause_duration
                logger.info(f"Game resumed. Pause duration: {pause_duration:.3f}s")
                self._pause_start_time = None
            else:
                logger.warning("Resume called but no pause start time recorded")

            self._is_paused = False

        else:
            # Pause game
            self._is_paused = True
            self._pause_start_time = current_time
            self._pause_count += 1
            logger.info(f"Game paused (pause #{self._pause_count})")

        return True

    def pause(self, current_time: Optional[float] = None) -> bool:
        """
        Pause the game if not already paused.

        Args:
            current_time: Current time in seconds

        Returns:
            True if successfully paused, False otherwise
        """
        if not self._is_paused:
            return self.toggle_pause(current_time)
        return False

    def resume(self, current_time: Optional[float] = None) -> bool:
        """
        Resume the game if paused.

        Args:
            current_time: Current time in seconds

        Returns:
            True if successfully resumed, False otherwise
        """
        if self._is_paused:
            return self.toggle_pause(current_time)
        return False

    def get_pause_stats(self) -> PauseStats:
        """
        Get current pause statistics.

        Returns:
            PauseStats object with current pause information
        """
        current_pause_duration = 0.0
        if self._is_paused and self._pause_start_time is not None:
            current_pause_duration = time.time() - self._pause_start_time

        return PauseStats(
            is_paused=self._is_paused,
            total_pause_duration=self._total_paused_time,
            current_pause_duration=current_pause_duration,
            pause_count=self._pause_count,
            last_toggle_time=self._last_toggle_time,
        )

    def calculate_game_time(self, start_time: float, current_time: Optional[float] = None) -> float:
        """
        Calculate pause-aware game time.

        Args:
            start_time: Game start time in seconds
            current_time: Current time in seconds. If None, uses time.time()

        Returns:
            Game time in seconds, excluding pause duration
        """
        if current_time is None:
            current_time = time.time()

        total_paused = self._total_paused_time

        # Add current pause duration if currently paused
        if self._is_paused and self._pause_start_time is not None:
            total_paused += current_time - self._pause_start_time

        game_time = current_time - start_time - total_paused
        return max(0.0, game_time)  # Ensure non-negative

    def reset(self):
        """Reset pause manager to initial state."""
        self._is_paused = False
        self._pause_start_time = None
        self._total_paused_time = 0.0
        self._pause_count = 0
        self._last_toggle_time = 0.0
        logger.debug("PauseManager reset")

    def get_total_pause_duration(self) -> float:
        """
        Get total time spent paused.

        Returns:
            Total pause duration in seconds
        """
        total = self._total_paused_time
        if self._is_paused and self._pause_start_time is not None:
            total += time.time() - self._pause_start_time
        return total

    def __str__(self) -> str:
        return f"PauseManager(paused={self._is_paused}, pause_count={self._pause_count})"
