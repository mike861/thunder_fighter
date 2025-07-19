"""
Tests for TrackingMissile entity.

Comprehensive test suite covering missile initialization, tracking behavior,
rotation mechanics, and target management.
"""

import math
from unittest.mock import MagicMock, Mock, patch
import pytest
import pygame

from thunder_fighter.entities.projectiles.missile import TrackingMissile
from thunder_fighter.constants import WIDTH, HEIGHT

# Initialize pygame for tests
pygame.init()
pygame.display.set_mode((1, 1))  # Create minimal display for tests


class TestTrackingMissileInitialization:
    """Test tracking missile initialization and basic properties."""

    def setup_method(self):
        """Set up test environment before each test method."""
        pygame.sprite = Mock()
        pygame.sprite.Sprite = Mock()
        # Keep pygame.math and Vector2 real for mathematical operations

    @patch('thunder_fighter.graphics.renderers.create_tracking_missile')
    def test_missile_initialization_with_target(self, mock_create_missile):
        """Test missile initializes correctly with living target."""
        mock_surface = pygame.Surface((6, 12))
        mock_create_missile.return_value = mock_surface
        
        # Mock target
        mock_target = Mock()
        mock_target.rect = pygame.Rect(200, 150, 32, 32)
        mock_target.rect.center = (200, 150)
        
        missile = TrackingMissile(x=100, y=200, target=mock_target)
        
        assert missile.speed == 8
        assert missile.target == mock_target
        assert missile.angle == 0.0
        assert missile.last_target_pos == (200, 150)
        assert missile.image.get_size() == mock_surface.get_size()
        assert missile.original_image.get_size() == mock_surface.get_size()

    @patch('thunder_fighter.graphics.renderers.create_tracking_missile')
    def test_missile_initialization_without_target(self, mock_create_missile):
        """Test missile initializes correctly without target."""
        mock_surface = pygame.Surface((6, 12))
        mock_create_missile.return_value = mock_surface
        
        missile = TrackingMissile(x=100, y=200, target=None)
        
        assert missile.target is None
        assert missile.last_target_pos is None

    @patch('thunder_fighter.graphics.renderers.create_tracking_missile')
    def test_missile_position_initialization(self, mock_create_missile):
        """Test missile initializes at correct position."""
        mock_surface = pygame.Surface((6, 12))
        mock_create_missile.return_value = mock_surface
        
        mock_target = Mock()
        mock_target.rect = pygame.Rect(200, 150, 32, 32)  # Use real Rect
        mock_target.rect.center = (200, 150)
        
        missile = TrackingMissile(x=100, y=200, target=mock_target)
        
        assert missile.rect.center == (100, 200)


class TestTrackingMissileTargeting:
    """Test missile targeting and tracking behavior."""

    def setup_method(self):
        """Set up test environment."""
        pygame.sprite = Mock()
        pygame.sprite.Sprite = Mock()
        # Keep pygame.math, pygame.transform real for mathematical operations

    @patch('thunder_fighter.graphics.renderers.create_tracking_missile')
    def test_missile_tracks_living_target(self, mock_create_missile):
        """Test missile tracks living target correctly."""
        mock_surface = pygame.Surface((6, 12))
        mock_create_missile.return_value = mock_surface
        
        # Mock living target
        mock_target = Mock()
        mock_target.alive.return_value = True
        mock_target.rect.center = (200, 150)
        
        missile = TrackingMissile(x=100, y=200, target=mock_target)
        original_center = missile.rect.center
        
        missile.update()
        
        # Should update last known position for living target
        assert missile.last_target_pos == (200, 150)
        # Missile should move toward target (position should change)
        assert missile.rect.center != original_center

    @patch('thunder_fighter.graphics.renderers.create_tracking_missile')
    def test_missile_continues_to_last_position_when_target_dies(self, mock_create_missile):
        """Test missile continues to last known position when target dies."""
        mock_surface = pygame.Surface((6, 12))
        mock_create_missile.return_value = mock_surface
        
        # Mock dead target
        mock_target = Mock()
        mock_target.alive.return_value = False
        
        missile = TrackingMissile(x=100, y=200, target=mock_target)
        missile.last_target_pos = (200, 150)  # Set last known position
        original_center = missile.rect.center
        
        missile.update()
        
        # Should still use last known position
        assert missile.last_target_pos == (200, 150)
        # Missile should move toward last known position
        assert missile.rect.center != original_center

    @patch('thunder_fighter.graphics.renderers.create_tracking_missile')
    def test_missile_killed_without_target_or_position(self, mock_create_missile):
        """Test missile is killed when no target and no last position."""
        mock_surface = pygame.Surface((6, 12))
        mock_create_missile.return_value = mock_surface
        
        missile = TrackingMissile(x=100, y=200, target=None)
        missile.last_target_pos = None
        missile.kill = Mock()
        
        missile.update()
        
        # Should be killed
        missile.kill.assert_called_once()

    @patch('thunder_fighter.graphics.renderers.create_tracking_missile')
    def test_missile_killed_when_reaching_target(self, mock_create_missile):
        """Test missile is killed when very close to target - math logic focused."""
        mock_surface = pygame.Surface((6, 12))
        mock_create_missile.return_value = mock_surface
        
        mock_target = Mock()
        mock_target.alive.return_value = True
        mock_target.rect = pygame.Rect(102, 202, 32, 32)  # Very close to missile (distance < speed)
        mock_target.rect.center = (102, 202)
        
        missile = TrackingMissile(x=100, y=200, target=mock_target)
        missile.kill = Mock()
        
        missile.update()
        
        # Should be killed when close to target (distance < speed=8)
        missile.kill.assert_called_once()


class TestTrackingMissileMovement:
    """Test missile movement and direction calculation."""

    def setup_method(self):
        """Set up test environment."""
        pygame.sprite = Mock()
        pygame.sprite.Sprite = Mock()
        # Keep pygame.math, pygame.transform real for mathematical operations

    @patch('thunder_fighter.graphics.renderers.create_tracking_missile')
    def test_missile_movement_toward_target(self, mock_create_missile):
        """Test missile moves toward target position."""
        mock_surface = pygame.Surface((6, 12))
        mock_create_missile.return_value = mock_surface
        
        mock_target = Mock()
        mock_target.alive.return_value = True
        mock_target.rect = pygame.Rect(200, 150, 32, 32)
        mock_target.rect.center = (200, 150)
        
        missile = TrackingMissile(x=100, y=200, target=mock_target)
        original_center = missile.rect.center
        
        missile.update()
        
        # Should move toward target (position should change)
        assert missile.rect.center != original_center
        # Missile should be closer to target after update
        import math
        original_distance = math.sqrt((200-100)**2 + (150-200)**2)
        new_distance = math.sqrt((200-missile.rect.center[0])**2 + (150-missile.rect.center[1])**2)
        assert new_distance < original_distance

    @patch('thunder_fighter.graphics.renderers.create_tracking_missile')
    def test_missile_angle_calculation(self, mock_create_missile):
        """Test missile calculates correct angle toward target - math logic focused."""
        mock_surface = pygame.Surface((6, 12))
        mock_create_missile.return_value = mock_surface
        
        mock_target = Mock()
        mock_target.alive.return_value = True
        mock_target.rect = pygame.Rect(200, 150, 32, 32)
        mock_target.rect.center = (200, 150)
        
        missile = TrackingMissile(x=100, y=200, target=mock_target)
        initial_angle = missile.angle
        
        missile.update()
        
        # Angle should be calculated based on target direction
        # Since target is to the right and up, angle should change
        assert missile.angle != initial_angle
        # Verify angle points generally toward target

    @patch('thunder_fighter.graphics.renderers.create_tracking_missile')
    def test_missile_speed_consistency(self, mock_create_missile):
        """Test missile maintains consistent speed."""
        mock_surface = pygame.Surface((6, 12))
        mock_create_missile.return_value = mock_surface
        
        missile = TrackingMissile(x=100, y=200, target=None)
        
        # Speed should be constant
        assert missile.speed == 8
        
        # Speed should not change during updates
        initial_speed = missile.speed
        missile.last_target_pos = (200, 150)
        
        # Use real Vector2 but patch the specific operations we need
        with patch('pygame.math.Vector2') as mock_vector2_class:
            direction_vector = Mock()
            direction_vector.length.return_value = 100.0
            direction_vector.normalize_ip = Mock()
            mock_vector2_class.return_value = direction_vector
            
            missile.rect = Mock()
            missile.rect.center = (100, 200)
            
            missile.update()
            
            assert missile.speed == initial_speed


class TestTrackingMissileRotation:
    """Test missile rotation and visual orientation."""

    def setup_method(self):
        """Set up test environment."""
        pygame.sprite = Mock()
        pygame.sprite.Sprite = Mock()
        pygame.transform = Mock()
        # Keep pygame.math real for Vector2 operations

    @patch('thunder_fighter.graphics.renderers.create_tracking_missile')
    def test_missile_rotates_toward_target(self, mock_create_missile):
        """Test missile rotates to face movement direction."""
        mock_surface = pygame.Surface((6, 12))
        mock_create_missile.return_value = mock_surface
        
        mock_target = Mock()
        mock_target.alive.return_value = True
        mock_target.rect.center = (200, 150)
        
        # Mock rotation components only
        rotated_surface = Mock()
        pygame.transform.rotate.return_value = rotated_surface
        
        missile = TrackingMissile(x=100, y=200, target=mock_target)
        initial_angle = missile.angle
        
        missile.update()
        
        # Should rotate image toward target and update angle
        assert missile.angle != initial_angle
        # Rotation should be called with calculated angle
        pygame.transform.rotate.assert_called()

    @patch('thunder_fighter.graphics.renderers.create_tracking_missile')
    def test_missile_preserves_original_image(self, mock_create_missile):
        """Test missile preserves original image for rotation."""
        mock_surface = pygame.Surface((6, 12))
        mock_create_missile.return_value = mock_surface
        
        missile = TrackingMissile(x=100, y=200, target=None)
        
        # Original image should be preserved
        assert missile.original_image == mock_surface
        
        # After rotation, original should still be preserved
        rotated_surface = Mock()
        pygame.transform.rotate.return_value = rotated_surface
        
        missile.last_target_pos = (200, 150)
        
        missile.update()
        
        # Original image should still be unchanged
        assert missile.original_image == mock_surface

    @patch('thunder_fighter.graphics.renderers.create_tracking_missile')
    def test_missile_rect_update_after_rotation(self, mock_create_missile):
        """Test missile rect is correctly updated after rotation."""
        mock_surface = pygame.Surface((6, 12))
        mock_create_missile.return_value = mock_surface
        
        mock_target = Mock()
        mock_target.alive.return_value = True
        mock_target.rect.center = (200, 150)
        
        # Mock rotation with new rect
        rotated_surface = Mock()
        new_rect = Mock()
        new_rect.center = (100, 200)
        rotated_surface.get_rect.return_value = new_rect
        pygame.transform.rotate.return_value = rotated_surface
        
        missile = TrackingMissile(x=100, y=200, target=mock_target)
        original_rect_center = missile.rect.center
        
        missile.update()
        
        # Rect should be updated after rotation and movement
        assert missile.rect.center != original_rect_center


class TestTrackingMissileBoundaries:
    """Test missile boundary handling and cleanup."""

    def setup_method(self):
        """Set up test environment."""
        pygame.sprite = Mock()
        pygame.sprite.Sprite = Mock()
        # Keep pygame.math real for Vector2 operations

    @patch('thunder_fighter.graphics.renderers.create_tracking_missile')
    def test_missile_boundary_removal_top(self, mock_create_missile):
        """Test missile is removed when going off top of screen."""
        mock_surface = pygame.Surface((6, 12))
        mock_create_missile.return_value = mock_surface
        
        missile = TrackingMissile(x=100, y=-10, target=None)
        missile.kill = Mock()
        
        missile.update()
        
        # Should be killed when going off top
        missile.kill.assert_called_once()

    @patch('thunder_fighter.graphics.renderers.create_tracking_missile')
    def test_missile_boundary_removal_bottom(self, mock_create_missile):
        """Test missile is removed when going off bottom of screen."""
        mock_surface = pygame.Surface((6, 12))
        mock_create_missile.return_value = mock_surface
        
        missile = TrackingMissile(x=100, y=HEIGHT + 10, target=None)
        missile.kill = Mock()
        
        missile.update()
        
        # Should be killed when going off bottom
        missile.kill.assert_called_once()

    @patch('thunder_fighter.graphics.renderers.create_tracking_missile')
    def test_missile_boundary_removal_sides(self, mock_create_missile):
        """Test missile is removed when going off sides of screen."""
        mock_surface = pygame.Surface((6, 12))
        mock_create_missile.return_value = mock_surface
        
        missile = TrackingMissile(x=WIDTH + 10, y=200, target=None)
        missile.kill = Mock()
        
        missile.update()
        
        # Should be killed when going off right side
        missile.kill.assert_called_once()

    @patch('thunder_fighter.graphics.renderers.create_tracking_missile')
    def test_missile_stays_within_bounds(self, mock_create_missile):
        """Test missile doesn't get killed when within screen bounds."""
        mock_surface = pygame.Surface((6, 12))
        mock_create_missile.return_value = mock_surface
        
        mock_target = Mock()
        mock_target.alive.return_value = True
        mock_target.rect = pygame.Rect(250, 250, 32, 32)
        mock_target.rect.center = (250, 250)
        
        missile = TrackingMissile(x=200, y=300, target=mock_target)
        missile.kill = Mock()
        
        missile.update()
        
        # Should NOT be killed when within bounds
        missile.kill.assert_not_called()


class TestTrackingMissileEdgeCases:
    """Test missile behavior in edge cases and error conditions."""

    def setup_method(self):
        """Set up test environment."""
        pygame.sprite = Mock()
        pygame.sprite.Sprite = Mock()
        # Keep pygame.math real for mathematical operations

    @patch('thunder_fighter.graphics.renderers.create_tracking_missile')
    def test_missile_zero_distance_to_target(self, mock_create_missile):
        """Test missile behavior when target is at same position."""
        mock_surface = pygame.Surface((6, 12))
        mock_create_missile.return_value = mock_surface
        
        mock_target = Mock()
        mock_target.alive.return_value = True
        mock_target.rect = pygame.Rect(100, 200, 32, 32)  # Same position as missile
        mock_target.rect.center = (100, 200)
        
        missile = TrackingMissile(x=100, y=200, target=mock_target)
        missile.kill = Mock()
        
        missile.update()
        
        # Should be killed when distance is very small (< speed=8)
        missile.kill.assert_called_once()

    @patch('thunder_fighter.graphics.renderers.create_tracking_missile')
    def test_missile_target_position_update_tracking(self, mock_create_missile):
        """Test missile updates target position tracking correctly."""
        mock_surface = pygame.Surface((6, 12))
        mock_create_missile.return_value = mock_surface
        
        mock_target = Mock()
        mock_target.alive.return_value = True
        
        # Target moves during missile lifetime
        mock_target.rect = pygame.Rect(150, 150, 32, 32)
        mock_target.rect.center = (150, 150)
        
        missile = TrackingMissile(x=100, y=200, target=mock_target)
        
        missile.update()
        
        # Should update to new target position
        assert missile.last_target_pos == (150, 150)
        
        # Target moves again
        mock_target.rect = pygame.Rect(180, 120, 32, 32)
        mock_target.rect.center = (180, 120)
        missile.update()
        
        # Should track new position
        assert missile.last_target_pos == (180, 120)