"""
Fast and dramatic 3D visual effects using optimized Pygame operations.

This module provides highly visible 3D effects with excellent performance,
using efficient Pygame operations with proper beveling and depth.
"""

import pygame

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
            result = pygame.Surface((width + 10, height + 10), pygame.SRCALPHA)

            # 1. STRONG DROP SHADOW
            # Create multiple shadow layers for depth
            for i in range(3, 0, -1):
                shadow = base_surface.copy()
                # Make shadow dark blue-black
                shadow.fill((0, 0, 30, 255), special_flags=pygame.BLEND_RGBA_MULT)
                shadow.set_alpha(150 - i * 30)
                result.blit(shadow, (5 + i, 5 + i))

            # 2. MAIN SHIP WITH EFFECTS
            main_ship = base_surface.copy()

            # 3. BEVELED EDGES - Top/Left highlight
            highlight = base_surface.copy()
            # Bright white highlight on top-left
            highlight.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_ADD)
            highlight.set_alpha(80)
            result.blit(highlight, (3, 3))

            # 4. BEVELED EDGES - Bottom/Right shadow
            edge_shadow = base_surface.copy()
            # Dark edge on bottom-right
            edge_shadow.fill((0, 0, 50, 0), special_flags=pygame.BLEND_RGBA_SUB)
            edge_shadow.set_alpha(100)
            result.blit(edge_shadow, (7, 7))

            # 5. METALLIC SHEEN
            # Create vertical gradient for metallic look
            metallic = pygame.Surface((width, height), pygame.SRCALPHA)
            for y in range(height):
                # Gradient from bright to dark
                brightness = int(220 - (y / height) * 150)
                color = (brightness, brightness, min(255, brightness + 30), 40)
                pygame.draw.line(metallic, color, (0, y), (width, y), 1)

            main_ship.blit(metallic, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            # 6. SPECULAR HIGHLIGHT (bright spot)
            specular = pygame.Surface((width, height), pygame.SRCALPHA)
            # Add bright white spot at top center (cockpit)
            pygame.draw.circle(specular, (255, 255, 255, 120), (width // 2, height // 3), 8)
            pygame.draw.circle(specular, (255, 255, 255, 80), (width // 2, height // 3), 12)
            main_ship.blit(specular, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            # 7. ENGINE GLOW
            engine = pygame.Surface((width, height), pygame.SRCALPHA)
            # Orange engine glow at bottom
            for i in range(3):
                alpha = 100 - i * 20
                pygame.draw.circle(engine, (255, 150, 0, alpha), (width // 3, height - 5), 6 - i)
                pygame.draw.circle(engine, (255, 150, 0, alpha), (2 * width // 3, height - 5), 6 - i)

            main_ship.blit(engine, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            # 8. Place main ship on result
            result.blit(main_ship, (5, 5))

            # 9. OUTER GLOW for visibility
            glow = base_surface.copy()
            glow.fill((100, 150, 255, 0), special_flags=pygame.BLEND_RGBA_ADD)
            glow.set_alpha(30)
            result.blit(glow, (4, 4))
            result.blit(glow, (6, 6))

            return result

        except Exception as e:
            logger.error(f"Error creating player 3D effect: {e}")
            return base_surface

    @staticmethod
    def create_enemy_3d_effect_clean(base_surface: pygame.Surface, level: int = 0) -> pygame.Surface:
        """
        Create clean 3D effect preserving original PNG colors.

        Only adds neutral shadows and highlights without color tinting.
        This preserves the original colors from enemy PNG textures.

        Args:
            base_surface: Original enemy PNG surface
            level: Enemy level (affects glow intensity)

        Returns:
            Enhanced surface with clean 3D effects preserving original colors
        """
        try:
            width, height = base_surface.get_size()

            # Create result surface with padding for effects
            result = pygame.Surface((width + 10, height + 10), pygame.SRCALPHA)

            # 1. NEUTRAL DROP SHADOW (gray-black, no color tint)
            for i in range(3, 0, -1):
                shadow = base_surface.copy()
                # Neutral dark shadow
                shadow.fill((20, 20, 20, 255), special_flags=pygame.BLEND_RGBA_MULT)
                shadow.set_alpha(100 - i * 20)
                result.blit(shadow, (5 + i, 5 + i))

            # 2. MAIN SPRITE (preserve original PNG colors)
            main_sprite = base_surface.copy()

            # 3. SUBTLE EDGE HIGHLIGHT (white, top-left)
            highlight = base_surface.copy()
            highlight.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_ADD)
            highlight.set_alpha(40)
            result.blit(highlight, (4, 4))

            # 4. SUBTLE EDGE SHADOW (dark, bottom-right)
            edge_shadow = base_surface.copy()
            edge_shadow.fill((10, 10, 10, 0), special_flags=pygame.BLEND_RGBA_SUB)
            edge_shadow.set_alpha(50)
            result.blit(edge_shadow, (6, 6))

            # 5. BRIGHTNESS BOOST (neutral, slight increase)
            brightness = base_surface.copy()
            brightness.fill((30, 30, 30, 0), special_flags=pygame.BLEND_RGBA_ADD)
            brightness.set_alpha(20)
            main_sprite.blit(brightness, (0, 0))

            # 6. OPTIONAL: Subtle glow for high-level enemies (white/neutral)
            if level >= 7:
                glow = pygame.Surface((width, height), pygame.SRCALPHA)
                # Neutral white glow at center
                glow_intensity = min(70, 30 + (level - 7) * 10)
                glow_radius = max(1, width // 3)
                pygame.draw.circle(glow, (255, 255, 255, glow_intensity), (width // 2, height // 2), glow_radius)
                # Rely on per-pixel alpha so highlights do not blow out original PNG colors
                main_sprite.blit(glow, (0, 0))

            # 7. Place main sprite on result
            result.blit(main_sprite, (5, 5))

            # 8. OUTER GLOW for visibility (very subtle white)
            outer_glow = base_surface.copy()
            outer_glow.fill((200, 200, 200, 0), special_flags=pygame.BLEND_RGBA_ADD)
            outer_glow.set_alpha(20)
            result.blit(outer_glow, (4, 4))
            result.blit(outer_glow, (6, 6))

            return result

        except Exception as e:
            logger.error(f"Error creating clean enemy 3D effect: {e}")
            return base_surface

    @staticmethod
    def create_enemy_3d_effect(base_surface: pygame.Surface, level: int = 0) -> pygame.Surface:
        """
        Create fast, dramatic 3D effect for enemy ship with red/organic tinting.

        NOTE: This adds red/orange color tinting to the original surface.
        Use create_enemy_3d_effect_clean() to preserve original PNG colors.

        Args:
            base_surface: Original enemy surface
            level: Enemy level for effect variation

        Returns:
            Enhanced surface with organic 3D effects
        """
        try:
            width, height = base_surface.get_size()

            # Create result surface
            result = pygame.Surface((width + 10, height + 10), pygame.SRCALPHA)

            # 1. STRONG DROP SHADOW (red-tinted for organic feel)
            for i in range(3, 0, -1):
                shadow = base_surface.copy()
                # Dark red shadow
                shadow.fill((50, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
                shadow.set_alpha(120 - i * 25)
                result.blit(shadow, (5 + i, 5 + i))

            # 2. MAIN ENEMY
            main_enemy = base_surface.copy()

            # 3. ORGANIC BEVELED EDGES - Top/Left (warm highlight)
            highlight = base_surface.copy()
            highlight.fill((255, 180, 100, 0), special_flags=pygame.BLEND_RGBA_ADD)
            highlight.set_alpha(70)
            result.blit(highlight, (3, 3))

            # 4. ORGANIC BEVELED EDGES - Bottom/Right (deep red shadow)
            edge_shadow = base_surface.copy()
            edge_shadow.fill((100, 0, 0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            edge_shadow.set_alpha(90)
            result.blit(edge_shadow, (7, 7))

            # 5. BIO-LUMINESCENT CORE
            bio_core = pygame.Surface((width, height), pygame.SRCALPHA)
            # Center glow based on level
            glow_color = (200 + level * 5, 100, 50) if level >= 5 else (180, 80, 50)
            pygame.draw.circle(bio_core, (*glow_color, 100), (width // 2, height // 2), 10)
            pygame.draw.circle(bio_core, (*glow_color, 60), (width // 2, height // 2), 15)

            # Side bio-panels
            pygame.draw.circle(bio_core, (200, 50, 50, 80), (width // 4, height // 2), 5)
            pygame.draw.circle(bio_core, (200, 50, 50, 80), (3 * width // 4, height // 2), 5)

            main_enemy.blit(bio_core, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            # 6. ORGANIC TEXTURE (veins/patterns)
            texture = pygame.Surface((width, height), pygame.SRCALPHA)
            # Add organic gradient
            for y in range(height):
                # Organic reddish gradient
                intensity = int(150 + (y / height) * 50)
                color = (intensity, intensity // 2, intensity // 3, 20)
                pygame.draw.line(texture, color, (0, y), (width, y), 1)

            main_enemy.blit(texture, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            # 7. BRIGHTNESS BOOST for visibility
            brightness = base_surface.copy()
            brightness.fill((60, 30, 30, 0), special_flags=pygame.BLEND_RGBA_ADD)
            brightness.set_alpha(60)
            main_enemy.blit(brightness, (0, 0))

            # 8. Place main enemy
            result.blit(main_enemy, (5, 5))

            # 9. THREAT AURA for high-level enemies
            if level >= 5:
                aura = base_surface.copy()
                aura.fill((255, 50, 0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                aura.set_alpha(40)
                for i in range(2):
                    result.blit(aura, (4 - i, 4 - i))
                    result.blit(aura, (6 + i, 6 + i))

            return result

        except Exception as e:
            logger.error(f"Error creating enemy 3D effect: {e}")
            return base_surface

    @staticmethod
    def create_boss_3d_effect(base_surface: pygame.Surface, level: int = 1) -> pygame.Surface:
        """
        Create dramatic 3D effect for boss ship with imposing presence.

        Args:
            base_surface: Original boss surface
            level: Boss level (1-3+) for effect variation

        Returns:
            Enhanced surface with powerful 3D effects
        """
        try:
            width, height = base_surface.get_size()

            # Create larger result surface for dramatic effects
            padding = 20
            result = pygame.Surface((width + padding * 2, height + padding * 2), pygame.SRCALPHA)

            # 1. MULTI-LAYER SHADOW for massive depth
            shadow_layers = [
                (10, 12, 80, (0, 0, 20)),  # Deep shadow
                (7, 9, 100, (20, 0, 30)),  # Mid shadow with purple tint
                (4, 5, 120, (40, 0, 40)),  # Close shadow
            ]

            for offset_x, offset_y, alpha, color in shadow_layers:
                shadow = base_surface.copy()
                shadow.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
                shadow.set_alpha(alpha)
                result.blit(shadow, (padding + offset_x, padding + offset_y))

            # 2. MAIN BOSS with enhancements
            main_boss = base_surface.copy()

            # 3. METALLIC ARMOR PLATING
            armor = pygame.Surface((width, height), pygame.SRCALPHA)
            for y in range(height):
                # Metallic gradient based on level
                base_brightness = 180 if level == 1 else (200 if level == 2 else 220)
                brightness = int(base_brightness - (y / height) * 100)

                # Level-specific color tints
                if level == 1:  # Purple tint
                    color = (brightness, brightness // 2, brightness, 50)
                elif level == 2:  # Blue tint
                    color = (brightness // 2, brightness // 2, brightness, 50)
                else:  # Red tint for level 3+
                    color = (brightness, brightness // 3, brightness // 3, 50)

                pygame.draw.line(armor, color, (0, y), (width, y), 1)

            main_boss.blit(armor, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            # 4. POWER CORE GLOW (center of boss)
            core = pygame.Surface((width, height), pygame.SRCALPHA)
            cx, cy = width // 2, height // 2

            # Core color based on level
            if level == 1:
                core_colors = [(200, 100, 255), (150, 50, 200), (100, 0, 150)]  # Purple
            elif level == 2:
                core_colors = [(100, 150, 255), (50, 100, 200), (0, 50, 150)]  # Blue
            else:
                core_colors = [(255, 100, 100), (200, 50, 50), (150, 0, 0)]  # Red

            # Multi-layer power core
            for i, color in enumerate(core_colors):
                radius = 20 - i * 5
                alpha = 120 - i * 20
                pygame.draw.circle(core, (*color, alpha), (cx, cy), radius)

            # Pulsing energy effect
            pygame.draw.circle(core, (255, 255, 255, 150), (cx, cy), 5)

            main_boss.blit(core, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            # 5. WEAPON SYSTEMS GLOW
            weapons = pygame.Surface((width, height), pygame.SRCALPHA)

            # Wing weapons
            weapon_positions = [
                (width // 4, height // 2),  # Left wing
                (3 * width // 4, height // 2),  # Right wing
                (width // 2, height // 4),  # Top cannon
            ]

            for wx, wy in weapon_positions:
                # Weapon glow based on level
                weapon_color = (255, 200, 100) if level >= 2 else (255, 150, 50)
                pygame.draw.circle(weapons, (*weapon_color, 100), (wx, wy), 8)
                pygame.draw.circle(weapons, (*weapon_color, 150), (wx, wy), 4)

            main_boss.blit(weapons, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            # 6. SHIELD SHIMMER EFFECT
            shield = pygame.Surface((width, height), pygame.SRCALPHA)

            # Create shield gradient from edges
            for x in range(width):
                for y in range(height):
                    # Distance from edge
                    edge_dist = min(x, y, width - x - 1, height - y - 1)
                    if edge_dist < 10:
                        intensity = int((10 - edge_dist) * 15)
                        shield.set_at((x, y), (100, 150, 255, intensity))

            main_boss.blit(shield, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            # 7. BOSS LEVEL INDICATORS (glowing orbs)
            indicators = pygame.Surface((width, height), pygame.SRCALPHA)
            for i in range(level):
                ix = width - 15 - i * 12
                iy = height - 15
                # Glowing level indicators
                pygame.draw.circle(indicators, (255, 255, 100, 150), (ix, iy), 5)
                pygame.draw.circle(indicators, (255, 255, 200, 200), (ix, iy), 3)

            main_boss.blit(indicators, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            # 8. Place enhanced boss on result
            result.blit(main_boss, (padding, padding))

            # 9. INTIMIDATION AURA (outer glow)
            # Create expanding auras based on level
            for i in range(level):
                aura = base_surface.copy()
                if level == 1:
                    aura.fill((150, 50, 200, 0), special_flags=pygame.BLEND_RGBA_ADD)
                elif level == 2:
                    aura.fill((50, 100, 200, 0), special_flags=pygame.BLEND_RGBA_ADD)
                else:
                    aura.fill((200, 50, 50, 0), special_flags=pygame.BLEND_RGBA_ADD)

                aura.set_alpha(30 - i * 10)
                offset = padding - 2 - i * 2
                result.blit(aura, (offset, offset))
                result.blit(aura, (offset + 4 + i * 4, offset + 4 + i * 4))

            # 10. SPECULAR HIGHLIGHTS for metallic finish
            specular = pygame.Surface((width, height), pygame.SRCALPHA)
            # Main highlight
            pygame.draw.ellipse(specular, (255, 255, 255, 100), (width // 2 - 15, height // 4 - 10, 30, 20))
            result.blit(specular, (padding, padding), special_flags=pygame.BLEND_RGBA_ADD)

            return result

        except Exception as e:
            logger.error(f"Error creating boss 3D effect: {e}")
            return base_surface


# Singleton instance
_fast_3d = None


def get_fast_3d() -> Fast3DEffects:
    """Get global Fast3D instance."""
    global _fast_3d
    if _fast_3d is None:
        _fast_3d = Fast3DEffects()
    return _fast_3d
