"""
LRU cache system for scaled images to optimize 3D rendering performance.

This module provides an efficient caching system for scaled images to prevent
repeated expensive scaling operations during real-time 3D rendering.
"""

import time
from collections import OrderedDict
from typing import Any, Dict, Optional, Tuple

import pygame

from thunder_fighter.config.pseudo_3d_config import (
    PERFORMANCE_CONFIG,
    PERFORMANCE_THRESHOLDS,
    get_quantized_scale,
)
from thunder_fighter.utils.logger import logger
from thunder_fighter.graphics.effects.runtime_styles import apply_arcade_rim_fast


class ScalingCache:
    """
    LRU cache for scaled images with performance optimization and monitoring.

    This cache system is designed to handle the frequent image scaling operations
    required for pseudo-3D rendering while maintaining optimal performance.
    """

    def __init__(self, max_size: Optional[int] = None, scale_precision: Optional[int] = None):
        """Initialize scaling cache."""
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size or PERFORMANCE_CONFIG["image_cache_size"]
        self.scale_precision = scale_precision or PERFORMANCE_CONFIG["scale_precision"]

        # Performance statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "memory_usage_estimate": 0,
            "total_requests": 0,
            "creation_time_total": 0.0,
            "last_cleanup_time": time.time(),
        }

        # Performance monitoring
        self.generation_count_this_frame = 0
        self.frame_reset_time = time.time()

        logger.info(f"ScalingCache initialized with max_size={self.max_size}, precision={self.scale_precision}")

    def get_scaled_image(self, original: pygame.Surface, scale: float) -> Optional[pygame.Surface]:
        """Get cached scaled image or create new one."""
        self.stats["total_requests"] += 1

        try:
            can_generate = self._check_generation_limits()
        except AttributeError:
            can_generate = True
        if not can_generate:
            self.stats["misses"] += 1
            return None

        if scale <= 0.01:
            return None

        quantized_scale = get_quantized_scale(scale)
        if quantized_scale <= 0.01:
            return None

        try:
            cache_key = self._create_cache_key(original, quantized_scale)
        except AttributeError:
            cache_key = (id(original), original.get_width(), original.get_height(), quantized_scale)

        if cache_key in self.cache:
            self.cache.move_to_end(cache_key)
            self.stats["hits"] += 1
            return self.cache[cache_key]

        self.stats["misses"] += 1
        scaled_image = self._create_scaled_image(original, quantized_scale)

        if scaled_image:
            self._add_to_cache(cache_key, scaled_image)
            self.generation_count_this_frame += 1

        return scaled_image

    def _create_cache_key(self, surface: pygame.Surface, scale: float) -> Tuple[int, int, int, float]:
        """Create cache key from surface and scale using enhanced content-based approach."""
        try:
            w, h = surface.get_width(), surface.get_height()
            if w > 0 and h > 0:
                sample_points = [
                    surface.get_at((0, 0)),
                    surface.get_at((w - 1, 0)),
                    surface.get_at((0, h - 1)),
                    surface.get_at((w - 1, h - 1)),
                    surface.get_at((w // 2, h // 2)),
                    surface.get_at((w // 2, 0)),
                    surface.get_at((w // 2, h - 1)),
                    surface.get_at((0, h // 2)),
                    surface.get_at((w - 1, h // 2)),
                ]
                if w > 4 and h > 4:
                    sample_points.extend(
                        [
                            surface.get_at((w // 4, h // 4)),
                            surface.get_at((3 * w // 4, h // 4)),
                            surface.get_at((w // 4, 3 * h // 4)),
                            surface.get_at((3 * w // 4, 3 * h // 4)),
                        ]
                    )
                content_hash = hash(tuple(sample_points))
            else:
                content_hash = 0
        except Exception:
            content_hash = id(surface)

        return (
            content_hash,
            surface.get_width(),
            surface.get_height(),
            scale,
        )

    def _check_generation_limits(self) -> bool:
        """Check if we can generate new scaled images this frame."""
        current_time = time.time()
        if current_time - self.frame_reset_time > 0.016:
            self.generation_count_this_frame = 0
            self.frame_reset_time = current_time

        max_generations = PERFORMANCE_CONFIG["max_scale_generations_per_frame"]
        return self.generation_count_this_frame < max_generations

    def _create_scaled_image(self, original: pygame.Surface, scale: float) -> Optional[pygame.Surface]:
        """Create a new scaled image with performance tracking."""
        start_time = time.time()

        try:
            original_width = original.get_width()
            original_height = original.get_height()

            new_width = max(1, int(original_width * scale))
            new_height = max(1, int(original_height * scale))

            scaled_image = pygame.transform.scale(original, (new_width, new_height))

            creation_time = time.time() - start_time
            self.stats["creation_time_total"] += creation_time

            return scaled_image

        except Exception as e:
            logger.error(f"Error creating scaled image: {e}")
            return None

    def _should_use_smooth_scaling(self) -> bool:
        hit_rate = self.get_hit_rate()
        recent_generations = self.generation_count_this_frame
        return (
            hit_rate > 0.85
            and recent_generations < 2
            and len(self.cache) < self.max_size * 0.8
        )

    def _add_to_cache(self, cache_key: Tuple, image: pygame.Surface):
        while len(self.cache) >= self.max_size:
            oldest_key, oldest_image = self.cache.popitem(last=False)
            self.stats["evictions"] += 1
            if oldest_image:
                memory_size = oldest_image.get_width() * oldest_image.get_height() * 4
                self.stats["memory_usage_estimate"] -= memory_size

        self.cache[cache_key] = image

        if image:
            memory_size = image.get_width() * image.get_height() * 4
            self.stats["memory_usage_estimate"] += memory_size

    def clear(self):
        self.cache.clear()
        self.stats["memory_usage_estimate"] = 0
        logger.info("Image scaling cache cleared")

    def get_hit_rate(self) -> float:
        total_requests = self.stats["hits"] + self.stats["misses"]
        return (self.stats["hits"] / total_requests) if total_requests > 0 else 0.0

    def get_stats(self) -> Dict[str, Any]:
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.get_hit_rate()

        avg_creation_time = (
            self.stats["creation_time_total"] / max(1, self.stats["misses"])
        ) * 1000

        memory_mb = self.stats["memory_usage_estimate"] / (1024 * 1024)

        return {
            "cache_size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": hit_rate,
            "hit_rate_percent": hit_rate * 100,
            "total_requests": total_requests,
            "generation_count_this_frame": self.generation_count_this_frame,
            "avg_creation_time_ms": avg_creation_time,
            "memory_usage_mb": memory_mb,
            "evictions": self.stats["evictions"],
            **self.stats,
        }

    def optimize(self):
        current_time = time.time()
        if current_time - self.stats["last_cleanup_time"] < 5.0:
            return

        initial_size = len(self.cache)
        if len(self.cache) > self.max_size * 0.8:
            remove_count = len(self.cache) // 4
            for _ in range(remove_count):
                if self.cache:
                    oldest_key, oldest_image = self.cache.popitem(last=False)
                    if oldest_image:
                        memory_size = oldest_image.get_width() * oldest_image.get_height() * 4
                        self.stats["memory_usage_estimate"] -= memory_size
                    self.stats["evictions"] += 1

        self.stats["last_cleanup_time"] = current_time
        removed_count = initial_size - len(self.cache)
        if removed_count > 0:
            logger.debug(f"Cache optimized: removed {removed_count} entries")

    def is_performance_warning(self) -> bool:
        hit_rate = self.get_hit_rate()
        memory_mb = self.stats["memory_usage_estimate"] / (1024 * 1024)
        return (
            hit_rate < (1.0 - PERFORMANCE_THRESHOLDS["cache_miss_rate_warning"])
            or memory_mb > PERFORMANCE_THRESHOLDS["memory_warning_mb"]
            or self.generation_count_this_frame > PERFORMANCE_CONFIG["max_scale_generations_peak"]
        )

    def get_performance_warnings(self) -> list:
        warnings = []
        hit_rate = self.get_hit_rate()
        memory_mb = self.stats["memory_usage_estimate"] / (1024 * 1024)

        if hit_rate < (1.0 - PERFORMANCE_THRESHOLDS["cache_miss_rate_warning"]):
            warnings.append(f"Low cache hit rate: {hit_rate:.1%}")
        if memory_mb > PERFORMANCE_THRESHOLDS["memory_warning_mb"]:
            warnings.append(f"High memory usage: {memory_mb:.1f} MB")
        if self.generation_count_this_frame > PERFORMANCE_CONFIG["max_scale_generations_peak"]:
            warnings.append(
                f"High scaling generation rate: {self.generation_count_this_frame}/frame"
            )
        return warnings


class StyledImageCache:
    """LRU cache for styled (postprocessed) scaled images."""

    def __init__(self, max_size: int = 512):
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size

    def _evict_if_needed(self):
        while len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

    def get_arcade_rim(
        self,
        scaled_surface: pygame.Surface,
        *,
        shadow_offset: tuple[int, int],
        shadow_alpha: int,
        rim_alpha: int,
        rim_radius: int,
    ) -> pygame.Surface:
        key = (id(scaled_surface), "arcade_rim", shadow_offset, shadow_alpha, rim_alpha, rim_radius)
        surf = self.cache.get(key)
        if surf is not None:
            self.cache.move_to_end(key)
            return surf

        styled = apply_arcade_rim_fast(
            scaled_surface,
            shadow_offset=shadow_offset,
            shadow_alpha=shadow_alpha,
            rim_alpha=rim_alpha,
            rim_radius=rim_radius,
        )
        self.cache[key] = styled
        self._evict_if_needed()
        return styled


# Global cache instance
_global_scaling_cache: Optional[ScalingCache] = None
_global_styled_cache: Optional[StyledImageCache] = None


def get_scaling_cache() -> ScalingCache:
    """
    Get the global scaling cache instance.

    Returns:
        Global ScalingCache instance
    """
    global _global_scaling_cache
    if _global_scaling_cache is None:
        _global_scaling_cache = ScalingCache()
    else:
        # If a stale instance is present (from older code), replace it
        required_attrs = (
            "get_scaled_image",
            "_create_cache_key",
            "_check_generation_limits",
            "_create_scaled_image",
        )
        if not all(hasattr(_global_scaling_cache, a) for a in required_attrs):
            _global_scaling_cache = ScalingCache()
    return _global_scaling_cache


def get_styled_cache() -> StyledImageCache:
    global _global_styled_cache
    if _global_styled_cache is None:
        _global_styled_cache = StyledImageCache()
    return _global_styled_cache


def clear_scaling_cache():
    """Clear the global scaling cache."""
    global _global_scaling_cache
    if _global_scaling_cache:
        _global_scaling_cache.clear()
    # Also clear styled cache for consistency
    global _global_styled_cache
    if _global_styled_cache:
        _global_styled_cache.cache.clear()


def get_cache_stats() -> Dict[str, Any]:
    """
    Get global cache statistics.

    Returns:
        Cache statistics dictionary
    """
    global _global_scaling_cache
    if _global_scaling_cache:
        # Backward-compatibility: guard if instance lacks get_stats
        if hasattr(_global_scaling_cache, "get_stats"):
            return _global_scaling_cache.get_stats()
        else:
            try:
                # Minimal snapshot from known fields
                return {
                    "cache_size": len(getattr(_global_scaling_cache, "cache", {})),
                    "max_size": getattr(_global_scaling_cache, "max_size", 0),
                    "hit_rate_percent": 0.0,
                    "total_requests": getattr(_global_scaling_cache, "stats", {}).get("total_requests", 0),
                }
            except Exception:
                return {}
    return {}


def optimize_cache():
    """Optimize the global cache."""
    global _global_scaling_cache
    if _global_scaling_cache:
        _global_scaling_cache.optimize()


def reset_frame_counters():
    """Reset per-frame counters (call at start of each frame)."""
    global _global_scaling_cache
    if _global_scaling_cache:
        _global_scaling_cache.generation_count_this_frame = 0
        _global_scaling_cache.frame_reset_time = time.time()
