"""
Tests for the Event System.

Tests the event-driven architecture components.
"""

import pytest
from unittest.mock import Mock
from thunder_fighter.events.event_system import EventSystem, Event, EventType


class TestEventSystem:
    """Test the EventSystem class."""
    
    @pytest.fixture
    def event_system(self):
        """Create an EventSystem for testing."""
        return EventSystem()
    
    def test_event_system_initialization(self, event_system):
        """Test that the event system initializes correctly."""
        assert event_system is not None
        assert hasattr(event_system, 'register_listener')
        assert hasattr(event_system, 'dispatch_event')
        assert hasattr(event_system, 'unregister_listener')
    
    def test_event_listener_management(self, event_system):
        """Test event listener registration and unregistration."""
        mock_listener = Mock()
        
        # Test registration
        event_system.register_listener(EventType.UNKNOWN, mock_listener)
        assert EventType.UNKNOWN in event_system._listeners
        assert mock_listener in event_system._listeners[EventType.UNKNOWN]
        
        # Test unregistration
        event_system.unregister_listener(EventType.UNKNOWN, mock_listener)
        if EventType.UNKNOWN in event_system._listeners:
            assert mock_listener not in event_system._listeners[EventType.UNKNOWN]
    
    def test_event_dispatch(self, event_system):
        """Test event dispatching to registered listeners."""
        mock_listener = Mock()
        test_event = Event(event_type=EventType.UNKNOWN, data={})
        
        event_system.register_listener(EventType.UNKNOWN, mock_listener)
        event_system.dispatch_event(test_event)
        
        mock_listener.assert_called_once_with(test_event)
    
    def test_multiple_listeners(self, event_system):
        """Test that multiple listeners receive events."""
        listener1 = Mock()
        listener2 = Mock()
        test_event = Event(event_type=EventType.UNKNOWN, data={})
        
        event_system.register_listener(EventType.UNKNOWN, listener1)
        event_system.register_listener(EventType.UNKNOWN, listener2)
        event_system.dispatch_event(test_event)
        
        listener1.assert_called_once_with(test_event)
        listener2.assert_called_once_with(test_event)
    
    # TODO: Add more comprehensive event system tests
    # - Test event filtering and priorities
    # - Test event system performance with many listeners
    # - Test error handling in event dispatch
    # - Test event data validation