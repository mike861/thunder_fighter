import pytest
import pygame
from unittest.mock import MagicMock, patch
from thunder_fighter.entities.player.player import Player
from thunder_fighter.constants import (
    PLAYER_HEALTH, PLAYER_SPEED, BULLET_SPEED_DEFAULT, BULLET_PATHS_DEFAULT,
    PLAYER_MAX_SPEED, BULLET_SPEED_MAX, BULLET_PATHS_MAX
)

# Mock pygame for testing
pygame.init()
pygame.display.set_mode((800, 600))

@pytest.fixture
def mock_game():
    """Create a mock game object"""
    game = MagicMock()
    game.boss = None
    game.enemies_group = MagicMock()
    game.enemies_group.sprites.return_value = []
    return game

@pytest.fixture
def mock_sprite_groups():
    """Create mock sprite groups"""
    all_sprites = MagicMock()
    bullets_group = MagicMock()
    missiles_group = MagicMock()
    enemies_group = MagicMock()
    return all_sprites, bullets_group, missiles_group, enemies_group

@pytest.fixture
def mock_sound_manager():
    """Create a mock sound manager"""
    return MagicMock()

@pytest.fixture
def player(mock_game, mock_sprite_groups, mock_sound_manager):
    """Create a player instance for testing"""
    all_sprites, bullets_group, missiles_group, enemies_group = mock_sprite_groups
    return Player(mock_game, all_sprites, bullets_group, missiles_group, enemies_group, mock_sound_manager)

class TestPlayer:
    """Test Player class functionality"""

    def test_player_initialization(self, player):
        """Test player is initialized with correct default values"""
        assert player.health == PLAYER_HEALTH
        assert player.speed == PLAYER_SPEED
        assert player.bullet_speed == BULLET_SPEED_DEFAULT
        assert player.bullet_paths == BULLET_PATHS_DEFAULT
        assert player.max_speed == PLAYER_MAX_SPEED
        assert player.max_bullet_speed == BULLET_SPEED_MAX
        assert player.max_bullet_paths == BULLET_PATHS_MAX
        assert len(player.wingmen_list) == 0

    def test_player_shoot(self, player):
        """Test player shooting functionality"""
        # Mock the time to ensure shooting is allowed
        with patch('thunder_fighter.sprites.player.ptime') as mock_ptime:
            mock_ptime.get_ticks.return_value = 1000  # Set current time
            player.last_shot = 0  # Ensure enough time has passed
            
            # Test shooting with default bullet paths (1)
            player.shoot()
            
            # Verify bullets were added to groups
            assert player.all_sprites.add.called
            assert player.bullets_group.add.called

    def test_player_heal(self, player):
        """Test player healing functionality"""
        # Damage player first
        player.health = 50
        
        # Heal player
        initial_health = player.health
        player.heal(30)
        
        # Verify health increased but doesn't exceed max
        assert player.health == min(PLAYER_HEALTH, initial_health + 30)

    def test_player_increase_bullet_speed(self, player):
        """Test increasing bullet speed"""
        initial_speed = player.bullet_speed
        new_speed = player.increase_bullet_speed(2)
        
        assert player.bullet_speed == initial_speed + 2
        assert new_speed == player.bullet_speed

    def test_player_increase_bullet_paths(self, player):
        """Test increasing bullet paths"""
        initial_paths = player.bullet_paths
        new_paths = player.increase_bullet_paths()
        
        assert player.bullet_paths == initial_paths + 1
        assert new_paths == player.bullet_paths

    def test_player_increase_speed(self, player):
        """Test increasing player speed"""
        initial_speed = player.speed
        result = player.increase_speed()
        
        assert result is True
        assert player.speed > initial_speed

    def test_player_take_damage_with_wingman(self, player):
        """Test player takes damage when having wingmen (wingman should be consumed first)"""
        # Add a wingman
        player.add_wingman()
        initial_wingmen = len(player.wingmen_list)
        initial_health = player.health
        
        # Take damage
        result = player.take_damage(10)
        
        # Wingman should be consumed, player health unchanged
        assert len(player.wingmen_list) == initial_wingmen - 1
        assert player.health == initial_health
        assert result is False  # Player not dead

    def test_player_take_damage_without_wingman(self, player):
        """Test player takes damage when having no wingmen"""
        initial_health = player.health
        
        # Take damage
        result = player.take_damage(10)
        
        # Player health should decrease
        assert player.health == initial_health - 10
        assert result is False  # Player not dead (still has health)

    def test_player_take_fatal_damage(self, player):
        """Test player takes fatal damage"""
        player.health = 5  # Low health
        
        # Take fatal damage
        result = player.take_damage(10)
        
        # Player should be dead
        assert player.health <= 0
        assert result is True  # Player dead

    def test_player_add_wingman(self, player):
        """Test adding wingmen to player"""
        initial_count = len(player.wingmen_list)
        
        # Add wingman
        result = player.add_wingman()
        
        assert result is True
        assert len(player.wingmen_list) == initial_count + 1

    def test_player_max_wingmen_limit(self, player):
        """Test that player cannot exceed maximum wingmen"""
        from thunder_fighter.constants import PLAYER_MAX_WINGMEN
        
        # Add maximum wingmen
        for _ in range(PLAYER_MAX_WINGMEN):
            player.add_wingman()
        
        # Try to add one more
        result = player.add_wingman()
        
        assert result is False
        assert len(player.wingmen_list) == PLAYER_MAX_WINGMEN 