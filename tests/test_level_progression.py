"""
Test module for level progression logic
"""
import pytest
import pygame
import time
from unittest.mock import MagicMock, patch
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

# Mock pygame modules before importing game modules
pygame.mixer = MagicMock()
pygame.font = MagicMock()
pygame.display = MagicMock()

from thunder_fighter.game import RefactoredGame as Game
from thunder_fighter.constants import SCORE_THRESHOLD, MAX_GAME_LEVEL


@pytest.fixture
def mock_pygame():
    """Mock pygame for testing"""
    with patch('pygame.init'), \
         patch('pygame.display.set_mode'), \
         patch('pygame.display.set_caption'), \
         patch('pygame.time.Clock'), \
         patch('pygame.sprite.Group'), \
         patch('thunder_fighter.utils.sound_manager.sound_manager'):
        yield


@pytest.fixture
def game_instance(mock_pygame):
    """Create a game instance for testing"""
    with patch('thunder_fighter.sprites.player.Player'), \
         patch('thunder_fighter.utils.stars.create_stars'), \
         patch('thunder_fighter.graphics.ui_manager.PlayerUIManager'):
        game = Game()
        # Mock essential attributes
        game.clock = MagicMock()
        game.screen = MagicMock()
        game.running = True
        game.paused = False
        game.boss_defeated = False
        game.game_won = False
        
        # Mock sprite groups
        game.enemies = MagicMock()
        game.boss = None
        game.boss_active = False
        
        # Mock UI manager
        game.ui_manager = MagicMock()
        
        # Mock player
        game.player = MagicMock()
        game.player.health = 100
        
        # Mock score
        game.score = MagicMock()
        game.score.value = 0
        
        return game


class TestLevelProgression:
    """Test level progression logic"""
    
    def test_score_based_level_up_level_0_to_1(self, game_instance):
        """Test that score-based level up works for level 0 to 1"""
        # Setup
        game_instance.game_level = 0
        game_instance.score.value = SCORE_THRESHOLD  # Enough to trigger level up
        
        # Mock the update methods to avoid side effects
        with patch.object(game_instance, 'update_ui_state'), \
             patch.object(game_instance, '_check_sound_system'), \
             patch.object(game_instance, 'handle_collisions'):
            
            # Call update which should trigger level up
            game_instance.update()
            
            # Verify level increased
            assert game_instance.game_level == 1
    
    def test_score_based_level_up_level_1_to_2(self, game_instance):
        """Test that score-based level up works for level 1 to 2"""
        # Setup
        game_instance.game_level = 1
        game_instance.score.value = SCORE_THRESHOLD * 2  # Enough to trigger level up
        
        # Mock the update methods to avoid side effects
        with patch.object(game_instance, 'update_ui_state'), \
             patch.object(game_instance, '_check_sound_system'), \
             patch.object(game_instance, 'handle_collisions'):
            
            # Call update which should trigger level up
            game_instance.update()
            
            # Verify level increased
            assert game_instance.game_level == 2
    
    def test_no_score_based_level_up_after_level_2(self, game_instance):
        """Test that score-based level up doesn't work after level 2"""
        # Setup
        game_instance.game_level = 2
        game_instance.score.value = SCORE_THRESHOLD * 10  # Way more than enough
        
        # Mock the update methods to avoid side effects
        with patch.object(game_instance, 'update_ui_state'), \
             patch.object(game_instance, '_check_sound_system'), \
             patch.object(game_instance, 'handle_collisions'):
            
            # Call update multiple times
            for _ in range(5):
                game_instance.update()
            
            # Verify level didn't change
            assert game_instance.game_level == 2
    
    def test_no_score_based_level_up_after_level_3(self, game_instance):
        """Test that score-based level up doesn't work at higher levels"""
        # Setup
        game_instance.game_level = 5
        game_instance.score.value = SCORE_THRESHOLD * 20  # Massive score
        
        # Mock the update methods to avoid side effects
        with patch.object(game_instance, 'update_ui_state'), \
             patch.object(game_instance, '_check_sound_system'), \
             patch.object(game_instance, 'handle_collisions'):
            
            # Call update
            game_instance.update()
            
            # Verify level didn't change
            assert game_instance.game_level == 5
    
    def test_boss_spawn_only_after_level_1(self, game_instance):
        """Test that boss only spawns after level 1"""
        # Test level 1 - no boss spawn
        game_instance.game_level = 1
        game_instance.boss_spawn_timer = time.time() - 100  # Long enough ago
        
        with patch.object(game_instance, 'update_ui_state'), \
             patch.object(game_instance, '_check_sound_system'), \
             patch.object(game_instance, 'handle_collisions'), \
             patch.object(game_instance, '_spawn_boss_via_factory') as mock_spawn_boss:
            
            game_instance.update()
            
            # Verify boss was not spawned
            mock_spawn_boss.assert_not_called()
        
        # Test level 2 - boss should spawn
        game_instance.game_level = 2
        
        with patch.object(game_instance, 'update_ui_state'), \
             patch.object(game_instance, '_check_sound_system'), \
             patch.object(game_instance, 'handle_collisions'), \
             patch.object(game_instance, '_spawn_boss_via_factory') as mock_spawn_boss:
            
            game_instance.update()
            
            # Verify boss was spawned
            mock_spawn_boss.assert_called_once()
    
    def test_boss_defeat_still_triggers_level_up(self, game_instance):
        """Test that boss defeat still triggers level up at any level"""
        # Setup
        game_instance.game_level = 3
        boss_level = 2
        
        # Create a mock boss
        mock_boss = MagicMock()
        mock_boss.level = boss_level
        mock_boss.kill = MagicMock()
        game_instance.boss = mock_boss
        
        # Setup mock enemies
        game_instance.enemies.__len__.return_value = 2
        game_instance.enemies.__iter__.return_value = iter([MagicMock(), MagicMock()])
        
        # Call boss defeat handler
        game_instance.handle_boss_defeated()
        
        # Verify level up occurred
        assert game_instance.game_level == 4
    
    def test_mixed_progression_path(self, game_instance):
        """Test the complete progression path: score up to level 2, then boss only"""
        # Start at level 0
        game_instance.game_level = 0
        
        # Score-based progression to level 1
        game_instance.score.value = SCORE_THRESHOLD
        with patch.object(game_instance, 'update_ui_state'), \
             patch.object(game_instance, '_check_sound_system'), \
             patch.object(game_instance, 'handle_collisions'):
            game_instance.update()
        assert game_instance.game_level == 1
        
        # Score-based progression to level 2
        game_instance.score.value = SCORE_THRESHOLD * 2
        with patch.object(game_instance, 'update_ui_state'), \
             patch.object(game_instance, '_check_sound_system'), \
             patch.object(game_instance, 'handle_collisions'):
            game_instance.update()
        assert game_instance.game_level == 2
        
        # Now only boss defeat should work
        game_instance.score.value = SCORE_THRESHOLD * 10  # Huge score
        with patch.object(game_instance, 'update_ui_state'), \
             patch.object(game_instance, '_check_sound_system'), \
             patch.object(game_instance, 'handle_collisions'):
            game_instance.update()
        # Level should still be 2 (no score-based upgrade)
        assert game_instance.game_level == 2
        
        # Boss defeat should advance to level 3
        mock_boss = MagicMock()
        mock_boss.level = 1
        game_instance.boss = mock_boss
        game_instance.enemies.__len__.return_value = 0
        game_instance.enemies.__iter__.return_value = iter([])
        
        game_instance.handle_boss_defeated()
        assert game_instance.game_level == 3 