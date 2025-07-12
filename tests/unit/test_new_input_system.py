"""
Unit tests for the new InputSystem facade.

This module tests the high-level InputSystem class, ensuring it correctly
integrates the core logic and adapters, and provides a robust, testable API.
"""

import pygame

from thunder_fighter.systems.input import (
    CommandType,
    Event,
    EventType,
    TestClock,
    TestEventSource,
    TestKeyboardState,
    TestLogger,
    TestScenario,
    create_for_testing,
)


class TestInputSystemCore:
    """Test Input System Core Functionality"""

    def test_system_creation(self):
        """Test system creation."""
        system, controllers = create_for_testing()

        assert system is not None
        assert 'event_source' in controllers
        assert 'keyboard_state' in controllers
        assert 'clock' in controllers
        assert 'logger' in controllers

    def test_simple_key_press_to_command(self):
        """Test simple key press to command conversion."""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']

        # Simulate spacebar press
        event_source.add_key_down(pygame.K_SPACE)

        # Process input
        commands = system.update()

        # Verify shoot command is generated
        assert len(commands) == 1
        assert commands[0].type == CommandType.SHOOT
        assert commands[0].get_data('key') == pygame.K_SPACE

    def test_movement_commands(self):
        """Test movement commands."""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']

        # Test all movement keys
        movement_keys = [
            (pygame.K_UP, CommandType.MOVE_UP),
            (pygame.K_DOWN, CommandType.MOVE_DOWN),
            (pygame.K_LEFT, CommandType.MOVE_LEFT),
            (pygame.K_RIGHT, CommandType.MOVE_RIGHT),
            (pygame.K_w, CommandType.MOVE_UP),
            (pygame.K_s, CommandType.MOVE_DOWN),
            (pygame.K_a, CommandType.MOVE_LEFT),
            (pygame.K_d, CommandType.MOVE_RIGHT),
        ]

        for key, expected_command in movement_keys:
            # Clear previous events and states
            event_source.clear_events()
            system.reset_state()  # Reset state, clear cooldown

            # Add key event
            event_source.add_key_down(key)

            # Process input
            commands = system.update()

            # Verify
            assert len(commands) == 1
            assert commands[0].type == expected_command

    def test_modifier_keys(self):
        """Test modifier keys."""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']

        # Add event with modifier keys
        event = Event(
            type=EventType.KEY_DOWN,
            key_code=pygame.K_SPACE,
            modifiers={'ctrl': True, 'shift': False, 'alt': False}
        )
        event_source.add_event(event)

        # Process input
        commands = system.update()

        # Verify modifier keys are passed correctly
        assert len(commands) == 1
        assert commands[0].get_data('modifiers')['ctrl'] is True
        assert commands[0].get_data('modifiers')['shift'] is False

    def test_continuous_movement(self):
        """Test continuous movement."""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']
        clock = controllers['clock']

        # Press W key
        event_source.add_key_down(pygame.K_w)

        # First process - initial key press
        commands = system.update()
        assert len(commands) == 1
        assert commands[0].type == CommandType.MOVE_UP
        assert commands[0].get_data('continuous') is False

        # Advance time
        clock.advance(0.1)

        # Second process - continuous key press
        commands = system.update()
        assert len(commands) == 1
        assert commands[0].type == CommandType.MOVE_UP
        assert commands[0].get_data('continuous') is True

    def test_command_cooldown(self):
        """Test command cooldown."""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']
        clock = controllers['clock']

        # Set a longer cooldown time
        system.configure_cooldown(0.5)

        # Rapid consecutive key presses
        event_source.add_key_down(pygame.K_SPACE)
        commands1 = system.update()

        # Press key again immediately
        clock.advance(0.1)  # Advance only 0.1 seconds, less than cooldown
        event_source.add_key_down(pygame.K_SPACE)
        commands2 = system.update()

        # First should succeed, second should be blocked by cooldown
        assert len(commands1) == 1
        assert len(commands2) == 0

        # Wait for cooldown to end
        clock.advance(0.5)
        event_source.add_key_down(pygame.K_SPACE)
        commands3 = system.update()

        # Should be able to trigger again now
        assert len(commands3) == 1


class TestCommandHandlers:
    """Test Command Handler System"""

    def test_command_handler_registration(self):
        """Test command handler registration."""
        system, controllers = create_for_testing()

        # Register handler
        shoot_called = False
        def on_shoot(cmd):
            nonlocal shoot_called
            shoot_called = True

        system.on_command(CommandType.SHOOT, on_shoot)

        # Trigger command
        event_source = controllers['event_source']
        event_source.add_key_down(pygame.K_SPACE)
        system.update()

        # Verify handler is called
        assert shoot_called is True

    def test_multiple_handlers_same_command(self):
        """Test multiple handlers for the same command."""
        system, controllers = create_for_testing()

        # Register multiple handlers
        handler1_called = False
        handler2_called = False

        def handler1(cmd):
            nonlocal handler1_called
            handler1_called = True

        def handler2(cmd):
            nonlocal handler2_called
            handler2_called = True

        system.on_command(CommandType.SHOOT, handler1)
        system.on_command(CommandType.SHOOT, handler2)

        # Trigger command
        event_source = controllers['event_source']
        event_source.add_key_down(pygame.K_SPACE)
        system.update()

        # Verify all handlers are called
        assert handler1_called is True
        assert handler2_called is True

    def test_handler_removal(self):
        """Test handler removal."""
        system, controllers = create_for_testing()

        # Register handler
        handler_called = False
        def handler(cmd):
            nonlocal handler_called
            handler_called = True

        system.on_command(CommandType.SHOOT, handler)

        # Remove handler
        system.remove_command_handler(CommandType.SHOOT, handler)

        # Trigger command
        event_source = controllers['event_source']
        event_source.add_key_down(pygame.K_SPACE)
        system.update()

        # Verify handler is not called
        assert handler_called is False


class TestInputSystemStates:
    """Test Input System State Management"""

    def test_key_held_detection(self):
        """Test key held detection."""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']

        # Check initial state
        assert not system.is_key_held(pygame.K_w)

        # Press key
        event_source.add_key_down(pygame.K_w)
        system.update()

        # Check held state
        assert system.is_key_held(pygame.K_w)

        # Release key
        event_source.add_key_up(pygame.K_w)
        system.update()

        # Check state after release
        assert not system.is_key_held(pygame.K_w)

    def test_multiple_held_keys(self):
        """Test multiple keys held simultaneously."""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']

        # Press multiple keys
        event_source.add_key_down(pygame.K_w)
        event_source.add_key_down(pygame.K_a)
        system.update()

        # Check state
        held_keys = system.get_held_keys()
        assert pygame.K_w in held_keys
        assert pygame.K_a in held_keys
        assert len(held_keys) == 2

    def test_system_enable_disable(self):
        """Test system enable/disable."""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']

        # Disable system
        system.disable()

        # Try input
        event_source.add_key_down(pygame.K_SPACE)
        commands = system.update()

        # No commands should be generated
        assert len(commands) == 0

        # Enable system
        system.enable()

        # Try input again
        event_source.add_key_down(pygame.K_SPACE)
        commands = system.update()

        # Now there should be commands
        assert len(commands) == 1

    def test_state_reset(self):
        """Test state reset."""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']

        # Press some keys
        event_source.add_key_down(pygame.K_w)
        event_source.add_key_down(pygame.K_SPACE)
        system.update()

        # Verify some keys are held down
        assert len(system.get_held_keys()) > 0

        # Reset state
        system.reset_state()

        # Verify state is cleared
        assert len(system.get_held_keys()) == 0


class TestTimeAndStats:
    """Test Time Control and Statistics"""

    def test_precise_timing_control(self):
        """Test precise timing control."""
        system, controllers = create_for_testing(initial_time=1000.0)
        event_source = controllers['event_source']
        clock = controllers['clock']

        # Add event at a specific time
        event_source.add_key_down(pygame.K_SPACE)
        commands = system.update()

        # Verify timestamp
        assert len(commands) == 1
        assert commands[0].timestamp == 1000.0

        # Advance time
        clock.advance(5.0)
        event_source.add_key_down(pygame.K_x)
        commands = system.update()

        # Verify new timestamp
        assert len(commands) == 1
        assert commands[0].timestamp == 1005.0

    def test_system_statistics(self):
        """Test system statistics."""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']

        # Get initial statistics
        initial_stats = system.get_stats()
        assert initial_stats['total_commands'] == 0

        # Generate some commands
        event_source.add_key_down(pygame.K_SPACE)
        event_source.add_key_down(pygame.K_x)
        system.update()

        # Check statistics update
        updated_stats = system.get_stats()
        assert updated_stats['total_commands'] == 2
        assert updated_stats['events_processed'] == 2


class TestTestHelpers:
    """Test Test Helpers"""

    def test_test_scenario_builder(self):
        """Test test scenario builder."""
        # Create test environment
        event_source = TestEventSource()
        keyboard = TestKeyboardState()
        clock = TestClock()

        # Use scenario builder
        scenario = TestScenario(event_source, clock, keyboard)

        # Build complex scenario
        scenario.at_time(0.0).press_key(pygame.K_w) \
               .wait(0.5).press_key(pygame.K_SPACE) \
               .wait(0.1).release_key(pygame.K_w) \
               .wait(0.2).release_key(pygame.K_SPACE)

        # Verify timeline
        assert clock.now() == 0.8
        assert not keyboard.is_pressed(pygame.K_SPACE)  # Should be released
        assert not keyboard.is_pressed(pygame.K_w)

    def test_logger_verification(self):
        """Test logger verification."""
        logger = TestLogger(print_logs=False)

        # Log messages of different levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        # Verify logging
        assert logger.count_level('DEBUG') == 1
        assert logger.count_level('INFO') == 1
        assert logger.count_level('WARNING') == 1
        assert logger.count_level('ERROR') == 1

        # Verify specific messages
        info_logs = logger.get_logs('INFO')
        assert "Info message" in info_logs


class TestIntegrationScenarios:
    """Integration Test Scenarios"""

    def test_complex_game_sequence(self):
        """Test complex game sequence."""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']
        clock = controllers['clock']

        # Collect all generated commands
        all_commands = []
        def command_collector(cmd):
            all_commands.append(cmd)

        # Register collector
        for cmd_type in CommandType:
            system.on_command(cmd_type, command_collector)

        # Simulate game sequence: move + shoot + pause
        # 1. Start moving up
        event_source.add_key_down(pygame.K_w)
        system.update()

        # 2. Continue moving for a while
        for _ in range(5):
            clock.advance(0.05)
            system.update()

        # 3. Start shooting (while moving)
        event_source.add_key_down(pygame.K_SPACE)
        system.update()

        # 4. Pause game
        clock.advance(0.1)
        event_source.add_key_down(pygame.K_p)
        system.update()

        # Analyze command sequence
        move_commands = [cmd for cmd in all_commands if cmd.type == CommandType.MOVE_UP]
        shoot_commands = [cmd for cmd in all_commands if cmd.type == CommandType.SHOOT]
        pause_commands = [cmd for cmd in all_commands if cmd.type == CommandType.PAUSE]

        # Verify sequence
        assert len(move_commands) >= 6  # Initial + 5 repeats
        assert len(shoot_commands) == 1
        assert len(pause_commands) == 1

        # Verify time order
        assert move_commands[0].timestamp < shoot_commands[0].timestamp
        assert shoot_commands[0].timestamp < pause_commands[0].timestamp

    def test_error_recovery(self):
        """Test error recovery."""
        system, controllers = create_for_testing()
        logger = controllers['logger']

        # Register a handler that raises an exception
        def failing_handler(cmd):
            raise ValueError("Test error")

        system.on_command(CommandType.SHOOT, failing_handler)

        # Trigger command (should not crash)
        event_source = controllers['event_source']
        event_source.add_key_down(pygame.K_SPACE)
        commands = system.update()

        # Verify system still works normally
        assert len(commands) == 1

        # Verify error is logged
        error_logs = logger.get_logs('ERROR')
        assert len(error_logs) > 0
        assert "Test error" in str(error_logs)
