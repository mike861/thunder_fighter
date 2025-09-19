"""
Tests for PauseManager

Tests the improved pause management system that provides
testable interfaces for pause functionality.
"""

from unittest.mock import patch

from thunder_fighter.utils.pause_manager import PauseManager


class TestPauseManager:
    """Test PauseManager functionality."""

    def test_initial_state(self):
        """Test initial pause manager state."""
        manager = PauseManager()

        assert not manager.is_paused
        assert manager.get_total_pause_duration() == 0.0

        stats = manager.get_pause_stats()
        assert not stats.is_paused
        assert stats.total_pause_duration == 0.0
        assert stats.current_pause_duration == 0.0
        assert stats.pause_count == 0

    def test_pause_toggle(self):
        """Test basic pause toggling."""
        manager = PauseManager(cooldown_ms=0)  # No cooldown for testing

        # Toggle to pause
        result = manager.toggle_pause(1000.0)
        assert result is True
        assert manager.is_paused

        # Toggle to resume
        result = manager.toggle_pause(1002.0)
        assert result is True
        assert not manager.is_paused
        assert manager.get_total_pause_duration() == 2.0

    def test_pause_resume_methods(self):
        """Test explicit pause and resume methods."""
        manager = PauseManager(cooldown_ms=0)

        # Pause when not paused
        result = manager.pause(1000.0)
        assert result is True
        assert manager.is_paused

        # Pause when already paused (should fail)
        result = manager.pause(1001.0)
        assert result is False
        assert manager.is_paused

        # Resume when paused
        result = manager.resume(1002.0)
        assert result is True
        assert not manager.is_paused

        # Resume when not paused (should fail)
        result = manager.resume(1003.0)
        assert result is False
        assert not manager.is_paused

    def test_cooldown_mechanism(self):
        """Test cooldown prevents rapid toggling."""
        manager = PauseManager(cooldown_ms=500)

        # First toggle should work
        result1 = manager.toggle_pause(1000.0)
        assert result1 is True
        assert manager.is_paused

        # Immediate toggle should fail due to cooldown
        result2 = manager.toggle_pause(1000.1)
        assert result2 is False
        assert manager.is_paused  # Still paused

        # Toggle after cooldown should work
        result3 = manager.toggle_pause(1000.6)
        assert result3 is True
        assert not manager.is_paused

    def test_pause_duration_calculation(self):
        """Test pause duration calculations."""
        manager = PauseManager(cooldown_ms=0)

        # Pause for 2 seconds
        manager.pause(1000.0)
        manager.resume(1002.0)

        assert manager.get_total_pause_duration() == 2.0

        # Pause for another 3 seconds
        manager.pause(1010.0)
        manager.resume(1013.0)

        assert manager.get_total_pause_duration() == 5.0

    def test_current_pause_duration(self):
        """Test current pause duration while paused."""
        manager = PauseManager(cooldown_ms=0)

        # Start pause
        manager.pause(1000.0)

        # Check current pause duration
        with patch("time.time", return_value=1002.0):
            stats = manager.get_pause_stats()
            assert stats.current_pause_duration == 2.0
            assert stats.total_pause_duration == 0.0  # Not yet accumulated

        # Resume
        manager.resume(1003.0)

        # Check after resume
        stats = manager.get_pause_stats()
        assert stats.current_pause_duration == 0.0
        assert stats.total_pause_duration == 3.0

    def test_game_time_calculation(self):
        """Test pause-aware game time calculation."""
        manager = PauseManager(cooldown_ms=0)
        start_time = 1000.0

        # No pause yet - game time equals real time
        game_time = manager.calculate_game_time(start_time, 1010.0)
        assert game_time == 10.0

        # Pause for 2 seconds
        manager.pause(1010.0)
        manager.resume(1012.0)

        # Game time should exclude pause duration
        game_time = manager.calculate_game_time(start_time, 1020.0)
        assert game_time == 18.0  # 20 - 2 (pause)

        # Multiple pauses
        manager.pause(1020.0)
        manager.resume(1025.0)  # Another 5 second pause

        game_time = manager.calculate_game_time(start_time, 1030.0)
        assert game_time == 23.0  # 30 - 7 (total pause)

    def test_game_time_while_paused(self):
        """Test game time calculation while currently paused."""
        manager = PauseManager(cooldown_ms=0)
        start_time = 1000.0

        # Pause at 10 seconds
        manager.pause(1010.0)

        # Game time should exclude current pause
        game_time = manager.calculate_game_time(start_time, 1015.0)
        assert game_time == 10.0  # Should stay at pause start time

        # Resume and check
        manager.resume(1020.0)
        game_time = manager.calculate_game_time(start_time, 1025.0)
        assert game_time == 15.0  # 25 - 10 (pause duration)

    def test_pause_count_tracking(self):
        """Test pause count tracking."""
        manager = PauseManager(cooldown_ms=0)

        assert manager.get_pause_stats().pause_count == 0

        # First pause
        manager.pause(1000.0)
        assert manager.get_pause_stats().pause_count == 1

        manager.resume(1001.0)
        assert manager.get_pause_stats().pause_count == 1

        # Second pause
        manager.pause(1002.0)
        assert manager.get_pause_stats().pause_count == 2

        manager.resume(1003.0)
        assert manager.get_pause_stats().pause_count == 2

    def test_reset_functionality(self):
        """Test reset method."""
        manager = PauseManager(cooldown_ms=0)

        # Create some pause state
        manager.pause(1000.0)
        manager.resume(1005.0)
        manager.pause(1010.0)

        stats_before = manager.get_pause_stats()
        assert stats_before.pause_count == 2
        assert stats_before.total_pause_duration == 5.0
        assert stats_before.is_paused

        # Reset
        manager.reset()

        # Check reset state
        assert not manager.is_paused
        assert manager.get_total_pause_duration() == 0.0

        stats_after = manager.get_pause_stats()
        assert stats_after.pause_count == 0
        assert stats_after.total_pause_duration == 0.0
        assert not stats_after.is_paused

    def test_negative_game_time_prevention(self):
        """Test that game time never goes negative."""
        manager = PauseManager(cooldown_ms=0)
        start_time = 1000.0

        # Create a situation where pause time exceeds total time
        manager.pause(1000.0)
        manager.resume(1010.0)  # 10 second pause

        # Calculate game time at a point before pause end
        game_time = manager.calculate_game_time(start_time, 1005.0)
        assert game_time >= 0.0

    def test_pause_stats_string_representation(self):
        """Test string representations."""
        manager = PauseManager()

        # Test PauseStats __str__
        stats = manager.get_pause_stats()
        stats_str = str(stats)
        assert "PauseStats" in stats_str
        assert "paused=False" in stats_str

        # Test PauseManager __str__
        manager_str = str(manager)
        assert "PauseManager" in manager_str
        assert "paused=False" in manager_str

    def test_default_time_usage(self):
        """Test that methods work with default time.time() when no time provided."""
        manager = PauseManager(cooldown_ms=0)

        # Use itertools.cycle to provide repeating values that won't cause StopIteration
        from itertools import cycle

        with patch("time.time") as mock_time:
            # Provide specific time values for the test logic
            # 1000.0 - pause time, 1000.0 - calculate game time (same as pause start)
            # 1002.0 - resume time, and extra values for logging calls
            time_values = cycle([1000.0, 1000.0, 1002.0, 1003.0, 1004.0])
            mock_time.side_effect = lambda: next(time_values)

            # Toggle pause (uses time.time() -> 1000.0)
            result = manager.toggle_pause()
            assert result is True
            assert manager.is_paused

            # Calculate game time while paused (uses time.time() -> 1000.0)
            # Since current_time == pause_start_time, no time has passed
            game_time = manager.calculate_game_time(1000.0)
            assert game_time == 0.0  # Paused immediately, so no game time elapsed

            # Resume (uses time.time() -> 1002.0, logging may use 1003.0, 1004.0, etc.)
            result = manager.toggle_pause()
            assert result is True
            assert not manager.is_paused


class TestPauseManagerIntegration:
    """Integration tests for PauseManager with realistic scenarios."""

    def test_realistic_gaming_session(self):
        """Test a realistic gaming session with multiple pauses."""
        manager = PauseManager(cooldown_ms=200)
        session_start = 1000.0

        # Game starts
        current_time = session_start

        # Play for 30 seconds
        current_time += 30
        game_time = manager.calculate_game_time(session_start, current_time)
        assert game_time == 30.0

        # Pause for 5 seconds (phone call)
        manager.pause(current_time)
        current_time += 5
        game_time = manager.calculate_game_time(session_start, current_time)
        assert game_time == 30.0  # Game time frozen

        # Resume and play for 20 seconds
        manager.resume(current_time)
        current_time += 20
        game_time = manager.calculate_game_time(session_start, current_time)
        assert game_time == 50.0  # 30 + 20, excluding 5s pause

        # Quick pause/resume (bathroom break - 2 minutes)
        manager.pause(current_time)
        current_time += 120
        manager.resume(current_time)

        # Play for another 10 seconds
        current_time += 10
        game_time = manager.calculate_game_time(session_start, current_time)
        assert game_time == 60.0  # 30 + 20 + 10, excluding both pauses

        # Check final stats
        stats = manager.get_pause_stats()
        assert stats.pause_count == 2
        assert stats.total_pause_duration == 125.0  # 5 + 120
        assert not stats.is_paused

    def test_cooldown_behavior_in_practice(self):
        """Test cooldown behavior in practical scenarios."""
        manager = PauseManager(cooldown_ms=300)

        # Rapid key presses (user mashing pause key)
        times = [1000.0, 1000.1, 1000.15, 1000.2, 1000.35, 1000.4]
        results = []

        for t in times:
            results.append(manager.toggle_pause(t))

        # Only first and fifth toggles should succeed (300ms cooldown)
        expected = [True, False, False, False, True, False]
        assert results == expected

        # Final state should be paused (first toggle) then resumed (fifth toggle)
        assert not manager.is_paused

    def test_error_recovery_scenarios(self):
        """Test error recovery and edge cases."""
        manager = PauseManager(cooldown_ms=0)

        # Simulate missing pause start time (shouldn't happen in practice)
        manager._is_paused = True
        manager._pause_start_time = None

        # Resume should handle gracefully
        result = manager.resume(1000.0)
        assert result is True
        assert not manager.is_paused

        # Game time calculation with malformed state
        manager._total_paused_time = 0.0
        game_time = manager.calculate_game_time(1000.0, 1010.0)
        assert game_time == 10.0
