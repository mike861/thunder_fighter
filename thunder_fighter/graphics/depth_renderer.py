"""
Depth-aware rendering system for pseudo-3D effects.

This module provides sprite groups and rendering utilities that handle proper
depth sorting and 3D perspective rendering for the pseudo-3D system.
"""

import time
from typing import List, Any, Optional, Dict

import pygame

from thunder_fighter.config.pseudo_3d_config import (
    DEBUG_3D_CONFIG,
    PERFORMANCE_CONFIG,
    PERFORMANCE_THRESHOLDS,
)
from thunder_fighter.graphics.image_cache import reset_frame_counters
from thunder_fighter.utils.logger import logger


class DepthSortedGroup(pygame.sprite.Group):
    """
    Sprite group that renders entities in proper depth order.

    This group automatically sorts sprites by depth (z-coordinate) and provides
    optimized rendering with LOD (Level of Detail) support.
    """

    def __init__(self):
        """Initialize depth-sorted sprite group."""
        super().__init__()
        self._sorted_sprites = []
        self._sort_dirty = True
        self._last_sort_time = 0.0
        self._sort_interval = 0.016  # Sort at most every ~16ms (60 FPS)

        # Performance statistics
        self._render_stats = {
            "rendered": 0,
            "skipped": 0,
            "total": 0,
            "sort_time_ms": 0.0,
            "render_time_ms": 0.0,
            "last_frame_time": time.time(),
        }

        # Frame counter for LOD updates
        self._current_frame = 0

    def add(self, *sprites):
        """
        Add sprites and mark for re-sorting.

        Args:
            *sprites: Sprites to add
        """
        super().add(*sprites)
        self._sort_dirty = True

    def remove(self, *sprites):
        """
        Remove sprites and mark for re-sorting.

        Args:
            *sprites: Sprites to remove
        """
        super().remove(*sprites)
        self._sort_dirty = True

    def _sort_by_depth(self):
        """Sort sprites by depth (farthest first for proper layering)."""
        current_time = time.time()

        # Only sort if needed and enough time has passed
        if not self._sort_dirty or (current_time - self._last_sort_time) < self._sort_interval:
            return

        sort_start = time.time()

        all_sprites = self.sprites()
        self._sorted_sprites = sorted(
            all_sprites,
            key=lambda sprite: getattr(sprite, 'z', 0),
            reverse=True  # Render far to near (painter's algorithm)
        )
        self._sort_dirty = False
        self._last_sort_time = current_time

        # Track sort performance
        sort_time = (time.time() - sort_start) * 1000
        self._render_stats["sort_time_ms"] = sort_time

    def render_with_depth(self, screen: pygame.Surface):
        """
        Render all sprites with depth-aware transformations.

        Args:
            screen: Surface to render on
        """
        render_start = time.time()
        self._current_frame += 1

        # Reset frame counters in cache system
        reset_frame_counters()

        # Sort sprites by depth
        self._sort_by_depth()

        # Record depth sort for performance monitoring
        try:
            from thunder_fighter.graphics.performance_monitor import get_performance_monitor
            monitor = get_performance_monitor()
            monitor.record_depth_sort()
        except ImportError:
            pass  # Performance monitoring not available

        rendered = 0
        skipped = 0

        for sprite in self._sorted_sprites:
            try:
                # Check if sprite should render based on LOD
                if hasattr(sprite, 'should_render') and not sprite.should_render():
                    skipped += 1
                    # Record culled sprite
                    try:
                        monitor.record_sprite_culled()
                    except (NameError, AttributeError):
                        pass
                    continue

                # Use 3D rendering if available
                if hasattr(sprite, 'render_3d'):
                    sprite.render_3d(screen)
                    rendered += 1
                elif hasattr(sprite, 'image') and hasattr(sprite, 'rect') and sprite.image:
                    # Fallback for 2D sprites
                    screen.blit(sprite.image, sprite.rect)
                    rendered += 1
                else:
                    skipped += 1

                # Record rendered sprite
                try:
                    monitor.record_sprite_rendered()
                except (NameError, AttributeError):
                    pass

            except Exception as e:
                logger.error(f"Error rendering sprite {sprite.__class__.__name__}: {e}")
                skipped += 1

        # Update performance statistics
        render_time = (time.time() - render_start) * 1000
        self._render_stats.update({
            "rendered": rendered,
            "skipped": skipped,
            "total": len(self._sorted_sprites),
            "render_time_ms": render_time,
            "last_frame_time": time.time(),
        })

        # Record render time for performance monitoring
        try:
            monitor.record_render_time(render_time)
        except (NameError, AttributeError):
            pass

        # Debug rendering if enabled
        if DEBUG_3D_CONFIG.get("render_depth_zones", False):
            self._render_debug_zones(screen)

        if DEBUG_3D_CONFIG.get("show_depth_values", False):
            self._render_depth_values(screen)

    def update(self, *args):
        """
        Override update to handle depth-based LOD.

        Args:
            *args: Arguments to pass to sprite update methods
        """
        for sprite in self.sprites():
            try:
                if hasattr(sprite, 'should_update_this_frame'):
                    # Use LOD-based update frequency
                    if sprite.should_update_this_frame(self._current_frame):
                        sprite.update(*args)
                elif hasattr(sprite, 'update'):
                    # Standard update for sprites without LOD support
                    sprite.update(*args)
            except Exception as e:
                logger.error(f"Error updating sprite {sprite.__class__.__name__}: {e}")

    def get_render_stats(self) -> Dict[str, Any]:
        """
        Get rendering performance statistics.

        Returns:
            Dictionary with rendering statistics
        """
        total = self._render_stats["total"]
        render_rate = (self._render_stats["rendered"] / total * 100) if total > 0 else 0

        return {
            **self._render_stats,
            "render_rate_percent": render_rate,
            "sprites_count": len(self.sprites()),
            "sort_interval_ms": self._sort_interval * 1000,
            "current_frame": self._current_frame,
        }

    def _render_debug_zones(self, screen: pygame.Surface):
        """
        Render depth zone visualization for debugging.

        Args:
            screen: Surface to render on
        """
        if not pygame.font.get_init():
            return

        try:
            font = pygame.font.Font(None, 24)
            screen_width = screen.get_width()
            screen_height = screen.get_height()

            # Draw depth zone indicators
            zones = [
                (0, 200, "NEAR", (0, 255, 0)),
                (200, 500, "MID", (255, 255, 0)),
                (500, 800, "FAR", (255, 165, 0)),
                (800, 1000, "DISTANT", (255, 0, 0)),
            ]

            y_pos = 10
            for min_depth, max_depth, label, color in zones:
                text = font.render(f"{label}: {min_depth}-{max_depth}", True, color)
                screen.blit(text, (screen_width - 200, y_pos))
                y_pos += 25

        except Exception as e:
            logger.error(f"Error rendering debug zones: {e}")

    def _render_depth_values(self, screen: pygame.Surface):
        """
        Render depth values on sprites for debugging.

        Args:
            screen: Surface to render on
        """
        if not pygame.font.get_init():
            return

        try:
            font = pygame.font.Font(None, 16)

            # Show depth values for first 10 sprites to avoid performance impact
            for sprite in self._sorted_sprites[:10]:
                if hasattr(sprite, 'z') and hasattr(sprite, 'rect'):
                    depth_text = font.render(f"Z:{sprite.z:.0f}", True, (255, 255, 0))
                    text_pos = (sprite.rect.x, max(0, sprite.rect.y - 18))
                    screen.blit(depth_text, text_pos)

        except Exception as e:
            logger.error(f"Error rendering depth values: {e}")

    def optimize_performance(self):
        """Optimize group performance by adjusting settings based on load."""
        stats = self.get_render_stats()

        # Adjust sort interval based on sprite count
        sprite_count = len(self.sprites())
        if sprite_count > 50:
            self._sort_interval = 0.033  # 30 FPS for high sprite counts
        elif sprite_count > 20:
            self._sort_interval = 0.022  # 45 FPS for medium sprite counts
        else:
            self._sort_interval = 0.016  # 60 FPS for low sprite counts


class DepthRenderer:
    """
    Main depth rendering coordinator that manages multiple sprite groups
    and provides global rendering performance monitoring.
    """

    def __init__(self):
        """Initialize depth renderer."""
        self.enabled = True
        self.debug_mode = DEBUG_3D_CONFIG.get("performance_overlay", False)
        self.performance_mode = "auto"

        # Performance monitoring
        self._performance_history = []
        self._last_performance_check = time.time()
        self._frame_times = []
        self._max_history_length = 60  # Keep 1 second of history at 60 FPS

        logger.info("DepthRenderer initialized")

    def render_scene(self, screen: pygame.Surface, sprite_groups: List[DepthSortedGroup]):
        """
        Render entire scene with depth sorting across all groups.

        Args:
            screen: Surface to render on
            sprite_groups: List of depth-sorted sprite groups
        """
        frame_start = time.time()

        if not self.enabled:
            # Fallback to standard rendering
            for group in sprite_groups:
                group.draw(screen)
            return

        # Option 1: Render each group separately (maintains group organization)
        for group in sprite_groups:
            if hasattr(group, 'render_with_depth'):
                group.render_with_depth(screen)
            else:
                group.draw(screen)

        # Track frame performance
        frame_time = (time.time() - frame_start) * 1000
        self._frame_times.append(frame_time)

        # Keep only recent frame times
        if len(self._frame_times) > self._max_history_length:
            self._frame_times.pop(0)

        # Check performance periodically
        current_time = time.time()
        if current_time - self._last_performance_check > 1.0:  # Every second
            self._check_performance()
            self._last_performance_check = current_time

        # Render debug overlay if enabled
        if self.debug_mode:
            self._render_performance_overlay(screen, sprite_groups)

    def render_scene_globally_sorted(self, screen: pygame.Surface, sprite_groups: List[DepthSortedGroup]):
        """
        Alternative rendering method that sorts all sprites globally.

        Args:
            screen: Surface to render on
            sprite_groups: List of sprite groups
        """
        frame_start = time.time()

        # Collect all sprites from all groups
        all_sprites = []
        for group in sprite_groups:
            all_sprites.extend(group.sprites())

        # Sort by depth globally
        all_sprites.sort(key=lambda sprite: getattr(sprite, 'z', 0), reverse=True)

        # Render in depth order
        rendered = 0
        for sprite in all_sprites:
            try:
                if hasattr(sprite, 'should_render') and not sprite.should_render():
                    continue

                if hasattr(sprite, 'render_3d'):
                    sprite.render_3d(screen)
                    rendered += 1
                elif hasattr(sprite, 'image') and hasattr(sprite, 'rect') and sprite.image:
                    screen.blit(sprite.image, sprite.rect)
                    rendered += 1

            except Exception as e:
                logger.error(f"Error in global sprite rendering: {e}")

        # Track performance
        frame_time = (time.time() - frame_start) * 1000
        self._frame_times.append(frame_time)

        if len(self._frame_times) > self._max_history_length:
            self._frame_times.pop(0)

    def _check_performance(self):
        """Check performance and adjust settings if needed."""
        if not self._frame_times:
            return

        avg_frame_time = sum(self._frame_times) / len(self._frame_times)
        fps = 1000.0 / avg_frame_time if avg_frame_time > 0 else 0

        # Performance warnings
        if fps < PERFORMANCE_THRESHOLDS["fps_warning"]:
            logger.warning(f"Low FPS detected: {fps:.1f}")

        if fps < PERFORMANCE_THRESHOLDS["fps_critical"]:
            logger.critical(f"Critical FPS drop: {fps:.1f}")
            # Could trigger automatic performance mode switching here

        # Store performance data
        self._performance_history.append({
            "timestamp": time.time(),
            "avg_frame_time_ms": avg_frame_time,
            "fps": fps,
        })

        # Keep only recent history
        if len(self._performance_history) > 300:  # 5 minutes at 1-second intervals
            self._performance_history.pop(0)

    def _render_performance_overlay(self, screen: pygame.Surface, sprite_groups: List[DepthSortedGroup]):
        """
        Render performance monitoring overlay.

        Args:
            screen: Surface to render on
            sprite_groups: Sprite groups for statistics
        """
        if not pygame.font.get_init():
            return

        try:
            font = pygame.font.Font(None, 20)
            y_offset = 10

            # Frame rate information
            if self._frame_times:
                avg_frame_time = sum(self._frame_times) / len(self._frame_times)
                fps = 1000.0 / avg_frame_time if avg_frame_time > 0 else 0
                fps_text = font.render(f"FPS: {fps:.1f} ({avg_frame_time:.1f}ms)", True, (255, 255, 255))
                screen.blit(fps_text, (10, y_offset))
                y_offset += 25

            # Sprite group statistics
            total_sprites = sum(len(group.sprites()) for group in sprite_groups)
            sprite_text = font.render(f"Sprites: {total_sprites}", True, (255, 255, 255))
            screen.blit(sprite_text, (10, y_offset))
            y_offset += 25

            # Cache statistics (if available)
            try:
                from thunder_fighter.graphics.image_cache import get_cache_stats
                cache_stats = get_cache_stats()
                if cache_stats:
                    hit_rate = cache_stats.get("hit_rate_percent", 0)
                    cache_text = font.render(f"Cache: {hit_rate:.1f}%", True, (255, 255, 255))
                    screen.blit(cache_text, (10, y_offset))
                    y_offset += 25
            except ImportError:
                pass

        except Exception as e:
            logger.error(f"Error rendering performance overlay: {e}")

    def set_performance_mode(self, mode: str):
        """
        Set performance mode for depth rendering.

        Args:
            mode: Performance mode ("high", "medium", "low", "auto")
        """
        self.performance_mode = mode
        logger.info(f"Depth renderer performance mode set to: {mode}")

    def toggle_debug(self):
        """Toggle debug visualization."""
        self.debug_mode = not self.debug_mode
        logger.info(f"Depth renderer debug mode: {self.debug_mode}")

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive performance statistics.

        Returns:
            Dictionary with performance data
        """
        if not self._frame_times:
            return {"fps": 0, "frame_time_ms": 0}

        avg_frame_time = sum(self._frame_times) / len(self._frame_times)
        fps = 1000.0 / avg_frame_time if avg_frame_time > 0 else 0

        return {
            "fps": fps,
            "avg_frame_time_ms": avg_frame_time,
            "frame_samples": len(self._frame_times),
            "performance_mode": self.performance_mode,
            "debug_mode": self.debug_mode,
            "enabled": self.enabled,
        }

    def reset_performance_data(self):
        """Reset all performance tracking data."""
        self._frame_times.clear()
        self._performance_history.clear()
        self._last_performance_check = time.time()
        logger.info("Performance data reset")