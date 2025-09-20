"""
LRU cache system for scaled images to optimize 3D rendering performance.

This module provides an efficient caching system for scaled images to prevent
repeated expensive scaling operations during real-time 3D rendering.
"""

import time
from collections import OrderedDict
from typing import Dict, Tuple, Optional, Any

import pygame

from thunder_fighter.config.pseudo_3d_config import (
    PERFORMANCE_CONFIG,
    PERFORMANCE_THRESHOLDS,
    get_quantized_scale,
)
from thunder_fighter.utils.logger import logger


class ScalingCache:
    """
    LRU cache for scaled images with performance optimization and monitoring.

    This cache system is designed to handle the frequent image scaling operations
    required for pseudo-3D rendering while maintaining optimal performance.
    """

    def __init__(self, max_size: Optional[int] = None, scale_precision: Optional[int] = None):
        """
        Initialize scaling cache.

        Args:
            max_size: Maximum number of cached images
            scale_precision: Decimal places for scale quantization
        """
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
        """
        Get cached scaled image or create new one.

        Args:
            original: Original image surface
            scale: Scale factor

        Returns:
            Scaled image surface or None if scale is too small
        """
        self.stats["total_requests"] += 1

        # Check frame-based generation limits
        if not self._check_generation_limits():
            self.stats["misses"] += 1
            return None

        # Validate inputs
        if scale <= 0.01:
            return None

        # Quantize scale to reduce cache fragmentation
        quantized_scale = get_quantized_scale(scale)
        if quantized_scale <= 0.01:
            return None

        # Create cache key
        cache_key = self._create_cache_key(original, quantized_scale)

        # Check cache
        if cache_key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(cache_key)
            self.stats["hits"] += 1
            return self.cache[cache_key]

        # Cache miss - create new scaled image
        self.stats["misses"] += 1

        scaled_image = self._create_scaled_image(original, quantized_scale)

        if scaled_image:
            self._add_to_cache(cache_key, scaled_image)
            self.generation_count_this_frame += 1

        return scaled_image

    def _create_cache_key(self, surface: pygame.Surface, scale: float) -> Tuple[int, int, int, float]:
        """
        Create cache key from surface and scale using content-based approach.

        Args:
            surface: Source surface
            scale: Scale factor

        Returns:
            Cache key tuple
        """
        # Use surface dimensions and content hash instead of object ID
        # This allows cache hits for identical image content regardless of object identity
        try:
            # Create a simple content hash using pixel data (sample approach)
            # We sample a few pixels to balance performance vs uniqueness
            w, h = surface.get_width(), surface.get_height()
            if w > 0 and h > 0:
                # Sample corner and center pixels for content identification
                corner_sample = (
                    surface.get_at((0, 0)) if w > 0 and h > 0 else (0, 0, 0, 0),
                    surface.get_at((min(w-1, 10), min(h-1, 10))),
                    surface.get_at((w//2, h//2)) if w > 2 and h > 2 else (0, 0, 0, 0)
                )
                content_hash = hash(corner_sample)
            else:
                content_hash = 0
        except:
            # Fallback to object ID if pixel sampling fails
            content_hash = id(surface)

        return (
            content_hash,        # Content-based hash instead of object ID
            surface.get_width(),
            surface.get_height(),
            scale
        )

    def _check_generation_limits(self) -> bool:
        """
        Check if we can generate new scaled images this frame.

        Returns:
            True if generation is allowed
        """
        current_time = time.time()

        # Reset frame counter every ~16ms (60 FPS)
        if current_time - self.frame_reset_time > 0.016:
            self.generation_count_this_frame = 0
            self.frame_reset_time = current_time

        max_generations = PERFORMANCE_CONFIG["max_scale_generations_per_frame"]
        return self.generation_count_this_frame < max_generations

    def _create_scaled_image(self, original: pygame.Surface, scale: float) -> Optional[pygame.Surface]:
        """
        Create a new scaled image with performance tracking.

        Args:
            original: Original image surface
            scale: Scale factor

        Returns:
            Scaled image surface or None on error
        """
        start_time = time.time()

        try:
            original_width = original.get_width()
            original_height = original.get_height()

            new_width = max(1, int(original_width * scale))
            new_height = max(1, int(original_height * scale))

            # Choose scaling method based on scale factor and performance mode
            if scale < 0.5:
                # For significant downscaling, use smoothscale for better quality
                # But only if we're not under performance pressure
                if self._should_use_smooth_scaling():
                    scaled_image = pygame.transform.smoothscale(original, (new_width, new_height))
                else:
                    scaled_image = pygame.transform.scale(original, (new_width, new_height))
            else:
                # For minor scaling, use faster algorithm
                scaled_image = pygame.transform.scale(original, (new_width, new_height))

            # Track creation time
            creation_time = time.time() - start_time
            self.stats["creation_time_total"] += creation_time

            return scaled_image

        except Exception as e:
            logger.error(f"Error creating scaled image: {e}")
            return None

    def _should_use_smooth_scaling(self) -> bool:
        """
        Determine if smooth scaling should be used based on performance.

        Returns:
            True if smooth scaling is recommended
        """
        # Use smooth scaling only if cache hit rate is good and we're not generating too many images
        hit_rate = self.get_hit_rate()
        recent_generations = self.generation_count_this_frame

        return (hit_rate > 0.85 and
                recent_generations < 2 and
                len(self.cache) < self.max_size * 0.8)

    def _add_to_cache(self, cache_key: Tuple, image: pygame.Surface):
        """
        Add image to cache with LRU management.

        Args:
            cache_key: Cache key
            image: Scaled image to cache
        """
        # Remove oldest entries if cache is full
        while len(self.cache) >= self.max_size:
            oldest_key, oldest_image = self.cache.popitem(last=False)
            self.stats["evictions"] += 1

            # Update memory usage estimate
            if oldest_image:
                memory_size = oldest_image.get_width() * oldest_image.get_height() * 4  # Assume 32-bit
                self.stats["memory_usage_estimate"] -= memory_size

        # Add new entry
        self.cache[cache_key] = image

        # Update memory usage estimate
        if image:
            memory_size = image.get_width() * image.get_height() * 4  # Assume 32-bit
            self.stats["memory_usage_estimate"] += memory_size

    def clear(self):
        """Clear the entire cache."""
        self.cache.clear()
        self.stats["memory_usage_estimate"] = 0
        logger.info("Image scaling cache cleared")

    def get_hit_rate(self) -> float:
        """
        Get cache hit rate.

        Returns:
            Hit rate as percentage (0.0-1.0)
        """
        total_requests = self.stats["hits"] + self.stats["misses"]
        return (self.stats["hits"] / total_requests) if total_requests > 0 else 0.0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache performance statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.get_hit_rate()

        avg_creation_time = (
            self.stats["creation_time_total"] / max(1, self.stats["misses"])
        ) * 1000  # Convert to milliseconds

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
            **self.stats
        }

    def optimize(self):
        """
        Optimize cache by removing rarely used entries.

        This method can be called periodically to maintain performance.
        """
        current_time = time.time()

        # Only optimize every few seconds to avoid overhead
        if current_time - self.stats["last_cleanup_time"] < 5.0:
            return

        initial_size = len(self.cache)

        # Remove oldest 25% of entries if cache is >80% full
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
        """
        Check if cache performance indicates potential issues.

        Returns:
            True if performance warning should be raised
        """
        hit_rate = self.get_hit_rate()
        memory_mb = self.stats["memory_usage_estimate"] / (1024 * 1024)

        return (
            hit_rate < (1.0 - PERFORMANCE_THRESHOLDS["cache_miss_rate_warning"]) or
            memory_mb > PERFORMANCE_THRESHOLDS["memory_warning_mb"] or
            self.generation_count_this_frame > PERFORMANCE_CONFIG["max_scale_generations_peak"]
        )

    def get_performance_warnings(self) -> list:
        """
        Get list of current performance warnings.

        Returns:
            List of warning strings
        """
        warnings = []

        hit_rate = self.get_hit_rate()
        memory_mb = self.stats["memory_usage_estimate"] / (1024 * 1024)

        if hit_rate < (1.0 - PERFORMANCE_THRESHOLDS["cache_miss_rate_warning"]):
            warnings.append(f"Low cache hit rate: {hit_rate:.1%}")

        if memory_mb > PERFORMANCE_THRESHOLDS["memory_warning_mb"]:
            warnings.append(f"High memory usage: {memory_mb:.1f} MB")

        if self.generation_count_this_frame > PERFORMANCE_CONFIG["max_scale_generations_peak"]:
            warnings.append(f"High scaling generation rate: {self.generation_count_this_frame}/frame")

        return warnings


# Global cache instance
_global_scaling_cache: Optional[ScalingCache] = None


def get_scaling_cache() -> ScalingCache:
    """
    Get the global scaling cache instance.

    Returns:
        Global ScalingCache instance
    """
    global _global_scaling_cache
    if _global_scaling_cache is None:
        _global_scaling_cache = ScalingCache()
    return _global_scaling_cache


def clear_scaling_cache():
    """Clear the global scaling cache."""
    global _global_scaling_cache
    if _global_scaling_cache:
        _global_scaling_cache.clear()


def get_cache_stats() -> Dict[str, Any]:
    """
    Get global cache statistics.

    Returns:
        Cache statistics dictionary
    """
    global _global_scaling_cache
    if _global_scaling_cache:
        return _global_scaling_cache.get_stats()
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