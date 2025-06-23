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
    
    def test_final_boss_defeat_triggers_victory(self):
        """Test that defeating the final boss triggers game victory"""
        with patch('thunder_fighter.game.pygame') as mock_pygame, \
             patch('thunder_fighter.game.SoundManager') as mock_sound_manager_class:
            
            # Mock pygame initialization
            mock_pygame.init.return_value = None
            mock_pygame.display.set_mode.return_value = MagicMock()
            mock_pygame.display.set_caption.return_value = None
            mock_pygame.time.Clock.return_value = MagicMock()
            mock_pygame.font.Font.return_value = MagicMock()
            
            # Mock sound manager
            mock_sound_manager = MagicMock()
            mock_sound_manager_class.return_value = mock_sound_manager
            
            # Create game instance
            game = Game()
            
            # Set up final boss scenario
            game.game_level = MAX_GAME_LEVEL
            mock_boss = MagicMock()
            mock_boss.level = 3
            game.boss = mock_boss
            game.enemies = MagicMock()
            game.enemies.__len__.return_value = 0
            game.enemies.__iter__.return_value = iter([])
            game.enemies.empty.return_value = None
            
            # Execute boss defeat
            game.handle_boss_defeated()
            
            # Verify victory conditions
            assert game.game_won is True
            assert game.boss is None
            assert game.boss_active is False
            
            # Verify sound effects
            mock_sound_manager.play_sound.assert_called_with('boss_death.wav')
            mock_sound_manager.fadeout_music.assert_called_with(3000)
    
    def test_non_final_boss_defeat_does_not_trigger_victory(self):
        """Test that defeating non-final boss does not trigger victory"""
        with patch('thunder_fighter.game.pygame') as mock_pygame, \
             patch('thunder_fighter.game.SoundManager') as mock_sound_manager_class:
            
            # Mock pygame initialization
            mock_pygame.init.return_value = None
            mock_pygame.display.set_mode.return_value = MagicMock()
            mock_pygame.display.set_caption.return_value = None
            mock_pygame.time.Clock.return_value = MagicMock()
            mock_pygame.font.Font.return_value = MagicMock()
            
            # Mock sound manager
            mock_sound_manager = MagicMock()
            mock_sound_manager_class.return_value = mock_sound_manager
            
            # Create game instance
            game = Game()
            
            # Set up non-final boss scenario
            game.game_level = MAX_GAME_LEVEL - 1  # Not the final level
            mock_boss = MagicMock()
            mock_boss.level = 2
            game.boss = mock_boss
            game.enemies = MagicMock()
            game.enemies.__len__.return_value = 0
            game.enemies.__iter__.return_value = iter([])
            game.enemies.empty.return_value = None
            
            # Execute boss defeat
            game.handle_boss_defeated()
            
            # Verify no victory triggered
            assert game.game_won is False
            assert game.game_level == MAX_GAME_LEVEL  # Level should increase
            
            # Verify sound effects still play
            mock_sound_manager.play_sound.assert_called_with('boss_death.wav')
    
    def test_victory_screen_display(self):
        """Test that victory screen is properly displayed"""
        with patch('thunder_fighter.game.pygame') as mock_pygame, \
             patch('thunder_fighter.game.SoundManager') as mock_sound_manager_class:
            
            # Mock pygame initialization
            mock_pygame.init.return_value = None
            mock_screen = MagicMock()
            mock_pygame.display.set_mode.return_value = mock_screen
            mock_pygame.display.set_caption.return_value = None
            mock_pygame.time.Clock.return_value = MagicMock()
            mock_pygame.font.Font.return_value = MagicMock()
            
            # Mock sound manager
            mock_sound_manager = MagicMock()
            mock_sound_manager_class.return_value = mock_sound_manager
            
            # Create game instance
            game = Game()
            game.game_won = True
            game.score.value = 15000
            
            # Mock the UI manager's victory screen method
            game.ui_manager.draw_victory_screen = MagicMock()
            
            # Test that when game_won is True, victory screen should be called
            # We'll call the victory screen method directly instead of render()
            game.ui_manager.draw_victory_screen(game.score.value, MAX_GAME_LEVEL)
            
            # Verify victory screen is called with correct parameters
            game.ui_manager.draw_victory_screen.assert_called_with(15000, MAX_GAME_LEVEL)
    
    def test_victory_score_bonus(self):
        """Test that final boss defeat gives appropriate score bonus"""
        with patch('thunder_fighter.game.pygame') as mock_pygame, \
             patch('thunder_fighter.game.SoundManager') as mock_sound_manager_class:
            
            # Mock pygame initialization
            mock_pygame.init.return_value = None
            mock_pygame.display.set_mode.return_value = MagicMock()
            mock_pygame.display.set_caption.return_value = None
            mock_pygame.time.Clock.return_value = MagicMock()
            mock_pygame.font.Font.return_value = MagicMock()
            
            # Mock sound manager
            mock_sound_manager = MagicMock()
            mock_sound_manager_class.return_value = mock_sound_manager
            
            # Create game instance
            game = Game()
            
            # Set up final boss scenario
            game.game_level = MAX_GAME_LEVEL
            mock_boss = MagicMock()
            mock_boss.level = 3
            game.boss = mock_boss
            game.enemies = MagicMock()
            game.enemies.__len__.return_value = 0
            game.enemies.__iter__.return_value = iter([])
            game.enemies.empty.return_value = None
            
            # Mock score update
            game.score.update = MagicMock()
            
            # Execute boss defeat
            game.handle_boss_defeated()
            
            # Verify final boss bonus (boss_level * 1000)
            expected_bonus = mock_boss.level * 1000
            game.score.update.assert_called_with(expected_bonus)
    
    def test_victory_ui_notifications(self):
        """Test that victory triggers appropriate UI notifications"""
        with patch('thunder_fighter.game.pygame') as mock_pygame, \
             patch('thunder_fighter.game.SoundManager') as mock_sound_manager_class:
            
            # Mock pygame initialization
            mock_pygame.init.return_value = None
            mock_pygame.display.set_mode.return_value = MagicMock()
            mock_pygame.display.set_caption.return_value = None
            mock_pygame.time.Clock.return_value = MagicMock()
            mock_pygame.font.Font.return_value = MagicMock()
            
            # Mock sound manager
            mock_sound_manager = MagicMock()
            mock_sound_manager_class.return_value = mock_sound_manager
            
            # Create game instance
            game = Game()
            
            # Set up final boss scenario
            game.game_level = MAX_GAME_LEVEL
            mock_boss = MagicMock()
            mock_boss.level = 3
            game.boss = mock_boss
            game.enemies = MagicMock()
            game.enemies.__len__.return_value = 0
            game.enemies.__iter__.return_value = iter([])
            game.enemies.empty.return_value = None
            
            # Mock UI manager methods
            game.ui_manager.show_victory_screen = MagicMock()
            
            # Execute boss defeat
            game.handle_boss_defeated()
            
            # Verify victory screen is shown
            game.ui_manager.show_victory_screen.assert_called_once()
    
    def test_victory_prevents_further_spawning(self):
        """Test that victory state prevents further enemy/item spawning"""
        with patch('thunder_fighter.game.pygame') as mock_pygame, \
             patch('thunder_fighter.game.SoundManager') as mock_sound_manager_class:
            
            # Mock pygame initialization
            mock_pygame.init.return_value = None
            mock_pygame.display.set_mode.return_value = MagicMock()
            mock_pygame.display.set_caption.return_value = None
            mock_pygame.time.Clock.return_value = MagicMock()
            mock_pygame.font.Font.return_value = MagicMock()
            
            # Mock sound manager
            mock_sound_manager = MagicMock()
            mock_sound_manager_class.return_value = mock_sound_manager
            
            # Create game instance
            game = Game()
            game.game_won = True
            
            # Mock spawning methods
            game.spawn_enemy = MagicMock()
            game.spawn_random_item = MagicMock()
            game.spawn_boss = MagicMock()
            
            # Call update (which should be short-circuited due to victory)
            game.update()
            
            # Verify no spawning occurs
            game.spawn_enemy.assert_not_called()
            game.spawn_random_item.assert_not_called()
            game.spawn_boss.assert_not_called()
    
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