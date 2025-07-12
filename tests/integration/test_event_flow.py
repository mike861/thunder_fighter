"""
Integration tests for event system flow.

This module tests the complete event propagation through the system,
verifying that events are properly dispatched and handled by all
registered listeners.
"""

from typing import List, Set

from thunder_fighter.events.event_system import Event, EventListener, EventSystem
from thunder_fighter.events.game_events import GameEvent, GameEventType


class MockEventListener(EventListener):
    """Mock event listener for integration testing."""

    def __init__(self, name: str, listen_events: Set[GameEventType] = None):
        """
        Initialize test listener.
        
        Args:
            name: Listener name for identification
            listen_events: Set of event types to listen for
        """
        self.name = name
        self.events_received: List[Event] = []
        self.listen_events = listen_events or set()
        self.should_stop_propagation = False

    def handle_event(self, event: Event) -> bool:
        """Handle received events."""
        self.events_received.append(event)
        return self.should_stop_propagation

    def get_listened_events(self) -> Set[GameEventType]:
        """Return events this listener is interested in."""
        return self.listen_events

    def clear_events(self):
        """Clear received events."""
        self.events_received.clear()


class TestEventFlow:
    """Test complete event flow through the system."""

    def setup_method(self):
        """Set up test environment."""
        self.event_system = EventSystem()
        self.listener1 = MockEventListener("listener1")
        self.listener2 = MockEventListener("listener2")
        self.global_listener = MockEventListener("global")

    def test_single_event_dispatch_and_handling(self):
        """Test that a single event is properly dispatched and handled."""
        # Register listeners
        self.event_system.register_listener(GameEventType.PLAYER_DIED, self.listener1)
        self.event_system.register_global_listener(self.global_listener)

        # Create and dispatch event
        event = GameEvent.create_player_died(source="test", cause="collision")
        self.event_system.dispatch_event(event)

        # Process events
        self.event_system.process_events()

        # Verify event was received
        assert len(self.listener1.events_received) == 1
        assert len(self.global_listener.events_received) == 1

        received_event = self.listener1.events_received[0]
        assert received_event.event_type == GameEventType.PLAYER_DIED
        assert received_event.get_data("cause") == "collision"
        assert received_event.source == "test"

    def test_multiple_listeners_same_event_type(self):
        """Test multiple listeners receiving the same event type."""
        # Register multiple listeners for same event
        self.event_system.register_listener(GameEventType.ENEMY_DIED, self.listener1)
        self.event_system.register_listener(GameEventType.ENEMY_DIED, self.listener2)

        # Dispatch event
        event = GameEvent.create_enemy_died(
            source="enemy",
            enemy_type="basic",
            score_awarded=100
        )
        self.event_system.dispatch_event(event)
        self.event_system.process_events()

        # Both listeners should receive the event
        assert len(self.listener1.events_received) == 1
        assert len(self.listener2.events_received) == 1

        # Verify event data
        for listener in [self.listener1, self.listener2]:
            received_event = listener.events_received[0]
            assert received_event.event_type == GameEventType.ENEMY_DIED
            assert received_event.get_data("enemy_type") == "basic"
            assert received_event.get_data("score_awarded") == 100

    def test_event_propagation_stopping(self):
        """Test that event propagation can be stopped by a listener."""
        # Set up listeners where first one stops propagation
        self.listener1.should_stop_propagation = True

        self.event_system.register_listener(GameEventType.BOSS_DIED, self.listener1)
        self.event_system.register_listener(GameEventType.BOSS_DIED, self.listener2)

        # Dispatch event
        event = GameEvent.create_boss_died(
            source="boss",
            boss_level=1,
            score_awarded=1000
        )
        self.event_system.dispatch_event(event)
        self.event_system.process_events()

        # First listener should receive event, second should not
        assert len(self.listener1.events_received) == 1
        assert len(self.listener2.events_received) == 0

    def test_global_listener_receives_all_events(self):
        """Test that global listeners receive all dispatched events."""
        self.event_system.register_global_listener(self.global_listener)

        # Dispatch multiple different event types
        events = [
            GameEvent.create_player_died(source="test"),
            GameEvent.create_enemy_spawned(source="factory", enemy_type="advanced"),
            GameEvent.create_score_changed(source="score", old_score=0, new_score=100),
            GameEvent.create_level_changed(source="game", old_level=1, new_level=2)
        ]

        for event in events:
            self.event_system.dispatch_event(event)

        self.event_system.process_events()

        # Global listener should receive all events
        assert len(self.global_listener.events_received) == 4

        # Verify event types
        received_types = [e.event_type for e in self.global_listener.events_received]
        expected_types = [
            GameEventType.PLAYER_DIED,
            GameEventType.ENEMY_SPAWNED,
            GameEventType.SCORE_CHANGED,
            GameEventType.LEVEL_CHANGED
        ]
        assert received_types == expected_types

    def test_immediate_vs_queued_event_processing(self):
        """Test difference between immediate and queued event processing."""
        self.event_system.register_listener(GameEventType.ITEM_COLLECTED, self.listener1)

        # Dispatch queued event
        queued_event = GameEvent.create_item_collected(
            source="item",
            item_type="health"
        )
        self.event_system.dispatch_event(queued_event, immediate=False)

        # Should not be processed yet
        assert len(self.listener1.events_received) == 0

        # Dispatch immediate event
        immediate_event = GameEvent.create_item_collected(
            source="item",
            item_type="power"
        )
        self.event_system.dispatch_event(immediate_event, immediate=True)

        # Immediate event should be processed
        assert len(self.listener1.events_received) == 1
        assert self.listener1.events_received[0].get_data("item_type") == "power"

        # Process queued events
        self.event_system.process_events()

        # Now both events should be processed
        assert len(self.listener1.events_received) == 2
        item_types = [e.get_data("item_type") for e in self.listener1.events_received]
        assert "health" in item_types
        assert "power" in item_types

    def test_event_system_statistics_tracking(self):
        """Test that event system tracks statistics correctly."""
        self.event_system.register_listener(GameEventType.PLAYER_HEALTH_CHANGED, self.listener1)

        # Initial statistics
        assert self.event_system.get_events_processed() == 0
        assert self.event_system.get_queue_size() == 0

        # Dispatch events
        for i in range(5):
            event = GameEvent.create_player_health_changed(
                source="player",
                old_health=100 - i * 10,
                new_health=100 - (i + 1) * 10
            )
            self.event_system.dispatch_event(event)

        # Check queue size
        assert self.event_system.get_queue_size() == 5

        # Process events
        self.event_system.process_events()

        # Check statistics
        assert self.event_system.get_events_processed() == 5
        assert self.event_system.get_queue_size() == 0
        assert len(self.listener1.events_received) == 5

    def test_listener_registration_and_unregistration(self):
        """Test listener registration and unregistration workflow."""
        # Register listener
        self.event_system.register_listener(GameEventType.BOSS_SPAWNED, self.listener1)

        # Verify listener count
        assert self.event_system.get_listener_count(GameEventType.BOSS_SPAWNED) == 1

        # Dispatch event
        event = GameEvent.create_boss_spawned(source="factory", boss_level=2)
        self.event_system.dispatch_event(event)
        self.event_system.process_events()

        # Listener should receive event
        assert len(self.listener1.events_received) == 1

        # Unregister listener
        self.event_system.unregister_listener(GameEventType.BOSS_SPAWNED, self.listener1)
        assert self.event_system.get_listener_count(GameEventType.BOSS_SPAWNED) == 0

        # Clear previous events
        self.listener1.clear_events()

        # Dispatch another event
        event2 = GameEvent.create_boss_spawned(source="factory", boss_level=3)
        self.event_system.dispatch_event(event2)
        self.event_system.process_events()

        # Listener should not receive the second event
        assert len(self.listener1.events_received) == 0

    def test_complex_event_chain_scenario(self):
        """Test a complex scenario with chained events."""
        # Set up listeners for different event types
        player_listener = MockEventListener("player_events")
        enemy_listener = MockEventListener("enemy_events")
        score_listener = MockEventListener("score_events")

        self.event_system.register_listener(GameEventType.PLAYER_DIED, player_listener)
        self.event_system.register_listener(GameEventType.ENEMY_DIED, enemy_listener)
        self.event_system.register_listener(GameEventType.SCORE_CHANGED, score_listener)

        # Simulate a game scenario: enemy dies -> score changes -> player levels up
        events_sequence = [
            GameEvent.create_enemy_died(
                source="enemy_basic",
                enemy_type="basic",
                score_awarded=50
            ),
            GameEvent.create_score_changed(
                source="score_manager",
                old_score=450,
                new_score=500,
                delta=50
            ),
            GameEvent.create_level_changed(
                source="game",
                old_level=1,
                new_level=2
            )
        ]

        # Dispatch all events
        for event in events_sequence:
            self.event_system.dispatch_event(event)

        # Process all events
        self.event_system.process_events()

        # Verify each listener received appropriate events
        assert len(enemy_listener.events_received) == 1
        assert len(score_listener.events_received) == 1
        assert len(player_listener.events_received) == 0  # No player death event

        # Verify event data integrity
        enemy_event = enemy_listener.events_received[0]
        assert enemy_event.get_data("enemy_type") == "basic"
        assert enemy_event.get_data("score_awarded") == 50

        score_event = score_listener.events_received[0]
        assert score_event.get_data("old_score") == 450
        assert score_event.get_data("new_score") == 500
        assert score_event.get_data("delta") == 50

    def test_event_system_error_handling(self):
        """Test event system behavior with listener errors."""
        class ErrorListener(EventListener):
            def handle_event(self, event: Event) -> bool:
                raise RuntimeError("Test error in listener")

        error_listener = ErrorListener()
        self.event_system.register_listener(GameEventType.GAME_STARTED, error_listener)
        self.event_system.register_listener(GameEventType.GAME_STARTED, self.listener1)

        # Dispatch event that will cause error
        event = GameEvent.create_game_state_changed(
            source="game",
            old_state="menu",
            new_state="started"
        )

        # Event processing should handle errors gracefully
        self.event_system.dispatch_event(event)

        # This should not raise an exception
        self.event_system.process_events()

        # Non-error listener should still receive event
        assert len(self.listener1.events_received) == 1
