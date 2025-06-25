"""
Tests for Game State Management

This module contains tests for the GameState and GameStateManager classes.
"""

import pytest
import time
from unittest.mock import Mock, patch
from thunder_fighter.state.game_state import GameState, GameStateManager


class TestGameState:
    """Tests for the GameState class."""
    
    def test_game_state_initialization(self):
        """Test that GameState initializes with correct default values."""
        state = GameState()
        
        assert state.running is True
        assert state.paused is False
        assert state.current_state == "menu"
        assert state.level == 1
        assert state.score == 0
        assert state.player_health == 100
        assert state.player_max_health == 100
        assert state.boss_active is False
        assert state.game_won is False
        assert state.game_over is False
    
    def test_update_game_time(self):
        """Test game time update functionality."""
        state = GameState()
        state.current_state = "playing"
        state.paused = False
        
        # Mock time to control the test
        with patch('time.time', return_value=100.0):
            state.game_start_time = 40.0  # 60 seconds ago
            state.update_game_time()
            
            # Should be 1 minute (60 seconds / 60)
            assert state.game_time == 1.0
    
    def test_update_game_time_when_paused(self):
        """Test that game time doesn't update when paused."""
        state = GameState()
        state.current_state = "playing"
        state.paused = True
        
        original_time = state.game_time
        state.update_game_time()
        
        # Time should not change when paused
        assert state.game_time == original_time
    
    def test_reset_for_new_game(self):
        """Test resetting state for a new game."""
        state = GameState()
        
        # Modify some values
        state.running = False
        state.level = 5
        state.score = 1000
        state.player_health = 50
        state.game_won = True
        state.boss_active = True
        
        # Reset
        state.reset_for_new_game()
        
        # Check that values are reset
        assert state.running is True
        assert state.current_state == "playing"
        assert state.level == 1
        assert state.score == 0
        assert state.player_health == 100
        assert state.game_won is False
        assert state.boss_active is False


class TestGameStateManager:
    """Tests for the GameStateManager class."""
    
    def test_initialization(self):
        """Test GameStateManager initialization."""
        manager = GameStateManager()
        
        assert manager.get_state() is not None
        assert isinstance(manager.get_state(), GameState)
        assert manager._state_listeners == {}
        assert manager._previous_state is None
    
    def test_set_current_state(self):
        """Test setting the current state."""
        manager = GameStateManager()
        
        # Test state change
        manager.set_current_state("playing")
        assert manager.get_state().current_state == "playing"
        
        # Test that the same state doesn't trigger a change
        with patch.object(manager, '_notify_state_change') as mock_notify:
            manager.set_current_state("playing")
            mock_notify.assert_not_called()
    
    def test_pause_and_resume_game(self):
        """Test pausing and resuming the game."""
        manager = GameStateManager()
        manager.set_current_state("playing")
        
        # Pause the game
        manager.pause_game()
        assert manager.get_state().paused is True
        assert manager.get_state().current_state == "paused"
        
        # Resume the game
        manager.resume_game()
        assert manager.get_state().paused is False
        assert manager.get_state().current_state == "playing"
    
    def test_start_game(self):
        """Test starting a new game."""
        manager = GameStateManager()
        
        # Modify state first
        state = manager.get_state()
        state.level = 5
        state.score = 1000
        
        # Start new game
        manager.start_game()
        
        # Check that state is reset
        assert state.level == 1
        assert state.score == 0
        assert state.current_state == "playing"
    
    def test_end_game_victory(self):
        """Test ending game with victory."""
        manager = GameStateManager()
        
        manager.end_game(victory=True)
        
        state = manager.get_state()
        assert state.game_won is True
        assert state.current_state == "victory"
    
    def test_end_game_defeat(self):
        """Test ending game with defeat."""
        manager = GameStateManager()
        
        manager.end_game(victory=False)
        
        state = manager.get_state()
        assert state.game_over is True
        assert state.current_state == "game_over"
    
    def test_level_up(self):
        """Test leveling up."""
        manager = GameStateManager()
        
        manager.level_up(3)
        
        state = manager.get_state()
        assert state.level == 3
        assert state.level_change_active is True
        assert state.current_state == "level_transition"
        
        # Test that level doesn't go backwards
        manager.level_up(2)
        assert state.level == 3  # Should remain 3
    
    def test_update_player_stats(self):
        """Test updating player statistics."""
        manager = GameStateManager()
        
        manager.update_player_stats(
            health=80,
            bullet_paths=3,
            speed=7
        )
        
        state = manager.get_state()
        assert state.player_health == 80
        assert state.player_bullet_paths == 3
        assert state.player_speed == 7
    
    def test_update_boss_stats(self):
        """Test updating boss statistics."""
        manager = GameStateManager()
        
        manager.update_boss_stats(
            active=True,
            health=500,
            max_health=1000,
            level=2
        )
        
        state = manager.get_state()
        assert state.boss_active is True
        assert state.boss_health == 500
        assert state.boss_max_health == 1000
        assert state.boss_level == 2
    
    def test_state_queries(self):
        """Test state query methods."""
        manager = GameStateManager()
        
        # Test playing state
        manager.set_current_state("playing")
        assert manager.is_playing() is True
        assert manager.is_paused() is False
        assert manager.is_game_over() is False
        assert manager.is_victory() is False
        
        # Test paused state
        manager.set_current_state("paused")
        assert manager.is_playing() is False
        assert manager.is_paused() is True
        
        # Test game over state
        manager.set_current_state("game_over")
        assert manager.is_game_over() is True
        
        # Test victory state
        manager.set_current_state("victory")
        assert manager.is_victory() is True
    
    def test_should_update_game_logic(self):
        """Test game logic update conditions."""
        manager = GameStateManager()
        
        # Should update during playing
        manager.set_current_state("playing")
        assert manager.should_update_game_logic() is True
        
        # Should update during level transition
        manager.set_current_state("level_transition")
        assert manager.should_update_game_logic() is True
        
        # Should not update when paused
        manager.set_current_state("paused")
        assert manager.should_update_game_logic() is False
        
        # Should not update when game over
        manager.set_current_state("game_over")
        assert manager.should_update_game_logic() is False
    
    def test_should_spawn_conditions(self):
        """Test spawning condition methods."""
        manager = GameStateManager()
        manager.set_current_state("playing")
        
        # Should spawn when playing and not won
        assert manager.should_spawn_enemies() is True
        assert manager.should_spawn_items() is True
        
        # Should not spawn when game is won
        manager.get_state().game_won = True
        assert manager.should_spawn_enemies() is False
        assert manager.should_spawn_items() is False
        
        # Should not spawn when not playing
        manager.get_state().game_won = False
        manager.set_current_state("paused")
        assert manager.should_spawn_enemies() is False
        assert manager.should_spawn_items() is False
    
    def test_state_listeners(self):
        """Test state change listeners."""
        manager = GameStateManager()
        
        # Create mock callbacks
        callback1 = Mock()
        callback2 = Mock()
        
        # Add listeners
        manager.add_state_listener("playing", callback1)
        manager.add_state_listener("playing", callback2)
        
        # Trigger state change
        manager.set_current_state("playing")
        
        # Check that callbacks were called
        callback1.assert_called_once()
        callback2.assert_called_once()
        
        # Remove a listener
        manager.remove_state_listener("playing", callback1)
        
        # Reset mocks
        callback1.reset_mock()
        callback2.reset_mock()
        
        # Trigger another state change
        manager.set_current_state("paused")
        manager.set_current_state("playing")
        
        # Only callback2 should be called
        callback1.assert_not_called()
        callback2.assert_called_once()
    
    def test_update_with_level_transition_timeout(self):
        """Test that level transition times out properly."""
        manager = GameStateManager()
        
        # Set up level transition
        manager.level_up(2)
        assert manager.get_state().current_state == "level_transition"
        
        # Mock time to simulate timeout
        with patch('time.time', return_value=manager.get_state().level_change_timer + 4.0):
            manager.update()
            
            # Should transition back to playing
            assert manager.get_state().current_state == "playing"
            assert manager.get_state().level_change_active is False
    
    def test_get_state_info(self):
        """Test getting state information dictionary."""
        manager = GameStateManager()
        
        # Set some state values
        state = manager.get_state()
        state.level = 3
        state.score = 1500
        state.player_health = 75
        
        info = manager.get_state_info()
        
        assert info['level'] == 3
        assert info['score'] == 1500
        assert info['player_health'] == 75
        assert 'current_state' in info
        assert 'running' in info 