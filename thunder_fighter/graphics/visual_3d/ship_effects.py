"""
Player ship visual enhancement for static 3D appearance.

This module provides functions to enhance player ship sprites with depth effects
like shadows, highlights, metallic sheen, and engine glow without runtime scaling.
"""

import math
from typing import Optional, Tuple

import pygame

from .effect_config import Visual3DConfig, blend_colors, adjust_brightness
from thunder_fighter.utils.logger import logger


class ShipVisualEnhancer:
    """Static visual enhancer for player ship 3D appearance."""

    def __init__(self):
        """Initialize ship visual enhancer."""
        self.config = Visual3DConfig.get_player_config()
        self.cache = {}  # Simple cache for enhanced images
        logger.debug("ShipVisualEnhancer initialized")

    def enhance_player_ship(self, original_surface: pygame.Surface) -> pygame.Surface:
        """
        Apply comprehensive 3D visual enhancements to player ship.

        Args:
            original_surface: Original player ship surface

        Returns:
            Enhanced surface with 3D appearance effects
        """
        # Check cache first
        cache_key = id(original_surface)
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # Create enhanced surface with alpha channel
            enhanced = pygame.Surface(original_surface.get_size(), pygame.SRCALPHA)
            enhanced.fill((0, 0, 0, 0))  # Transparent background

            # Apply enhancements in layers (order matters for visual quality)
            enhanced = self._apply_base_ship(enhanced, original_surface)
            enhanced = self._add_depth_shadow(enhanced, original_surface)
            enhanced = self._add_metallic_sheen(enhanced)
            enhanced = self._add_specular_highlights(enhanced)
            enhanced = self._add_edge_lighting(enhanced)
            enhanced = self._add_engine_glow(enhanced)

            # Cache the result
            if Visual3DConfig.PERFORMANCE["enable_caching"]:
                if len(self.cache) < Visual3DConfig.PERFORMANCE["max_cache_size"]:
                    self.cache[cache_key] = enhanced

            return enhanced

        except Exception as e:
            logger.error(f"Error enhancing player ship: {e}")
            return original_surface  # Fallback to original

    def _apply_base_ship(self, target: pygame.Surface, original: pygame.Surface) -> pygame.Surface:
        """Apply the base ship image to the enhanced surface."""
        target.blit(original, (0, 0))
        return target

    def _add_depth_shadow(self, surface: pygame.Surface, original: pygame.Surface) -> pygame.Surface:
        """
        Add depth shadow effect beneath the ship.

        Args:
            surface: Target surface to draw on
            original: Original ship surface for shape reference

        Returns:
            Surface with shadow effect applied
        """
        try:
            shadow_offset = self.config["shadow_offset"]
            shadow_alpha = self.config["shadow_alpha"]
            shadow_color = self.config["shadow_color"]

            # Create shadow surface
            shadow_surface = pygame.Surface(original.get_size(), pygame.SRCALPHA)

            # Generate shadow by darkening the original shape
            for x in range(original.get_width()):
                for y in range(original.get_height()):
                    original_pixel = original.get_at((x, y))
                    if original_pixel[3] > 0:  # If pixel is not transparent
                        # Create shadow pixel
                        shadow_pixel = (*shadow_color, shadow_alpha)
                        shadow_surface.set_at((x, y), shadow_pixel)

            # Blit shadow with offset (beneath the ship)
            shadow_rect = shadow_surface.get_rect()
            shadow_rect.x += shadow_offset[0]
            shadow_rect.y += shadow_offset[1]

            # Draw shadow first (behind the ship)
            temp_surface = pygame.Surface(
                (surface.get_width() + abs(shadow_offset[0]),
                 surface.get_height() + abs(shadow_offset[1])),
                pygame.SRCALPHA
            )
            temp_surface.blit(shadow_surface, shadow_rect)
            temp_surface.blit(surface, (0, 0))  # Original ship on top

            return temp_surface

        except Exception as e:
            logger.warning(f"Error adding shadow effect: {e}")
            return surface

    def _add_metallic_sheen(self, surface: pygame.Surface) -> pygame.Surface:
        """
        Add metallic surface sheen effect.

        Args:
            surface: Surface to enhance

        Returns:
            Surface with metallic sheen applied
        """
        if not self.config.get("metallic_sheen", False):
            return surface

        try:
            # Create subtle gradient overlay for metallic effect
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

            width, height = surface.get_size()
            center_x, center_y = width // 2, height // 3  # Upper center for light source

            # Apply gradient from center outward
            for y in range(height):
                for x in range(width):
                    # Check if original pixel exists (not transparent)
                    original_pixel = surface.get_at((x, y))
                    if original_pixel[3] > 0:
                        # Calculate distance from light center
                        distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                        max_distance = math.sqrt(width**2 + height**2) / 2

                        # Calculate metallic intensity (higher near center)
                        intensity = max(0, 1 - (distance / max_distance))
                        metallic_alpha = int(intensity * 80)  # More visible metallic overlay

                        if metallic_alpha > 5:  # Only apply if significant
                            metallic_color = (200, 200, 255, metallic_alpha)  # Cool metallic tint
                            overlay.set_at((x, y), metallic_color)

            # Blend overlay with surface
            surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
            return surface

        except Exception as e:
            logger.warning(f"Error adding metallic sheen: {e}")
            return surface

    def _add_specular_highlights(self, surface: pygame.Surface) -> pygame.Surface:
        """
        Add specular highlight points.

        Args:
            surface: Surface to enhance

        Returns:
            Surface with specular highlights
        """
        try:
            highlight_positions = self.config.get("highlight_positions", [])
            highlight_color = self.config.get("highlight_color", (255, 255, 255))
            highlight_intensity = self.config.get("highlight_intensity", 0.4)

            width, height = surface.get_size()

            for pos_ratio in highlight_positions:
                # Convert ratio to pixel coordinates
                x = int(pos_ratio[0] * width)
                y = int(pos_ratio[1] * height)

                # Draw small highlight circle
                highlight_radius = 3
                highlight_alpha = int(255 * highlight_intensity)

                # Create highlight with gradient
                for radius in range(highlight_radius, 0, -1):
                    alpha = int(highlight_alpha * (radius / highlight_radius))
                    highlight_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(
                        highlight_surf,
                        (*highlight_color, alpha),
                        (radius, radius),
                        radius
                    )

                    # Blit centered on highlight position
                    surface.blit(
                        highlight_surf,
                        (x - radius, y - radius),
                        special_flags=pygame.BLEND_ALPHA_SDL2
                    )

            return surface

        except Exception as e:
            logger.warning(f"Error adding specular highlights: {e}")
            return surface

    def _add_edge_lighting(self, surface: pygame.Surface) -> pygame.Surface:
        """
        Add edge lighting effect for 3D depth.

        Args:
            surface: Surface to enhance

        Returns:
            Surface with edge lighting
        """
        if not self.config.get("edge_lighting", False):
            return surface

        try:
            # Create edge detection and lighting
            width, height = surface.get_size()
            edge_surface = pygame.Surface((width, height), pygame.SRCALPHA)

            # Simple edge detection - check for transparent neighbors
            for x in range(1, width - 1):
                for y in range(1, height - 1):
                    current_pixel = surface.get_at((x, y))

                    if current_pixel[3] > 0:  # Current pixel is not transparent
                        # Check left neighbor
                        left_pixel = surface.get_at((x - 1, y))
                        if left_pixel[3] == 0:  # Left is transparent = left edge
                            # Add highlight to left edge
                            edge_color = (255, 255, 255, 120)  # More visible white edge
                            edge_surface.set_at((x, y), edge_color)

            # Blend edge lighting
            surface.blit(edge_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
            return surface

        except Exception as e:
            logger.warning(f"Error adding edge lighting: {e}")
            return surface

    def _add_engine_glow(self, surface: pygame.Surface) -> pygame.Surface:
        """
        Add engine glow effect at the rear of the ship.

        Args:
            surface: Surface to enhance

        Returns:
            Surface with engine glow effect
        """
        engine_config = self.config.get("engine_glow", {})
        if not engine_config.get("enabled", False):
            return surface

        try:
            glow_color = engine_config.get("color", (255, 150, 100))
            glow_intensity = engine_config.get("intensity", 0.6)
            glow_radius = engine_config.get("radius", 4)

            width, height = surface.get_size()

            # Engine positions (rear of ship - bottom area)
            engine_positions = [
                (width * 0.35, height * 0.85),  # Left engine
                (width * 0.65, height * 0.85),  # Right engine
            ]

            for engine_x, engine_y in engine_positions:
                # Create glow effect with gradient
                for radius in range(glow_radius, 0, -1):
                    alpha = int(255 * glow_intensity * (radius / glow_radius) * 0.5)
                    glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

                    pygame.draw.circle(
                        glow_surf,
                        (*glow_color, alpha),
                        (radius, radius),
                        radius
                    )

                    surface.blit(
                        glow_surf,
                        (int(engine_x - radius), int(engine_y - radius)),
                        special_flags=pygame.BLEND_ALPHA_SDL2
                    )

            return surface

        except Exception as e:
            logger.warning(f"Error adding engine glow: {e}")
            return surface

    def clear_cache(self):
        """Clear the enhancement cache."""
        self.cache.clear()
        logger.debug("Ship visual enhancer cache cleared")

    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "cached_items": len(self.cache),
            "max_cache_size": Visual3DConfig.PERFORMANCE["max_cache_size"],
            "cache_enabled": Visual3DConfig.PERFORMANCE["enable_caching"],
        }


# Singleton instance for global use
_ship_enhancer = None


def get_ship_enhancer() -> ShipVisualEnhancer:
    """Get global ship visual enhancer instance."""
    global _ship_enhancer
    if _ship_enhancer is None:
        _ship_enhancer = ShipVisualEnhancer()
    return _ship_enhancer


def enhance_player_ship(surface: pygame.Surface) -> pygame.Surface:
    """
    Convenience function to enhance player ship surface.

    Args:
        surface: Original player ship surface

    Returns:
        Enhanced surface with 3D visual effects
    """
    enhancer = get_ship_enhancer()
    return enhancer.enhance_player_ship(surface)