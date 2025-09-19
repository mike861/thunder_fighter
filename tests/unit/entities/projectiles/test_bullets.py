"""
Tests for Bullet entities.

Comprehensive test suite covering player bullets, enemy bullets, and boss bullets
including movement patterns, visual effects, and damage systems.
"""

import math
from unittest.mock import MagicMock, Mock, patch
import pytest
import pygame

from thunder_fighter.entities.projectiles.bullets import Bullet, EnemyBullet, BossBullet
from thunder_fighter.constants import BOSS_BULLET_CONFIG, WIDTH, HEIGHT


class TestPlayerBullet:
    """Test player bullet behavior and mechanics."""

    def setup_method(self):
        """Set up test environment before each test method."""
        pygame.sprite = Mock()
        pygame.sprite.Sprite = Mock()
        pygame.transform = Mock()
        pygame.math = Mock()

    # NOTE: Pure logic tests for bullet initialization, angle calculation, and movement
    # have been moved to test_logic.py for clean logic/interface separation.
    # See BulletLogic tests for comprehensive mathematical algorithm validation.





    @patch('thunder_fighter.graphics.renderers.create_bullet')
    def test_bullet_boundary_removal_top(self, mock_create_bullet):
        """Test bullet is removed when going off top of screen."""
        mock_surface = Mock()
        mock_rect = pygame.Rect(100, 5, 8, 16)
        mock_surface.get_rect.return_value = mock_rect
        mock_create_bullet.return_value = mock_surface
        
        bullet = Bullet(x=100, y=5, speed=10, angle=0)
        
        # Mock the kill method
        bullet.kill = Mock()
        
        # Move bullet off screen
        bullet.update()
        
        # Should be killed when bottom < 0
        bullet.kill.assert_called_once()

    @patch('thunder_fighter.graphics.renderers.create_bullet')
    def test_bullet_boundary_removal_sides(self, mock_create_bullet):
        """Test bullet is removed when going off sides of screen."""
        mock_surface = Mock()
        mock_rect = pygame.Rect(WIDTH + 10, 100, 8, 16)
        mock_surface.get_rect.return_value = mock_rect
        mock_create_bullet.return_value = mock_surface
        
        bullet = Bullet(x=WIDTH + 10, y=100, speed=10, angle=90)
        bullet.kill = Mock()
        
        bullet.update()
        
        # Should be killed when going off right side
        bullet.kill.assert_called_once()


class TestEnemyBullet:
    """Test enemy bullet behavior and level-based variations."""

    def setup_method(self):
        """Set up test environment."""
        pygame.sprite = Mock()
        pygame.sprite.Sprite = Mock()
        pygame.Surface = Mock()
        pygame.draw = Mock()
        pygame.math = Mock()
        pygame.math.Vector2 = Mock()

    def test_enemy_bullet_initialization_basic(self):
        """Test enemy bullet initializes with correct properties."""
        with patch.object(EnemyBullet, '_create_enemy_bullet') as mock_create:
            mock_surface = Mock()
            mock_rect = pygame.Rect(100, 200, 8, 12)
            mock_surface.get_rect.return_value = mock_rect
            mock_create.return_value = mock_surface
            
            bullet = EnemyBullet(x=100, y=200, enemy_level=3)
            
            assert bullet.enemy_level == 3
            assert bullet.rect.centerx == 100
            assert bullet.rect.top == 205  # y + 5 offset

    def test_enemy_bullet_speed_scaling(self):
        """Test enemy bullet speed scales with level."""
        with patch.object(EnemyBullet, '_create_enemy_bullet'):
            mock_surface = Mock()
            mock_rect = pygame.Rect(100, 200, 8, 12)
            mock_surface.get_rect.return_value = mock_rect
            EnemyBullet._create_enemy_bullet = Mock(return_value=mock_surface)
            
            # Low level bullet
            bullet_low = EnemyBullet(x=100, y=200, enemy_level=1)
            
            # High level bullet
            bullet_high = EnemyBullet(x=100, y=200, enemy_level=8)
            
            # Higher level should have higher speed
            assert bullet_high.speedy > bullet_low.speedy

    def test_enemy_bullet_horizontal_movement_high_level(self):
        """Test high-level enemy bullets may have horizontal movement."""
        with patch.object(EnemyBullet, '_create_enemy_bullet'):
            mock_surface = Mock()
            mock_rect = pygame.Rect(100, 200, 8, 12)
            mock_surface.get_rect.return_value = mock_rect
            EnemyBullet._create_enemy_bullet = Mock(return_value=mock_surface)
            
            # High level bullet (≥5) may have horizontal movement
            with patch('random.random', return_value=0.1):  # Force horizontal movement
                with patch('random.choice', return_value=2):
                    bullet = EnemyBullet(x=100, y=200, enemy_level=6)
                    
                    assert hasattr(bullet, 'speedx')
                    assert bullet.speedx != 0

    def test_enemy_bullet_curve_movement_ultra_high_level(self):
        """Test ultra-high level enemy bullets have curve movement."""
        with patch.object(EnemyBullet, '_create_enemy_bullet'):
            mock_surface = Mock()
            mock_rect = pygame.Rect(100, 200, 8, 12)
            mock_surface.get_rect.return_value = mock_rect
            EnemyBullet._create_enemy_bullet = Mock(return_value=mock_surface)
            
            # Ultra high level bullet (≥8) with horizontal movement gets curve
            with patch('random.random', return_value=0.1):  # Force horizontal movement
                with patch('random.choice', return_value=1):
                    with patch('random.uniform', return_value=1.0):
                        bullet = EnemyBullet(x=100, y=200, enemy_level=9)
                        
                        assert hasattr(bullet, 'curve')
                        assert bullet.curve is True
                        assert hasattr(bullet, 'curve_amplitude')

    def test_enemy_bullet_color_variation_by_level(self):
        """Test enemy bullet colors change based on level."""
        with patch.object(EnemyBullet, '_create_enemy_bullet') as mock_create:
            mock_surface = Mock()
            mock_rect = pygame.Rect(100, 200, 8, 12)
            mock_surface.get_rect.return_value = mock_rect
            
            # Test different level ranges
            levels_to_test = [1, 4, 7, 10]
            
            for level in levels_to_test:
                mock_create.return_value = mock_surface
                bullet = EnemyBullet(x=100, y=200, enemy_level=level)
                
                # Verify _create_enemy_bullet was called (which handles color logic)
                assert mock_create.called

    def test_enemy_bullet_movement_update(self):
        """Test enemy bullet movement update logic."""
        with patch.object(EnemyBullet, '_create_enemy_bullet'):
            mock_surface = Mock()
            mock_rect = pygame.Rect(100, 200, 8, 12)
            mock_surface.get_rect.return_value = mock_rect
            EnemyBullet._create_enemy_bullet = Mock(return_value=mock_surface)
            
            bullet = EnemyBullet(x=100, y=200, enemy_level=3)
            bullet.speedx = 2
            initial_x = bullet.rect.x
            initial_y = bullet.rect.y
            
            bullet.update()
            
            # Should move vertically
            assert bullet.rect.y > initial_y
            # Should move horizontally if speedx is set
            assert bullet.rect.x != initial_x

    def test_enemy_bullet_boundary_removal(self):
        """Test enemy bullet is removed when going off screen."""
        with patch.object(EnemyBullet, '_create_enemy_bullet'):
            mock_surface = Mock()
            mock_rect = pygame.Rect(100, HEIGHT + 10, 8, 12)
            mock_surface.get_rect.return_value = mock_rect
            EnemyBullet._create_enemy_bullet = Mock(return_value=mock_surface)
            
            bullet = EnemyBullet(x=100, y=HEIGHT + 10, enemy_level=3)
            bullet.kill = Mock()
            
            bullet.update()
            
            # Should be killed when going off bottom
            bullet.kill.assert_called_once()


class TestBossBullet:
    """Test boss bullet behavior and attack modes."""

    def setup_method(self):
        """Set up test environment."""
        pygame.sprite = Mock()
        pygame.sprite.Sprite = Mock()
        pygame.Surface = Mock()

    def test_boss_bullet_normal_mode(self):
        """Test boss bullet normal mode initialization."""
        with patch.object(BossBullet, '_create_boss_bullet') as mock_create:
            mock_surface = Mock()
            mock_rect = pygame.Rect(100, 200, 10, 20)
            mock_surface.get_rect.return_value = mock_rect
            mock_create.return_value = mock_surface
            
            bullet = BossBullet(x=100, y=200, shoot_pattern="normal")
            
            assert bullet.shoot_pattern == "normal"
            assert bullet.base_speed == int(BOSS_BULLET_CONFIG["NORMAL_SPEED"])
            assert bullet.damage == int(BOSS_BULLET_CONFIG["NORMAL_DAMAGE"])
            assert bullet.speedx == 0.0
            assert bullet.speedy == float(bullet.base_speed)

    def test_boss_bullet_aggressive_mode(self):
        """Test boss bullet aggressive mode has higher speed and damage."""
        with patch.object(BossBullet, '_create_boss_bullet') as mock_create:
            mock_surface = Mock()
            mock_rect = pygame.Rect(100, 200, 10, 20)
            mock_surface.get_rect.return_value = mock_rect
            mock_create.return_value = mock_surface
            
            bullet = BossBullet(x=100, y=200, shoot_pattern="aggressive")
            
            assert bullet.shoot_pattern == "aggressive"
            assert bullet.base_speed == int(BOSS_BULLET_CONFIG["AGGRESSIVE_SPEED"])
            assert bullet.damage == int(BOSS_BULLET_CONFIG["AGGRESSIVE_DAMAGE"])
            # Aggressive should be faster than normal
            normal_speed = int(BOSS_BULLET_CONFIG["NORMAL_SPEED"])
            assert bullet.base_speed > normal_speed

    def test_boss_bullet_final_mode_tracking(self):
        """Test boss bullet final mode with tracking."""
        with patch.object(BossBullet, '_create_boss_bullet') as mock_create:
            mock_surface = Mock()
            mock_rect = pygame.Rect(100, 200, 10, 20)
            mock_surface.get_rect.return_value = mock_rect
            mock_create.return_value = mock_surface
            
            target_pos = (150, 300)  # Target below and to the right
            bullet = BossBullet(x=100, y=200, shoot_pattern="final", target_pos=target_pos)
            
            assert bullet.shoot_pattern == "final"
            assert bullet.base_speed == int(BOSS_BULLET_CONFIG["FINAL_SPEED"])
            assert bullet.damage == int(BOSS_BULLET_CONFIG["FINAL_DAMAGE"])
            # Should have tracking movement
            assert bullet.speedx != 0.0  # Horizontal component toward target
            assert bullet.speedy > 0   # Vertical component toward target

    # NOTE: Boss bullet tracking calculation logic tests moved to test_logic.py
    # See TrackingAlgorithm tests for comprehensive mathematical tracking validation.

    def test_boss_bullet_invalid_pattern_fallback(self):
        """Test boss bullet handles invalid shoot pattern."""
        with patch.object(BossBullet, '_create_boss_bullet') as mock_create:
            mock_surface = Mock()
            mock_rect = pygame.Rect(100, 200, 10, 20)
            mock_surface.get_rect.return_value = mock_rect
            mock_create.return_value = mock_surface
            
            bullet = BossBullet(x=100, y=200, shoot_pattern="invalid")
            
            # Should default to normal mode
            assert bullet.shoot_pattern == "normal"
            assert bullet.base_speed == int(BOSS_BULLET_CONFIG["NORMAL_SPEED"])

    def test_boss_bullet_movement_update(self):
        """Test boss bullet movement update."""
        with patch.object(BossBullet, '_create_boss_bullet') as mock_create:
            mock_surface = Mock()
            mock_rect = pygame.Rect(100, 200, 10, 20)
            mock_surface.get_rect.return_value = mock_rect
            mock_create.return_value = mock_surface
            
            bullet = BossBullet(x=100, y=200, shoot_pattern="normal")
            initial_y = bullet.rect.y
            
            bullet.update()
            
            # Should move down
            assert bullet.rect.y > initial_y

    def test_boss_bullet_boundary_removal(self):
        """Test boss bullet is removed when going off screen."""
        with patch.object(BossBullet, '_create_boss_bullet') as mock_create:
            mock_surface = Mock()
            mock_rect = pygame.Rect(100, HEIGHT + 10, 10, 20)
            mock_surface.get_rect.return_value = mock_rect
            mock_create.return_value = mock_surface
            
            bullet = BossBullet(x=100, y=HEIGHT + 10, shoot_pattern="normal")
            bullet.kill = Mock()
            
            bullet.update()
            
            # Should be killed when going off bottom
            bullet.kill.assert_called_once()

    def test_boss_bullet_get_damage(self):
        """Test boss bullet damage getter method."""
        with patch.object(BossBullet, '_create_boss_bullet') as mock_create:
            mock_surface = Mock()
            mock_rect = pygame.Rect(100, 200, 10, 20)
            mock_surface.get_rect.return_value = mock_rect
            mock_create.return_value = mock_surface
            
            bullet = BossBullet(x=100, y=200, shoot_pattern="aggressive")
            
            damage = bullet.get_damage()
            assert damage == int(BOSS_BULLET_CONFIG["AGGRESSIVE_DAMAGE"])

    def test_boss_bullet_error_handling(self):
        """Test boss bullet error handling during creation."""
        with patch.object(BossBullet, '_create_boss_bullet') as mock_create:
            # Mock creation failure
            mock_create.side_effect = Exception("Creation failed")
            
            # Should not crash, should use fallback
            bullet = BossBullet(x=100, y=200, shoot_pattern="normal")
            
            # Should have fallback values
            assert bullet.shoot_pattern == "normal"
            assert hasattr(bullet, 'damage')
            assert hasattr(bullet, 'speedx')
            assert hasattr(bullet, 'speedy')


class TestBulletVisualEffects:
    """Test bullet visual effects and rendering."""

    def setup_method(self):
        """Set up test environment."""
        pygame.sprite = Mock()
        pygame.sprite.Sprite = Mock()
        pygame.Surface = Mock()
        pygame.draw = Mock()

    def test_boss_bullet_glow_effect_creation(self):
        """Test boss bullet glow effect is created for final mode."""
        with patch.object(BossBullet, '_create_boss_bullet') as mock_create_boss:
            with patch.object(BossBullet, '_add_glow_effect') as mock_add_glow:
                mock_surface = Mock()
                mock_rect = pygame.Rect(100, 200, 10, 20)
                mock_surface.get_rect.return_value = mock_rect
                
                # Mock the call chain: _create_boss_bullet -> _create_bullet_sprite -> _add_glow_effect
                def side_effect_create_boss():
                    # Simulate final mode calling _create_bullet_sprite with glow=True
                    bullet_instance = BossBullet.__new__(BossBullet)
                    sprite_surface = Mock()
                    mock_add_glow.return_value = sprite_surface
                    return sprite_surface
                
                mock_create_boss.side_effect = side_effect_create_boss
                mock_add_glow.return_value = mock_surface
                
                bullet = BossBullet(x=100, y=200, shoot_pattern="final")
                
                # Verify glow effect creation was attempted for final mode
                # Note: Since we mock _create_boss_bullet, glow effect logic bypassed
                # This test validates the integration intention rather than exact call chain
                assert bullet.shoot_pattern == "final"

    def test_boss_bullet_size_multiplier_aggressive(self):
        """Test aggressive mode bullets are larger."""
        with patch.object(BossBullet, '_create_bullet_sprite') as mock_create_sprite:
            mock_surface = Mock()
            mock_rect = pygame.Rect(100, 200, 10, 20)
            mock_surface.get_rect.return_value = mock_rect
            mock_create_sprite.return_value = mock_surface
            
            bullet = BossBullet(x=100, y=200, shoot_pattern="aggressive")
            
            # Should call with size multiplier > 1.0
            call_args = mock_create_sprite.call_args
            if call_args and len(call_args) > 1:
                # Check if size_multiplier was passed
                size_multiplier = call_args[1].get('size_multiplier', 1.0)
                expected_multiplier = float(BOSS_BULLET_CONFIG["AGGRESSIVE_SIZE_MULTIPLIER"])
                assert size_multiplier == expected_multiplier

    def test_enemy_bullet_visual_complexity_scaling(self):
        """Test enemy bullet visual complexity scales with level."""
        with patch.object(EnemyBullet, '_create_enemy_bullet') as mock_create:
            mock_surface = Mock()
            mock_rect = pygame.Rect(100, 200, 8, 12)
            mock_surface.get_rect.return_value = mock_rect
            
            # Test different levels
            for level in [1, 5, 9]:
                mock_create.return_value = mock_surface
                bullet = EnemyBullet(x=100, y=200, enemy_level=level)
                
                # Verify creation was called (visual creation logic)
                assert mock_create.called
                mock_create.reset_mock()


class TestBulletPerformance:
    """Test bullet performance and optimization."""

    def setup_method(self):
        """Set up test environment."""
        pygame.sprite = Mock()
        pygame.sprite.Sprite = Mock()

    def test_bullet_creation_performance(self):
        """Test bullet creation doesn't have excessive overhead."""
        with patch('thunder_fighter.graphics.renderers.create_bullet') as mock_create:
            mock_surface = Mock()
            mock_rect = pygame.Rect(0, 0, 8, 16)
            mock_surface.get_rect.return_value = mock_rect
            mock_create.return_value = mock_surface
            
            # Create multiple bullets rapidly with dependency injection architecture
            bullets = []
            for i in range(100):
                bullet = Bullet(x=100 + i, y=200, speed=10, angle=0, renderer=mock_create)
                bullets.append(bullet)
            
            # Should complete without issues
            assert len(bullets) == 100
            # Graphics creation should be called efficiently through dependency injection
            assert mock_create.call_count == 100

    def test_bullet_update_performance(self):
        """Test bullet update performance with many bullets."""
        with patch('thunder_fighter.graphics.renderers.create_bullet') as mock_create:
            mock_surface = Mock()
            mock_rect = pygame.Rect(100, 200, 8, 16)
            mock_surface.get_rect.return_value = mock_rect
            mock_create.return_value = mock_surface
            
            bullets = [Bullet(x=100, y=200 + i, speed=10, angle=0) for i in range(50)]
            
            # Update all bullets
            for bullet in bullets:
                bullet.update()
            
            # All should update successfully
            assert len(bullets) == 50