#!/usr/bin/env python3
"""
Thunder Fighter
A simple space shooting game

Use arrow keys to control the aircraft movement, space key to shoot bullets.
"""

from thunder_fighter.game import Game

def main():
    """Main entry point for the game"""
    game = Game()
    game.run()

if __name__ == "__main__":
    main() 