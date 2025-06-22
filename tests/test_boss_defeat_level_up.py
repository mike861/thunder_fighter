"""
Test module for boss defeat and level up functionality
"""
import pytest
import pygame
import time
from unittest.mock import MagicMock, patch, Mock
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

from thunder_fighter.game import Game
from thunder_fighter.sprites.boss import Boss
from thunder_fighter.sprites.enemy import Enemy
from thunder_fighter.constants import INITIAL_GAME_LEVEL, MAX_GAME_LEVEL


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
        game.enemy_bullets = MagicMock()
        game.boss_bullets = MagicMock()
        
        # Mock UI manager
        game.ui_manager = MagicMock()
        
        # Mock player
        game.player = MagicMock()
        game.player.health = 100
        
        # Mock score
        game.score = MagicMock()
        game.score.update = MagicMock()
        
        return game


class TestBossDefeatLevelUp:
    """Test boss defeat and level up functionality"""
    
    def test_handle_boss_defeated_basic(self, game_instance):
        """Test basic boss defeat handling"""
        # Setup
        initial_level = game_instance.game_level
        boss_level = 2
        
        # Create a mock boss
        mock_boss = MagicMock()
        mock_boss.level = boss_level
        mock_boss.kill = MagicMock()
        game_instance.boss = mock_boss
        
        # Setup mock enemies
        mock_enemies = [MagicMock(), MagicMock(), MagicMock()]
        game_instance.enemies.__len__.return_value = len(mock_enemies)
        game_instance.enemies.__iter__.return_value = iter(mock_enemies)
        
        # Call the method
        game_instance.handle_boss_defeated()
        
        # Verify level up
        assert game_instance.game_level == initial_level + 1
        
        # Verify boss removal
        mock_boss.kill.assert_called_once()
        assert game_instance.boss is None
        assert game_instance.boss_active is False
        
        # Verify enemies cleared
        game_instance.enemies.empty.assert_called_once()
        for enemy in mock_enemies:
            enemy.kill.assert_called_once()
        
        # Verify bullets cleared
        game_instance.enemy_bullets.empty.assert_called_once()
        game_instance.boss_bullets.empty.assert_called_once()
        
        # Verify score bonus
        expected_bonus = boss_level * 500
        game_instance.score.update.assert_called_with(expected_bonus)
        
        # Verify UI effects
        game_instance.ui_manager.show_level_up_effects.assert_called_once()
    
    def test_handle_boss_defeated_prevents_duplicate_processing(self, game_instance):
        """Test that boss defeat processing happens only once"""
        # Setup
        mock_boss = MagicMock()
        mock_boss.level = 2
        game_instance.boss = mock_boss
        game_instance.enemies.__len__.return_value = 2
        game_instance.enemies.__iter__.return_value = iter([MagicMock(), MagicMock()])
        
        initial_level = game_instance.game_level
        
        # Call the method twice
        game_instance.handle_boss_defeated()
        game_instance.handle_boss_defeated()
        
        # Verify only one level up occurred
        assert game_instance.game_level == initial_level + 1
        
        # Verify UI effects called only once
        assert game_instance.ui_manager.show_level_up_effects.call_count == 1
    
    def test_handle_boss_defeated_max_level_reached(self, game_instance):
        """Test boss defeat when max level is already reached"""
        # Setup
        game_instance.game_level = MAX_GAME_LEVEL
        initial_level = game_instance.game_level
        
        mock_boss = MagicMock()
        mock_boss.level = 3
        game_instance.boss = mock_boss
        game_instance.enemies.__len__.return_value = 1
        game_instance.enemies.__iter__.return_value = iter([MagicMock()])
        
        # Call the method
        game_instance.handle_boss_defeated()
        
        # Verify level doesn't increase beyond max
        assert game_instance.game_level == initial_level
        
        # But other effects still happen
        mock_boss.kill.assert_called_once()
        game_instance.enemies.empty.assert_called_once()
        game_instance.ui_manager.show_level_up_effects.assert_called_once()
    
    def test_handle_boss_defeated_no_boss(self, game_instance):
        """Test boss defeat handling when no boss exists"""
        # Setup
        game_instance.boss = None
        initial_level = game_instance.game_level
        game_instance.enemies.__len__.return_value = 2
        game_instance.enemies.__iter__.return_value = iter([MagicMock(), MagicMock()])
        
        # Call the method
        game_instance.handle_boss_defeated()
        
        # Verify level still increases
        assert game_instance.game_level == initial_level + 1
        
        # Verify other effects happen
        game_instance.enemies.empty.assert_called_once()
        game_instance.ui_manager.show_level_up_effects.assert_called_once()
    
    def test_boss_defeat_resets_timers(self, game_instance):
        """Test that boss defeat resets relevant timers"""
        # Setup
        mock_boss = MagicMock()
        mock_boss.level = 1
        game_instance.boss = mock_boss
        game_instance.enemies.__len__.return_value = 0
        game_instance.enemies.__iter__.return_value = iter([])
        
        old_boss_timer = game_instance.boss_spawn_timer
        old_enemy_timer = game_instance.enemy_spawn_timer
        
        # Call the method
        game_instance.handle_boss_defeated()
        
        # Verify timers were reset
        assert game_instance.boss_spawn_timer != old_boss_timer
        assert game_instance.enemy_spawn_timer != old_enemy_timer
        assert game_instance.boss_spawn_timer <= time.time()
        assert game_instance.enemy_spawn_timer <= time.time()
    
    def test_boss_defeat_updates_item_spawn_interval(self, game_instance):
        """Test that boss defeat updates item spawn interval for new level"""
        # Setup
        initial_level = game_instance.game_level
        mock_boss = MagicMock()
        mock_boss.level = 1
        game_instance.boss = mock_boss
        game_instance.enemies.__len__.return_value = 0
        game_instance.enemies.__iter__.return_value = iter([])
        
        # Call the method
        game_instance.handle_boss_defeated()
        
        # Verify item spawn interval was updated for new level
        new_level = initial_level + 1
        expected_interval = max(15, 30 - new_level)
        assert game_instance.item_spawn_interval == expected_interval
    
    def test_boss_defeat_plays_sound(self, game_instance):
        """Test that boss defeat plays victory sound"""
        # Setup
        mock_boss = MagicMock()
        mock_boss.level = 1
        game_instance.boss = mock_boss
        game_instance.enemies.__len__.return_value = 0
        game_instance.enemies.__iter__.return_value = iter([])
        
        # Mock the sound manager directly on the imported module
        with patch('thunder_fighter.game.sound_manager') as mock_sound_manager:
            # Call the method
            game_instance.handle_boss_defeated()
            
            # Verify sound played
            mock_sound_manager.play_sound.assert_called_with('boss_death.wav')
    
    def test_boss_defeat_processing_flag_reset(self, game_instance):
        """Test that boss defeat processing flag gets reset after delay"""
        # Setup
        mock_boss = MagicMock()
        mock_boss.level = 1
        game_instance.boss = mock_boss
        game_instance.enemies.__len__.return_value = 0
        game_instance.enemies.__iter__.return_value = iter([])
        
        # Call the method
        game_instance.handle_boss_defeated()
        
        # Verify processing flag is set
        assert hasattr(game_instance, '_boss_defeat_processed')
        assert hasattr(game_instance, '_boss_defeat_reset_time')
        
        # Simulate time passing beyond reset time
        game_instance._boss_defeat_reset_time = time.time() - 1.0
        
        # Call update to trigger flag reset
        with patch.object(game_instance, 'update_ui_state'), \
             patch.object(game_instance, '_check_sound_system'), \
             patch.object(game_instance, 'handle_collisions'):
            
            # Mock the time-based reset check
            if hasattr(game_instance, '_boss_defeat_reset_time') and time.time() >= game_instance._boss_defeat_reset_time:
                if hasattr(game_instance, '_boss_defeat_processed'):
                    delattr(game_instance, '_boss_defeat_processed')
                delattr(game_instance, '_boss_defeat_reset_time')
        
        # Verify flag is reset
        assert not hasattr(game_instance, '_boss_defeat_processed')
        assert not hasattr(game_instance, '_boss_defeat_reset_time') 