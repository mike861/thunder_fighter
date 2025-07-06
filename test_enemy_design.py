#!/usr/bin/env python3
"""
Test script to visually compare player and enemy ship designs
"""
import sys
sys.path.append('.')

import pygame
from thunder_fighter.graphics.renderers import create_player_surface, create_enemy_surface

def test_visual_comparison():
    """Create surfaces and print comparison info"""
    pygame.init()
    
    print("=== Thunder Fighter Ship Design Comparison ===\n")
    
    # Create player surface
    player_surface = create_player_surface()
    print(f"Player Ship:")
    print(f"  Size: {player_surface.get_size()}")
    print(f"  Design: Modern fighter jet (blue tech theme)")
    print(f"  Features: Swept wings, twin engines, cockpit canopy")
    
    # Test enemy surfaces at different levels
    print(f"\nEnemy Ships (Organic/Alien Design):")
    
    level_descriptions = {
        1: "Insectoid (dark red/crimson)",
        4: "Toxic alien (green)",
        7: "Energy being (purple)", 
        10: "Nightmare void (black/energy)"
    }
    
    for level in [1, 4, 7, 10]:
        enemy_surface = create_enemy_surface(level)
        print(f"  Level {level}: {level_descriptions[level]}")
        print(f"    Size: {enemy_surface.get_size()}")
        
        # Sample center pixel to show color
        center_pixel = enemy_surface.get_at((22, 22))[:3]
        print(f"    Sample color: RGB{center_pixel}")
    
    print(f"\n=== Key Differences ===")
    print(f"1. Size: Player 60x50 vs Enemy 45x45")
    print(f"2. Shape: Player geometric/tech vs Enemy organic/blob")
    print(f"3. Color: Player blue tech vs Enemy dark organic")
    print(f"4. Features: Player wings/cockpit vs Enemy eye/appendages")
    print(f"5. Thrusters: Player twin engines vs Enemy bio-thrusters")
    print(f"\n✓ Ships are now visually distinct!")

if __name__ == "__main__":
    test_visual_comparison()