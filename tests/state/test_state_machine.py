"""
Tests for State Machine Framework

This module contains tests for the StateMachine and State classes.
"""

from unittest.mock import Mock

from thunder_fighter.state.state_machine import State, StateMachine


class MockState(State):
    """Mock state for testing."""

    def __init__(self, name: str):
        super().__init__(name)
        self.enter_called = False
        self.exit_called = False
        self.update_called = False
        self.handle_event_called = False
        self.enter_previous = None
        self.exit_next = None

    def enter(self, previous_state=None):
        self.enter_called = True
        self.enter_previous = previous_state

    def exit(self, next_state=None):
        self.exit_called = True
        self.exit_next = next_state

    def update(self, dt: float):
        self.update_called = True
        self.last_dt = dt

    def handle_event(self, event):
        self.handle_event_called = True
        self.last_event = event


class RestrictedState(MockState):
    """Mock state that restricts transitions."""

    def can_transition_to(self, state_name: str) -> bool:
        # Only allow transition to "allowed" state
        return state_name == "allowed"


class TestStateMachine:
    """Tests for the StateMachine class."""

    def test_initialization(self):
        """Test StateMachine initialization."""
        sm = StateMachine()

        assert sm._states == {}
        assert sm._current_state is None
        assert sm._previous_state is None
        assert sm._transition_callbacks == {}
        assert sm._global_callbacks == []

    def test_initialization_with_initial_state(self):
        """Test StateMachine initialization with initial state."""
        initial_state = MockState("initial")
        sm = StateMachine(initial_state)

        assert "initial" in sm._states
        assert sm._current_state == initial_state
        assert initial_state.enter_called is True

    def test_add_state(self):
        """Test adding states to the state machine."""
        sm = StateMachine()
        state1 = MockState("state1")
        state2 = MockState("state2")

        sm.add_state(state1)
        sm.add_state(state2)

        assert "state1" in sm._states
        assert "state2" in sm._states
        assert sm._states["state1"] == state1
        assert sm._states["state2"] == state2
        assert state1._context == sm
        assert state2._context == sm

    def test_remove_state(self):
        """Test removing states from the state machine."""
        sm = StateMachine()
        state1 = MockState("state1")
        state2 = MockState("state2")

        sm.add_state(state1)
        sm.add_state(state2)
        sm.set_current_state("state1")

        # Should not be able to remove current state
        sm.remove_state("state1")
        assert "state1" in sm._states

        # Should be able to remove non-current state
        sm.remove_state("state2")
        assert "state2" not in sm._states

    def test_get_state(self):
        """Test getting states by name."""
        sm = StateMachine()
        state1 = MockState("state1")

        sm.add_state(state1)

        assert sm.get_state("state1") == state1
        assert sm.get_state("nonexistent") is None

    def test_set_current_state(self):
        """Test setting the current state."""
        sm = StateMachine()
        state1 = MockState("state1")
        state2 = MockState("state2")

        sm.add_state(state1)
        sm.add_state(state2)

        # Set initial state
        result = sm.set_current_state("state1")
        assert result is True
        assert sm._current_state == state1
        assert state1.enter_called is True

        # Transition to another state
        result = sm.set_current_state("state2")
        assert result is True
        assert sm._current_state == state2
        assert sm._previous_state == state1
        assert state1.exit_called is True
        assert state2.enter_called is True
        assert state1.exit_next == state2
        assert state2.enter_previous == state1

    def test_set_current_state_nonexistent(self):
        """Test setting a nonexistent state."""
        sm = StateMachine()

        result = sm.set_current_state("nonexistent")
        assert result is False
        assert sm._current_state is None

    def test_set_current_state_with_restrictions(self):
        """Test state transitions with restrictions."""
        sm = StateMachine()
        restricted = RestrictedState("restricted")
        allowed = MockState("allowed")
        forbidden = MockState("forbidden")

        sm.add_state(restricted)
        sm.add_state(allowed)
        sm.add_state(forbidden)

        sm.set_current_state("restricted")

        # Should allow transition to "allowed"
        result = sm.set_current_state("allowed")
        assert result is True

        # Reset to restricted state
        sm.set_current_state("restricted", force=True)

        # Should not allow transition to "forbidden"
        result = sm.set_current_state("forbidden")
        assert result is False
        assert sm._current_state == restricted

        # Should allow with force=True
        result = sm.set_current_state("forbidden", force=True)
        assert result is True
        assert sm._current_state == forbidden

    def test_transition_to(self):
        """Test the transition_to method."""
        sm = StateMachine()
        state1 = MockState("state1")
        state2 = MockState("state2")

        sm.add_state(state1)
        sm.add_state(state2)

        result = sm.transition_to("state1")
        assert result is True
        assert sm._current_state == state1

    def test_update(self):
        """Test updating the current state."""
        sm = StateMachine()
        state1 = MockState("state1")

        sm.add_state(state1)
        sm.set_current_state("state1")

        sm.update(0.016)  # 16ms delta time

        assert state1.update_called is True
        assert state1.last_dt == 0.016

    def test_update_with_no_current_state(self):
        """Test updating when there's no current state."""
        sm = StateMachine()

        # Should not raise an exception
        sm.update(0.016)

    def test_handle_event(self):
        """Test handling events in the current state."""
        sm = StateMachine()
        state1 = MockState("state1")

        sm.add_state(state1)
        sm.set_current_state("state1")

        mock_event = Mock()
        sm.handle_event(mock_event)

        assert state1.handle_event_called is True
        assert state1.last_event == mock_event

    def test_handle_event_with_no_current_state(self):
        """Test handling events when there's no current state."""
        sm = StateMachine()

        mock_event = Mock()
        # Should not raise an exception
        sm.handle_event(mock_event)

    def test_transition_callbacks(self):
        """Test transition callbacks."""
        sm = StateMachine()
        state1 = MockState("state1")
        state2 = MockState("state2")

        sm.add_state(state1)
        sm.add_state(state2)

        # Add callbacks
        callback1 = Mock()
        callback2 = Mock()
        global_callback = Mock()

        sm.add_transition_callback("state2", callback1)
        sm.add_transition_callback("state2", callback2)
        sm.add_global_callback(global_callback)

        # Transition to state1 first
        sm.set_current_state("state1")

        # Reset global callback to only track the transition we care about
        global_callback.reset_mock()

        # Transition to state2
        sm.set_current_state("state2")

        # Check callbacks were called
        callback1.assert_called_once_with(state1, state2)
        callback2.assert_called_once_with(state1, state2)
        global_callback.assert_called_once_with(state1, state2)

    def test_remove_callbacks(self):
        """Test removing callbacks."""
        sm = StateMachine()
        state1 = MockState("state1")

        sm.add_state(state1)

        callback1 = Mock()
        global_callback = Mock()

        sm.add_transition_callback("state1", callback1)
        sm.add_global_callback(global_callback)

        # Remove callbacks
        sm.remove_transition_callback("state1", callback1)
        sm.remove_global_callback(global_callback)

        # Transition should not call removed callbacks
        sm.set_current_state("state1")

        callback1.assert_not_called()
        global_callback.assert_not_called()

    def test_utility_methods(self):
        """Test utility methods."""
        sm = StateMachine()
        state1 = MockState("state1")
        state2 = MockState("state2")

        sm.add_state(state1)
        sm.add_state(state2)

        # Test get_state_names
        assert set(sm.get_state_names()) == {"state1", "state2"}

        # Test has_state
        assert sm.has_state("state1") is True
        assert sm.has_state("nonexistent") is False

        # Test current state methods
        assert sm.get_current_state_name() is None
        assert sm.get_previous_state_name() is None

        sm.set_current_state("state1")
        assert sm.get_current_state_name() == "state1"

        sm.set_current_state("state2")
        assert sm.get_current_state_name() == "state2"
        assert sm.get_previous_state_name() == "state1"

    def test_str_representation(self):
        """Test string representation of StateMachine."""
        sm = StateMachine()
        state1 = MockState("state1")

        sm.add_state(state1)

        # Without current state
        assert "current=None" in str(sm)
        assert "states=1" in str(sm)

        # With current state
        sm.set_current_state("state1")
        assert "current=state1" in str(sm)


class TestState:
    """Tests for the State abstract base class."""

    def test_state_initialization(self):
        """Test State initialization."""
        state = MockState("test")

        assert state.name == "test"
        assert state._context is None

    def test_set_context(self):
        """Test setting state context."""
        state = MockState("test")
        context = Mock()

        state.set_context(context)
        assert state._context == context

    def test_can_transition_to_default(self):
        """Test default transition behavior."""
        state = MockState("test")

        # Default implementation should allow all transitions
        assert state.can_transition_to("any_state") is True

    def test_str_representation(self):
        """Test string representation of State."""
        state = MockState("test")

        assert str(state) == "State(test)"
