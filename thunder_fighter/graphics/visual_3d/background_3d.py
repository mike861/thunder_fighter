"""
Background 3D visual effects for planets and space elements.

This module provides functions to create 3D appearance for background elements
like planets, nebulae, and other space objects without complex transformations.
"""

import math
from typing import Tuple, Optional

import pygame

from .effect_config import Visual3DConfig, blend_colors, adjust_brightness
from thunder_fighter.utils.logger import logger


class BackgroundVisual3D:
    """Generator for 3D background visual effects."""

    def __init__(self):
        """Initialize background 3D visual generator."""
        self.config = Visual3DConfig.get_background_config()
        self.planet_cache = {}  # Cache for generated planets
        logger.debug("BackgroundVisual3D initialized")

    def create_3d_planet(self,
                        radius: int,
                        base_color: Tuple[int, int, int],
                        light_angle: float = 45.0,
                        atmosphere: bool = True) -> pygame.Surface:
        """
        Create a 3D planet with spherical shading and atmosphere.

        Args:
            radius: Planet radius in pixels
            base_color: Base RGB color of the planet
            light_angle: Light source angle in degrees (0-360)
            atmosphere: Whether to add atmospheric rim

        Returns:
            Surface with 3D planet appearance
        """
        # Create cache key
        cache_key = (radius, base_color, light_angle, atmosphere)
        if cache_key in self.planet_cache:
            return self.planet_cache[cache_key]

        try:
            # Create surface with extra space for atmosphere
            surface_size = radius * 2 + (10 if atmosphere else 0)
            surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
            surface.fill((0, 0, 0, 0))

            # Calculate center position
            center_x = surface_size // 2
            center_y = surface_size // 2

            # Get configuration
            planet_config = self.config.get("planets", {})
            gradient_steps = planet_config.get("gradient_steps", 32)
            atmosphere_thickness = planet_config.get("atmosphere_thickness", 0.15)
            specular_intensity = planet_config.get("specular_intensity", 0.8)
            specular_size = planet_config.get("specular_size", 0.1)

            # Convert light angle to radians
            light_angle_rad = math.radians(light_angle)
            light_dir_x = math.cos(light_angle_rad)
            light_dir_y = math.sin(light_angle_rad)

            # Draw planet surface with spherical shading
            self._draw_planet_surface(
                surface, center_x, center_y, radius,
                base_color, light_dir_x, light_dir_y,
                gradient_steps
            )

            # Add specular highlight
            if specular_intensity > 0:
                self._add_specular_highlight(
                    surface, center_x, center_y, radius,
                    light_dir_x, light_dir_y, specular_intensity,
                    specular_size
                )

            # Add atmospheric rim
            if atmosphere:
                self._add_atmospheric_rim(
                    surface, center_x, center_y, radius,
                    base_color, atmosphere_thickness
                )

            # Cache the result
            if len(self.planet_cache) < 20:  # Limit cache size
                self.planet_cache[cache_key] = surface

            return surface

        except Exception as e:
            logger.error(f"Error creating 3D planet: {e}")
            # Fallback: create simple circle
            return self._create_fallback_planet(radius, base_color)

    def _draw_planet_surface(self,
                            surface: pygame.Surface,
                            center_x: int, center_y: int, radius: int,
                            base_color: Tuple[int, int, int],
                            light_dir_x: float, light_dir_y: float,
                            gradient_steps: int):
        """Draw planet surface with spherical lighting."""

        # Draw planet pixel by pixel for realistic sphere shading
        for y in range(center_y - radius, center_y + radius + 1):
            for x in range(center_x - radius, center_x + radius + 1):
                # Calculate distance from center
                dx = x - center_x
                dy = y - center_y
                distance_from_center = math.sqrt(dx * dx + dy * dy)

                # Only draw pixels within the circle
                if distance_from_center <= radius:
                    # Calculate sphere surface normal
                    # For a sphere at origin with radius R, normal at (x,y,z) is (x,y,z)/R
                    # We need to find z from x,y: z = sqrt(R² - x² - y²)

                    z_squared = radius * radius - dx * dx - dy * dy
                    if z_squared >= 0:
                        z = math.sqrt(z_squared)

                        # Surface normal (unit vector)
                        normal_length = radius
                        normal_x = dx / normal_length
                        normal_y = dy / normal_length
                        normal_z = z / normal_length

                        # Calculate lighting (dot product of normal and light direction)
                        # Light direction in 3D (we assume light_z = 0.5 for nice lighting)
                        light_z = 0.5
                        light_length = math.sqrt(light_dir_x**2 + light_dir_y**2 + light_z**2)
                        light_unit_x = light_dir_x / light_length
                        light_unit_y = light_dir_y / light_length
                        light_unit_z = light_z / light_length

                        # Dot product for lighting intensity
                        lighting = (normal_x * light_unit_x +
                                  normal_y * light_unit_y +
                                  normal_z * light_unit_z)

                        # Clamp lighting to [0, 1]
                        lighting = max(0, min(1, lighting))

                        # Apply ambient lighting (prevent pure black)
                        ambient = 0.2
                        final_lighting = ambient + (1 - ambient) * lighting

                        # Calculate final color
                        final_color = (
                            int(base_color[0] * final_lighting),
                            int(base_color[1] * final_lighting),
                            int(base_color[2] * final_lighting)
                        )

                        # Set pixel
                        surface.set_at((x, y), final_color)

    def _add_specular_highlight(self,
                              surface: pygame.Surface,
                              center_x: int, center_y: int, radius: int,
                              light_dir_x: float, light_dir_y: float,
                              intensity: float, size: float):
        """Add specular highlight to simulate reflective surface."""

        # Calculate highlight position (where light reflects directly toward viewer)
        highlight_x = center_x + int(light_dir_x * radius * 0.3)
        highlight_y = center_y + int(light_dir_y * radius * 0.3)

        # Create highlight
        highlight_radius = max(1, int(radius * size))
        highlight_alpha = int(255 * intensity)

        # Draw gradient highlight
        for highlight_r in range(highlight_radius, 0, -1):
            alpha = int(highlight_alpha * (highlight_r / highlight_radius))
            highlight_color = (255, 255, 255, alpha)

            # Create small surface for this highlight ring
            highlight_surf = pygame.Surface((highlight_r * 2, highlight_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                highlight_surf,
                highlight_color,
                (highlight_r, highlight_r),
                highlight_r
            )

            # Blit with blending
            surface.blit(
                highlight_surf,
                (highlight_x - highlight_r, highlight_y - highlight_r),
                special_flags=pygame.BLEND_ALPHA_SDL2
            )

    def _add_atmospheric_rim(self,
                            surface: pygame.Surface,
                            center_x: int, center_y: int, radius: int,
                            base_color: Tuple[int, int, int],
                            thickness: float):
        """Add atmospheric rim glow around planet."""

        # Calculate atmospheric layer
        atmo_radius = int(radius * (1 + thickness))
        atmo_color = adjust_brightness(base_color, 1.5)  # Brighter atmospheric color

        # Draw atmospheric glow
        for ring_radius in range(radius + 1, atmo_radius + 1):
            # Calculate alpha based on distance from surface
            distance_from_surface = ring_radius - radius
            max_distance = atmo_radius - radius
            alpha_ratio = 1 - (distance_from_surface / max_distance)

            alpha = int(50 * alpha_ratio)  # Max alpha of 50 for subtle effect

            if alpha > 5:  # Only draw significant atmosphere
                # Create ring surface
                ring_surface = pygame.Surface((ring_radius * 2, ring_radius * 2), pygame.SRCALPHA)

                # Draw atmospheric ring
                pygame.draw.circle(
                    ring_surface,
                    (*atmo_color, alpha),
                    (ring_radius, ring_radius),
                    ring_radius,
                    1  # Ring thickness
                )

                # Blit centered
                surface.blit(
                    ring_surface,
                    (center_x - ring_radius, center_y - ring_radius),
                    special_flags=pygame.BLEND_ALPHA_SDL2
                )

    def _create_fallback_planet(self, radius: int, base_color: Tuple[int, int, int]) -> pygame.Surface:
        """Create simple fallback planet if 3D rendering fails."""
        surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, base_color, (radius, radius), radius)
        return surface

    def create_nebula_layer(self,
                           width: int, height: int,
                           base_color: Tuple[int, int, int],
                           depth_factor: float = 1.0) -> pygame.Surface:
        """
        Create nebula background layer with depth effect.

        Args:
            width: Layer width
            height: Layer height
            base_color: Base nebula color
            depth_factor: Depth factor (1.0 = foreground, 0.5 = background)

        Returns:
            Nebula layer surface
        """
        try:
            surface = pygame.Surface((width, height), pygame.SRCALPHA)

            # Apply depth-based color and opacity adjustments
            depth_color = adjust_brightness(base_color, depth_factor)
            base_alpha = int(80 * depth_factor)  # Deeper layers more transparent

            # Create nebula pattern using noise-like generation
            for y in range(0, height, 4):  # Skip pixels for performance
                for x in range(0, width, 4):
                    # Generate noise pattern
                    noise_x = x * 0.01
                    noise_y = y * 0.01

                    noise_value = (math.sin(noise_x) * math.cos(noise_y) +
                                  math.sin(noise_x * 2.3) * math.cos(noise_y * 1.7)) * 0.5

                    if abs(noise_value) > 0.3:  # Only draw significant noise
                        alpha = int(base_alpha * abs(noise_value))
                        nebula_color = (*depth_color, alpha)

                        # Draw small nebula cloud
                        cloud_size = 2 + int(depth_factor * 2)
                        pygame.draw.circle(surface, nebula_color, (x, y), cloud_size)

            return surface

        except Exception as e:
            logger.error(f"Error creating nebula layer: {e}")
            return pygame.Surface((width, height), pygame.SRCALPHA)

    def clear_cache(self):
        """Clear planet cache."""
        self.planet_cache.clear()
        logger.debug("Background 3D cache cleared")

    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "cached_planets": len(self.planet_cache),
        }


# Singleton instance
_background_3d = None


def get_background_3d() -> BackgroundVisual3D:
    """Get global background 3D instance."""
    global _background_3d
    if _background_3d is None:
        _background_3d = BackgroundVisual3D()
    return _background_3d


def create_3d_planet(radius: int,
                    base_color: Tuple[int, int, int],
                    light_angle: float = 45.0,
                    atmosphere: bool = True) -> pygame.Surface:
    """
    Convenience function to create 3D planet.

    Args:
        radius: Planet radius
        base_color: Base planet color
        light_angle: Light angle in degrees
        atmosphere: Enable atmospheric rim

    Returns:
        3D planet surface
    """
    bg_3d = get_background_3d()
    return bg_3d.create_3d_planet(radius, base_color, light_angle, atmosphere)