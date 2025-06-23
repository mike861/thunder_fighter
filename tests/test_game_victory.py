"""Test cases for game victory functionality when defeating level 10 boss"""

import pytest
import pygame
import time
from unittest.mock import Mock, patch, MagicMock
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

from thunder_fighter.game import Game
from thunder_fighter.constants import MAX_GAME_LEVEL


class TestGameVictory:
    """Test cases for game victory functionality"""
    
    def setup_method(self):
        """Set up test environment before each test"""
        # Initialize pygame for testing
        pygame.init()
        pygame.display.set_mode((1, 1))  # Minimal display for testing
        
    def teardown_method(self):
        """Clean up after each test"""
        pygame.quit()
    
    @patch('thunder_fighter.game.sound_manager')
    def test_final_boss_defeat_triggers_victory(self, mock_sound_manager):
        """Test that defeating the level 10 boss triggers game victory"""
        # Create game instance
        game = Game()
        
        # Set game to level 10 (final level)
        game.game_level = MAX_GAME_LEVEL
        game.game_won = False
        
        # Create a mock boss at level 10
        mock_boss = Mock()
        mock_boss.level = 5  # Boss level for scoring
        mock_boss.kill = Mock()
        game.boss = mock_boss
        game.boss_active = True
        
        # Mock UI manager methods
        game.ui_manager.update_boss_info = Mock()
        game.ui_manager.show_victory_screen = Mock()
        
        # Mock score
        game.score.update = Mock()
        
        # Call handle_boss_defeated
        game.handle_boss_defeated()
        
        # Verify victory state
        assert game.game_won == True, "Game should be won after defeating final boss"
        
        # Verify victory screen is shown
        game.ui_manager.show_victory_screen.assert_called_once()
        
        # Verify final boss bonus is applied (boss_level * 1000)
        game.score.update.assert_called_with(5000)
        
        # Verify victory sound is played
        mock_sound_manager.play_sound.assert_called_with('boss_death.wav')
        
        # Verify music fades out
        mock_sound_manager.fadeout_music.assert_called_with(3000)
    
    @patch('thunder_fighter.game.sound_manager')
    def test_non_final_boss_defeat_does_not_trigger_victory(self, mock_sound_manager):
        """Test that defeating a non-final boss does not trigger victory"""
        # Create game instance
        game = Game()
        
        # Set game to level 2 (not final level, MAX_GAME_LEVEL = 4)
        game.game_level = 2
        game.game_won = False
        
        # Create a mock boss
        mock_boss = Mock()
        mock_boss.level = 3
        mock_boss.kill = Mock()
        game.boss = mock_boss
        game.boss_active = True
        
        # Mock UI manager methods
        game.ui_manager.update_boss_info = Mock()
        game.ui_manager.show_victory_screen = Mock()
        game.ui_manager.show_level_up_effects = Mock()
        
        # Mock score and sprite groups properly
        game.score.update = Mock()
        
        # Mock sprite groups with proper methods
        mock_enemies = Mock()
        mock_enemies.__len__ = Mock(return_value=2)
        mock_enemies.__iter__ = Mock(return_value=iter([Mock(), Mock()]))
        mock_enemies.empty = Mock()
        game.enemies = mock_enemies
        
        mock_enemy_bullets = Mock()
        mock_enemy_bullets.__iter__ = Mock(return_value=iter([]))
        mock_enemy_bullets.empty = Mock()
        game.enemy_bullets = mock_enemy_bullets
        
        mock_boss_bullets = Mock()
        mock_boss_bullets.__iter__ = Mock(return_value=iter([]))
        mock_boss_bullets.empty = Mock()
        game.boss_bullets = mock_boss_bullets
        
        # Call handle_boss_defeated
        game.handle_boss_defeated()
        
        # Verify victory state is NOT triggered
        assert game.game_won == False, "Game should not be won for non-final boss"
        
        # Verify victory screen is NOT shown
        game.ui_manager.show_victory_screen.assert_not_called()
        
        # Verify level up effects are shown instead
        game.ui_manager.show_level_up_effects.assert_called_once()
        
        # Verify normal boss bonus is applied (boss_level * 500)
        game.score.update.assert_called_with(1500)
        
        # Verify game level increases
        assert game.game_level == 3, "Game level should increase after non-final boss defeat"
    
    def test_victory_ui_state_update(self):
        """Test that victory state is properly updated in UI"""
        # Create game instance
        game = Game()
        
        # Set victory state
        game.game_won = True
        
        # Mock UI manager
        game.ui_manager.update_game_state = Mock()
        game.ui_manager.persistent_info = {}  # Make it a real dict
        
        # Call update_ui_state
        game.update_ui_state()
        
        # Verify victory state is passed to UI
        game.ui_manager.update_game_state.assert_called()
        call_args = game.ui_manager.update_game_state.call_args[1]
        assert call_args['victory'] == True, "Victory state should be passed to UI manager"
    
    def test_victory_stops_game_updates(self):
        """Test that game updates stop when victory is achieved"""
        # Create game instance
        game = Game()
        
        # Set victory state
        game.game_won = True
        game.paused = False
        
        # Mock methods that should not be called during victory
        game.spawn_enemy = Mock()
        game.spawn_boss = Mock()
        game.spawn_random_item = Mock()
        game.handle_collisions = Mock()
        
        # Mock required attributes
        game.background = Mock()
        game.background.update = Mock()
        game.all_sprites = Mock()
        game.all_sprites.update = Mock()
        game.ui_manager.update = Mock()
        game.ui_manager.update_game_state = Mock()
        game.ui_manager.persistent_info = {}  # Make it a real dict
        
        # Call update method
        game.update()
        
        # Verify game logic methods are not called
        game.spawn_enemy.assert_not_called()
        game.spawn_boss.assert_not_called()
        game.spawn_random_item.assert_not_called()
        game.handle_collisions.assert_not_called()
    
    def test_show_victory_screen_method(self):
        """Test the show_victory_screen method in UI manager"""
        # Create game instance
        game = Game()
        
        # Mock notification methods and capture calls
        captured_calls = []
        def mock_add_notification(text, notification_type="normal"):
            captured_calls.append((text, notification_type))
        
        game.ui_manager.add_notification = Mock(side_effect=mock_add_notification)
        
        # Call show_victory_screen
        final_score = 50000
        game.ui_manager.show_victory_screen(final_score)
        
        # Verify victory state is set
        assert game.ui_manager.game_state['victory'] == True, "Victory state should be set in UI manager"
        
        # Verify victory notifications are added
        assert len(captured_calls) == 2, f"Two victory notifications should be added, got {len(captured_calls)}"
        
        # Check notification calls - verify the actual localized texts
        notification_texts = [call[0] for call in captured_calls]
        notification_types = [call[1] for call in captured_calls]
        
        # Verify the notifications contain the expected content
        assert any("Final Boss Defeated" in text for text in notification_texts), f"Final boss defeated notification should be added. Got: {notification_texts}"
        assert any("Congratulations" in text and "Thunder Fighter" in text for text in notification_texts), f"Game completed notification should be added. Got: {notification_texts}"
        
        # Verify both notifications are achievement type
        assert all(ntype == "achievement" for ntype in notification_types), "All victory notifications should be achievement type"
    
    def test_victory_prevents_duplicate_processing(self):
        """Test that victory processing prevents duplicate boss defeat handling"""
        # Create game instance
        game = Game()
        
        # Set game to level 10
        game.game_level = MAX_GAME_LEVEL
        game.game_won = False
        
        # Create a mock boss
        mock_boss = Mock()
        mock_boss.level = 5
        mock_boss.kill = Mock()
        game.boss = mock_boss
        game.boss_active = True
        
        # Mock UI manager methods
        game.ui_manager.update_boss_info = Mock()
        game.ui_manager.show_victory_screen = Mock()
        game.score.update = Mock()
        
        # Call handle_boss_defeated first time
        game.handle_boss_defeated()
        
        # Verify victory is triggered
        assert game.game_won == True
        first_call_count = game.ui_manager.show_victory_screen.call_count
        
        # Call handle_boss_defeated second time (should not process again)
        game.handle_boss_defeated()
        
        # Verify victory screen is not called again
        assert game.ui_manager.show_victory_screen.call_count == first_call_count, "Victory screen should not be called multiple times" 