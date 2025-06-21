import pygame
import pytest
from unittest.mock import MagicMock, patch

from thunder_fighter.game import Game
from thunder_fighter.utils.score import Score
from thunder_fighter.graphics.ui_manager import PlayerUIManager

# Pytest fixture to create a mock game instance
@pytest.fixture
def mock_game():
    """Fixture to create a mocked Game instance for testing."""
    with patch('pygame.display.set_mode'), \
         patch('pygame.display.set_caption'), \
         patch('pygame.time.Clock'), \
         patch('thunder_fighter.sprites.player.Player'), \
         patch('thunder_fighter.utils.stars.create_stars'), \
         patch('thunder_fighter.utils.sound_manager.sound_manager'):
        
        # Mock the sound manager to prevent it from playing sounds
        sound_manager_mock = MagicMock()

        # Mock the UI manager
        ui_manager_mock = MagicMock(spec=PlayerUIManager)
        ui_manager_mock.persistent_info = {}

        # Mock the Score class
        score_mock = MagicMock(spec=Score)
        score_mock.value = 0

        with patch('thunder_fighter.game.PlayerUIManager', return_value=ui_manager_mock), \
             patch('thunder_fighter.game.Score', return_value=score_mock):
            game = Game()
            game.ui_manager = ui_manager_mock
            game.score = score_mock
            yield game

class TestGame:
    """Test suite for the main Game class."""

    def test_score_update_in_ui_state(self, mock_game):
        """
        Tests if the score is correctly updated in the UI manager's state.
        This test verifies the fix for the score always displaying as 0.
        """
        # Arrange: Set a score value
        test_score = 150
        mock_game.score.value = test_score
        
        # Act: Call the method that updates the UI state
        mock_game.update_ui_state()
        
        # Assert: Check if the UI manager's persistent info was updated
        assert 'score' in mock_game.ui_manager.persistent_info, "Score key should be in persistent_info"
        assert mock_game.ui_manager.persistent_info['score'] == test_score, \
            "UI manager's score should match the game's score" 