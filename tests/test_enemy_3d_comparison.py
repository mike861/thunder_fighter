#!/usr/bin/env python
"""
Compare enemy 3D effects: Clean vs Original (red-tinted).

Shows side-by-side comparison of the two 3D effect methods.
"""

import os
import sys

import pygame

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from thunder_fighter.graphics.renderers import create_enemy_ship
from thunder_fighter.graphics.visual_3d.fast_3d_effects import Fast3DEffects


def main():
    """Main test function."""
    pygame.init()

    # Create window
    screen_width, screen_height = 1200, 800
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Enemy 3D Effects Comparison - Clean vs Original")

    bg_color = (10, 10, 20)
    clock = pygame.time.Clock()

    # Test levels
    test_levels = [0, 2, 5, 9]

    # Create enemy sprites with both effects
    enemy_data = []
    for level in test_levels:
        base_enemy = create_enemy_ship(level)

        # Clean effect (preserves colors)
        clean_effect = Fast3DEffects.create_enemy_3d_effect_clean(base_enemy, level)

        # Original effect (red-tinted)
        original_effect = Fast3DEffects.create_enemy_3d_effect(base_enemy, level)

        enemy_data.append(
            {
                "level": level,
                "base": base_enemy,
                "clean": clean_effect,
                "original": original_effect,
            }
        )
        print(
            f"✓ Created Level {level} - Base: {base_enemy.get_size()}, "
            f"Clean: {clean_effect.get_size()}, Original: {original_effect.get_size()}"
        )

    # Fonts
    font_title = pygame.font.Font(None, 48)
    font_subtitle = pygame.font.Font(None, 32)
    font_label = pygame.font.Font(None, 28)
    font_info = pygame.font.Font(None, 22)

    print("\n" + "=" * 70)
    print("ENEMY 3D EFFECTS COMPARISON TEST")
    print("=" * 70)
    print("Showing Clean (preserves PNG colors) vs Original (red-tinted)")
    print("Press ESC to exit")
    print("=" * 70 + "\n")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Clear
        screen.fill(bg_color)

        # Title
        title = font_title.render("Enemy 3D Effects Comparison", True, (255, 255, 255))
        title_rect = title.get_rect(centerx=screen_width // 2, y=20)
        screen.blit(title, title_rect)

        # Column headers
        y_header = 90
        base_label = font_subtitle.render("Original PNG", True, (150, 200, 255))
        base_rect = base_label.get_rect(centerx=300, y=y_header)
        screen.blit(base_label, base_rect)

        clean_label = font_subtitle.render("Clean 3D", True, (100, 255, 100))
        clean_rect = clean_label.get_rect(centerx=600, y=y_header)
        screen.blit(clean_label, clean_rect)

        original_label = font_subtitle.render("Original 3D (Red)", True, (255, 100, 100))
        original_rect = original_label.get_rect(centerx=900, y=y_header)
        screen.blit(original_label, original_rect)

        # Info text
        clean_info = font_info.render("Preserves PNG colors", True, (80, 200, 80))
        screen.blit(clean_info, (clean_rect.centerx - 80, y_header + 35))

        original_info = font_info.render("Adds red/orange tint", True, (200, 80, 80))
        screen.blit(original_info, (original_rect.centerx - 80, y_header + 35))

        # Draw enemies in rows
        y_start = 160
        y_spacing = 150

        for i, data in enumerate(enemy_data):
            y = y_start + i * y_spacing

            # Level label
            level_text = f"Level {data['level']}"
            level_label = font_label.render(level_text, True, (220, 220, 100))
            screen.blit(level_label, (50, y + 40))

            # Base PNG
            base_rect = data["base"].get_rect(center=(300, y + 50))
            screen.blit(data["base"], base_rect.topleft)
            pygame.draw.rect(screen, (80, 100, 120), base_rect.inflate(10, 10), 2)

            # Clean effect
            clean_rect = data["clean"].get_rect(center=(600, y + 50))
            screen.blit(data["clean"], clean_rect.topleft)
            pygame.draw.rect(screen, (50, 150, 50), clean_rect.inflate(10, 10), 2)

            # Original effect
            original_rect = data["original"].get_rect(center=(900, y + 50))
            screen.blit(data["original"], original_rect.topleft)
            pygame.draw.rect(screen, (150, 50, 50), original_rect.inflate(10, 10), 2)

            # Size info
            size_y = y + 110
            base_size = font_info.render(
                f"{data['base'].get_width()}x{data['base'].get_height()}", True, (150, 150, 150)
            )
            screen.blit(base_size, (300 - base_size.get_width() // 2, size_y))

            clean_size = font_info.render(
                f"{data['clean'].get_width()}x{data['clean'].get_height()}", True, (150, 150, 150)
            )
            screen.blit(clean_size, (600 - clean_size.get_width() // 2, size_y))

            original_size = font_info.render(
                f"{data['original'].get_width()}x{data['original'].get_height()}", True, (150, 150, 150)
            )
            screen.blit(original_size, (900 - original_size.get_width() // 2, size_y))

        # Bottom info
        info_y = screen_height - 80
        info_texts = [
            "Clean 3D: Neutral shadows & highlights - preserves original PNG colors",
            "Original 3D: Red/orange tinting - adds organic/alien feel",
        ]

        for idx, text in enumerate(info_texts):
            color = (100, 200, 100) if idx == 0 else (200, 100, 100)
            info_render = font_info.render(text, True, color)
            info_rect = info_render.get_rect(centerx=screen_width // 2, y=info_y + idx * 25)
            screen.blit(info_render, info_rect)

        # Controls
        controls = "Press ESC to exit"
        control_text = font_info.render(controls, True, (100, 120, 140))
        control_rect = control_text.get_rect(centerx=screen_width // 2, y=screen_height - 25)
        screen.blit(control_text, control_rect)

        # FPS
        fps = clock.get_fps()
        fps_text = font_info.render(f"FPS: {fps:.1f}", True, (100, 255, 100))
        screen.blit(fps_text, (screen_width - 100, 30))

        # Update
        pygame.display.flip()
        clock.tick(60)

    print("\n" + "=" * 70)
    print("Test completed!")
    print("=" * 70)

    pygame.quit()


if __name__ == "__main__":
    main()
