#!/usr/bin/env python3
"""
Thunder Fighter - Refactored Version
A space shooting game with architectural improvements

This version uses:
- Centralized resource management
- Event-driven input handling
- Factory pattern for entity creation
- Decoupled UI system
- Event-driven game logic

Use arrow keys or WASD to control the aircraft movement, space key to shoot bullets.
"""

from thunder_fighter.game import RefactoredGame
from thunder_fighter.utils.logger import logger

def main():
    """Main entry point for the refactored game"""
    try:
        logger.info("Starting Thunder Fighter - Refactored Version")
        game = RefactoredGame()
        game.run()
    except KeyboardInterrupt:
        logger.info("Game interrupted by user")
    except Exception as e:
        logger.error(f"Game crashed with error: {e}", exc_info=True)
        raise
    finally:
        logger.info("Game ended")

if __name__ == "__main__":
    main() 