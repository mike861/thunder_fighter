"""
Tests for Boss Spawn Timing with Pause Handling

This module tests the boss spawn timing logic to ensure that pause time
is correctly excluded from boss spawn interval calculations, preventing
boss spawning inconsistencies during paused gameplay.
"""

import time
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import TYPE_CHECKING

from thunder_fighter.utils.pause_manager import PauseManager
from thunder_fighter.constants import BOSS_SPAWN_INTERVAL

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


class TestBossSpawnTimingWithPause:
    """Test boss spawn timing logic with pause handling."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.pause_manager = PauseManager()
        self.boss_spawn_timer = time.time()
        self.game_level = 2  # Boss spawning starts at level 2
        
    def test_boss_spawn_interval_without_pause(self):
        """Test boss spawn interval calculation without any pause."""
        # Simulate time passing without pause
        with patch('time.time') as mock_time:
            mock_time.return_value = self.boss_spawn_timer + BOSS_SPAWN_INTERVAL + 1
            
            elapsed_time = self.pause_manager.calculate_game_time(self.boss_spawn_timer)
            should_spawn = elapsed_time > BOSS_SPAWN_INTERVAL
            
            assert should_spawn, f"Boss should spawn after {BOSS_SPAWN_INTERVAL} seconds"
            assert elapsed_time == BOSS_SPAWN_INTERVAL + 1
            
    def test_boss_spawn_interval_with_pause(self):
        """Test boss spawn interval calculation with pause time excluded."""
        # Simulate normal gameplay for 10 seconds
        with patch('time.time') as mock_time:
            mock_time.return_value = self.boss_spawn_timer + 10
            
            elapsed_time = self.pause_manager.calculate_game_time(self.boss_spawn_timer)
            assert elapsed_time == 10, "Should have 10 seconds of game time"
            
            # Pause the game
            self.pause_manager.pause()
            
            # Simulate 20 seconds of pause time
            mock_time.return_value = self.boss_spawn_timer + 30
            
            elapsed_time = self.pause_manager.calculate_game_time(self.boss_spawn_timer)
            assert elapsed_time == 10, "Game time should not increase during pause"
            
            # Resume the game
            self.pause_manager.resume()
            
            # Simulate 25 more seconds of gameplay (total real time: 55 seconds)
            mock_time.return_value = self.boss_spawn_timer + 55
            
            elapsed_time = self.pause_manager.calculate_game_time(self.boss_spawn_timer)
            expected_game_time = 35  # 10 + 25 seconds, excluding 20 seconds of pause
            assert elapsed_time == expected_game_time
            
            # Check if boss should spawn
            should_spawn = elapsed_time > BOSS_SPAWN_INTERVAL
            assert should_spawn, f"Boss should spawn after {BOSS_SPAWN_INTERVAL} seconds of game time"
            
    def test_boss_spawn_interval_with_multiple_pauses(self):
        """Test boss spawn interval with multiple pause/resume cycles."""
        with patch('time.time') as mock_time:
            # Initial gameplay: 5 seconds
            mock_time.return_value = self.boss_spawn_timer + 5
            elapsed_time = self.pause_manager.calculate_game_time(self.boss_spawn_timer)
            assert elapsed_time == 5
            
            # First pause: 10 seconds
            self.pause_manager.pause()
            mock_time.return_value = self.boss_spawn_timer + 15
            elapsed_time = self.pause_manager.calculate_game_time(self.boss_spawn_timer)
            assert elapsed_time == 5, "Game time should not increase during first pause"
            
            # Resume and play: 10 more seconds
            self.pause_manager.resume()
            mock_time.return_value = self.boss_spawn_timer + 25
            elapsed_time = self.pause_manager.calculate_game_time(self.boss_spawn_timer)
            assert elapsed_time == 15, "Game time should be 5 + 10 = 15 seconds"
            
            # Second pause: 5 seconds
            self.pause_manager.pause()
            mock_time.return_value = self.boss_spawn_timer + 30
            elapsed_time = self.pause_manager.calculate_game_time(self.boss_spawn_timer)
            assert elapsed_time == 15, "Game time should not increase during second pause"
            
            # Resume and play: 20 more seconds
            self.pause_manager.resume()
            mock_time.return_value = self.boss_spawn_timer + 50
            elapsed_time = self.pause_manager.calculate_game_time(self.boss_spawn_timer)
            assert elapsed_time == 35, "Game time should be 15 + 20 = 35 seconds"
            
            # Check boss spawn condition
            should_spawn = elapsed_time > BOSS_SPAWN_INTERVAL
            assert should_spawn, f"Boss should spawn after {BOSS_SPAWN_INTERVAL} seconds of game time"
            
    def test_boss_spawn_timing_edge_cases(self):
        """Test edge cases for boss spawn timing."""
        with patch('time.time') as mock_time:
            # Test exactly at spawn interval
            mock_time.return_value = self.boss_spawn_timer + BOSS_SPAWN_INTERVAL
            elapsed_time = self.pause_manager.calculate_game_time(self.boss_spawn_timer)
            should_spawn = elapsed_time > BOSS_SPAWN_INTERVAL
            assert not should_spawn, "Boss should not spawn exactly at interval (> not >=)"
            
            # Test just over spawn interval
            mock_time.return_value = self.boss_spawn_timer + BOSS_SPAWN_INTERVAL + 0.1
            elapsed_time = self.pause_manager.calculate_game_time(self.boss_spawn_timer)
            should_spawn = elapsed_time > BOSS_SPAWN_INTERVAL
            assert should_spawn, "Boss should spawn just over interval"
            
    def test_boss_spawn_with_long_pause(self):
        """Test boss spawn timing with very long pause periods."""
        with patch('time.time') as mock_time:
            # Play for 5 seconds
            mock_time.return_value = self.boss_spawn_timer + 5
            elapsed_time = self.pause_manager.calculate_game_time(self.boss_spawn_timer)
            assert elapsed_time == 5
            
            # Pause for a very long time (2 minutes)
            self.pause_manager.pause()
            mock_time.return_value = self.boss_spawn_timer + 125  # 5 + 120 seconds
            elapsed_time = self.pause_manager.calculate_game_time(self.boss_spawn_timer)
            assert elapsed_time == 5, "Game time should not increase during long pause"
            
            # Resume and play for 26 more seconds
            self.pause_manager.resume()
            mock_time.return_value = self.boss_spawn_timer + 151  # 125 + 26 seconds
            elapsed_time = self.pause_manager.calculate_game_time(self.boss_spawn_timer)
            assert elapsed_time == 31, "Game time should be 5 + 26 = 31 seconds"
            
            # Boss should spawn (31 > 30)
            should_spawn = elapsed_time > BOSS_SPAWN_INTERVAL
            assert should_spawn, f"Boss should spawn after {BOSS_SPAWN_INTERVAL} seconds of game time"
            
    def test_boss_spawn_level_requirement(self):
        """Test that boss spawn level requirement is correctly enforced."""
        with patch('time.time') as mock_time:
            # Test level 1 (should not spawn boss)
            game_level = 1
            mock_time.return_value = self.boss_spawn_timer + BOSS_SPAWN_INTERVAL + 1
            elapsed_time = self.pause_manager.calculate_game_time(self.boss_spawn_timer)
            
            # Even if time condition is met, boss should not spawn at level 1
            should_spawn = game_level > 1 and elapsed_time > BOSS_SPAWN_INTERVAL
            assert not should_spawn, "Boss should not spawn at level 1"
            
            # Test level 2 (should spawn boss)
            game_level = 2
            should_spawn = game_level > 1 and elapsed_time > BOSS_SPAWN_INTERVAL
            assert should_spawn, "Boss should spawn at level 2 with sufficient time"
            
    def test_boss_spawn_interval_constant_validation(self):
        """Test that the boss spawn interval constant is reasonable."""
        assert BOSS_SPAWN_INTERVAL > 0, "Boss spawn interval should be positive"
        assert BOSS_SPAWN_INTERVAL <= 120, "Boss spawn interval should be reasonable (≤ 2 minutes)"
        assert isinstance(BOSS_SPAWN_INTERVAL, (int, float)), "Boss spawn interval should be numeric"


class TestBossSpawnTimingIntegration:
    """Integration tests for boss spawn timing in realistic scenarios."""
    
    def test_realistic_boss_spawn_scenario(self):
        """Test a realistic boss spawn scenario with multiple pause cycles."""
        pause_manager = PauseManager()
        boss_spawn_timer = 1000000000.0  # Fixed timestamp
        game_level = 3
        
        # Simulate realistic gameplay with pauses using fixed timestamps
        current_time = boss_spawn_timer
        
        # Play 5 seconds
        current_time += 5
        elapsed_time_1 = pause_manager.calculate_game_time(boss_spawn_timer, current_time)
        
        # Pause for 10 seconds
        pause_manager.pause(current_time)
        current_time += 10
        elapsed_time_2 = pause_manager.calculate_game_time(boss_spawn_timer, current_time)
        
        # Resume and play 15 seconds
        pause_manager.resume(current_time)
        current_time += 15
        elapsed_time_3 = pause_manager.calculate_game_time(boss_spawn_timer, current_time)
        
        # Pause for 5 seconds
        pause_manager.pause(current_time)
        current_time += 5
        elapsed_time_4 = pause_manager.calculate_game_time(boss_spawn_timer, current_time)
        
        # Resume and play 15 seconds
        pause_manager.resume(current_time)
        current_time += 15
        elapsed_time_5 = pause_manager.calculate_game_time(boss_spawn_timer, current_time)
        
        # Verify game time progression
        assert elapsed_time_1 == 5, "After 5 seconds of gameplay"
        assert elapsed_time_2 == 5, "Pause doesn't increase game time"
        assert elapsed_time_3 == 20, "5 + 15 seconds of gameplay"
        assert elapsed_time_4 == 20, "Pause doesn't increase game time"
        assert elapsed_time_5 == 35, "20 + 15 seconds of gameplay"
        
        # Final boss spawn check
        should_spawn = game_level > 1 and elapsed_time_5 > BOSS_SPAWN_INTERVAL
        
        assert should_spawn, f"Boss should spawn after {BOSS_SPAWN_INTERVAL} seconds of game time"
        assert elapsed_time_5 == 35, "Final game time should be 35 seconds"
            
    def test_boss_spawn_consistency_across_sessions(self):
        """Test boss spawn timing consistency across different game sessions."""
        for session in range(3):
            pause_manager = PauseManager()
            boss_spawn_timer = time.time()
            
            with patch('time.time') as mock_time:
                # Each session: 10 seconds play, 20 seconds pause, 25 seconds play
                mock_time.return_value = boss_spawn_timer + 10
                elapsed_time_1 = pause_manager.calculate_game_time(boss_spawn_timer)
                
                pause_manager.pause()
                mock_time.return_value = boss_spawn_timer + 30
                elapsed_time_2 = pause_manager.calculate_game_time(boss_spawn_timer)
                
                pause_manager.resume()
                mock_time.return_value = boss_spawn_timer + 55
                elapsed_time_3 = pause_manager.calculate_game_time(boss_spawn_timer)
                
                # All sessions should have consistent behavior
                assert elapsed_time_1 == 10, f"Session {session}: First checkpoint should be 10 seconds"
                assert elapsed_time_2 == 10, f"Session {session}: Pause should not increase game time"
                assert elapsed_time_3 == 35, f"Session {session}: Final time should be 35 seconds"
                
                should_spawn = elapsed_time_3 > BOSS_SPAWN_INTERVAL
                assert should_spawn, f"Session {session}: Boss should spawn consistently"


class TestBossSpawnTimingEdgeCases:
    """Test edge cases and error scenarios for boss spawn timing."""
    
    def test_boss_spawn_with_zero_game_time(self):
        """Test boss spawn timing when game time is zero."""
        pause_manager = PauseManager()
        boss_spawn_timer = time.time()
        
        with patch('time.time') as mock_time:
            mock_time.return_value = boss_spawn_timer
            
            elapsed_time = pause_manager.calculate_game_time(boss_spawn_timer)
            should_spawn = elapsed_time > BOSS_SPAWN_INTERVAL
            
            assert elapsed_time == 0, "Game time should be zero at start"
            assert not should_spawn, "Boss should not spawn with zero game time"
            
    def test_boss_spawn_with_negative_time_prevention(self):
        """Test that negative game time is prevented in boss spawn calculations."""
        pause_manager = PauseManager()
        
        # Use real time values instead of mocks for this test
        future_time = 1000000000.0  # Fixed timestamp
        boss_spawn_timer = future_time
        
        # Move time "backwards" (shouldn't happen in reality, but test protection)
        past_time = future_time - 10
        
        elapsed_time = pause_manager.calculate_game_time(boss_spawn_timer, past_time)
        assert elapsed_time >= 0, "Game time should never be negative"
            
    def test_boss_spawn_with_pause_before_game_start(self):
        """Test boss spawn timing when pause occurs before game properly starts."""
        pause_manager = PauseManager()
        
        # Use real time values for this test
        current_time = 1000000000.0  # Fixed timestamp
        
        # Pause immediately (before setting boss_spawn_timer)
        pause_manager.pause(current_time)
        
        # Set boss spawn timer after pause
        boss_spawn_timer = current_time
        
        # Resume and advance time
        pause_time = current_time + 5  # 5 seconds of pause
        pause_manager.resume(pause_time)
        final_time = pause_time + BOSS_SPAWN_INTERVAL + 1
        
        elapsed_time = pause_manager.calculate_game_time(boss_spawn_timer, final_time)
        should_spawn = elapsed_time > BOSS_SPAWN_INTERVAL
        
        assert should_spawn, "Boss should spawn normally even if pause occurred before timer set"
            
    def test_boss_spawn_with_rapid_pause_toggle(self):
        """Test boss spawn timing with rapid pause/resume cycles."""
        pause_manager = PauseManager(cooldown_ms=0)  # Disable cooldown for this test
        boss_spawn_timer = 1000000000.0  # Fixed timestamp
        current_time = boss_spawn_timer
        
        # Rapid pause/resume cycles
        for i in range(10):
            current_time += 1
            
            if i % 2 == 0:
                pause_manager.pause(current_time)
            else:
                pause_manager.resume(current_time)
                
        # Final resume and advance to spawn time
        if pause_manager.is_paused:
            pause_manager.resume(current_time)
        current_time += BOSS_SPAWN_INTERVAL
        
        elapsed_time = pause_manager.calculate_game_time(boss_spawn_timer, current_time)
        
        # Should have accumulated some game time despite rapid toggling
        assert elapsed_time > 0, "Some game time should have accumulated"
        assert elapsed_time < current_time - boss_spawn_timer, "Game time should be less than total time"
            
    def test_boss_spawn_constant_validation(self):
        """Test validation of boss spawn interval constant."""
        # Test that constant is properly imported and has expected value
        assert BOSS_SPAWN_INTERVAL == 30, "Boss spawn interval should be 30 seconds"
        
        # Test that it's a reasonable value for gameplay
        assert 10 <= BOSS_SPAWN_INTERVAL <= 300, "Boss spawn interval should be between 10 seconds and 5 minutes"
        
    def test_boss_spawn_game_level_boundaries(self):
        """Test boss spawn behavior at game level boundaries."""
        pause_manager = PauseManager()
        boss_spawn_timer = time.time()
        
        with patch('time.time') as mock_time:
            mock_time.return_value = boss_spawn_timer + BOSS_SPAWN_INTERVAL + 1
            elapsed_time = pause_manager.calculate_game_time(boss_spawn_timer)
            
            # Test level boundaries
            test_levels = [0, 1, 2, 3, 10, 100]
            for level in test_levels:
                should_spawn = level > 1 and elapsed_time > BOSS_SPAWN_INTERVAL
                expected = level > 1
                assert should_spawn == expected, f"Level {level}: expected {expected}, got {should_spawn}"
                
    def test_boss_spawn_timing_precision(self):
        """Test boss spawn timing with high precision time values."""
        pause_manager = PauseManager()
        boss_spawn_timer = time.time()
        
        with patch('time.time') as mock_time:
            # Test with microsecond precision
            mock_time.return_value = boss_spawn_timer + BOSS_SPAWN_INTERVAL + 0.000001
            
            elapsed_time = pause_manager.calculate_game_time(boss_spawn_timer)
            should_spawn = elapsed_time > BOSS_SPAWN_INTERVAL
            
            assert should_spawn, "Boss should spawn with microsecond precision over interval"
            
            # Test just under interval
            mock_time.return_value = boss_spawn_timer + BOSS_SPAWN_INTERVAL - 0.000001
            
            elapsed_time = pause_manager.calculate_game_time(boss_spawn_timer)
            should_spawn = elapsed_time > BOSS_SPAWN_INTERVAL
            
            assert not should_spawn, "Boss should not spawn just under interval"
            
    def test_boss_spawn_with_pause_manager_reset(self):
        """Test boss spawn timing when pause manager is reset mid-game."""
        pause_manager = PauseManager()
        boss_spawn_timer = time.time()
        
        with patch('time.time') as mock_time:
            # Play for some time
            mock_time.return_value = boss_spawn_timer + 10
            elapsed_time_1 = pause_manager.calculate_game_time(boss_spawn_timer)
            assert elapsed_time_1 == 10
            
            # Pause and advance time
            pause_manager.pause()
            mock_time.return_value = boss_spawn_timer + 20
            elapsed_time_2 = pause_manager.calculate_game_time(boss_spawn_timer)
            assert elapsed_time_2 == 10
            
            # Reset pause manager (simulating game restart)
            pause_manager.reset()
            
            # Continue from current time
            mock_time.return_value = boss_spawn_timer + 30
            elapsed_time_3 = pause_manager.calculate_game_time(boss_spawn_timer)
            
            # After reset, should calculate from start without pause consideration
            assert elapsed_time_3 == 30, "After reset, should calculate full time elapsed"
            
    def test_boss_spawn_with_system_clock_changes(self):
        """Test boss spawn timing resilience to system clock changes."""
        pause_manager = PauseManager()
        
        with patch('time.time') as mock_time:
            # Start time
            start_time = 1000000000  # Arbitrary timestamp
            mock_time.return_value = start_time
            boss_spawn_timer = start_time
            
            # Normal progression
            mock_time.return_value = start_time + 10
            elapsed_time_1 = pause_manager.calculate_game_time(boss_spawn_timer)
            assert elapsed_time_1 == 10
            
            # Simulate system clock jump (e.g., NTP sync, daylight saving)
            mock_time.return_value = start_time + 1000000  # Big jump forward
            elapsed_time_2 = pause_manager.calculate_game_time(boss_spawn_timer)
            
            # Should handle gracefully (though this would be a real edge case)
            assert elapsed_time_2 >= 10, "Should handle clock jumps gracefully"