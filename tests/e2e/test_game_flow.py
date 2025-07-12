"""
End-to-end tests for complete game flow.

This module tests the full game lifecycle through API calls,
ensuring all systems work together correctly without requiring
a full pygame environment.
"""

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

if TYPE_CHECKING:
    pass

from thunder_fighter.constants import INITIAL_GAME_LEVEL, PLAYER_HEALTH
from thunder_fighter.events.game_events import GameEvent


class TestGameFlow:
    """Test complete game flow scenarios through API calls."""

    def setup_method(self):
        """Set up test environment."""
        pass

    def teardown_method(self):
        """Clean up test environment."""
        pass

    def _create_mock_player(self):
        """Create a properly configured mock player with all necessary attributes."""
        mock_player = Mock()

        # Basic attributes
        mock_player.health = PLAYER_HEALTH
        mock_player.speed = 5  # Numeric value for mathematical operations
        mock_player.x = 100
        mock_player.y = 200
        mock_player.width = 32
        mock_player.height = 32

        # Player-specific attributes
        mock_player.bullet_paths = 1
        mock_player.bullet_speed = 10
        mock_player.wingmen_list = []

        # Sprite behavior - make it behave like a pygame Sprite
        mock_player.alive.return_value = True
        mock_player.kill.return_value = None
        mock_player.add_internal = Mock()
        mock_player.groups.return_value = []

        # Methods
        mock_player.add_wingman = Mock()

        return mock_player

    def _create_mock_ui_manager(self):
        """Create a properly configured mock UI manager."""
        mock_ui = Mock()

        # Dictionary-like persistent_info attribute
        mock_ui.persistent_info = {}

        # Methods
        mock_ui.update_game_state = Mock()
        mock_ui.update_player_info = Mock()
        mock_ui.update_boss_info = Mock()
        mock_ui.update = Mock()
        mock_ui.show_score_milestone = Mock()

        return mock_ui

    def _create_mock_score(self):
        """Create a properly configured mock score."""
        mock_score = Mock()
        mock_score.value = 0
        return mock_score

    def _create_mock_pygame_sprite_group(self):
        """Create a mock pygame sprite group that handles add() properly."""
        mock_group = Mock()

        # Mock the add method to not fail with Mock objects
        def mock_add(*sprites):
            for sprite in sprites:
                # Just accept the sprite without validation
                pass

        mock_group.add = mock_add
        mock_group.update = Mock()
        mock_group.__len__ = Mock(return_value=0)
        mock_group.__iter__ = Mock(return_value=iter([]))  # Make it iterable
        mock_group.empty = Mock()  # Add empty method

        return mock_group

    @patch('thunder_fighter.game.pygame.sprite.Group')
    @patch('thunder_fighter.game.pygame.init')
    @patch('thunder_fighter.game.pygame.display.set_mode')
    @patch('thunder_fighter.game.SoundManager')
    @patch('thunder_fighter.game.get_resource_manager')
    @patch('thunder_fighter.game.Player')
    @patch('thunder_fighter.game.DynamicBackground')
    @patch('thunder_fighter.game.Score')
    @patch('thunder_fighter.game.UIManager')
    def test_game_initialization_components(self, mock_ui, mock_score, mock_bg,
                                          mock_player, mock_resource_manager,
                                          mock_sound_manager, mock_display, mock_pygame_init,
                                          mock_sprite_group):
        """Test that game initialization creates all required components."""
        from thunder_fighter.game import RefactoredGame

        # Mock all the components
        mock_rm = Mock()
        mock_rm.preload_common_assets.return_value = None
        mock_rm.get_music_path.return_value = "test_music.mp3"
        mock_rm.get_cache_stats.return_value = {'loaded': 10, 'cached': 5}
        mock_resource_manager.return_value = mock_rm

        mock_screen = Mock()
        mock_display.return_value = mock_screen

        mock_sm = Mock()
        mock_sm.play_music = Mock()
        mock_sound_manager.return_value = mock_sm

        # Create properly configured mock objects
        mock_player_instance = self._create_mock_player()
        mock_player.return_value = mock_player_instance

        mock_ui_instance = self._create_mock_ui_manager()
        mock_ui.return_value = mock_ui_instance

        mock_score_instance = self._create_mock_score()
        mock_score.return_value = mock_score_instance

        # Mock sprite groups
        mock_sprite_group.return_value = self._create_mock_pygame_sprite_group()

        # Create game instance
        game = RefactoredGame()

        # Verify initialization
        assert game.running is True
        assert game.paused is False
        assert game.game_level == INITIAL_GAME_LEVEL
        assert game.game_won is False
        assert game.boss is None
        assert game.boss_active is False

        # Verify systems are initialized
        assert game.event_system is not None
        assert game.input_manager is not None

        # Verify factories are initialized
        assert game.enemy_factory is not None
        assert game.boss_factory is not None
        assert game.item_factory is not None
        assert game.projectile_factory is not None

    def test_level_progression_logic(self):
        """Test level progression mechanics through event handling."""
        from thunder_fighter.game import RefactoredGame

        # Create a minimal game instance for testing event handlers
        with patch.multiple(
            'thunder_fighter.game',
            pygame=Mock(),
            SoundManager=Mock(),
            get_resource_manager=Mock(return_value=Mock()),
            Player=Mock(return_value=self._create_mock_player()),
            DynamicBackground=Mock(),
            Score=Mock(return_value=self._create_mock_score()),
            UIManager=Mock(return_value=self._create_mock_ui_manager())
        ):
            with patch('thunder_fighter.game.pygame.sprite.Group', return_value=self._create_mock_pygame_sprite_group()):
                game = RefactoredGame()

                # Test level up event handling
                initial_level = game.game_level
                level_up_event = GameEvent.create_level_changed(
                    source="test",
                    old_level=initial_level,
                    new_level=initial_level + 1
                )

                game._handle_level_up_event(level_up_event)

                # Verify level increased
                assert game.game_level == initial_level + 1

    def test_boss_defeat_handling(self):
        """Test boss defeat event handling."""
        from thunder_fighter.game import RefactoredGame

        with patch.multiple(
            'thunder_fighter.game',
            pygame=Mock(),
            SoundManager=Mock(),
            get_resource_manager=Mock(return_value=Mock()),
            Player=Mock(return_value=self._create_mock_player()),
            DynamicBackground=Mock(),
            Score=Mock(return_value=self._create_mock_score()),
            UIManager=Mock(return_value=self._create_mock_ui_manager())
        ):
            with patch('thunder_fighter.game.pygame.sprite.Group', return_value=self._create_mock_pygame_sprite_group()):
                game = RefactoredGame()

                # Simulate boss defeat event
                boss_defeat_event = GameEvent.create_boss_died(
                    source="boss",
                    boss_level=game.game_level,
                    score_awarded=1000
                )

                initial_level = game.game_level
                game._handle_boss_defeated_event(boss_defeat_event)

                # The boss defeat handler should trigger level up events
                # Since we're at level 1 (< MAX_GAME_LEVEL), it should trigger a level up
                # Process events to handle the level up
                game.event_system.process_events()

                # Verify level increased (boss defeat triggers level up)
                assert game.game_level == initial_level + 1

    def test_item_collection_handling(self):
        """Test item collection event handling."""
        from thunder_fighter.game import RefactoredGame

        with patch.multiple(
            'thunder_fighter.game',
            pygame=Mock(),
            SoundManager=Mock(),
            get_resource_manager=Mock(return_value=Mock()),
            Player=Mock(return_value=self._create_mock_player()),
            DynamicBackground=Mock(),
            Score=Mock(return_value=self._create_mock_score()),
            UIManager=Mock(return_value=self._create_mock_ui_manager())
        ):
            with patch('thunder_fighter.game.pygame.sprite.Group', return_value=self._create_mock_pygame_sprite_group()):
                game = RefactoredGame()

                # Simulate item collection events
                health_event = GameEvent.create_item_collected(
                    source="health_item",
                    item_type="health",
                    player_id="player"
                )

                wingman_event = GameEvent.create_item_collected(
                    source="wingman_item",
                    item_type="wingman",
                    player_id="player"
                )

                # Handle events (should not raise exceptions)
                game._handle_item_collected(health_event)
                game._handle_item_collected(wingman_event)

                # Verify events were handled without errors
                assert True

    def test_player_death_handling(self):
        """Test player death event handling."""
        from thunder_fighter.game import RefactoredGame

        with patch.multiple(
            'thunder_fighter.game',
            pygame=Mock(),
            SoundManager=Mock(),
            get_resource_manager=Mock(return_value=Mock()),
            Player=Mock(return_value=self._create_mock_player()),
            DynamicBackground=Mock(),
            Score=Mock(return_value=self._create_mock_score()),
            UIManager=Mock(return_value=self._create_mock_ui_manager())
        ):
            with patch('thunder_fighter.game.pygame.sprite.Group', return_value=self._create_mock_pygame_sprite_group()):
                game = RefactoredGame()

                # Simulate player death event
                player_death_event = GameEvent.create_player_died(
                    source="player",
                    cause="enemy_collision"
                )

                # Handle player death
                game._handle_player_died(player_death_event)

                # Verify event was handled without errors
                assert True

    def test_factory_integration(self):
        """Test that all factories are properly integrated."""
        from thunder_fighter.game import RefactoredGame

        with patch.multiple(
            'thunder_fighter.game',
            pygame=Mock(),
            SoundManager=Mock(),
            get_resource_manager=Mock(return_value=Mock()),
            Player=Mock(return_value=self._create_mock_player()),
            DynamicBackground=Mock(),
            Score=Mock(return_value=self._create_mock_score()),
            UIManager=Mock(return_value=self._create_mock_ui_manager())
        ):
            with patch('thunder_fighter.game.pygame.sprite.Group', return_value=self._create_mock_pygame_sprite_group()):
                game = RefactoredGame()

                # Verify all factories are available
                assert hasattr(game, 'enemy_factory')
                assert hasattr(game, 'boss_factory')
                assert hasattr(game, 'item_factory')
                assert hasattr(game, 'projectile_factory')

                # Verify factories have expected methods
                assert hasattr(game.enemy_factory, 'create')
                assert hasattr(game.boss_factory, 'create')
                assert hasattr(game.item_factory, 'create')
                assert hasattr(game.projectile_factory, 'create')

    def test_input_system_integration(self):
        """Test input system integration."""
        from thunder_fighter.game import RefactoredGame

        # Create a mock pygame with proper event.get method
        mock_pygame = Mock()
        mock_pygame.event.get.return_value = []

        with patch.multiple(
            'thunder_fighter.game',
            pygame=mock_pygame,
            SoundManager=Mock(),
            get_resource_manager=Mock(return_value=Mock()),
            Player=Mock(return_value=self._create_mock_player()),
            DynamicBackground=Mock(),
            Score=Mock(return_value=self._create_mock_score()),
            UIManager=Mock(return_value=self._create_mock_ui_manager())
        ):
            with patch('thunder_fighter.game.pygame.sprite.Group', return_value=self._create_mock_pygame_sprite_group()):
                game = RefactoredGame()

                # Verify input manager is initialized
                assert game.input_manager is not None

                # Test input processing doesn't crash
                game.handle_events()

                # Verify game is still running
                assert game.running is True

    def test_resource_management_integration(self):
        """Test resource management system integration."""
        from thunder_fighter.game import RefactoredGame

        mock_rm = Mock()
        mock_rm.preload_common_assets.return_value = None
        mock_rm.get_music_path.return_value = None
        mock_rm.get_cache_stats.return_value = {'loaded': 10, 'cached': 5}

        with patch.multiple(
            'thunder_fighter.game',
            pygame=Mock(),
            SoundManager=Mock(),
            get_resource_manager=Mock(return_value=mock_rm),
            Player=Mock(return_value=self._create_mock_player()),
            DynamicBackground=Mock(),
            Score=Mock(return_value=self._create_mock_score()),
            UIManager=Mock(return_value=self._create_mock_ui_manager())
        ):
            with patch('thunder_fighter.game.pygame.sprite.Group', return_value=self._create_mock_pygame_sprite_group()):
                game = RefactoredGame()

                # Verify resource manager is working
                assert game.resource_manager is not None

                # Test resource access
                cache_stats = game.resource_manager.get_cache_stats()
                assert isinstance(cache_stats, dict)

    def test_game_state_consistency(self):
        """Test that game state remains consistent through operations."""
        from thunder_fighter.game import RefactoredGame

        with patch.multiple(
            'thunder_fighter.game',
            pygame=Mock(),
            SoundManager=Mock(),
            get_resource_manager=Mock(return_value=Mock()),
            Player=Mock(return_value=self._create_mock_player()),
            DynamicBackground=Mock(),
            Score=Mock(return_value=self._create_mock_score()),
            UIManager=Mock(return_value=self._create_mock_ui_manager())
        ):
            with patch('thunder_fighter.game.pygame.sprite.Group', return_value=self._create_mock_pygame_sprite_group()):
                game = RefactoredGame()

                # Test initial state
                assert game.running is True
                assert game.paused is False
                assert game.game_level == INITIAL_GAME_LEVEL
                assert game.game_won is False

                # Test that event system maintains state
                assert game.event_system.get_events_processed() >= 0

                # Test that UI state can be updated
                game._update_ui_state()

                # Verify state consistency
                assert game.running is True
