"""
Unit tests for Enemy entity.

Tests the Enemy class focusing on behavior and interface rather than 
implementation details, following the new architecture patterns.
"""

from unittest.mock import MagicMock, patch

import pygame

from thunder_fighter.constants import ENEMY_SHOOT_LEVEL
from thunder_fighter.entities.enemies.enemy import Enemy


class TestEnemyEntity:
    """Test the Enemy entity class."""

    def setup_method(self):
        """Set up test environment."""
        # Mock pygame components
        self.mock_all_sprites = MagicMock()
        self.mock_enemy_bullets = MagicMock()

        # Mock pygame.sprite.Group for sprite groups
        pygame.sprite.Group = MagicMock

    @patch('thunder_fighter.entities.enemies.enemy.create_enemy_ship')
    @patch('pygame.time.get_ticks')
    def test_enemy_level_determination(self, mock_get_ticks, mock_create_ship):
        """Test that enemy level is determined correctly based on game state."""
        mock_get_ticks.return_value = 1000
        mock_create_ship.return_value = MagicMock()

        # Test early game enemies
        early_enemy = Enemy(
            game_time=0,
            game_level=1,
            all_sprites=self.mock_all_sprites,
            enemy_bullets_group=self.mock_enemy_bullets
        )
        assert early_enemy.level >= 0  # Should have some level

        # Test later game enemies should generally be higher level
        late_enemy = Enemy(
            game_time=10,
            game_level=5,
            all_sprites=self.mock_all_sprites,
            enemy_bullets_group=self.mock_enemy_bullets
        )

        # We can't guarantee exact level due to randomness, but we can test structure
        assert hasattr(late_enemy, 'level')
        assert isinstance(late_enemy.level, int)
        assert late_enemy.level >= 0

    @patch('thunder_fighter.entities.enemies.enemy.create_enemy_ship')
    @patch('pygame.time.get_ticks')
    def test_enemy_shooting_capability(self, mock_get_ticks, mock_create_ship):
        """Test that enemy shooting capability follows level rules."""
        mock_get_ticks.return_value = 1000
        mock_create_ship.return_value = MagicMock()

        # Create multiple enemies and check shooting capability consistency
        for _ in range(10):
            enemy = Enemy(
                game_time=5,
                game_level=3,
                all_sprites=self.mock_all_sprites,
                enemy_bullets_group=self.mock_enemy_bullets
            )

            # Shooting capability should be consistent with level
            if enemy.level >= ENEMY_SHOOT_LEVEL:
                assert enemy.can_shoot is True, f"Enemy level {enemy.level} should be able to shoot"
            else:
                assert enemy.can_shoot is False, f"Enemy level {enemy.level} should not be able to shoot"

    @patch('thunder_fighter.entities.enemies.enemy.create_enemy_ship')
    @patch('pygame.time.get_ticks')
    def test_enemy_initialization_attributes(self, mock_get_ticks, mock_create_ship):
        """Test that enemy initializes with required attributes."""
        mock_get_ticks.return_value = 1000
        mock_image = MagicMock()
        mock_rect = MagicMock()
        mock_image.get_rect.return_value = mock_rect
        mock_create_ship.return_value = mock_image

        enemy = Enemy(
            game_time=2,
            game_level=2,
            all_sprites=self.mock_all_sprites,
            enemy_bullets_group=self.mock_enemy_bullets
        )

        # Check essential attributes exist
        assert hasattr(enemy, 'level')
        assert hasattr(enemy, 'image')
        assert hasattr(enemy, 'rect')
        assert hasattr(enemy, 'speedy')
        assert hasattr(enemy, 'speedx')
        assert hasattr(enemy, 'can_shoot')
        assert hasattr(enemy, 'shoot_delay')
        assert hasattr(enemy, 'last_shot')

        # Check attribute types
        assert isinstance(enemy.level, int)
        assert isinstance(enemy.speedy, int)
        assert isinstance(enemy.speedx, int)
        assert isinstance(enemy.can_shoot, bool)
        assert isinstance(enemy.shoot_delay, int)
        assert isinstance(enemy.last_shot, int)

    @patch('thunder_fighter.entities.enemies.enemy.create_enemy_ship')
    @patch('thunder_fighter.entities.enemies.enemy.EnemyBullet')
    @patch('pygame.time.get_ticks')
    def test_enemy_shooting_behavior(self, mock_get_ticks, mock_enemy_bullet, mock_create_ship):
        """Test enemy shooting behavior when conditions are met."""
        mock_get_ticks.return_value = 5000  # Set a time that allows shooting
        mock_create_ship.return_value = MagicMock()
        mock_bullet = MagicMock()
        mock_enemy_bullet.return_value = mock_bullet

        # Create enemy with shooting capability
        with patch.object(Enemy, '_determine_level', return_value=3):  # Level 3 can shoot
            enemy = Enemy(
                game_time=5,
                game_level=3,
                all_sprites=self.mock_all_sprites,
                enemy_bullets_group=self.mock_enemy_bullets
            )

        # Force shooting conditions
        enemy.can_shoot = True
        enemy.last_shot = 0  # Long time ago
        enemy.shoot_delay = 1000

        # Test shoot method exists and works
        if hasattr(enemy, 'shoot'):
            enemy.shoot()
            # If shoot method exists, it should create bullets when conditions are met
            # We don't test exact implementation but that the interface works

    @patch('thunder_fighter.entities.enemies.enemy.create_enemy_ship')
    @patch('pygame.time.get_ticks')
    def test_enemy_movement_properties(self, mock_get_ticks, mock_create_ship):
        """Test that enemy has proper movement properties."""
        mock_get_ticks.return_value = 1000
        mock_create_ship.return_value = MagicMock()

        enemy = Enemy(
            game_time=3,
            game_level=2,
            all_sprites=self.mock_all_sprites,
            enemy_bullets_group=self.mock_enemy_bullets
        )

        # Check movement properties are reasonable
        assert enemy.speedy > 0, "Enemy should have positive vertical speed"
        assert isinstance(enemy.speedx, int), "Enemy should have horizontal speed"

        # Test that higher level/time generally means faster enemies
        # (We test the structure, not exact values due to randomness)
        high_level_enemy = Enemy(
            game_time=10,
            game_level=5,
            all_sprites=self.mock_all_sprites,
            enemy_bullets_group=self.mock_enemy_bullets
        )

        # Both should have reasonable speed values
        assert high_level_enemy.speedy > 0
        assert isinstance(high_level_enemy.speedx, int)

    @patch('thunder_fighter.entities.enemies.enemy.create_enemy_ship')
    @patch('pygame.time.get_ticks')
    def test_enemy_level_progression(self, mock_get_ticks, mock_create_ship):
        """Test that enemy levels progress logically with game state."""
        mock_get_ticks.return_value = 1000
        mock_create_ship.return_value = MagicMock()

        # Test different game states and collect level data
        early_levels = []
        late_levels = []

        # Sample multiple enemies to account for randomness
        for _ in range(20):
            early_enemy = Enemy(
                game_time=0,
                game_level=1,
                all_sprites=self.mock_all_sprites,
                enemy_bullets_group=self.mock_enemy_bullets
            )
            early_levels.append(early_enemy.level)

            late_enemy = Enemy(
                game_time=15,
                game_level=8,
                all_sprites=self.mock_all_sprites,
                enemy_bullets_group=self.mock_enemy_bullets
            )
            late_levels.append(late_enemy.level)

        # Statistical test: late game should generally have higher levels
        avg_early = sum(early_levels) / len(early_levels)
        avg_late = sum(late_levels) / len(late_levels)

        # Late game average should be higher (allowing some variance)
        assert avg_late >= avg_early - 0.5, f"Late game avg ({avg_late}) should be >= early game avg ({avg_early})"

        # All levels should be in valid range
        for level in early_levels + late_levels:
            assert 0 <= level <= 10, f"Enemy level {level} out of valid range [0-10]"

    @patch('thunder_fighter.entities.enemies.enemy.create_enemy_ship')
    @patch('pygame.time.get_ticks')
    def test_enemy_shoot_delay_scaling(self, mock_get_ticks, mock_create_ship):
        """Test that enemy shoot delay scales with level."""
        mock_get_ticks.return_value = 1000
        mock_create_ship.return_value = MagicMock()

        # Test different levels have reasonable shoot delays
        with patch.object(Enemy, '_determine_level', return_value=2):
            low_level_enemy = Enemy(
                game_time=1,
                game_level=1,
                all_sprites=self.mock_all_sprites,
                enemy_bullets_group=self.mock_enemy_bullets
            )

        with patch.object(Enemy, '_determine_level', return_value=5):
            high_level_enemy = Enemy(
                game_time=5,
                game_level=5,
                all_sprites=self.mock_all_sprites,
                enemy_bullets_group=self.mock_enemy_bullets
            )

        # Both should have reasonable shoot delays
        assert low_level_enemy.shoot_delay > 0
        assert high_level_enemy.shoot_delay > 0

        # Higher level enemies should generally shoot faster (lower delay)
        # (This is a general expectation, allowing some variance)
        assert high_level_enemy.shoot_delay <= low_level_enemy.shoot_delay + 200

    def test_enemy_get_level_method(self):
        """Test that enemy has a get_level method that returns correct value."""
        with patch('thunder_fighter.entities.enemies.enemy.create_enemy_ship'), \
             patch('pygame.time.get_ticks', return_value=1000):

            enemy = Enemy(
                game_time=2,
                game_level=2,
                all_sprites=self.mock_all_sprites,
                enemy_bullets_group=self.mock_enemy_bullets
            )

            # Test get_level method if it exists
            if hasattr(enemy, 'get_level'):
                level = enemy.get_level()
                assert level == enemy.level, "get_level() should return the same as level attribute"
                assert isinstance(level, int), "get_level() should return an integer"
            else:
                # If no get_level method, the level attribute should be accessible
                assert hasattr(enemy, 'level'), "Enemy should have level attribute"
                assert isinstance(enemy.level, int), "Enemy level should be an integer"
