"""
Enemy ship visual enhancement for organic/biological 3D appearance.

This module provides functions to enhance enemy ship sprites with organic
depth effects contrasting with the player's mechanical/metallic appearance.
"""

import math
import random
from typing import Tuple

import pygame

from .effect_config import Visual3DConfig, blend_colors, adjust_brightness
from thunder_fighter.utils.logger import logger


class EnemyVisualEnhancer:
    """Static visual enhancer for enemy ship organic 3D appearance."""

    def __init__(self):
        """Initialize enemy visual enhancer."""
        self.config = Visual3DConfig.get_enemy_config()
        self.cache = {}  # Simple cache for enhanced images
        logger.debug("EnemyVisualEnhancer initialized")

    def enhance_enemy_ship(self, original_surface: pygame.Surface, enemy_level: int = 0) -> pygame.Surface:
        """
        Apply organic 3D visual enhancements to enemy ship.

        Args:
            original_surface: Original enemy ship surface
            enemy_level: Enemy level for level-based variations

        Returns:
            Enhanced surface with organic 3D appearance
        """
        # Create cache key including level
        cache_key = (id(original_surface), enemy_level)
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # Create enhanced surface
            enhanced = pygame.Surface(original_surface.get_size(), pygame.SRCALPHA)
            enhanced.fill((0, 0, 0, 0))

            # Apply organic enhancement layers
            enhanced = self._apply_base_enemy(enhanced, original_surface)
            enhanced = self._add_organic_shadow(enhanced, original_surface)
            enhanced = self._add_bio_highlights(enhanced, enemy_level)
            enhanced = self._add_surface_texture(enhanced, enemy_level)
            enhanced = self._add_bio_glow(enhanced, enemy_level)

            # Cache result
            if Visual3DConfig.PERFORMANCE["enable_caching"]:
                if len(self.cache) < Visual3DConfig.PERFORMANCE["max_cache_size"]:
                    self.cache[cache_key] = enhanced

            return enhanced

        except Exception as e:
            logger.error(f"Error enhancing enemy ship: {e}")
            return original_surface

    def _apply_base_enemy(self, target: pygame.Surface, original: pygame.Surface) -> pygame.Surface:
        """Apply the base enemy image."""
        target.blit(original, (0, 0))
        return target

    def _add_organic_shadow(self, surface: pygame.Surface, original: pygame.Surface) -> pygame.Surface:
        """
        Add organic shadow effect with biological characteristics.

        Args:
            surface: Target surface
            original: Original enemy surface for shape

        Returns:
            Surface with organic shadow
        """
        try:
            shadow_offset = self.config["shadow_offset"]
            shadow_alpha = self.config["shadow_alpha"]
            shadow_color = self.config["shadow_color"]

            # Create organic shadow (more irregular than mechanical shadow)
            shadow_surface = pygame.Surface(original.get_size(), pygame.SRCALPHA)

            for x in range(original.get_width()):
                for y in range(original.get_height()):
                    original_pixel = original.get_at((x, y))
                    if original_pixel[3] > 0:
                        # Add slight randomness for organic feel
                        noise_factor = random.uniform(0.8, 1.2)
                        organic_alpha = int(shadow_alpha * noise_factor)

                        shadow_pixel = (*shadow_color, min(255, organic_alpha))
                        shadow_surface.set_at((x, y), shadow_pixel)

            # Apply shadow with offset
            temp_surface = pygame.Surface(
                (surface.get_width() + abs(shadow_offset[0]),
                 surface.get_height() + abs(shadow_offset[1])),
                pygame.SRCALPHA
            )

            shadow_rect = shadow_surface.get_rect()
            shadow_rect.x += shadow_offset[0]
            shadow_rect.y += shadow_offset[1]

            temp_surface.blit(shadow_surface, shadow_rect)
            temp_surface.blit(surface, (0, 0))

            return temp_surface

        except Exception as e:
            logger.warning(f"Error adding organic shadow: {e}")
            return surface

    def _add_bio_highlights(self, surface: pygame.Surface, enemy_level: int) -> pygame.Surface:
        """
        Add biological highlight patterns.

        Args:
            surface: Surface to enhance
            enemy_level: Enemy level for intensity variation

        Returns:
            Surface with bio highlights
        """
        try:
            bio_highlights = self.config.get("bio_highlights", [])
            highlight_color = self.config.get("highlight_color", (180, 60, 60))

            width, height = surface.get_size()

            # Adjust highlight intensity based on enemy level
            base_intensity = 0.3 + (enemy_level * 0.05)  # Higher level = more intense
            base_intensity = min(base_intensity, 0.8)  # Cap at 0.8

            for i, pos_ratio in enumerate(bio_highlights):
                x = int(pos_ratio[0] * width)
                y = int(pos_ratio[1] * height)

                # Create organic highlight pattern (not perfect circles)
                highlight_size = 2 + (enemy_level // 3)  # Larger highlights for higher levels

                # Create irregular bio-highlight
                for offset_x in range(-highlight_size, highlight_size + 1):
                    for offset_y in range(-highlight_size, highlight_size + 1):
                        distance = math.sqrt(offset_x**2 + offset_y**2)
                        if distance <= highlight_size:
                            # Add organic irregularity
                            irregularity = random.uniform(0.7, 1.3)
                            if distance * irregularity <= highlight_size:
                                alpha = int(255 * base_intensity * (1 - distance / highlight_size))

                                if alpha > 20:  # Only draw significant highlights
                                    highlight_x = x + offset_x
                                    highlight_y = y + offset_y

                                    if (0 <= highlight_x < width and 0 <= highlight_y < height):
                                        current_pixel = surface.get_at((highlight_x, highlight_y))
                                        if current_pixel[3] > 0:  # Only on existing pixels
                                            bio_color = (*highlight_color, alpha)

                                            # Create small highlight surface for blending
                                            highlight_surf = pygame.Surface((1, 1), pygame.SRCALPHA)
                                            highlight_surf.fill(bio_color)

                                            surface.blit(
                                                highlight_surf,
                                                (highlight_x, highlight_y),
                                                special_flags=pygame.BLEND_ALPHA_SDL2
                                            )

            return surface

        except Exception as e:
            logger.warning(f"Error adding bio highlights: {e}")
            return surface

    def _add_surface_texture(self, surface: pygame.Surface, enemy_level: int) -> pygame.Surface:
        """
        Add organic surface texture effect.

        Args:
            surface: Surface to enhance
            enemy_level: Enemy level for texture complexity

        Returns:
            Surface with organic texture
        """
        texture_config = self.config.get("surface_texture", {})
        if not texture_config.get("enabled", False):
            return surface

        try:
            roughness = texture_config.get("roughness", 0.3)
            bio_pattern = texture_config.get("bio_pattern", False)

            if not bio_pattern:
                return surface

            width, height = surface.get_size()

            # Create subtle bio-pattern overlay
            texture_surface = pygame.Surface((width, height), pygame.SRCALPHA)

            # Generate organic pattern based on enemy level
            pattern_complexity = 1 + (enemy_level // 2)  # More complex patterns for higher levels

            for x in range(0, width, 2):  # Skip pixels for performance
                for y in range(0, height, 2):
                    original_pixel = surface.get_at((x, y))
                    if original_pixel[3] > 0:  # Only on existing pixels
                        # Create bio-pattern using sine waves (simulating organic structure)
                        wave1 = math.sin(x * 0.2 + y * 0.1) * pattern_complexity
                        wave2 = math.cos(y * 0.15 + x * 0.25) * pattern_complexity

                        texture_intensity = (wave1 + wave2) * roughness * 0.1
                        texture_alpha = max(0, min(255, int(abs(texture_intensity) * 255)))

                        if texture_alpha > 10:  # Only apply significant texture
                            # Use dark organic color for texture
                            texture_color = (40, 20, 20, texture_alpha)
                            texture_surface.set_at((x, y), texture_color)

            # Blend texture
            surface.blit(texture_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
            return surface

        except Exception as e:
            logger.warning(f"Error adding surface texture: {e}")
            return surface

    def _add_bio_glow(self, surface: pygame.Surface, enemy_level: int) -> pygame.Surface:
        """
        Add biological glow effect for high-level enemies.

        Args:
            surface: Surface to enhance
            enemy_level: Enemy level

        Returns:
            Surface with bio glow
        """
        # Only add glow for higher level enemies
        if enemy_level < 5:
            return surface

        try:
            width, height = surface.get_size()

            # Bio-glow intensity based on level
            glow_intensity = min(0.4, (enemy_level - 4) * 0.05)
            glow_color = (180, 40, 40)  # Dark red biological glow

            # Add subtle glow around the entire ship
            glow_surface = pygame.Surface((width + 4, height + 4), pygame.SRCALPHA)

            # Create glow outline
            for x in range(width):
                for y in range(height):
                    original_pixel = surface.get_at((x, y))
                    if original_pixel[3] > 0:  # Existing pixel
                        # Add glow pixels around original
                        for glow_x in range(-2, 3):
                            for glow_y in range(-2, 3):
                                if glow_x == 0 and glow_y == 0:
                                    continue  # Skip center pixel

                                distance = math.sqrt(glow_x**2 + glow_y**2)
                                if distance <= 2:
                                    glow_alpha = int(255 * glow_intensity * (1 - distance / 2))

                                    if glow_alpha > 10:
                                        glow_pixel = (*glow_color, glow_alpha)
                                        target_x = x + glow_x + 2
                                        target_y = y + glow_y + 2

                                        if (0 <= target_x < glow_surface.get_width() and
                                            0 <= target_y < glow_surface.get_height()):
                                            glow_surface.set_at((target_x, target_y), glow_pixel)

            # Combine glow with original
            temp_surface = pygame.Surface((width + 4, height + 4), pygame.SRCALPHA)
            temp_surface.blit(glow_surface, (0, 0))
            temp_surface.blit(surface, (2, 2))  # Center original on glow

            return temp_surface

        except Exception as e:
            logger.warning(f"Error adding bio glow: {e}")
            return surface

    def clear_cache(self):
        """Clear the enhancement cache."""
        self.cache.clear()
        logger.debug("Enemy visual enhancer cache cleared")

    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "cached_items": len(self.cache),
            "max_cache_size": Visual3DConfig.PERFORMANCE["max_cache_size"],
            "cache_enabled": Visual3DConfig.PERFORMANCE["enable_caching"],
        }


# Singleton instance
_enemy_enhancer = None


def get_enemy_enhancer() -> EnemyVisualEnhancer:
    """Get global enemy visual enhancer instance."""
    global _enemy_enhancer
    if _enemy_enhancer is None:
        _enemy_enhancer = EnemyVisualEnhancer()
    return _enemy_enhancer


def enhance_enemy_ship(surface: pygame.Surface, enemy_level: int = 0) -> pygame.Surface:
    """
    Convenience function to enhance enemy ship surface.

    Args:
        surface: Original enemy ship surface
        enemy_level: Enemy level for enhancement variations

    Returns:
        Enhanced surface with organic 3D effects
    """
    enhancer = get_enemy_enhancer()
    return enhancer.enhance_enemy_ship(surface, enemy_level)