"""
Score Management System

Manages game score, level, achievements, and related logic in a unified way.
Refactored from utils/score.py.
"""

from typing import Callable, List, Optional

import pygame

from thunder_fighter.constants import FONT_NAME, FONT_SIZE_MEDIUM, WHITE
from thunder_fighter.utils.logger import logger


class ScoringSystem:
    """Score Management System Class"""

    def __init__(self):
        self.score = 0
        self.level = 1
        self.score_multiplier = 1.0
        self.achievement_callbacks: List[Callable] = []

        # Display related
        self.font: Optional[pygame.font.Font] = None
        self.text: Optional[pygame.Surface] = None
        self.rect: Optional[pygame.Rect] = None

        self._init_display()
        self.update_display()

    def _init_display(self):
        """Initializes display-related components."""
        # Use resource manager to load font with caching
        from thunder_fighter.utils.resource_manager import get_resource_manager

        resource_manager = get_resource_manager()

        try:
            # Use original font size with Chinese character support
            self.font = resource_manager.load_font(FONT_NAME, FONT_SIZE_MEDIUM, system_font=True)
        except Exception:
            self.font = resource_manager.load_font(None, FONT_SIZE_MEDIUM, system_font=True)

    def add_score(self, points: int, source: str = ""):
        """Adds score."""
        actual_points = int(points * self.score_multiplier)
        self.score += actual_points
        logger.debug(f"Score added: {actual_points} from {source}")
        self.update_display()
        self._check_level_up()
        self._check_achievements()

    def update_score(self, points: int):
        """Updates score (for compatibility with the original interface)."""
        self.add_score(points)

    def get_score(self) -> int:
        """Gets the current score."""
        return self.score

    def get_level(self) -> int:
        """Gets the current level."""
        return self.level

    def set_multiplier(self, multiplier: float):
        """Sets the score multiplier."""
        self.score_multiplier = multiplier
        logger.info(f"Score multiplier set to: {multiplier}")

    def reset(self):
        """Resets the score and level."""
        self.score = 0
        self.level = 1
        self.score_multiplier = 1.0
        self.update_display()
        logger.info("Scoring system reset")

    def _check_level_up(self):
        """Checks for level up."""
        # Level up every 1000 points
        new_level = (self.score // 1000) + 1
        if new_level > self.level:
            old_level = self.level
            self.level = new_level
            logger.info(f"Level up! {old_level} -> {new_level}")
            self._trigger_level_up_callbacks(old_level, new_level)

    def _check_achievements(self):
        """Checks for achievements."""
        # Trigger achievement callbacks
        for callback in self.achievement_callbacks:
            try:
                callback(self.score, self.level)
            except Exception as e:
                logger.error(f"Error in achievement callback: {e}")

    def add_achievement_callback(self, callback: Callable):
        """Adds an achievement callback function."""
        self.achievement_callbacks.append(callback)

    def _trigger_level_up_callbacks(self, old_level: int, new_level: int):
        """Triggers level up callbacks."""
        # Special effects for level up can be added here
        pass

    # Display methods (compatible with original Score class)
    def update_display(self):
        """Updates the score display."""
        from thunder_fighter.localization import _

        score_text = _("SCORE_DISPLAY", self.score)
        if self.font is not None:
            self.text = self.font.render(score_text, True, WHITE)
        else:
            # Fallback if font is None
            import pygame

            default_font = pygame.font.Font(None, 24)
            self.text = default_font.render(score_text, True, WHITE)
        self.rect = self.text.get_rect()
        self.rect.topleft = (10, 10)

    def draw(self, screen: pygame.Surface):
        """Draws the score."""
        if self.text and self.rect:
            screen.blit(self.text, self.rect)

    @property
    def value(self) -> int:
        """Compatibility with the value attribute of the original Score class."""
        return self.score

    def update(self, points: int):
        """Compatibility with the update method of the original Score class."""
        self.add_score(points)


# Compatibility function: create a traditional Score class instance
def create_legacy_score():
    """Creates an instance compatible with the original Score class."""
    return ScoringSystem()


# Compatibility alias
Score = ScoringSystem
