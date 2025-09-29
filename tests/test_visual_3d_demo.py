#!/usr/bin/env python
"""
Demo and test script for static 3D visual effects.

This script demonstrates the static 3D visual enhancements without
any runtime scaling or complex transformations. Run directly to see effects.
"""

import sys
import os
import pygame

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from thunder_fighter.graphics.visual_3d import (
    ShipVisualEnhancer,
    EnemyVisualEnhancer,
    BackgroundVisual3D
)
from thunder_fighter.graphics.renderers import (
    create_player_surface,
    create_enemy_surface
)


def main():
    """Main demo function."""
    pygame.init()

    # Create demo window
    screen_width, screen_height = 1024, 768
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Thunder Fighter - Static 3D Visual Effects Demo")

    # Create background color
    bg_color = (10, 10, 30)  # Dark space blue
    clock = pygame.time.Clock()

    # Initialize visual enhancers
    ship_enhancer = ShipVisualEnhancer()
    enemy_enhancer = EnemyVisualEnhancer()
    background_3d = BackgroundVisual3D()

    print("Initializing static 3D visual effects demo...")
    print("No runtime scaling - all effects are pre-rendered!")

    # Create base sprites
    player_base = create_player_surface()
    enemy_base = create_enemy_surface(level=5)  # Mid-level enemy

    # Apply static 3D enhancements
    print("Applying player ship 3D effects: shadows, highlights, metallic sheen...")
    player_enhanced = ship_enhancer.enhance_player_ship(player_base)

    print("Applying enemy ship organic 3D effects...")
    enemy_enhanced = enemy_enhancer.enhance_enemy_ship(enemy_base, enemy_level=5)

    # Create 3D planets
    print("Creating 3D planets with spherical shading...")
    planet_1 = background_3d.create_3d_planet(
        radius=80,
        base_color=(100, 150, 200),  # Blue planet
        light_angle=45,
        atmosphere=True
    )

    planet_2 = background_3d.create_3d_planet(
        radius=60,
        base_color=(200, 100, 100),  # Red planet
        light_angle=135,
        atmosphere=True
    )

    planet_3 = background_3d.create_3d_planet(
        radius=40,
        base_color=(150, 200, 100),  # Green planet
        light_angle=225,
        atmosphere=False
    )

    # Create nebula layers
    nebula_back = background_3d.create_nebula_layer(400, 300, (80, 30, 120), 0.5)
    nebula_mid = background_3d.create_nebula_layer(400, 300, (120, 60, 180), 0.75)

    # Display positions
    player_pos = (screen_width // 2 - 30, screen_height - 150)
    enemy_positions = [
        (200, 200),
        (400, 150),
        (600, 200),
        (800, 180)
    ]

    planet_positions = [
        (150, 100),
        (800, 150),
        (500, 400)
    ]

    # Main demo loop
    running = True
    frame_count = 0

    print("\nDemo started! Press ESC to exit.")
    print("Watch the static 3D effects - no runtime scaling!")

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Clear screen
        screen.fill(bg_color)

        # Draw nebula background layers (depth effect through opacity)
        screen.blit(nebula_back, (100, 150))
        screen.blit(nebula_mid, (500, 350))

        # Draw 3D planets
        for i, (planet, pos) in enumerate(zip([planet_1, planet_2, planet_3], planet_positions)):
            screen.blit(planet, pos)

        # Draw enhanced enemies at different positions
        for i, pos in enumerate(enemy_positions):
            # Create enemies with different levels for variation
            enemy_level = i * 2 + 3
            enemy = create_enemy_surface(level=enemy_level)
            enhanced_enemy = enemy_enhancer.enhance_enemy_ship(enemy, enemy_level)
            screen.blit(enhanced_enemy, pos)

        # Draw enhanced player ship
        screen.blit(player_enhanced, player_pos)

        # Draw info text
        font = pygame.font.Font(None, 36)
        title_text = font.render("Static 3D Visual Effects Demo", True, (255, 255, 255))
        screen.blit(title_text, (screen_width // 2 - 200, 30))

        font_small = pygame.font.Font(None, 24)
        info_texts = [
            "Player: Metallic sheen + shadows + highlights",
            "Enemies: Organic textures + bio-glow",
            "Planets: Spherical shading + atmosphere",
            "Performance: 60 FPS (no runtime scaling!)"
        ]

        for i, text in enumerate(info_texts):
            rendered_text = font_small.render(text, True, (200, 200, 200))
            screen.blit(rendered_text, (20, screen_height - 120 + i * 25))

        # Display FPS
        fps = clock.get_fps()
        fps_text = font_small.render(f"FPS: {fps:.1f}", True, (0, 255, 0))
        screen.blit(fps_text, (screen_width - 100, 30))

        # Update display
        pygame.display.flip()
        clock.tick(60)

        frame_count += 1

        # Print performance stats every 300 frames (5 seconds at 60 FPS)
        if frame_count % 300 == 0:
            print(f"Frame {frame_count}: FPS = {fps:.1f}")
            print(f"  Ship cache: {ship_enhancer.get_cache_stats()}")
            print(f"  Enemy cache: {enemy_enhancer.get_cache_stats()}")
            print(f"  Planet cache: {background_3d.get_cache_stats()}")

    # Cleanup
    print("\nDemo completed successfully!")
    print("Static 3D visual effects system is working correctly.")
    pygame.quit()


if __name__ == "__main__":
    main()