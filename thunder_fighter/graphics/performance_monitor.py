"""
Performance monitoring and debug tools for pseudo-3D rendering system.

This module provides comprehensive performance tracking, bottleneck detection,
and debug visualization tools for the 3D rendering pipeline.
"""

import time
from collections import deque
from typing import Dict, List, Any, Optional, Tuple

import pygame

from thunder_fighter.config.pseudo_3d_config import (
    DEBUG_3D_CONFIG,
    PERFORMANCE_THRESHOLDS,
    PERFORMANCE_CONFIG,
)
from thunder_fighter.utils.logger import logger


class PerformanceMonitor:
    """
    Comprehensive performance monitoring for 3D rendering system.

    Tracks frame rates, cache performance, rendering statistics, and provides
    performance warnings and optimization suggestions.
    """

    def __init__(self, history_length: int = 300):
        """
        Initialize performance monitor.

        Args:
            history_length: Number of frames to keep in history (5 minutes at 60 FPS)
        """
        self.history_length = history_length

        # Frame timing
        self.frame_times = deque(maxlen=history_length)
        self.frame_start_time = 0.0
        self.last_fps_calculation = time.time()
        self.current_fps = 0.0

        # Performance counters
        self.performance_data = {
            "total_frames": 0,
            "total_render_time": 0.0,
            "total_update_time": 0.0,
            "cache_misses": 0,
            "cache_hits": 0,
            "depth_sorts": 0,
            "sprites_rendered": 0,
            "sprites_culled": 0,
        }

        # Warning tracking
        self.performance_warnings = []
        self.last_warning_time = 0.0
        self.warning_cooldown = 5.0  # 5 seconds between identical warnings

        # Bottleneck detection
        self.bottleneck_thresholds = {
            "frame_time_ms": 20.0,  # Above 20ms (50 FPS)
            "render_time_ms": 10.0,  # Render taking more than 10ms
            "cache_miss_rate": 0.30,  # Cache miss rate above 30%
            "cull_rate": 0.80,  # More than 80% sprites culled
        }

        # Performance mode tracking
        self.suggested_performance_mode = "auto"
        self.last_mode_suggestion = time.time()

        logger.info("PerformanceMonitor initialized")

    def start_frame(self):
        """Mark the start of a new frame."""
        self.frame_start_time = time.time()

    def end_frame(self):
        """Mark the end of a frame and record timing."""
        if self.frame_start_time == 0.0:
            return

        frame_time = (time.time() - self.frame_start_time) * 1000  # Convert to milliseconds
        self.frame_times.append(frame_time)
        self.performance_data["total_frames"] += 1

        # Calculate FPS every second
        current_time = time.time()
        if current_time - self.last_fps_calculation >= 1.0:
            self._calculate_fps()
            self.last_fps_calculation = current_time

        # Check for performance issues
        self._check_performance_warnings(frame_time)

        # Reset frame timer
        self.frame_start_time = 0.0

    def record_render_time(self, render_time_ms: float):
        """Record rendering time for this frame."""
        self.performance_data["total_render_time"] += render_time_ms

    def record_update_time(self, update_time_ms: float):
        """Record update time for this frame."""
        self.performance_data["total_update_time"] += update_time_ms

    def record_cache_hit(self):
        """Record a cache hit."""
        self.performance_data["cache_hits"] += 1

    def record_cache_miss(self):
        """Record a cache miss."""
        self.performance_data["cache_misses"] += 1

    def record_depth_sort(self):
        """Record a depth sorting operation."""
        self.performance_data["depth_sorts"] += 1

    def record_sprite_rendered(self):
        """Record a sprite being rendered."""
        self.performance_data["sprites_rendered"] += 1

    def record_sprite_culled(self):
        """Record a sprite being culled."""
        self.performance_data["sprites_culled"] += 1

    def _calculate_fps(self):
        """Calculate current FPS from recent frame times."""
        if not self.frame_times:
            self.current_fps = 0.0
            return

        # Use recent frames for FPS calculation
        recent_frames = list(self.frame_times)[-60:]  # Last 60 frames
        if recent_frames:
            avg_frame_time_ms = sum(recent_frames) / len(recent_frames)
            self.current_fps = 1000.0 / avg_frame_time_ms if avg_frame_time_ms > 0 else 0.0

    def _check_performance_warnings(self, frame_time_ms: float):
        """Check for performance issues and add warnings."""
        current_time = time.time()

        # Avoid spamming warnings
        if current_time - self.last_warning_time < self.warning_cooldown:
            return

        # Check frame time
        if frame_time_ms > self.bottleneck_thresholds["frame_time_ms"]:
            self._add_warning(f"High frame time: {frame_time_ms:.1f}ms", "frame_time")

        # Check cache performance
        cache_miss_rate = self.get_cache_miss_rate()
        if cache_miss_rate > self.bottleneck_thresholds["cache_miss_rate"]:
            self._add_warning(f"High cache miss rate: {cache_miss_rate:.1%}", "cache")

        # Check cull rate
        cull_rate = self.get_cull_rate()
        if cull_rate > self.bottleneck_thresholds["cull_rate"]:
            self._add_warning(f"High cull rate: {cull_rate:.1%} (may indicate depth issues)", "culling")

    def _add_warning(self, message: str, category: str):
        """Add a performance warning."""
        warning = {
            "message": message,
            "category": category,
            "timestamp": time.time(),
        }
        self.performance_warnings.append(warning)
        self.last_warning_time = time.time()

        # Keep only recent warnings
        if len(self.performance_warnings) > 10:
            self.performance_warnings.pop(0)

        logger.warning(f"Performance warning [{category}]: {message}")

    def get_current_fps(self) -> float:
        """Get current FPS."""
        return self.current_fps

    def get_average_frame_time(self) -> float:
        """Get average frame time in milliseconds."""
        if not self.frame_times:
            return 0.0
        return sum(self.frame_times) / len(self.frame_times)

    def get_cache_hit_rate(self) -> float:
        """Get cache hit rate as percentage from actual image cache."""
        try:
            from thunder_fighter.graphics.image_cache import get_cache_stats
            cache_stats = get_cache_stats()
            if cache_stats and "hit_rate" in cache_stats:
                return cache_stats["hit_rate"]
        except Exception:
            pass

        # Fallback to internal tracking
        total_requests = self.performance_data["cache_hits"] + self.performance_data["cache_misses"]
        if total_requests == 0:
            return 0.0
        return self.performance_data["cache_hits"] / total_requests

    def get_cache_miss_rate(self) -> float:
        """Get cache miss rate as percentage."""
        return 1.0 - self.get_cache_hit_rate()

    def get_cull_rate(self) -> float:
        """Get sprite culling rate."""
        total_sprites = self.performance_data["sprites_rendered"] + self.performance_data["sprites_culled"]
        if total_sprites == 0:
            return 0.0
        return self.performance_data["sprites_culled"] / total_sprites

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        return {
            "fps": {
                "current": self.current_fps,
                "average_frame_time_ms": self.get_average_frame_time(),
                "frame_count": len(self.frame_times),
            },
            "cache": {
                "hit_rate": self.get_cache_hit_rate(),
                "miss_rate": self.get_cache_miss_rate(),
                "total_hits": self.performance_data["cache_hits"],
                "total_misses": self.performance_data["cache_misses"],
            },
            "rendering": {
                "sprites_rendered": self.performance_data["sprites_rendered"],
                "sprites_culled": self.performance_data["sprites_culled"],
                "cull_rate": self.get_cull_rate(),
                "depth_sorts": self.performance_data["depth_sorts"],
            },
            "warnings": {
                "active_warnings": len(self.performance_warnings),
                "recent_warnings": [w["message"] for w in self.performance_warnings[-3:]],
            },
            "totals": {
                "total_frames": self.performance_data["total_frames"],
                "total_render_time": self.performance_data["total_render_time"],
                "total_update_time": self.performance_data["total_update_time"],
            },
        }

    def suggest_performance_mode(self) -> str:
        """Suggest optimal performance mode based on current metrics."""
        current_time = time.time()

        # Only suggest mode changes every 10 seconds
        if current_time - self.last_mode_suggestion < 10.0:
            return self.suggested_performance_mode

        fps = self.current_fps
        cache_hit_rate = self.get_cache_hit_rate()
        avg_frame_time = self.get_average_frame_time()

        # Performance mode logic
        if fps >= 55 and cache_hit_rate >= 0.8 and avg_frame_time <= 15:
            mode = "high"
        elif fps >= 40 and cache_hit_rate >= 0.6 and avg_frame_time <= 22:
            mode = "medium"
        else:
            mode = "low"

        if mode != self.suggested_performance_mode:
            logger.info(f"Performance mode suggestion changed: {self.suggested_performance_mode} -> {mode}")
            self.suggested_performance_mode = mode

        self.last_mode_suggestion = current_time
        return mode

    def reset_statistics(self):
        """Reset all performance statistics."""
        self.frame_times.clear()
        self.performance_data = {key: 0 if isinstance(value, (int, float)) else value
                               for key, value in self.performance_data.items()}
        self.performance_warnings.clear()
        logger.info("Performance statistics reset")


class DebugOverlay:
    """
    Visual debug overlay for 3D rendering system.

    Provides on-screen display of performance metrics, warnings, and
    debug information during development.
    """

    def __init__(self, monitor: PerformanceMonitor):
        """
        Initialize debug overlay.

        Args:
            monitor: Performance monitor instance
        """
        self.monitor = monitor
        self.enabled = DEBUG_3D_CONFIG.get("performance_overlay", False)
        self.font_size = 16
        self.line_height = 20
        self.text_color = (255, 255, 255)
        self.bg_color = (0, 0, 0, 128)  # Semi-transparent black

    def render(self, screen: pygame.Surface):
        """
        Render debug overlay on screen.

        Args:
            screen: Surface to render on
        """
        if not self.enabled or not pygame.font.get_init():
            return

        try:
            # Get performance summary
            summary = self.monitor.get_performance_summary()

            # Create overlay surface
            overlay_width = 300
            overlay_height = 200
            overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
            overlay.fill(self.bg_color)

            # Render text
            font = pygame.font.Font(None, self.font_size)
            y_offset = 10

            # Performance data
            lines = [
                f"FPS: {summary['fps']['current']:.1f}",
                f"Frame Time: {summary['fps']['average_frame_time_ms']:.1f}ms",
                f"Cache Hit: {summary['cache']['hit_rate']:.1%}",
                f"Rendered: {summary['rendering']['sprites_rendered']}",
                f"Culled: {summary['rendering']['sprites_culled']} ({summary['rendering']['cull_rate']:.1%})",
                f"Depth Sorts: {summary['rendering']['depth_sorts']}",
                f"Warnings: {summary['warnings']['active_warnings']}",
            ]

            # Add recent warnings
            if summary['warnings']['recent_warnings']:
                lines.append("Recent Warnings:")
                for warning in summary['warnings']['recent_warnings'][-2:]:
                    lines.append(f"  {warning[:35]}...")

            # Render each line
            for line in lines:
                text_surface = font.render(line, True, self.text_color)
                overlay.blit(text_surface, (10, y_offset))
                y_offset += self.line_height

            # Position overlay in top-right corner
            screen.blit(overlay, (screen.get_width() - overlay_width - 10, 10))

        except Exception as e:
            logger.error(f"Error rendering debug overlay: {e}")

    def toggle(self):
        """Toggle debug overlay visibility."""
        self.enabled = not self.enabled
        logger.info(f"Debug overlay {'enabled' if self.enabled else 'disabled'}")


# Global performance monitor instance
_global_performance_monitor: Optional[PerformanceMonitor] = None
_global_debug_overlay: Optional[DebugOverlay] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _global_performance_monitor
    if _global_performance_monitor is None:
        _global_performance_monitor = PerformanceMonitor()
    return _global_performance_monitor


def get_debug_overlay() -> DebugOverlay:
    """Get the global debug overlay instance."""
    global _global_debug_overlay, _global_performance_monitor
    if _global_debug_overlay is None:
        if _global_performance_monitor is None:
            _global_performance_monitor = PerformanceMonitor()
        _global_debug_overlay = DebugOverlay(_global_performance_monitor)
    return _global_debug_overlay


def reset_performance_monitoring():
    """Reset all performance monitoring data."""
    global _global_performance_monitor
    if _global_performance_monitor:
        _global_performance_monitor.reset_statistics()