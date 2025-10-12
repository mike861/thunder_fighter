"""
Advanced bloom and glow effects for boss sprites.

This module implements industry-standard visual effects techniques
including bloom, rim lighting, and energy effects for boss ships.
Based on popular game development techniques.
"""

import math
from typing import Tuple

import pygame

from thunder_fighter.utils.logger import logger


class BloomBossEffect:
    """Create cinematic boss effects using bloom and glow techniques."""

    @staticmethod
    def create_bloom_glow(surface: pygame.Surface, threshold: int = 128) -> pygame.Surface:
        """
        Create bloom/glow effect using standard game industry technique.

        Args:
            surface: Input surface
            threshold: Brightness threshold for bloom (0-255)

        Returns:
            Surface with bloom effect
        """
        width, height = surface.get_size()

        # Step 1: Extract bright parts
        bright_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Scan for bright pixels
        for y in range(height):
            for x in range(width):
                color = surface.get_at((x, y))
                if len(color) >= 3:
                    brightness = (color[0] + color[1] + color[2]) / 3
                    if brightness > threshold:
                        # Keep only bright parts
                        bright_surface.set_at((x, y), color)

        # Step 2: Create multiple blur levels (simulated bloom)
        bloom_layers = []

        # Different blur sizes for layered glow
        blur_sizes = [2, 4, 8]
        for blur_size in blur_sizes:
            # Downscale for blur
            small_size = (max(1, width // blur_size), max(1, height // blur_size))
            small_bright = pygame.transform.smoothscale(bright_surface, small_size)

            # Apply simple box blur
            blurred = BloomBossEffect._simple_blur(small_bright, 2)

            # Upscale back to original size
            upscaled = pygame.transform.smoothscale(blurred, (width, height))
            bloom_layers.append(upscaled)

        # Step 3: Combine all bloom layers (much more subtle)
        result = surface.copy()
        for i, layer in enumerate(bloom_layers):
            # Very subtle bloom - decreasing intensity for each layer
            layer.set_alpha(20 - i * 5)  # Much lower alpha (20, 15, 10)
            result.blit(layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        return result

    @staticmethod
    def _simple_blur(surface: pygame.Surface, passes: int = 1) -> pygame.Surface:
        """Apply simple box blur to surface."""
        result = surface.copy()
        width, height = surface.get_size()

        for _ in range(passes):
            temp = pygame.Surface((width, height), pygame.SRCALPHA)

            # Simple 3x3 box blur
            for y in range(1, height - 1):
                for x in range(1, width - 1):
                    # Get surrounding pixels
                    colors = []
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            colors.append(result.get_at((x + dx, y + dy)))

                    # Average the colors
                    avg_r = sum(c[0] for c in colors) // 9
                    avg_g = sum(c[1] for c in colors) // 9
                    avg_b = sum(c[2] for c in colors) // 9
                    avg_a = sum(c[3] if len(c) > 3 else 255 for c in colors) // 9

                    temp.set_at((x, y), (avg_r, avg_g, avg_b, avg_a))

            result = temp

        return result

    @staticmethod
    def create_rim_lighting(
        surface: pygame.Surface, rim_color: Tuple[int, int, int] = (100, 150, 255), rim_width: int = 2
    ) -> pygame.Surface:
        """
        Create rim lighting effect (outline glow).

        Args:
            surface: Input surface
            rim_color: Color of the rim light
            rim_width: Width of the rim in pixels

        Returns:
            Surface with rim lighting
        """
        width, height = surface.get_size()
        result = pygame.Surface((width + rim_width * 2, height + rim_width * 2), pygame.SRCALPHA)

        # Create mask from original surface
        mask = pygame.mask.from_surface(surface, threshold=10)

        # Draw expanding outlines for rim effect (subtle)
        for i in range(rim_width, 0, -1):
            # Calculate color intensity based on distance
            intensity = (rim_width - i + 1) / rim_width
            color = (*rim_color, int(30 * intensity))  # Much lower intensity (was 100)

            # Create outline surface
            outline_surf = pygame.Surface((width + i * 2, height + i * 2), pygame.SRCALPHA)

            # Get outline points from mask
            outline_points = mask.outline()

            if len(outline_points) > 2:
                # Scale outline points for this layer
                scaled_points = [(x + i, y + i) for x, y in outline_points]

                # Draw outline
                pygame.draw.polygon(outline_surf, color, scaled_points, 2)

            # Blit to result
            result.blit(outline_surf, (rim_width - i, rim_width - i))

        # Place original on top
        result.blit(surface, (rim_width, rim_width))

        return result

    @staticmethod
    def create_energy_core(surface: pygame.Surface, level: int = 1, pulse_phase: float = 0.0) -> pygame.Surface:
        """
        Create pulsing energy core effect.

        Args:
            surface: Input surface
            level: Boss level (1-3)
            pulse_phase: Animation phase (0-1)

        Returns:
            Surface with energy core effect
        """
        width, height = surface.get_size()
        result = surface.copy()

        # Create energy layer
        energy_layer = pygame.Surface((width, height), pygame.SRCALPHA)

        # Center of the boss
        cx, cy = width // 2, height // 2

        # Level-based colors
        level_colors = {
            1: [(150, 50, 200), (200, 100, 255)],  # Purple
            2: [(50, 100, 200), (100, 150, 255)],  # Blue
            3: [(200, 50, 50), (255, 100, 100)],  # Red
        }

        colors = level_colors.get(level, level_colors[1])

        # Pulsing effect (subtle)
        pulse = 0.9 + 0.1 * math.sin(pulse_phase * math.pi * 2)  # Much smaller pulse range

        # Draw multiple energy rings
        max_radius = min(width, height) // 4  # Smaller radius
        for i in range(3):
            radius = int(max_radius * (1 - i * 0.3) * pulse)
            alpha = 60 - i * 15  # Much lower alpha (was 150-40)

            # Inner glow
            for r in range(radius, 0, -2):
                intensity = r / radius
                color = (
                    int(colors[0][0] * intensity + colors[1][0] * (1 - intensity)),
                    int(colors[0][1] * intensity + colors[1][1] * (1 - intensity)),
                    int(colors[0][2] * intensity + colors[1][2] * (1 - intensity)),
                    int(alpha * intensity),
                )
                pygame.draw.circle(energy_layer, color, (cx, cy), r)

        # Bright core (subtle)
        pygame.draw.circle(energy_layer, (255, 255, 255, 80), (cx, cy), 3)  # Smaller and less bright

        # Apply energy layer
        result.blit(energy_layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        return result

    @staticmethod
    def create_shadow(
        surface: pygame.Surface,
        offset_x: int = 5,
        offset_y: int = 6,
        shadow_color: Tuple[int, int, int] = (0, 0, 30),
        shadow_alpha: int = 60,
    ) -> pygame.Surface:
        """
        Create drop shadow effect.

        Args:
            surface: Input surface
            offset_x: Shadow X offset
            offset_y: Shadow Y offset
            shadow_color: Shadow color
            shadow_alpha: Shadow transparency

        Returns:
            Surface with shadow
        """
        width, height = surface.get_size()

        # Create result with extra space for shadow
        result = pygame.Surface((width + abs(offset_x) + 10, height + abs(offset_y) + 10), pygame.SRCALPHA)

        # Create shadow
        shadow = surface.copy()
        shadow.fill((*shadow_color, 255), special_flags=pygame.BLEND_RGBA_MULT)

        # Apply blur to shadow
        shadow = BloomBossEffect._simple_blur(shadow, 2)
        shadow.set_alpha(shadow_alpha)

        # Position shadow
        shadow_x = offset_x if offset_x > 0 else 0
        shadow_y = offset_y if offset_y > 0 else 0
        result.blit(shadow, (shadow_x + 5, shadow_y + 5))

        # Place original on top
        orig_x = 0 if offset_x > 0 else abs(offset_x)
        orig_y = 0 if offset_y > 0 else abs(offset_y)
        result.blit(surface, (orig_x + 5, orig_y + 5))

        return result

    @staticmethod
    def create_shield_shimmer(
        surface: pygame.Surface, shield_strength: float = 1.0, shimmer_phase: float = 0.0
    ) -> pygame.Surface:
        """
        Create shield shimmer effect.

        Args:
            surface: Input surface
            shield_strength: Shield strength (0-1)
            shimmer_phase: Animation phase for shimmer

        Returns:
            Surface with shield effect
        """
        if shield_strength <= 0:
            return surface

        width, height = surface.get_size()
        result = surface.copy()

        # Create shield layer
        shield_layer = pygame.Surface((width, height), pygame.SRCALPHA)

        # Create hexagonal shield pattern
        hex_size = 15
        for y in range(0, height, hex_size):
            for x in range(0, width, hex_size):
                # Create shimmer wave effect
                wave = math.sin(x * 0.1 + shimmer_phase * 2) * math.cos(y * 0.1 + shimmer_phase * 3)
                intensity = int(25 * shield_strength * (0.5 + 0.5 * wave))  # Reduced from 50

                if intensity > 10:
                    # Draw hexagon-like shape (simplified to diamond)
                    points = [
                        (x + hex_size // 2, y),
                        (x + hex_size, y + hex_size // 2),
                        (x + hex_size // 2, y + hex_size),
                        (x, y + hex_size // 2),
                    ]
                    pygame.draw.polygon(shield_layer, (100, 150, 255, intensity), points, 1)

        # Apply shield layer
        result.blit(shield_layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        return result

    @staticmethod
    def apply_all_effects(surface: pygame.Surface, level: int = 1, animation_time: float = 0.0) -> pygame.Surface:
        """
        Apply all boss effects in sequence.

        Args:
            surface: Base boss surface
            level: Boss level (1-3)
            animation_time: Time for animated effects

        Returns:
            Surface with all effects applied
        """
        try:
            # Start with shadow
            result = BloomBossEffect.create_shadow(surface)

            # Add energy core
            result = BloomBossEffect.create_energy_core(result, level, animation_time)

            # Add rim lighting
            rim_colors = {
                1: (150, 50, 200),  # Purple
                2: (50, 100, 200),  # Blue
                3: (200, 50, 50),  # Red
            }
            rim_color = rim_colors.get(level, rim_colors[1])
            result = BloomBossEffect.create_rim_lighting(result, rim_color)

            # Add bloom/glow (with higher threshold for less glow)
            result = BloomBossEffect.create_bloom_glow(result, threshold=150)

            # Add shield shimmer for higher levels
            if level >= 2:
                shield_strength = 0.15 if level == 2 else 0.25  # Much lower strength
                result = BloomBossEffect.create_shield_shimmer(result, shield_strength, animation_time)

            return result

        except Exception as e:
            logger.error(f"Error applying boss effects: {e}")
            return surface
