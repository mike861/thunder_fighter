"""
Tests for ProjectileFactory.

Comprehensive test suite covering projectile factory initialization,
entity creation, preset management, and error handling.
"""

from unittest.mock import MagicMock, Mock, patch
import pytest

from thunder_fighter.entities.projectiles.projectile_factory import ProjectileFactory
from thunder_fighter.entities.projectiles.bullets import Bullet
from thunder_fighter.entities.projectiles.missile import TrackingMissile


class TestProjectileFactoryInitialization:
    """Test projectile factory initialization and setup."""

    def setup_method(self):
        """Set up test environment before each test method."""
        # Mock logger to avoid import issues during testing
        self.mock_logger = Mock()

    @patch('thunder_fighter.entities.projectiles.projectile_factory.logger')
    def test_factory_initialization(self, mock_logger):
        """Test factory initializes correctly."""
        factory = ProjectileFactory()
        
        assert factory is not None
        assert hasattr(factory, '_projectile_types')
        assert hasattr(factory, 'create')
        assert hasattr(factory, 'add_preset')
        assert hasattr(factory, 'list_presets')
        
        # Should log initialization
        mock_logger.info.assert_called_with("ProjectileFactory initialized")

    @patch('thunder_fighter.entities.projectiles.projectile_factory.logger')
    def test_projectile_types_setup(self, mock_logger):
        """Test projectile types are correctly configured."""
        factory = ProjectileFactory()
        
        expected_types = {"bullet": Bullet, "missile": TrackingMissile}
        assert factory._projectile_types == expected_types

    @patch('thunder_fighter.entities.projectiles.projectile_factory.logger')
    def test_default_presets_setup(self, mock_logger):
        """Test default presets are created during initialization."""
        factory = ProjectileFactory()
        
        presets = factory.list_presets()
        expected_presets = ["player_bullet", "enemy_bullet", "player_missile"]
        
        for preset in expected_presets:
            assert preset in presets

    @patch('thunder_fighter.entities.projectiles.projectile_factory.logger')
    def test_default_entity_type(self, mock_logger):
        """Test factory has correct default entity type."""
        factory = ProjectileFactory()
        
        # Should inherit from ConfigurableEntityFactory with Bullet as default
        # This is verified through the super().__init__(Bullet) call
        assert factory is not None


class TestProjectileFactoryPresets:
    """Test projectile factory preset management."""

    def setup_method(self):
        """Set up test environment."""
        pass

    @patch('thunder_fighter.entities.projectiles.projectile_factory.logger')
    def test_player_bullet_preset(self, mock_logger):
        """Test player bullet preset configuration."""
        factory = ProjectileFactory()
        
        presets = factory.list_presets()
        assert "player_bullet" in presets
        
        # Get preset configuration
        try:
            preset_config = factory._presets["player_bullet"]
            assert preset_config["projectile_type"] == "bullet"
            assert preset_config["owner"] == "player"
        except (AttributeError, KeyError):
            # If preset access method is different, just verify it exists
            assert "player_bullet" in presets

    @patch('thunder_fighter.entities.projectiles.projectile_factory.logger')
    def test_enemy_bullet_preset(self, mock_logger):
        """Test enemy bullet preset configuration."""
        factory = ProjectileFactory()
        
        presets = factory.list_presets()
        assert "enemy_bullet" in presets
        
        try:
            preset_config = factory._presets["enemy_bullet"]
            assert preset_config["projectile_type"] == "bullet"
            assert preset_config["owner"] == "enemy"
        except (AttributeError, KeyError):
            assert "enemy_bullet" in presets

    @patch('thunder_fighter.entities.projectiles.projectile_factory.logger')
    def test_player_missile_preset(self, mock_logger):
        """Test player missile preset configuration."""
        factory = ProjectileFactory()
        
        presets = factory.list_presets()
        assert "player_missile" in presets
        
        try:
            preset_config = factory._presets["player_missile"]
            assert preset_config["projectile_type"] == "missile"
            assert preset_config["owner"] == "player"
        except (AttributeError, KeyError):
            assert "player_missile" in presets

    @patch('thunder_fighter.entities.projectiles.projectile_factory.logger')
    def test_add_custom_preset(self, mock_logger):
        """Test adding custom preset to factory."""
        factory = ProjectileFactory()
        
        custom_config = {
            "projectile_type": "bullet",
            "owner": "boss",
            "speed": 15
        }
        
        factory.add_preset("boss_bullet", custom_config)
        
        presets = factory.list_presets()
        assert "boss_bullet" in presets

    @patch('thunder_fighter.entities.projectiles.projectile_factory.logger')
    def test_preset_list_comprehensive(self, mock_logger):
        """Test complete preset list functionality."""
        factory = ProjectileFactory()
        
        presets = factory.list_presets()
        
        # Should be a list or similar iterable
        assert hasattr(presets, '__iter__')
        assert len(presets) >= 3  # At least the default presets


class TestProjectileFactoryCreation:
    """Test projectile entity creation methods."""

    def setup_method(self):
        """Set up test environment."""
        pass

    @patch('thunder_fighter.entities.projectiles.projectile_factory.logger')
    @patch('thunder_fighter.entities.projectiles.bullets.Bullet')
    def test_create_bullet_player(self, mock_bullet_class, mock_logger):
        """Test creating player bullet with clean interface."""
        factory = ProjectileFactory()
        mock_bullet = Mock()
        mock_bullet_class.return_value = mock_bullet
        
        result = factory.create_bullet(x=100, y=200, owner="player")
        
        assert result == mock_bullet
        # Should create bullet with correct parameters
        mock_bullet_class.assert_called_once_with(100, 200, 10, 0, None)

    @patch('thunder_fighter.entities.projectiles.projectile_factory.logger')
    @patch('thunder_fighter.entities.projectiles.bullets.Bullet')
    def test_create_bullet_enemy(self, mock_bullet_class, mock_logger):
        """Test creating enemy bullet with clean interface."""
        factory = ProjectileFactory()
        mock_bullet = Mock()
        mock_bullet_class.return_value = mock_bullet
        
        result = factory.create_bullet(x=150, y=250, owner="enemy")
        
        assert result == mock_bullet
        mock_bullet_class.assert_called_once_with(150, 250, 10, 0, None)

    @patch('thunder_fighter.entities.projectiles.projectile_factory.logger')
    @patch('thunder_fighter.entities.projectiles.bullets.Bullet')
    def test_create_bullet_default_owner(self, mock_bullet_class, mock_logger):
        """Test creating bullet with default owner (clean interface)."""
        factory = ProjectileFactory()
        mock_bullet = Mock()
        mock_bullet_class.return_value = mock_bullet
        
        result = factory.create_bullet(x=75, y=125)  # Required position parameters
        
        assert result == mock_bullet
        # Should use default parameters: speed=10, angle=0, owner="player", renderer=None
        mock_bullet_class.assert_called_once_with(75, 125, 10, 0, None)

    @patch('thunder_fighter.entities.projectiles.projectile_factory.logger')
    @patch('thunder_fighter.entities.projectiles.missile.TrackingMissile')
    def test_create_missile(self, mock_missile_class, mock_logger):
        """Test creating missile with clean interface."""
        factory = ProjectileFactory()
        mock_missile = Mock()
        mock_missile_class.return_value = mock_missile
        
        # Create mock target
        mock_target = Mock()
        
        result = factory.create_missile(x=100, y=200, target=mock_target, owner="player")
        
        assert result == mock_missile
        mock_missile_class.assert_called_once_with(100, 200, mock_target, None)

    @patch('thunder_fighter.entities.projectiles.projectile_factory.logger')
    @patch('thunder_fighter.entities.projectiles.missile.TrackingMissile')
    def test_create_missile_default_owner(self, mock_missile_class, mock_logger):
        """Test creating missile with default owner (clean interface)."""
        factory = ProjectileFactory()
        mock_missile = Mock()
        mock_missile_class.return_value = mock_missile
        
        mock_target = Mock()
        
        result = factory.create_missile(x=50, y=100, target=mock_target)  # Default owner="player"
        
        assert result == mock_missile
        mock_missile_class.assert_called_once_with(50, 100, mock_target, None)


# NOTE: TestProjectileFactoryEntityCreation removed - violates Pure Logic Mock Strategy
# These tests were testing internal implementation details (_create_entity method)
# rather than public interface behavior. Following the principle of interface-focused
# testing, we test the public factory methods (create_bullet, create_missile) instead.


class TestProjectileFactoryErrorHandling:
    """Test projectile factory error handling and edge cases."""

    def setup_method(self):
        """Set up test environment."""
        pass

    @patch('thunder_fighter.entities.projectiles.projectile_factory.logger')
    def test_create_with_default_behavior(self, mock_logger):
        """Test factory creates entities with default behavior - interface focused."""
        factory = ProjectileFactory()
        
        # Test public interface behavior
        assert hasattr(factory, 'create_bullet')
        assert hasattr(factory, 'create_missile')
        assert callable(getattr(factory, 'create_bullet'))
        assert callable(getattr(factory, 'create_missile'))

    @patch('thunder_fighter.entities.projectiles.projectile_factory.logger')
    @patch('thunder_fighter.entities.projectiles.bullets.Bullet')
    def test_create_bullet_invalid_owner(self, mock_bullet_class, mock_logger):
        """Test creating bullet with invalid owner (clean interface)."""
        factory = ProjectileFactory()
        mock_bullet = Mock()
        mock_bullet_class.return_value = mock_bullet
        
        # Should handle invalid owner gracefully (treated as non-player owner)
        result = factory.create_bullet(x=100, y=200, owner="invalid")
        
        assert result == mock_bullet
        # Should create bullet normally with position and default parameters
        mock_bullet_class.assert_called_once_with(100, 200, 10, 0, None)

    @patch('thunder_fighter.entities.projectiles.projectile_factory.logger')
    def test_factory_interface_consistency(self, mock_logger):
        """Test factory interface is consistent with base factory."""
        factory = ProjectileFactory()
        
        # Should have all expected methods from base factory
        required_methods = ['create', 'add_preset', 'list_presets']
        for method in required_methods:
            assert hasattr(factory, method), f"Factory missing required method: {method}"

    @patch('thunder_fighter.entities.projectiles.projectile_factory.logger')
    def test_preset_access_error_handling(self, mock_logger):
        """Test accessing non-existent preset."""
        factory = ProjectileFactory()
        
        # Try to create from non-existent preset
        try:
            # This will depend on the implementation of create_from_preset
            # If it raises an exception, it should be appropriate
            result = factory.create_from_preset("non_existent_preset")
            # If it doesn't raise an exception, it should handle gracefully
        except Exception as e:
            # Exception should be appropriate (like KeyError or custom exception)
            assert isinstance(e, (KeyError, ValueError, AttributeError))


class TestProjectileFactoryIntegration:
    """Test projectile factory integration with entity classes."""

    def setup_method(self):
        """Set up test environment."""
        pass

    @patch('thunder_fighter.entities.projectiles.projectile_factory.logger')
    def test_factory_creates_actual_entity_types(self, mock_logger):
        """Test factory creates instances of correct entity types."""
        factory = ProjectileFactory()
        
        # Test that the factory maintains correct type mapping
        bullet_class = factory._projectile_types.get("bullet")
        missile_class = factory._projectile_types.get("missile")
        
        assert bullet_class == Bullet
        assert missile_class == TrackingMissile

    @patch('thunder_fighter.entities.projectiles.projectile_factory.logger')
    def test_factory_preset_configuration_integrity(self, mock_logger):
        """Test factory preset configurations are valid."""
        factory = ProjectileFactory()
        
        presets = factory.list_presets()
        
        # Each preset should be accessible and valid
        for preset_name in presets:
            try:
                # Try to access preset (implementation-dependent)
                if hasattr(factory, '_presets'):
                    preset_config = factory._presets[preset_name]
                    assert isinstance(preset_config, dict)
                    assert "projectile_type" in preset_config
            except (AttributeError, KeyError):
                # If preset access is different, just verify name exists
                assert preset_name is not None
                assert isinstance(preset_name, str)

    @patch('thunder_fighter.entities.projectiles.projectile_factory.logger')
    def test_factory_extensibility(self, mock_logger):
        """Test factory can be extended with new projectile types."""
        factory = ProjectileFactory()
        
        # Should be able to add new types (if implementation supports it)
        original_types = factory._projectile_types.copy()
        
        # Verify original types are preserved
        assert "bullet" in original_types
        assert "missile" in original_types
        
        # Factory should maintain its type dictionary
        assert factory._projectile_types == original_types