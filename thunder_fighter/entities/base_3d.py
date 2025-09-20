"""
3D-aware base entity classes for pseudo-3D rendering.

This module provides the foundation classes for entities that support depth-based
rendering, scaling, and perspective effects while maintaining compatibility with
the existing 2D entity system.
"""

import math
from typing import Tuple

import pygame

from thunder_fighter.config.pseudo_3d_config import (
    DEPTH_SETTINGS,
    VISUAL_EFFECTS_CONFIG,
    get_lod_level,
    get_quantized_scale,
    get_update_frequency,
    should_render_entity,
)
from thunder_fighter.constants import HEIGHT, WIDTH
from thunder_fighter.entities.base import GameObject
from thunder_fighter.utils.logger import logger


class GameObject3D(GameObject):
    """
    Base 3D-aware game object with depth support.

    Extends the base GameObject class to add depth (z-coordinate) support,
    perspective scaling, and depth-based visual effects while maintaining
    backward compatibility with 2D rendering.
    """

    def __init__(self, x: float, y: float, width: int, height: int, z: float = 0.0):
        """
        Initialize 3D game object.

        Args:
            x: X position
            y: Y position
            width: Object width
            height: Object height
            z: Depth coordinate (0=nearest, 1000=farthest)
        """
        super().__init__(x, y, width, height)
        self.z = z
        self.perspective_enabled = True

        # Performance caching
        self._cache_scale = None
        self._cache_screen_pos = None
        self._cache_visual_size = None
        self._cache_z = None
        self._cache_dirty = True

        # Depth configuration (loaded from config)
        self.depth_factor = DEPTH_SETTINGS["depth_factor"]
        self.vanish_point = (
            WIDTH * DEPTH_SETTINGS["vanish_point_x"],
            HEIGHT * DEPTH_SETTINGS["vanish_point_y"]
        )
        self.perspective_x_factor = DEPTH_SETTINGS["perspective_x_factor"]
        self.perspective_y_factor = DEPTH_SETTINGS["perspective_y_factor"]

        # LOD and update frequency tracking
        self._lod_counter = 0
        self._last_update_frame = 0

    def get_depth_scale(self) -> float:
        """
        Calculate perspective scaling factor based on depth.

        Returns:
            Scale factor (1.0 = normal size, <1.0 = smaller/distant)
        """
        if self._cache_scale is None or self._cache_dirty:
            # Linear perspective formula with configurable depth factor
            raw_scale = 1.0 / (1.0 + self.z * self.depth_factor)
            # Quantize scale for cache optimization
            self._cache_scale = get_quantized_scale(raw_scale)
        return self._cache_scale

    def get_screen_position(self) -> Tuple[float, float]:
        """
        Calculate perspective-adjusted screen position.

        Returns:
            Screen position tuple (x, y)
        """
        if self._cache_screen_pos is None or self._cache_dirty:
            if not self.perspective_enabled:
                self._cache_screen_pos = (self.x, self.y)
            else:
                depth_factor = self.z / 1000.0
                screen_x = self.x + (self.vanish_point[0] - self.x) * depth_factor * self.perspective_x_factor
                screen_y = self.y + (self.vanish_point[1] - self.y) * depth_factor * self.perspective_y_factor
                self._cache_screen_pos = (screen_x, screen_y)
        return self._cache_screen_pos

    def get_visual_size(self) -> Tuple[int, int]:
        """
        Get scaled size for rendering.

        Returns:
            Visual size tuple (width, height)
        """
        if self._cache_visual_size is None or self._cache_dirty:
            scale = self.get_depth_scale()
            self._cache_visual_size = (
                max(1, int(self.width * scale)),
                max(1, int(self.height * scale))
            )
        return self._cache_visual_size

    def set_depth(self, z: float):
        """
        Update depth and invalidate cache.

        Args:
            z: New depth value
        """
        # Only update if change is significant (performance optimization)
        if abs(self.z - z) > 0.1:
            self.z = z
            self._invalidate_cache()

    def _invalidate_cache(self):
        """Mark all cached values as dirty."""
        self._cache_dirty = True
        self._cache_scale = None
        self._cache_screen_pos = None
        self._cache_visual_size = None

    def should_render(self) -> bool:
        """
        Determine if entity should be rendered based on size/distance.

        Returns:
            True if entity should be rendered
        """
        scale = self.get_depth_scale()
        visual_size = self.get_visual_size()
        return should_render_entity(scale, visual_size)

    def get_lod_level(self) -> str:
        """
        Get current level of detail.

        Returns:
            LOD level: "high", "medium", or "low"
        """
        scale = self.get_depth_scale()
        return get_lod_level(scale)

    def should_update_this_frame(self, current_frame: int) -> bool:
        """
        Determine if entity should update this frame based on LOD.

        Args:
            current_frame: Current frame number

        Returns:
            True if entity should update this frame
        """
        scale = self.get_depth_scale()
        update_freq = get_update_frequency(scale)

        if update_freq >= 1.0:
            return True

        # Check if enough frames have passed based on update frequency
        frames_since_last_update = current_frame - self._last_update_frame
        required_frame_interval = int(1.0 / update_freq)

        if frames_since_last_update >= required_frame_interval:
            self._last_update_frame = current_frame
            return True

        return False

    def get_fog_intensity(self) -> float:
        """
        Calculate fog intensity based on depth.

        Returns:
            Fog intensity (0.0 = no fog, 1.0 = maximum fog)
        """
        if not VISUAL_EFFECTS_CONFIG["fog_enabled"]:
            return 0.0

        scale = self.get_depth_scale()
        fog_start = VISUAL_EFFECTS_CONFIG["fog_start_distance"]

        if scale >= fog_start:
            return 0.0

        # Linear fog falloff
        fog_intensity = (fog_start - scale) / fog_start
        return min(1.0, fog_intensity)


class Entity3D(GameObject3D):
    """
    3D-aware entity with perspective rendering and depth movement.

    Extends GameObject3D to add movement in the depth dimension and
    specialized rendering methods for 3D effects.
    """

    def __init__(self, x: float, y: float, width: int, height: int, z: float = 0.0):
        """
        Initialize 3D entity.

        Args:
            x: X position
            y: Y position
            width: Entity width
            height: Entity height
            z: Depth coordinate
        """
        super().__init__(x, y, width, height, z)
        self.z_velocity = 0.0  # Depth movement speed

        # Depth animation support
        self.depth_oscillation_enabled = False
        self.depth_oscillation_phase = 0.0
        self.depth_oscillation_amplitude = 0.0
        self.depth_oscillation_frequency = 2.0

        # Performance tracking
        self._render_stats = {
            "rendered_frames": 0,
            "skipped_frames": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }

    def update(self, dt: float):
        """
        Update entity with depth movement and perspective effects.

        Args:
            dt: Delta time in seconds
        """
        # Standard position update
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

        # Depth movement and oscillation
        new_z = self.z
        depth_changed = False

        # Apply z_velocity movement
        if self.z_velocity != 0:
            new_z += self.z_velocity * dt
            depth_changed = True

        # Apply depth oscillation if enabled (independent of z_velocity)
        if self.depth_oscillation_enabled:
            self.depth_oscillation_phase += dt * self.depth_oscillation_frequency * 2 * math.pi
            oscillation = math.sin(self.depth_oscillation_phase) * self.depth_oscillation_amplitude
            new_z += oscillation
            depth_changed = True

        # Update depth if any changes occurred
        if depth_changed:
            self.set_depth(new_z)

        # Update rect for collision detection (use screen position)
        screen_pos = self.get_screen_position()
        visual_size = self.get_visual_size()

        # Update rect to match visual representation
        self.rect.x = int(screen_pos[0] - visual_size[0] // 2)
        self.rect.y = int(screen_pos[1] - visual_size[1] // 2)
        self.rect.width = visual_size[0]
        self.rect.height = visual_size[1]

    def render_3d(self, screen: pygame.Surface):
        """
        Render entity with 3D perspective effects.

        Args:
            screen: Surface to render on
        """
        if not self.should_render() or not self.image:
            self._render_stats["skipped_frames"] += 1
            return

        try:
            # Get cached values
            scale = self.get_depth_scale()
            screen_pos = self.get_screen_position()
            visual_size = self.get_visual_size()

            # Get scaled image from cache
            from thunder_fighter.graphics.image_cache import get_scaling_cache
            cache = get_scaling_cache()
            scaled_image = cache.get_scaled_image(self.image, scale)

            if scaled_image:
                self._render_stats["cache_hits"] += 1

                # Apply depth effects
                final_image = self._apply_depth_effects(scaled_image, scale)

                # Calculate centered render position
                render_x = screen_pos[0] - visual_size[0] // 2
                render_y = screen_pos[1] - visual_size[1] // 2

                screen.blit(final_image, (render_x, render_y))
                self._render_stats["rendered_frames"] += 1
            else:
                self._render_stats["cache_misses"] += 1
                # Fallback to standard rendering
                self._fallback_render(screen)

        except Exception as e:
            logger.error(f"Error in 3D rendering for {self.__class__.__name__}: {e}")
            self._fallback_render(screen)

    def _apply_depth_effects(self, image: pygame.Surface, scale: float) -> pygame.Surface:
        """
        Apply fog and depth-based visual effects.

        Args:
            image: Source image
            scale: Current scale factor

        Returns:
            Image with depth effects applied
        """
        fog_intensity = self.get_fog_intensity()

        if fog_intensity <= 0.1:
            return image  # No significant fog

        try:
            # Create fog overlay
            fog_alpha = int(fog_intensity * VISUAL_EFFECTS_CONFIG["fog_intensity_max"])
            fog_color = VISUAL_EFFECTS_CONFIG["fog_color"]

            # Create fog surface with alpha
            fog_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
            fog_surface.fill((*fog_color, fog_alpha))

            # Apply fog blend
            result = image.copy()
            result.blit(fog_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)

            return result

        except Exception as e:
            logger.warning(f"Error applying depth effects: {e}")
            return image

    def _fallback_render(self, screen: pygame.Surface):
        """
        Fallback to standard 2D rendering.

        Args:
            screen: Surface to render on
        """
        if hasattr(self, 'render') and self.image and self.rect:
            self.render(screen)

    def set_z_velocity(self, z_velocity: float):
        """
        Set depth movement speed.

        Args:
            z_velocity: Depth velocity (negative = toward player)
        """
        self.z_velocity = z_velocity

    def enable_depth_oscillation(self, amplitude: float, frequency: float = 2.0):
        """
        Enable depth oscillation for visual effect.

        Args:
            amplitude: Oscillation amplitude
            frequency: Oscillation frequency in Hz
        """
        self.depth_oscillation_enabled = True
        self.depth_oscillation_amplitude = amplitude
        self.depth_oscillation_frequency = frequency
        self.depth_oscillation_phase = 0.0

    def disable_depth_oscillation(self):
        """Disable depth oscillation."""
        self.depth_oscillation_enabled = False

    def get_render_stats(self) -> dict:
        """
        Get rendering performance statistics.

        Returns:
            Dictionary with rendering statistics
        """
        total_frames = self._render_stats["rendered_frames"] + self._render_stats["skipped_frames"]
        render_rate = (self._render_stats["rendered_frames"] / total_frames * 100) if total_frames > 0 else 0

        total_cache_attempts = self._render_stats["cache_hits"] + self._render_stats["cache_misses"]
        cache_hit_rate = (self._render_stats["cache_hits"] / total_cache_attempts * 100) if total_cache_attempts > 0 else 0

        return {
            **self._render_stats,
            "render_rate_percent": render_rate,
            "cache_hit_rate_percent": cache_hit_rate,
        }

    def reset_stats(self):
        """Reset performance statistics."""
        self._render_stats = {
            "rendered_frames": 0,
            "skipped_frames": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }

    def render(self, screen: pygame.Surface):
        """
        Standard 2D render method for compatibility.

        This provides backward compatibility with 2D rendering. Subclasses
        can override this method or use render_3d() for enhanced 3D effects.
        """
        if self.image and hasattr(self, 'rect'):
            screen.blit(self.image, self.rect)
        elif not self.image:
            # For testing: draw a simple rectangle if no image is available
            if hasattr(self, 'rect'):
                pygame.draw.rect(screen, (255, 0, 255), self.rect, 2)


def upgrade_to_3d(entity: 'GameObject', z: float = 0.0) -> Entity3D:
    """
    Upgrade a 2D entity to 3D capabilities.

    This provides backward compatibility during the transition phase.

    Args:
        entity: 2D entity to upgrade
        z: Initial depth value

    Returns:
        New 3D entity with copied properties
    """
    try:
        # Create new 3D entity with same properties
        entity_3d = Entity3D(entity.x, entity.y, entity.width, entity.height, z)

        # Copy relevant attributes
        entity_3d.velocity_x = entity.velocity_x
        entity_3d.velocity_y = entity.velocity_y
        entity_3d.health = entity.health
        entity_3d.max_health = entity.max_health
        entity_3d.active = entity.active

        # Copy image and rect if they exist
        if hasattr(entity, 'image'):
            entity_3d.image = entity.image
        if hasattr(entity, 'rect'):
            entity_3d.rect = entity.rect.copy()

        logger.debug(f"Upgraded {entity.__class__.__name__} to 3D at depth {z}")
        return entity_3d

    except Exception as e:
        logger.error(f"Error upgrading entity to 3D: {e}")
        raise
