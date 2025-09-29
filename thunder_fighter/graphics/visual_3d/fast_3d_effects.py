"""
Fast and dramatic 3D visual effects using optimized Pygame operations.

This module provides highly visible 3D effects with excellent performance,
using Pygame's native functions instead of pixel-by-pixel operations.
"""

import pygame
from typing import Tuple
from thunder_fighter.utils.logger import logger


class Fast3DEffects:
    """Fast 3D effects with dramatic visual impact using native Pygame."""

    @staticmethod
    def create_player_3d_effect(base_surface: pygame.Surface) -> pygame.Surface:
        """
        Create fast, dramatic 3D effect for player ship.

        Args:
            base_surface: Original player surface

        Returns:
            Enhanced surface with visible 3D effects
        """
        try:
            width, height = base_surface.get_size()

            # Create result surface with extra space for effects
            result_width = width + 20  # Extra space for shadow and glow
            result_height = height + 20
            result = pygame.Surface((result_width, result_height), pygame.SRCALPHA)

            # 1. CREATE DRAMATIC DROP SHADOW (dark and offset)
            shadow = base_surface.copy()
            shadow.fill((30, 30, 60, 0), special_flags=pygame.BLEND_RGBA_MULT)  # Dark blue shadow
            shadow.set_alpha(200)  # Strong shadow visibility

            # Draw multiple shadow layers for soft effect
            for i in range(3, 0, -1):
                shadow_copy = shadow.copy()
                shadow_copy.set_alpha(100 - i * 20)
                result.blit(shadow_copy, (8 + i, 8 + i))

            # 2. ADD INNER BEVEL/3D EDGE EFFECT
            # Create highlight version for top-left edges
            highlight = base_surface.copy()
            highlight.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_ADD)
            highlight.set_alpha(120)

            # Create shadow version for bottom-right edges
            edge_shadow = base_surface.copy()
            edge_shadow.fill((0, 0, 100, 0), special_flags=pygame.BLEND_RGBA_SUB)
            edge_shadow.set_alpha(100)

            # Apply edge effects with slight offsets
            result.blit(highlight, (4, 4))  # Top-left highlight
            result.blit(edge_shadow, (6, 6))  # Bottom-right shadow

            # 3. ADD METALLIC SHEEN
            # Create gradient overlay using vertical lines
            sheen = pygame.Surface((width, height), pygame.SRCALPHA)
            for y in range(height):
                # Metallic gradient from bright to dark
                brightness = int(255 - (y / height) * 200)
                color = (brightness, brightness, min(255, brightness + 50), 30)
                pygame.draw.line(sheen, color, (0, y), (width, y), 1)

            # 4. ADD ENGINE GLOW
            # Create bright orange glow at bottom
            glow_color = (255, 150, 50)
            glow_y = height - 10

            # Draw multiple glow circles for engine effect
            for i in range(3):
                alpha = 150 - i * 40
                glow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*glow_color, alpha), (10, 10), 8 - i)
                result.blit(glow_surf, (width // 3 - 5, glow_y))
                result.blit(glow_surf, (2 * width // 3 - 5, glow_y))

            # 5. APPLY MAIN SHIP WITH METALLIC SHEEN
            main_ship = base_surface.copy()
            main_ship.blit(sheen, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            result.blit(main_ship, (5, 5))

            # 6. ADD OUTER GLOW/ENERGY FIELD
            # Create subtle blue energy field around ship
            for i in range(2, 0, -1):
                glow = base_surface.copy()
                glow.fill((100, 150, 255, 0), special_flags=pygame.BLEND_RGBA_ADD)
                glow.set_alpha(40 - i * 10)
                result.blit(glow, (5 - i, 5 - i))
                result.blit(glow, (5 + i, 5 + i))

            return result

        except Exception as e:
            logger.error(f"Error creating player 3D effect: {e}")
            return base_surface

    @staticmethod
    def create_enemy_3d_effect(base_surface: pygame.Surface, level: int = 0) -> pygame.Surface:
        """
        Create fast, dramatic 3D effect for enemy ship.

        Args:
            base_surface: Original enemy surface
            level: Enemy level for effect variation

        Returns:
            Enhanced surface with organic 3D effects
        """
        try:
            width, height = base_surface.get_size()

            # Create result surface
            result_width = width + 16
            result_height = height + 16
            result = pygame.Surface((result_width, result_height), pygame.SRCALPHA)

            # 1. CREATE ORGANIC SHADOW (reddish-dark)
            shadow = base_surface.copy()
            shadow_color = (60, 20, 20, 0)  # Dark red for organic feel
            shadow.fill(shadow_color, special_flags=pygame.BLEND_RGBA_MULT)
            shadow.set_alpha(180)

            # Multiple shadow layers
            for i in range(2, 0, -1):
                shadow_copy = shadow.copy()
                shadow_copy.set_alpha(120 - i * 30)
                result.blit(shadow_copy, (6 + i, 6 + i))

            # 2. ORGANIC TEXTURE OVERLAY
            # Create rough organic surface texture
            texture = pygame.Surface((width, height), pygame.SRCALPHA)

            # Add random organic spots for texture
            import random
            random.seed(level)  # Consistent texture per level
            for _ in range(10 + level):
                x = random.randint(0, width - 5)
                y = random.randint(0, height - 5)
                spot_color = (random.randint(100, 150), random.randint(20, 50), random.randint(20, 50), 50)
                pygame.draw.circle(texture, spot_color, (x, y), random.randint(1, 3))

            # 3. BIO-LUMINESCENT HIGHLIGHTS
            # Create organic glow spots
            bio_glow = pygame.Surface((width, height), pygame.SRCALPHA)

            # Center bio-core glow
            core_color = (200 + level * 5, 60, 60, 100)
            pygame.draw.circle(bio_glow, core_color, (width // 2, height // 3), 5)

            # Side bio-panels
            panel_color = (180, 40, 40, 80)
            pygame.draw.circle(bio_glow, panel_color, (width // 4, height // 2), 3)
            pygame.draw.circle(bio_glow, panel_color, (3 * width // 4, height // 2), 3)

            # 4. APPLY MAIN ENEMY WITH ORGANIC EFFECTS
            main_enemy = base_surface.copy()

            # Apply texture
            main_enemy.blit(texture, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            # Apply bio-glow
            main_enemy.blit(bio_glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            # Add organic edge darkening
            edge_dark = base_surface.copy()
            edge_dark.fill((50, 0, 0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            edge_dark.set_alpha(80)
            main_enemy.blit(edge_dark, (1, 1))

            result.blit(main_enemy, (4, 4))

            # 5. HIGH LEVEL ENEMY EFFECTS
            if level >= 5:
                # Add pulsing bio-energy field
                for i in range(2, 0, -1):
                    energy = base_surface.copy()
                    energy.fill((255, 50 + level * 10, 50, 0), special_flags=pygame.BLEND_RGBA_ADD)
                    energy.set_alpha(50 - i * 15)
                    result.blit(energy, (4 - i, 4 - i))
                    result.blit(energy, (4 + i, 4 + i))

            return result

        except Exception as e:
            logger.error(f"Error creating enemy 3D effect: {e}")
            return base_surface


# Singleton instance
_fast_3d = None


def get_fast_3d() -> Fast3DEffects:
    """Get global Fast3D instance."""
    global _fast_3d
    if _fast_3d is None:
        _fast_3d = Fast3DEffects()
    return _fast_3d