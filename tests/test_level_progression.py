"""
Test module for level progression functionality
"""

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

if TYPE_CHECKING:
    pass

from thunder_fighter.constants import GAME_CONFIG
from thunder_fighter.game import RefactoredGame as Game


class TestLevelProgression:
    """Test level progression logic - simplified version"""

    def test_initial_game_level(self):
        """Test that game starts at correct level"""
        # Mock pygame modules inside the test method to avoid global pollution
        with patch("pygame.mixer", MagicMock()), patch("pygame.font", MagicMock()), patch(
            "pygame.display", MagicMock()
        ), patch("pygame.init"), patch("pygame.display.set_mode"), patch(
            "thunder_fighter.entities.player.player.Player"
        ), patch("thunder_fighter.graphics.effects.stars.create_stars"):
            game = Game()
            assert game.game_level == 1

    def test_score_threshold_constant(self):
        """Test that score threshold is properly defined"""
        SCORE_THRESHOLD = int(GAME_CONFIG["SCORE_THRESHOLD"])
        assert SCORE_THRESHOLD > 0
        assert isinstance(SCORE_THRESHOLD, int)

    def test_max_game_level_constant(self):
        """Test that max game level is properly defined"""
        MAX_GAME_LEVEL = int(GAME_CONFIG["MAX_GAME_LEVEL"])
        assert MAX_GAME_LEVEL > 1
        assert isinstance(MAX_GAME_LEVEL, int)

    def test_level_progression_event_system_exists(self):
        """Test that game has event system for level progression"""
        with patch("pygame.init"), patch("pygame.display.set_mode"), patch(
            "thunder_fighter.entities.player.player.Player"
        ), patch("thunder_fighter.graphics.effects.stars.create_stars"):
            game = Game()
            assert hasattr(game, "event_system")
            assert hasattr(game.event_system, "dispatch_event")
            assert hasattr(game.event_system, "register_listener")
