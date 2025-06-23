#!/usr/bin/env python3
"""
State Management System Demo

This script demonstrates the basic usage of the Thunder Fighter state management system.
It shows how to create states, manage transitions, and handle events.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from thunder_fighter.state import (
    GameStateManager,
    StateMachine,
    StateFactory
)


class DemoGame:
    """Simple demo game class to demonstrate state management."""
    
    def __init__(self):
        self.running = True
        self.score = 0
        self.level = 1
        
    def spawn_enemy(self, game_time, game_level):
        print(f"Spawning enemy at time {game_time:.1f}, level {game_level}")
        
    def spawn_boss(self):
        print("Boss spawned!")
        
    def spawn_random_item(self, game_time):
        print(f"Item spawned at time {game_time:.1f}")


def demo_basic_state_management():
    """Demonstrate basic state management functionality."""
    print("=== Basic State Management Demo ===")
    
    # Create state manager
    state_manager = GameStateManager()
    
    # Show initial state
    print(f"Initial state: {state_manager.get_state().current_state}")
    
    # Change states
    state_manager.set_current_state("playing")
    print(f"After starting game: {state_manager.get_state().current_state}")
    
    # Pause and resume
    state_manager.pause_game()
    print(f"After pausing: {state_manager.get_state().current_state}")
    
    state_manager.resume_game()
    print(f"After resuming: {state_manager.get_state().current_state}")
    
    # Level up
    state_manager.level_up(2)
    print(f"After level up: {state_manager.get_state().current_state}")
    print(f"Current level: {state_manager.get_state().level}")
    
    # End game
    state_manager.end_game(victory=True)
    print(f"After victory: {state_manager.get_state().current_state}")
    
    print()


def demo_state_machine():
    """Demonstrate state machine functionality."""
    print("=== State Machine Demo ===")
    
    # Create demo game instance
    game = DemoGame()
    
    # Create state machine
    state_machine = StateMachine()
    
    # Create and add states
    states = StateFactory.create_all_states(game)
    for state in states:
        state_machine.add_state(state)
    
    print(f"Available states: {state_machine.get_state_names()}")
    
    # Set initial state
    state_machine.set_current_state("playing")
    print(f"Current state: {state_machine.get_current_state_name()}")
    
    # Transition to different states
    state_machine.transition_to("paused")
    print(f"After pause: {state_machine.get_current_state_name()}")
    
    state_machine.transition_to("playing")
    print(f"After resume: {state_machine.get_current_state_name()}")
    
    state_machine.transition_to("level_transition")
    print(f"During level transition: {state_machine.get_current_state_name()}")
    
    # Simulate time passing for level transition
    import time
    print("Waiting for level transition to complete...")
    time.sleep(0.1)  # Short wait for demo
    
    # Update state machine (would normally timeout the transition)
    state_machine.update(3.5)  # Simulate 3.5 seconds
    print(f"After transition timeout: {state_machine.get_current_state_name()}")
    
    print()


def demo_state_listeners():
    """Demonstrate state change listeners."""
    print("=== State Listeners Demo ===")
    
    state_manager = GameStateManager()
    
    # Define callback functions
    def on_victory(old_state, new_state):
        print(f"🎉 Victory achieved! Transitioned from {old_state} to {new_state}")
    
    def on_game_over(old_state, new_state):
        print(f"💀 Game over! Transitioned from {old_state} to {new_state}")
    
    def on_any_state_change(old_state, new_state):
        print(f"📝 State change logged: {old_state} -> {new_state}")
    
    # Add listeners
    state_manager.add_state_listener("victory", on_victory)
    state_manager.add_state_listener("game_over", on_game_over)
    
    # Start game and trigger state changes
    state_manager.set_current_state("playing")
    
    # Trigger victory
    state_manager.end_game(victory=True)
    
    # Reset and trigger game over
    state_manager.start_game()
    state_manager.end_game(victory=False)
    
    print()


def demo_state_queries():
    """Demonstrate state query methods."""
    print("=== State Queries Demo ===")
    
    state_manager = GameStateManager()
    
    # Test different states
    states_to_test = ["playing", "paused", "game_over", "victory"]
    
    for state_name in states_to_test:
        state_manager.set_current_state(state_name)
        
        print(f"\nTesting state: {state_name}")
        print(f"  is_playing(): {state_manager.is_playing()}")
        print(f"  is_paused(): {state_manager.is_paused()}")
        print(f"  is_game_over(): {state_manager.is_game_over()}")
        print(f"  is_victory(): {state_manager.is_victory()}")
        print(f"  should_update_game_logic(): {state_manager.should_update_game_logic()}")
        print(f"  should_spawn_enemies(): {state_manager.should_spawn_enemies()}")
    
    print()


def demo_state_data():
    """Demonstrate state data management."""
    print("=== State Data Demo ===")
    
    state_manager = GameStateManager()
    
    # Update player stats
    state_manager.update_player_stats(
        health=75,
        bullet_paths=3,
        speed=8,
        wingmen=2
    )
    
    # Update boss stats
    state_manager.update_boss_stats(
        active=True,
        health=800,
        max_health=1000,
        level=3,
        mode="aggressive"
    )
    
    # Update game stats
    state_manager.update_score(15000)
    state_manager.update_enemy_count(8, 12)
    
    # Get state info
    info = state_manager.get_state_info()
    
    print("Current game state:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print()


def main():
    """Run all demos."""
    print("Thunder Fighter State Management System Demo")
    print("=" * 50)
    print()
    
    try:
        demo_basic_state_management()
        demo_state_machine()
        demo_state_listeners()
        demo_state_queries()
        demo_state_data()
        
        print("✅ All demos completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 