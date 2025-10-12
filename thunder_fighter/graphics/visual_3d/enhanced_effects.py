"""
Enhanced 3D visual effects with more dramatic and visible results.

This module provides stronger, more visible 3D effects for ships,
fixing transparency issues and adding dramatic visual enhancements.
"""

import math
from typing import Tuple

import pygame

from thunder_fighter.utils.logger import logger


class Enhanced3DEffects:
    """Enhanced 3D effects with dramatic visual impact."""

    @staticmethod
    def create_dramatic_shadow(
        surface: pygame.Surface,
        offset: Tuple[int, int] = (6, 6),
        color: Tuple[int, int, int] = (0, 0, 0),
        blur_radius: int = 3,
    ) -> pygame.Surface:
        """
        Create a dramatic shadow with proper transparency handling.

        Args:
            surface: Original surface
            offset: Shadow offset (x, y)
            color: Shadow color
            blur_radius: Blur radius for soft shadow

        Returns:
            Surface with shadow applied
        """
        width, height = surface.get_size()

        # Create larger surface for shadow and blur
        shadow_width = width + abs(offset[0]) + blur_radius * 2
        shadow_height = height + abs(offset[1]) + blur_radius * 2

        result = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
        result.fill((0, 0, 0, 0))  # Ensure transparent background

        # Create shadow surface
        shadow = pygame.Surface((width, height), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 0))

        # Copy only non-transparent pixels as shadow
        for x in range(width):
            for y in range(height):
                pixel = surface.get_at((x, y))
                if pixel[3] > 10:  # If pixel is not transparent
                    shadow.set_at((x, y), (*color, 200))  # Strong shadow

        # Apply blur to shadow for soft edges
        for _blur_pass in range(blur_radius):
            blurred = pygame.Surface((width, height), pygame.SRCALPHA)
            blurred.fill((0, 0, 0, 0))

            for x in range(1, width - 1):
                for y in range(1, height - 1):
                    # Simple box blur
                    total_alpha = 0
                    count = 0
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            px = shadow.get_at((x + dx, y + dy))
                            total_alpha += px[3]
                            count += 1

                    avg_alpha = total_alpha // count
                    if avg_alpha > 0:
                        blurred.set_at((x, y), (*color, avg_alpha))

            shadow = blurred

        # Draw shadow with offset
        shadow_pos = (blur_radius + offset[0], blur_radius + offset[1])
        result.blit(shadow, shadow_pos)

        # Draw original on top
        original_pos = (blur_radius, blur_radius)
        result.blit(surface, original_pos)

        return result

    @staticmethod
    def add_3d_bevel(
        surface: pygame.Surface,
        bevel_size: int = 3,
        highlight_color: Tuple[int, int, int] = (255, 255, 255),
        shadow_color: Tuple[int, int, int] = (0, 0, 0),
    ) -> pygame.Surface:
        """
        Add 3D bevel effect to edges.

        Args:
            surface: Original surface
            bevel_size: Size of bevel effect
            highlight_color: Color for top-left edges (light)
            shadow_color: Color for bottom-right edges (dark)

        Returns:
            Surface with bevel effect
        """
        result = surface.copy()
        width, height = surface.get_size()

        # Create edge detection and apply bevel
        for x in range(width):
            for y in range(height):
                pixel = surface.get_at((x, y))
                if pixel[3] > 10:  # Non-transparent pixel
                    # Check if edge pixel
                    is_edge = False

                    # Check all directions for transparency
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            neighbor = surface.get_at((nx, ny))
                            if neighbor[3] < 10:  # Neighbor is transparent
                                is_edge = True
                                break

                    if is_edge:
                        # Determine which edge (top-left or bottom-right)
                        # Top-left edges get highlight
                        if x > 0 and y > 0:
                            left = surface.get_at((x - 1, y))
                            top = surface.get_at((x, y - 1))
                            if left[3] < 10 or top[3] < 10:
                                # Apply highlight
                                for i in range(1, bevel_size + 1):
                                    alpha = 150 - (i * 30)  # Gradient
                                    if alpha > 0:
                                        highlight_surf = pygame.Surface((1, 1), pygame.SRCALPHA)
                                        highlight_surf.fill((*highlight_color, alpha))
                                        result.blit(highlight_surf, (x, y), special_flags=pygame.BLEND_RGBA_ADD)

                        # Bottom-right edges get shadow
                        if x < width - 1 and y < height - 1:
                            right = surface.get_at((x + 1, y))
                            bottom = surface.get_at((x, y + 1))
                            if right[3] < 10 or bottom[3] < 10:
                                # Apply shadow
                                for i in range(1, bevel_size + 1):
                                    alpha = 100 - (i * 20)  # Gradient
                                    if alpha > 0:
                                        shadow_surf = pygame.Surface((1, 1), pygame.SRCALPHA)
                                        shadow_surf.fill((*shadow_color, alpha))
                                        result.blit(shadow_surf, (x, y), special_flags=pygame.BLEND_RGBA_SUB)

        return result

    @staticmethod
    def add_metallic_gradient(surface: pygame.Surface, gradient_type: str = "vertical") -> pygame.Surface:
        """
        Add metallic gradient overlay.

        Args:
            surface: Original surface
            gradient_type: "vertical", "horizontal", or "radial"

        Returns:
            Surface with metallic gradient
        """
        result = surface.copy()
        width, height = surface.get_size()

        overlay = pygame.Surface((width, height), pygame.SRCALPHA)

        if gradient_type == "vertical":
            for y in range(height):
                intensity = int(255 * (1 - (y / height)))  # Brighter at top
                for x in range(width):
                    pixel = surface.get_at((x, y))
                    if pixel[3] > 10:  # Non-transparent
                        gradient_color = (intensity, intensity, min(255, intensity + 50))
                        overlay.set_at((x, y), (*gradient_color, 40))

        elif gradient_type == "radial":
            center_x, center_y = width // 2, height // 2
            max_dist = math.sqrt(center_x**2 + center_y**2)

            for x in range(width):
                for y in range(height):
                    pixel = surface.get_at((x, y))
                    if pixel[3] > 10:  # Non-transparent
                        dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                        intensity = int(255 * (1 - (dist / max_dist)))
                        gradient_color = (intensity, intensity, min(255, intensity + 50))
                        overlay.set_at((x, y), (*gradient_color, 50))

        result.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return result

    @staticmethod
    def add_outer_glow(
        surface: pygame.Surface,
        glow_color: Tuple[int, int, int] = (100, 200, 255),
        glow_radius: int = 5,
        glow_intensity: float = 0.8,
    ) -> pygame.Surface:
        """
        Add outer glow effect.

        Args:
            surface: Original surface
            glow_color: Color of the glow
            glow_radius: Radius of the glow
            glow_intensity: Intensity (0.0 - 1.0)

        Returns:
            Surface with outer glow
        """
        width, height = surface.get_size()

        # Create larger surface for glow
        glow_width = width + glow_radius * 2
        glow_height = height + glow_radius * 2

        result = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)
        result.fill((0, 0, 0, 0))

        # Create glow layers
        for radius in range(glow_radius, 0, -1):
            alpha = int(255 * glow_intensity * (radius / glow_radius) * 0.3)
            glow_surf = pygame.Surface((width, height), pygame.SRCALPHA)

            # Create glow outline
            for x in range(width):
                for y in range(height):
                    pixel = surface.get_at((x, y))
                    if pixel[3] > 10:  # Non-transparent
                        # Check if edge
                        is_edge = False
                        for dx in range(-radius, radius + 1):
                            for dy in range(-radius, radius + 1):
                                if dx * dx + dy * dy <= radius * radius:
                                    nx, ny = x + dx, y + dy
                                    if 0 <= nx < width and 0 <= ny < height:
                                        neighbor = surface.get_at((nx, ny))
                                        if neighbor[3] < 10:
                                            is_edge = True
                                            break
                            if is_edge:
                                break

                        if is_edge:
                            glow_surf.set_at((x, y), (*glow_color, alpha))

            # Draw glow layer
            for offset_x in range(-radius, radius + 1):
                for offset_y in range(-radius, radius + 1):
                    if offset_x * offset_x + offset_y * offset_y <= radius * radius:
                        result.blit(
                            glow_surf,
                            (glow_radius + offset_x, glow_radius + offset_y),
                            special_flags=pygame.BLEND_RGBA_MAX,
                        )

        # Draw original on top
        result.blit(surface, (glow_radius, glow_radius))

        return result

    @staticmethod
    def create_enhanced_player_ship(base_surface: pygame.Surface) -> pygame.Surface:
        """
        Create dramatically enhanced player ship with all effects.

        Args:
            base_surface: Original player ship surface

        Returns:
            Enhanced surface with dramatic 3D effects
        """
        try:
            # Apply effects in sequence
            enhanced = base_surface.copy()

            # 1. Add metallic gradient for shiny surface
            enhanced = Enhanced3DEffects.add_metallic_gradient(enhanced, "radial")

            # 2. Add 3D bevel for depth
            enhanced = Enhanced3DEffects.add_3d_bevel(
                enhanced, bevel_size=2, highlight_color=(255, 255, 255), shadow_color=(0, 0, 50)
            )

            # 3. Add outer glow for energy effect
            enhanced = Enhanced3DEffects.add_outer_glow(
                enhanced, glow_color=(100, 150, 255), glow_radius=4, glow_intensity=0.9
            )

            # 4. Add dramatic shadow last
            enhanced = Enhanced3DEffects.create_dramatic_shadow(
                enhanced, offset=(5, 5), color=(0, 0, 50), blur_radius=2
            )

            return enhanced

        except Exception as e:
            logger.error(f"Error creating enhanced player ship: {e}")
            return base_surface

    @staticmethod
    def create_enhanced_enemy_ship(base_surface: pygame.Surface, level: int = 0) -> pygame.Surface:
        """
        Create dramatically enhanced enemy ship with organic effects.

        Args:
            base_surface: Original enemy ship surface
            level: Enemy level for effect variation

        Returns:
            Enhanced surface with dramatic organic 3D effects
        """
        try:
            enhanced = base_surface.copy()

            # 1. Add organic gradient
            enhanced = Enhanced3DEffects.add_metallic_gradient(enhanced, "vertical")

            # 2. Add organic bevel with red tints
            enhanced = Enhanced3DEffects.add_3d_bevel(
                enhanced, bevel_size=2, highlight_color=(255, 150, 150), shadow_color=(50, 0, 0)
            )

            # 3. Add bio-glow for high level enemies
            if level >= 5:
                enhanced = Enhanced3DEffects.add_outer_glow(
                    enhanced, glow_color=(255, 50, 50), glow_radius=3, glow_intensity=0.7
                )

            # 4. Add organic shadow
            enhanced = Enhanced3DEffects.create_dramatic_shadow(
                enhanced, offset=(4, 4), color=(50, 0, 0), blur_radius=2
            )

            return enhanced

        except Exception as e:
            logger.error(f"Error creating enhanced enemy ship: {e}")
            return base_surface
