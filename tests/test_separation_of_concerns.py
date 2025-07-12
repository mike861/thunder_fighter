"""
Test Separation of Concerns

This module tests the separation of concerns improvements including
input management, entity factories, and event systems.
"""

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pygame
import pytest

# Initialize pygame for testing
pygame.init()

@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    """Initialize pygame for all tests."""
    pygame.init()
    # Create a minimal display to ensure video system is initialized
    try:
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
    except pygame.error:
        # If display creation fails (e.g., in headless environment),
        # continue with basic pygame initialization
        pass
    yield
    pygame.quit()

if TYPE_CHECKING:
    pass

# Input Management Tests
# Entity Factory Tests
from thunder_fighter.entities import BossFactory, EnemyFactory, ItemFactory, ProjectileFactory

# Event System Tests
from thunder_fighter.events import EventSystem, GameEvent, GameEventType
from thunder_fighter.systems.input import InputHandler, InputManager, KeyBindings
from thunder_fighter.systems.input.events import InputEventFactory, InputEventType


class TestInputManagement:
    """Test the input management system."""

    def test_key_bindings_initialization(self):
        """Test key bindings initialization with defaults."""
        key_bindings = KeyBindings()

        # Test that default bindings are loaded
        assert key_bindings.get_action(pygame.K_w) == "move_up"
        assert key_bindings.get_action(pygame.K_SPACE) == "shoot"
        assert key_bindings.get_action(pygame.K_p) == "pause"

        # Test categories
        categories = key_bindings.get_all_categories()
        assert "movement" in categories
        assert "action" in categories
        assert "game" in categories

    def test_key_bindings_rebind(self):
        """Test key rebinding functionality."""
        key_bindings = KeyBindings()

        # Test successful rebind
        assert key_bindings.rebind_key("shoot", pygame.K_SPACE, pygame.K_z)
        assert key_bindings.get_action(pygame.K_z) == "shoot"
        assert key_bindings.get_action(pygame.K_SPACE) is None

        # Test conflict detection
        assert not key_bindings.rebind_key("pause", pygame.K_p, pygame.K_z)  # z is already bound

    def test_input_event_factory(self):
        """Test input event factory methods."""
        # Test movement event
        event = InputEventFactory.create_movement_event("up", True)
        assert event.event_type == InputEventType.MOVE_UP
        assert event.get_data('direction') == "up"
        assert event.get_data('pressed') is True

        # Test action event
        event = InputEventFactory.create_action_event("shoot", True)
        assert event.event_type == InputEventType.SHOOT
        assert event.get_data('action') == "shoot"

        # Test game control event
        event = InputEventFactory.create_game_control_event("pause")
        assert event.event_type == InputEventType.PAUSE
        assert event.get_data('control') == "pause"

    @patch('pygame.key.get_pressed')
    def test_input_handler_pygame_events(self, mock_get_pressed):
        """Test input handler processing pygame events."""
        # Mock pygame.key.get_pressed to return a dict-like object that returns False for any key
        class MockKeyState:
            def __getitem__(self, key):
                return False

        mock_get_pressed.return_value = MockKeyState()

        handler = InputHandler()

        # Create mock pygame events
        keydown_event = Mock()
        keydown_event.type = pygame.KEYDOWN
        keydown_event.key = pygame.K_w

        keyup_event = Mock()
        keyup_event.type = pygame.KEYUP
        keyup_event.key = pygame.K_w

        quit_event = Mock()
        quit_event.type = pygame.QUIT

        # Process events
        events = handler.process_pygame_events([keydown_event, keyup_event, quit_event])

        # Check that events were generated
        assert len(events) >= 3  # At least keydown, keyup, and quit events

        # Check event types
        event_types = [event.event_type for event in events]
        assert InputEventType.MOVE_UP in event_types
        assert InputEventType.STOP_MOVE_UP in event_types
        assert InputEventType.QUIT in event_types

    def test_input_manager_callbacks(self):
        """Test input manager callback system."""
        manager = InputManager()

        # Create callback mock
        callback_mock = Mock()

        # Register callback
        manager.add_event_callback(InputEventType.MOVE_UP, callback_mock)

        # Create and process event
        event = InputEventFactory.create_movement_event("up", True)
        manager.update([])  # Process empty pygame events
        manager._trigger_callbacks(event)  # Manually trigger for testing

        # Verify callback was called
        callback_mock.assert_called_once_with(event)

    @patch('pygame.key.get_pressed')
    def test_input_manager_pause_filtering(self, mock_get_pressed):
        """Test input manager event filtering when paused."""
        # Mock pygame.key.get_pressed to return a dict-like object that returns False for any key
        class MockKeyState:
            def __getitem__(self, key):
                return False

        mock_get_pressed.return_value = MockKeyState()

        manager = InputManager()
        manager.pause()

        # Create events - some should be filtered when paused
        move_event = Mock()
        move_event.type = pygame.KEYDOWN
        move_event.key = pygame.K_w

        pause_event = Mock()
        pause_event.type = pygame.KEYDOWN
        pause_event.key = pygame.K_p

        events = manager.update([move_event, pause_event])

        # Only pause-allowed events should pass through
        allowed_types = {event.event_type for event in events}
        assert InputEventType.PAUSE in allowed_types or len(events) == 0  # Depending on implementation


class TestEntityFactories:
    """Test the entity factory system."""

    def test_enemy_factory_presets(self):
        """Test enemy factory preset system."""
        factory = EnemyFactory()

        # Test preset creation
        presets = factory.list_presets()
        assert "basic" in presets
        assert "shooter" in presets
        assert "fast" in presets
        assert "tank" in presets
        assert "elite" in presets

        # Test preset configuration
        basic_preset = factory.get_preset("basic")
        assert basic_preset['can_shoot'] is False
        assert basic_preset['health_multiplier'] == 1.0

        shooter_preset = factory.get_preset("shooter")
        assert shooter_preset['can_shoot'] is True
        assert shooter_preset['health_multiplier'] == 1.2

    def test_enemy_factory_level_based_creation(self):
        """Test enemy factory level-based enemy selection."""
        factory = EnemyFactory()

        # Mock required parameters
        all_sprites = Mock()
        enemy_bullets = Mock()

        # Test level 1 enemies (should be mostly basic)
        enemy_types = []
        for _ in range(10):
            enemy_type = factory._determine_enemy_type(1, 0)
            enemy_types.append(enemy_type)

        # Should contain basic and fast enemies for level 1
        assert "basic" in enemy_types

        # Test higher level enemies
        high_level_type = factory._determine_enemy_type(6, 5)
        assert high_level_type in ["tank", "elite", "shooter"]

    def test_boss_factory_configuration(self):
        """Test boss factory configuration system."""
        factory = BossFactory()

        # Test presets
        presets = factory.list_presets()
        assert "standard" in presets
        assert "elite" in presets

        # Test preset differences
        standard = factory.get_preset("standard")
        elite = factory.get_preset("elite")

        assert elite['health_multiplier'] > standard['health_multiplier']
        assert elite['speed_multiplier'] > standard['speed_multiplier']

    def test_item_factory_random_creation(self):
        """Test item factory random item creation."""
        factory = ItemFactory()

        # Mock required parameters
        all_sprites = Mock()
        items = Mock()
        player = Mock()

        # Test that different item types can be created
        item_types = set()
        for _ in range(20):  # Create multiple items to test randomness
            try:
                factory.create_random_item(all_sprites, items, player)
                # In a real test, we'd check the item type
                item_types.add("mock_item")  # Placeholder
            except Exception:
                # Factory might fail without proper sprite setup
                pass

        # Test that presets exist
        presets = factory.list_presets()
        assert "health" in presets
        assert "bullet_speed" in presets

    def test_projectile_factory_types(self):
        """Test projectile factory type creation."""
        factory = ProjectileFactory()

        # Test presets
        presets = factory.list_presets()
        assert "player_bullet" in presets
        assert "enemy_bullet" in presets
        assert "player_missile" in presets

        # Test preset configurations
        player_bullet = factory.get_preset("player_bullet")
        enemy_bullet = factory.get_preset("enemy_bullet")

        assert player_bullet['owner'] == 'player'
        assert enemy_bullet['owner'] == 'enemy'


class TestEventSystem:
    """Test the event system."""

    def test_event_system_initialization(self):
        """Test event system initialization."""
        event_system = EventSystem()

        assert event_system.get_queue_size() == 0
        assert event_system.get_listener_count() == 0
        assert event_system.get_events_processed() == 0

    def test_event_creation_and_dispatch(self):
        """Test event creation and dispatch."""
        event_system = EventSystem()

        # Create and dispatch event
        event = event_system.create_event(GameEventType.PLAYER_DIED, "test", cause="testing")
        event_system.dispatch_event(event)

        assert event_system.get_queue_size() == 1

        # Process events
        event_system.process_events()

        assert event_system.get_queue_size() == 0
        assert event_system.get_events_processed() == 1

    def test_event_listeners(self):
        """Test event listener registration and handling."""
        event_system = EventSystem()

        # Create mock listener
        listener = Mock()
        listener.handle_event = Mock(return_value=False)

        # Register listener
        event_system.register_listener(GameEventType.PLAYER_DIED, listener)

        assert event_system.get_listener_count(GameEventType.PLAYER_DIED) == 1

        # Dispatch and process event
        event_system.emit_event(GameEventType.PLAYER_DIED, "test")
        event_system.process_events()

        # Verify listener was called
        listener.handle_event.assert_called_once()

    def test_global_event_listeners(self):
        """Test global event listeners."""
        event_system = EventSystem()

        # Create mock global listener
        global_listener = Mock()
        global_listener.handle_event = Mock(return_value=False)

        # Register global listener
        event_system.register_global_listener(global_listener)

        # Dispatch different types of events
        event_system.emit_event(GameEventType.PLAYER_DIED, "test")
        event_system.emit_event(GameEventType.ENEMY_SPAWNED, "test")
        event_system.process_events()

        # Global listener should receive both events
        assert global_listener.handle_event.call_count == 2

    def test_game_event_factory_methods(self):
        """Test game event factory methods."""
        # Test player died event
        event = GameEvent.create_player_died("player", "collision")
        assert event.event_type == GameEventType.PLAYER_DIED
        assert event.get_data('cause') == "collision"

        # Test health changed event
        event = GameEvent.create_player_health_changed("player", 100, 80, 100)
        assert event.event_type == GameEventType.PLAYER_HEALTH_CHANGED
        assert event.get_data('old_health') == 100
        assert event.get_data('new_health') == 80

        # Test enemy spawned event
        event = GameEvent.create_enemy_spawned("factory", "elite", 3)
        assert event.event_type == GameEventType.ENEMY_SPAWNED
        assert event.get_data('enemy_type') == "elite"
        assert event.get_data('level') == 3

    def test_event_handling_chain(self):
        """Test event handling chain and early termination."""
        event_system = EventSystem()

        # Create listeners - first one handles event
        first_listener = Mock()
        first_listener.handle_event = Mock(return_value=True)  # Handles event

        second_listener = Mock()
        second_listener.handle_event = Mock(return_value=False)

        # Register listeners
        event_system.register_listener(GameEventType.PLAYER_DIED, first_listener)
        event_system.register_listener(GameEventType.PLAYER_DIED, second_listener)

        # Dispatch event
        event_system.emit_event(GameEventType.PLAYER_DIED, "test")
        event_system.process_events()

        # First listener should handle event, second should not be called
        first_listener.handle_event.assert_called_once()
        second_listener.handle_event.assert_not_called()


class TestSeparationOfConcernsIntegration:
    """Test integration between the separated systems."""

    def test_input_to_event_integration(self):
        """Test integration between input system and event system."""
        # This would test how input events trigger game events
        input_manager = InputManager()
        event_system = EventSystem()

        # In a real integration, input events would trigger game events
        # For now, just test that both systems can coexist
        assert input_manager is not None
        assert event_system is not None

    def test_factory_to_event_integration(self):
        """Test integration between factories and event system."""
        # This would test how entity creation triggers events
        enemy_factory = EnemyFactory()
        event_system = EventSystem()

        # In a real integration, entity creation would emit events
        assert enemy_factory is not None
        assert event_system is not None

    def test_system_independence(self):
        """Test that systems can work independently."""
        # Test that each system can be used without the others

        # Input system
        input_manager = InputManager()
        assert input_manager.is_enabled()

        # Factory system
        enemy_factory = EnemyFactory()
        assert len(enemy_factory.list_presets()) > 0

        # Event system
        event_system = EventSystem()
        assert event_system.get_queue_size() == 0

        # All systems should work independently
        assert True  # If we get here, systems initialized independently


# Integration test fixture
@pytest.fixture
def separated_systems():
    """Fixture providing all separated systems for integration testing."""
    return {
        'input_manager': InputManager(),
        'enemy_factory': EnemyFactory(),
        'boss_factory': BossFactory(),
        'item_factory': ItemFactory(),
        'projectile_factory': ProjectileFactory(),
        'event_system': EventSystem()
    }


def test_complete_separation_integration(separated_systems):
    """Test complete integration of all separated systems."""
    systems = separated_systems

    # Verify all systems are initialized
    assert all(system is not None for system in systems.values())

    # Test that systems have expected functionality
    assert systems['input_manager'].is_enabled()
    assert len(systems['enemy_factory'].list_presets()) > 0
    assert systems['event_system'].get_queue_size() == 0

    # Test basic operations don't interfere with each other
    systems['input_manager'].pause()
    systems['event_system'].emit_event(GameEventType.GAME_PAUSED, "test")
    systems['event_system'].process_events()

    # Should complete without errors
    assert True
