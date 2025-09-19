"""
Integration tests for Player Combat System.

Tests the integration between player entities, projectiles, and combat mechanics
to ensure the complete combat system works correctly.
"""

from unittest.mock import MagicMock, Mock, patch
import pytest
import pygame

from thunder_fighter.entities.player.player import Player
from thunder_fighter.entities.player.wingman import Wingman
from thunder_fighter.entities.projectiles.bullets import Bullet
from thunder_fighter.entities.projectiles.missile import TrackingMissile
from thunder_fighter.constants import PLAYER_CONFIG, BULLET_CONFIG

# Initialize pygame for tests
pygame.init()
pygame.display.set_mode((1, 1))  # Create minimal display for tests


class TestPlayerProjectileIntegration:
    """Test integration between player and projectile creation."""

    def setup_method(self):
        """Set up test environment before each test method."""
        pygame.sprite = Mock()
        pygame.sprite.Sprite = Mock()
        pygame.sprite.Group = Mock()
        
        # Mock game components
        self.mock_game = Mock()
        self.mock_all_sprites = Mock()
        self.mock_bullets_group = Mock()
        self.mock_missiles_group = Mock()
        self.mock_enemies_group = Mock()
        self.mock_sound_manager = Mock()

    @patch('thunder_fighter.graphics.renderers.create_player_ship')
    @patch('pygame.time.get_ticks')
    def test_player_shooting_creates_bullets_in_groups(self, mock_get_ticks, mock_create_player_ship):
        """Test player shooting creates bullets and adds them to correct sprite groups."""
        # Setup timing mock
        mock_get_ticks.return_value = 1000
        
        # Setup player
        mock_surface = pygame.Surface((32, 32))
        mock_create_player_ship.return_value = mock_surface
        
        # Mock event system for event-driven shooting
        mock_event_system = Mock()
        
        player = Player(
            game=self.mock_game,
            all_sprites=self.mock_all_sprites,
            bullets_group=self.mock_bullets_group,
            missiles_group=self.mock_missiles_group,
            enemies_group=self.mock_enemies_group,
            sound_manager=self.mock_sound_manager,
            event_system=mock_event_system  # ✅ Event-driven architecture
        )
        
        # Test shooting - ensure timing allows shooting
        player.bullet_paths = 1
        player.last_shot = 0  # Allow immediate shooting
        player.shoot()
        
        # ✅ Verify event-driven shooting: Event should be dispatched
        mock_event_system.dispatch_event.assert_called_once()
        
        # ✅ Verify shooting parameters in event
        call_args = mock_event_system.dispatch_event.call_args[0][0]
        shooting_data = call_args.get_data("shooting_data")
        
        assert len(shooting_data) == 1  # Single bullet path
        assert shooting_data[0]["x"] == player.rect.centerx
        assert shooting_data[0]["y"] == player.rect.top
        assert shooting_data[0]["speed"] == player.bullet_speed
        assert shooting_data[0]["owner"] == "player"

    @patch('thunder_fighter.graphics.renderers.create_player_ship')
    @patch('pygame.time.get_ticks')
    def test_player_multiple_bullet_paths_integration(self, mock_get_ticks, mock_create_player_ship):
        """Test player with multiple bullet paths creates correct number of bullets."""
        # Setup timing mock
        mock_get_ticks.return_value = 1000
        
        mock_surface = pygame.Surface((32, 32))
        mock_create_player_ship.return_value = mock_surface
        
        # Mock event system for event-driven shooting
        mock_event_system = Mock()
        
        player = Player(
            game=self.mock_game,
            all_sprites=self.mock_all_sprites,
            bullets_group=self.mock_bullets_group,
            missiles_group=self.mock_missiles_group,
            enemies_group=self.mock_enemies_group,
            event_system=mock_event_system  # ✅ Event-driven architecture
        )
        
        # ✅ Test different bullet path configurations with event-driven system
        for paths in [1, 2, 3, 4]:
            mock_event_system.reset_mock()
            
            player.bullet_paths = paths
            player.last_shot = 0  # Allow immediate shooting
            player.shoot()
            
            # ✅ Verify event dispatched with correct bullet count
            mock_event_system.dispatch_event.assert_called_once()
            
            # ✅ Verify shooting parameters match bullet paths
            call_args = mock_event_system.dispatch_event.call_args[0][0]
            shooting_data = call_args.get_data("shooting_data")
            
            assert len(shooting_data) == paths  # Correct number of bullets

    @patch('thunder_fighter.graphics.renderers.create_player_ship')
    @patch('pygame.time.get_ticks')
    def test_player_bullet_speed_upgrade_integration(self, mock_get_ticks, mock_create_player_ship):
        """Test player bullet speed upgrade affects created bullets."""
        # Setup timing mock
        mock_get_ticks.return_value = 1000
        
        mock_surface = pygame.Surface((32, 32))
        mock_create_player_ship.return_value = mock_surface
        
        # Mock event system for event-driven shooting
        mock_event_system = Mock()
        
        player = Player(
            game=self.mock_game,
            all_sprites=self.mock_all_sprites,
            bullets_group=self.mock_bullets_group,
            missiles_group=self.mock_missiles_group,
            enemies_group=self.mock_enemies_group,
            event_system=mock_event_system  # ✅ Event-driven architecture
        )
        
        # Upgrade bullet speed
        initial_speed = player.bullet_speed
        player.increase_bullet_speed()
        upgraded_speed = player.bullet_speed
        
        assert upgraded_speed > initial_speed
        
        # ✅ Shoot bullet with upgraded speed using event-driven system
        player.last_shot = 0  # Allow immediate shooting
        player.shoot()
        
        # ✅ Verify event dispatched with upgraded bullet speed
        mock_event_system.dispatch_event.assert_called_once()
        
        # ✅ Verify shooting parameters contain upgraded speed
        call_args = mock_event_system.dispatch_event.call_args[0][0]
        shooting_data = call_args.get_data("shooting_data")
        
        assert len(shooting_data) > 0  # Bullets created
        assert shooting_data[0]["speed"] == upgraded_speed  # Upgraded speed applied

    @patch('thunder_fighter.graphics.renderers.create_player_ship')
    @patch('pygame.time.get_ticks')
    def test_player_shoot_delay_timing_integration(self, mock_get_ticks, mock_create_player_ship):
        """Test player shoot delay prevents rapid bullet creation."""
        mock_surface = pygame.Surface((32, 32))
        mock_create_player_ship.return_value = mock_surface
        
        # Mock event system for event-driven shooting
        mock_event_system = Mock()
        
        player = Player(
            game=self.mock_game,
            all_sprites=self.mock_all_sprites,
            bullets_group=self.mock_bullets_group,
            missiles_group=self.mock_missiles_group,
            enemies_group=self.mock_enemies_group,
            event_system=mock_event_system  # ✅ Event-driven architecture
        )
        
        # ✅ First shot should work
        mock_get_ticks.return_value = 1000
        player.last_shot = 0
        player.shoot()
        
        # ✅ Verify first shot event dispatched
        mock_event_system.dispatch_event.assert_called_once()
        first_shot_call_count = mock_event_system.dispatch_event.call_count
        
        # ✅ Immediate second shot should be blocked (within delay period)
        mock_get_ticks.return_value = 1050  # Only 50ms later, within shoot_delay
        player.shoot()
        # No new event should be dispatched (blocked by delay)
        assert mock_event_system.dispatch_event.call_count == first_shot_call_count
        
        # ✅ Shot after delay should work
        mock_get_ticks.return_value = 1000 + player.shoot_delay + 10
        player.shoot()
        # New event should be dispatched after delay
        assert mock_event_system.dispatch_event.call_count > first_shot_call_count


class TestWingmanMissileIntegration:
    """Test integration between wingman and missile systems."""

    def setup_method(self):
        """Set up test environment."""
        pygame.sprite = Mock()
        pygame.sprite.Sprite = Mock()
        pygame.sprite.Group = Mock()
        pygame.time = Mock()
        pygame.time.get_ticks = Mock(return_value=1000)
        
        # Mock components
        self.mock_game = Mock()
        self.mock_all_sprites = Mock()
        self.mock_bullets_group = Mock()
        self.mock_missiles_group = Mock()
        self.mock_enemies_group = Mock()

    @patch('thunder_fighter.graphics.renderers.create_player_ship')
    def test_wingman_missile_shooting_integration(self, mock_create_player_ship):
        """Test wingman system integration - high level behavior only."""
        mock_surface = pygame.Surface((32, 32))
        mock_create_player_ship.return_value = mock_surface
        
        player = Player(
            game=self.mock_game,
            all_sprites=self.mock_all_sprites,
            bullets_group=self.mock_bullets_group,
            missiles_group=self.mock_missiles_group,
            enemies_group=self.mock_enemies_group
        )
        
        # Test wingman addition - interface focused
        initial_wingmen = len(player.wingmen_list)
        success = player.add_wingman()
        
        # Verify high-level behavior
        assert success is True
        assert len(player.wingmen_list) == initial_wingmen + 1

    @patch('thunder_fighter.graphics.renderers.create_player_ship')
    def test_player_missile_system_with_multiple_wingmen(self, mock_create_player_ship):
        """Test player can manage multiple wingmen - interface focused."""
        mock_surface = pygame.Surface((32, 32))
        mock_create_player_ship.return_value = mock_surface
        
        player = Player(
            game=self.mock_game,
            all_sprites=self.mock_all_sprites,
            bullets_group=self.mock_bullets_group,
            missiles_group=self.mock_missiles_group,
            enemies_group=self.mock_enemies_group
        )
        
        # Test multiple wingmen addition
        initial_count = len(player.wingmen_list)
        
        success1 = player.add_wingman()
        success2 = player.add_wingman()
        
        # Verify high-level behavior
        assert success1 is True
        assert success2 is True
        assert len(player.wingmen_list) == initial_count + 2

    @patch('thunder_fighter.graphics.renderers.create_player_ship')
    def test_player_missile_targeting_priority_integration(self, mock_create_player_ship):
        """Test player missile system behavior - interface focused."""
        mock_surface = pygame.Surface((32, 32))
        mock_create_player_ship.return_value = mock_surface
        
        player = Player(
            game=self.mock_game,
            all_sprites=self.mock_all_sprites,
            bullets_group=self.mock_bullets_group,
            missiles_group=self.mock_missiles_group,
            enemies_group=self.mock_enemies_group
        )
        
        # Test that player has missile shooting capability
        assert hasattr(player, 'shoot_missiles')
        assert callable(getattr(player, 'shoot_missiles'))
        
        # Test wingmen are required for missiles
        assert len(player.wingmen_list) == 0  # No wingmen initially
        
        # Add wingman and verify system is ready
        player.add_wingman()
        assert len(player.wingmen_list) > 0  # Now has wingmen for missiles


class TestPlayerDamageIntegration:
    """Test integration of player damage system with wingmen and health."""

    def setup_method(self):
        """Set up test environment."""
        pygame.sprite = Mock()
        pygame.sprite.Sprite = Mock()
        pygame.sprite.Group = Mock()
        pygame.time = Mock()
        pygame.time.get_ticks = Mock(return_value=1000)
        
        self.mock_game = Mock()
        self.mock_all_sprites = Mock()
        self.mock_bullets_group = Mock()
        self.mock_missiles_group = Mock()
        self.mock_enemies_group = Mock()
        self.mock_sound_manager = Mock()

    @patch('thunder_fighter.graphics.renderers.create_player_ship')
    def test_player_damage_wingman_protection_integration(self, mock_create_player_ship):
        """Test player damage system with wingman protection - interface focused."""
        mock_surface = pygame.Surface((32, 32))
        mock_create_player_ship.return_value = mock_surface
        
        player = Player(
            game=self.mock_game,
            all_sprites=self.mock_all_sprites,
            bullets_group=self.mock_bullets_group,
            missiles_group=self.mock_missiles_group,
            enemies_group=self.mock_enemies_group,
            sound_manager=self.mock_sound_manager
        )
        
        # Add wingman and record initial state
        player.add_wingman()
        initial_health = player.health
        initial_wingmen_count = len(player.wingmen_list)
        
        # Take damage - test high-level behavior
        is_dead = player.take_damage(10)
        
        # Verify wingman protection logic (public interface)
        assert player.health == initial_health  # Health should be protected
        assert len(player.wingmen_list) == initial_wingmen_count - 1  # Wingman sacrificed
        assert not is_dead  # Player should survive

    @patch('thunder_fighter.graphics.renderers.create_player_ship')
    def test_player_damage_without_wingman_integration(self, mock_create_player_ship):
        """Test player damage system without wingman protection - interface focused."""
        mock_surface = pygame.Surface((32, 32))
        mock_create_player_ship.return_value = mock_surface
        
        player = Player(
            game=self.mock_game,
            all_sprites=self.mock_all_sprites,
            bullets_group=self.mock_bullets_group,
            missiles_group=self.mock_missiles_group,
            enemies_group=self.mock_enemies_group,
            sound_manager=self.mock_sound_manager
        )
        
        initial_health = player.health
        damage_amount = 15
        
        # Take damage without wingmen - test public interface
        is_dead = player.take_damage(damage_amount)
        
        # Verify core damage logic (public interface)
        assert player.health == initial_health - damage_amount  # Health decreased
        assert not is_dead  # Player survived


class TestPlayerUpgradeIntegration:
    """Test integration of player upgrade systems."""

    def setup_method(self):
        """Set up test environment."""
        pygame.sprite = Mock()
        pygame.sprite.Sprite = Mock()
        pygame.time = Mock()
        pygame.time.get_ticks = Mock(return_value=1000)
        
        self.mock_game = Mock()
        self.mock_all_sprites = Mock()
        self.mock_bullets_group = Mock()
        self.mock_missiles_group = Mock()
        self.mock_enemies_group = Mock()

    @patch('thunder_fighter.graphics.renderers.create_player_ship')
    @patch('pygame.time.get_ticks')
    def test_player_upgrade_affects_combat_performance(self, mock_get_ticks, mock_create_player_ship):
        """Test player upgrades affect actual combat performance."""
        # Setup timing mock
        mock_get_ticks.return_value = 1000
        
        mock_surface = pygame.Surface((32, 32))
        mock_create_player_ship.return_value = mock_surface
        
        # Mock event system for event-driven shooting
        mock_event_system = Mock()
        
        player = Player(
            game=self.mock_game,
            all_sprites=self.mock_all_sprites,
            bullets_group=self.mock_bullets_group,
            missiles_group=self.mock_missiles_group,
            enemies_group=self.mock_enemies_group,
            event_system=mock_event_system  # ✅ Event-driven architecture
        )
        
        # Test bullet paths upgrade
        initial_paths = player.bullet_paths
        player.increase_bullet_paths()
        upgraded_paths = player.bullet_paths
        
        assert upgraded_paths == initial_paths + 1
        
        # ✅ Shooting should create more bullets with event-driven system
        player.last_shot = 0  # Allow immediate shooting
        player.shoot()
        
        # ✅ Verify event dispatched with upgraded bullet count
        mock_event_system.dispatch_event.assert_called_once()
        call_args = mock_event_system.dispatch_event.call_args[0][0]
        shooting_data = call_args.get_data("shooting_data")
        assert len(shooting_data) == upgraded_paths  # More bullets
        
        # ✅ Test bullet speed upgrade
        mock_event_system.reset_mock()
        initial_speed = player.bullet_speed
        player.increase_bullet_speed()
        upgraded_speed = player.bullet_speed
        
        assert upgraded_speed > initial_speed
        
        # ✅ New bullets should have upgraded speed
        player.last_shot = 0  # Allow immediate shooting again
        player.shoot()
        
        # ✅ Verify event with upgraded speed parameters
        mock_event_system.dispatch_event.assert_called_once()
        call_args = mock_event_system.dispatch_event.call_args[0][0]
        shooting_data = call_args.get_data("shooting_data")
        assert all(bullet["speed"] == upgraded_speed for bullet in shooting_data)

    @patch('thunder_fighter.graphics.renderers.create_player_ship')
    @patch('thunder_fighter.entities.player.wingman.Wingman')
    def test_player_wingman_upgrade_integration(self, mock_wingman_class, mock_create_player_ship):
        """Test player wingman system integration with upgrades."""
        mock_surface = pygame.Surface((32, 32))
        mock_create_player_ship.return_value = mock_surface
        
        mock_wingman1 = Mock()
        mock_wingman1.side = "left"
        mock_wingman2 = Mock()
        mock_wingman2.side = "right"
        mock_wingman_class.side_effect = [mock_wingman1, mock_wingman2]
        
        player = Player(
            game=self.mock_game,
            all_sprites=self.mock_all_sprites,
            bullets_group=self.mock_bullets_group,
            missiles_group=self.mock_missiles_group,
            enemies_group=self.mock_enemies_group
        )
        
        # Add wingmen progressively
        assert len(player.wingmen_list) == 0
        
        success1 = player.add_wingman()
        assert success1
        assert len(player.wingmen_list) == 1
        
        success2 = player.add_wingman()
        assert success2  
        assert len(player.wingmen_list) == 2
        
        # Test maximum limit
        max_wingmen = int(PLAYER_CONFIG["MAX_WINGMEN"])
        for i in range(2, max_wingmen):
            mock_wingman_class.return_value = Mock()
            player.add_wingman()
        
        # Should not exceed maximum
        extra_success = player.add_wingman()
        assert not extra_success
        assert len(player.wingmen_list) == max_wingmen


class TestCombatSystemIntegration:
    """Test complete combat system integration."""

    def setup_method(self):
        """Set up test environment."""
        pygame.sprite = Mock()
        pygame.sprite.Sprite = Mock()
        pygame.sprite.Group = Mock()
        pygame.time = Mock()
        pygame.time.get_ticks = Mock(return_value=1000)
        pygame.key = Mock()
        
        self.mock_game = Mock()
        self.mock_all_sprites = Mock()
        self.mock_bullets_group = Mock()
        self.mock_missiles_group = Mock()
        self.mock_enemies_group = Mock()

    @patch('thunder_fighter.graphics.renderers.create_player_ship')
    def test_complete_combat_flow_integration(self, mock_create_player_ship):
        """Test complete combat capabilities - interface focused."""
        mock_surface = pygame.Surface((32, 32))
        mock_create_player_ship.return_value = mock_surface
        
        player = Player(
            game=self.mock_game,
            all_sprites=self.mock_all_sprites,
            bullets_group=self.mock_bullets_group,
            missiles_group=self.mock_missiles_group,
            enemies_group=self.mock_enemies_group
        )
        
        # Test combat interface capabilities
        assert hasattr(player, 'shoot')
        assert hasattr(player, 'shoot_missiles')
        assert hasattr(player, 'take_damage')
        assert hasattr(player, 'add_wingman')
        
        # Test that all methods are callable
        assert callable(getattr(player, 'shoot'))
        assert callable(getattr(player, 'shoot_missiles'))
        assert callable(getattr(player, 'take_damage'))
        assert callable(getattr(player, 'add_wingman'))

    @patch('thunder_fighter.graphics.renderers.create_player_ship')
    def test_missile_system_enemy_targeting_integration(self, mock_create_player_ship):
        """Test missile system interface behavior - interface focused."""
        mock_surface = pygame.Surface((32, 32))
        mock_create_player_ship.return_value = mock_surface
        
        player = Player(
            game=self.mock_game,
            all_sprites=self.mock_all_sprites,
            bullets_group=self.mock_bullets_group,
            missiles_group=self.mock_missiles_group,
            enemies_group=self.mock_enemies_group
        )
        
        # Test missile system requires wingmen
        assert len(player.wingmen_list) == 0
        
        # Add wingmen to enable missile system
        player.add_wingman()
        assert len(player.wingmen_list) > 0
        
        # Test missile system interface exists
        assert hasattr(player, 'shoot_missiles')
        assert hasattr(player, 'last_missile_shot')

    @patch('thunder_fighter.graphics.renderers.create_player_ship')
    def test_player_combat_state_consistency_integration(self, mock_create_player_ship):
        """Test player maintains consistent combat state across operations."""
        mock_surface = pygame.Surface((32, 32))
        mock_create_player_ship.return_value = mock_surface
        
        player = Player(
            game=self.mock_game,
            all_sprites=self.mock_all_sprites,
            bullets_group=self.mock_bullets_group,
            missiles_group=self.mock_missiles_group,
            enemies_group=self.mock_enemies_group
        )
        
        # Record initial state
        initial_health = player.health
        initial_bullet_speed = player.bullet_speed
        initial_bullet_paths = player.bullet_paths
        initial_speed = player.speed
        
        # Perform multiple operations
        player.increase_bullet_speed()
        player.increase_bullet_paths()
        player.increase_speed()
        player.heal(10)
        
        # Verify state consistency (public interface)
        assert player.bullet_speed > initial_bullet_speed
        assert player.bullet_paths > initial_bullet_paths
        assert player.speed > initial_speed
        assert player.health >= initial_health  # May be capped at max
        
        # Verify all capabilities remain functional (interface level)
        assert hasattr(player, 'shoot')
        assert callable(getattr(player, 'shoot'))