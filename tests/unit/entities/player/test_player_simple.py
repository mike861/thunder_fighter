"""
Simple Player entity tests following project patterns.

Following the lightweight mock strategy used in existing tests.
"""

from unittest.mock import MagicMock, patch

from thunder_fighter.entities.player.player import Player


class TestPlayerEntity:
    """Test Player entity using project's lightweight mock pattern."""

    def setup_method(self):
        """Set up test environment following existing patterns."""
        # Mock sprite groups (following test_enemy_entity.py pattern)
        self.mock_game = MagicMock()
        self.mock_all_sprites = MagicMock()
        self.mock_bullets_group = MagicMock()
        self.mock_missiles_group = MagicMock()
        self.mock_enemies_group = MagicMock()
        self.mock_sound_manager = MagicMock()

    @patch("thunder_fighter.graphics.renderers.create_player_ship")
    @patch("pygame.time.get_ticks")
    def test_player_initialization(self, mock_get_ticks, mock_create_ship):
        """Test player initializes correctly."""
        mock_get_ticks.return_value = 1000
        mock_create_ship.return_value = MagicMock()  # Simple mock, not real Surface

        player = Player(
            game=self.mock_game,
            all_sprites=self.mock_all_sprites,
            bullets_group=self.mock_bullets_group,
            missiles_group=self.mock_missiles_group,
            enemies_group=self.mock_enemies_group,
            sound_manager=self.mock_sound_manager,
        )

        # Test interface existence, not specific values
        assert hasattr(player, "health")
        assert hasattr(player, "speed")
        assert hasattr(player, "bullet_speed")
        assert hasattr(player, "bullet_paths")
        assert player.health > 0
        assert player.speed > 0

    @patch("thunder_fighter.graphics.renderers.create_player_ship")
    @patch("pygame.time.get_ticks")
    def test_player_sprite_groups(self, mock_get_ticks, mock_create_ship):
        """Test player correctly stores sprite group references."""
        mock_get_ticks.return_value = 1000
        mock_create_ship.return_value = MagicMock()

        player = Player(
            game=self.mock_game,
            all_sprites=self.mock_all_sprites,
            bullets_group=self.mock_bullets_group,
            missiles_group=self.mock_missiles_group,
            enemies_group=self.mock_enemies_group,
        )

        assert player.all_sprites == self.mock_all_sprites
        assert player.bullets_group == self.mock_bullets_group
        assert player.missiles_group == self.mock_missiles_group

    @patch("thunder_fighter.graphics.renderers.create_player_ship")
    @patch("pygame.time.get_ticks")
    def test_player_methods_exist(self, mock_get_ticks, mock_create_ship):
        """Test that player has required methods."""
        mock_get_ticks.return_value = 1000
        mock_create_ship.return_value = MagicMock()

        player = Player(
            game=self.mock_game,
            all_sprites=self.mock_all_sprites,
            bullets_group=self.mock_bullets_group,
            missiles_group=self.mock_missiles_group,
            enemies_group=self.mock_enemies_group,
        )

        # Test method existence (following test_physics_system.py pattern)
        required_methods = ["update", "shoot", "take_damage", "heal", "add_wingman"]
        for method_name in required_methods:
            assert hasattr(player, method_name)
            assert callable(getattr(player, method_name))
