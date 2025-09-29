"""
Configuration constants for pseudo-3D rendering system.

This module contains all configuration parameters for the depth scaling system,
performance settings, and visual effects parameters.
"""

from typing import Any, Dict, Tuple

# Core 3D rendering settings
PSEUDO_3D_CONFIG: Dict[str, Any] = {
    "enabled": True,
    "depth_intensity": 1.0,          # 0.5-2.0 range for effect strength
    "fog_enabled": True,             # Enable distance fog effects
    "perspective_strength": 1.0,     # 0.5-2.0 range for perspective distortion
    "performance_mode": "auto",      # "high", "medium", "low", "auto"
}

# Depth calculation parameters
DEPTH_SETTINGS: Dict[str, float] = {
    "depth_factor": 0.004,           # Perspective scaling factor (slightly increased for more visible 3D effect)
    "vanish_point_x": 0.5,           # Vanishing point X (0.0-1.0 screen ratio)
    "vanish_point_y": 0.6,           # Vanishing point Y (0.0-1.0 screen ratio) - moved down for screen entry
    "perspective_x_factor": 0.2,     # Horizontal perspective strength
    "perspective_y_factor": 1.2,     # Vertical perspective strength (increased for fast screen entry)
    "min_render_scale": 0.05,        # Minimum scale before culling
    "min_render_size": 2,            # Minimum pixel size before culling
}

# Spawning depth ranges
SPAWN_DEPTH_CONFIG: Dict[str, float] = {
    "enemy_min_depth": 150,          # Minimum enemy spawn depth (closer for larger appearance)
    "enemy_max_depth": 300,          # Maximum enemy spawn depth (closer for larger appearance)
    "enemy_depth_variation": 80,     # Random depth variation (adjusted for new range)
    "boss_spawn_depth": 600,         # Boss spawn depth
    "item_spawn_depth": 400,         # Item spawn depth
    "bullet_start_depth": 100,       # Player bullet starting depth
    "bullet_max_depth": 900,         # Maximum bullet travel depth
}

# Performance settings (conservative targets for Phase 1)
PERFORMANCE_CONFIG: Dict[str, Any] = {
    "image_cache_size": 800,         # Increased for 11 levels × 24 rotations × multiple scales
    "scale_precision": 2,            # Decimal places for scale quantization
    "max_scale_generations_per_frame": 3,  # Average limit for new scaling
    "max_scale_generations_peak": 8, # Peak limit for new scaling
    "cache_hit_rate_target": 0.80,  # Target cache hit rate (80%)
    "lod_thresholds": {              # Level of detail thresholds
        "high": 0.8,                 # Above this: full quality
        "medium": 0.4,               # Above this: medium quality
        "low": 0.2,                  # Above this: low quality
    },
    "update_frequencies": {          # Update frequency multipliers
        "high": 1.0,                 # Full update rate
        "medium": 0.5,               # Half update rate
        "low": 0.25,                 # Quarter update rate
    },
}

# Visual effects settings
VISUAL_EFFECTS_CONFIG: Dict[str, Any] = {
    "fog_enabled": False,            # Disable distance fog to avoid haze/blur in Phase 1
    "fog_color": (20, 30, 50),       # RGB color for distance fog
    "fog_intensity_max": 80,         # Maximum fog alpha value
    "fog_start_distance": 0.8,       # Scale value where fog starts
    "depth_color_shift": True,       # Enable color shifting by depth
    "particle_depth_scaling": True,  # Scale particle effects by depth
    "depth_blur_enabled": False,     # Disable blur effects for Phase 1
    "glow_effects_enabled": True,    # Enable glow for near objects
    # Ship visual style (2.5D arcade rendering cues)
    "ship_style_enabled": True,
    "ship_style": "arcade_rim",      # Options: "arcade_rim", "classic_3d", None
    "ship_style_params": {
        "arcade_rim": {
            "base_shadow_offset_px": 6,  # Shadow offset at scale=1.0
            "shadow_alpha": 140,
            "rim_alpha": 60,
            "rim_radius_max": 2,
        }
    },
}

# Debug settings (Phase 1 focus on core performance monitoring)
DEBUG_3D_CONFIG: Dict[str, bool] = {
    "show_depth_values": False,      # Display depth numbers on entities
    "render_depth_zones": False,     # Show depth zone boundaries
    "collision_depth_visualization": False,  # Visualize collision depths
    "performance_overlay": True,     # Show performance metrics (enabled for Phase 1)
    "cache_statistics": True,        # Display cache hit rates (enabled for Phase 1)
    "frame_time_graph": False,       # Show frame time graph
    "memory_usage_monitor": True,    # Monitor memory usage
}

# Gameplay balance settings
GAMEPLAY_3D_CONFIG: Dict[str, Any] = {
    "depth_hit_probability": False,  # Disable for Phase 1 - keep gameplay simple
    "depth_score_bonus": True,       # Bonus points for distant hits
    "depth_difficulty_scaling": False,  # Disable for Phase 1
    "auto_aim_assistance": False,    # Provide aim assistance for distant targets
    "collision_depth_tolerance": 600, # Max depth difference for collisions (increased for 2D bullet compatibility)
    "preserve_2d_collision": True,   # Keep original collision boxes for Phase 1
}

# Movement and animation settings
MOVEMENT_3D_CONFIG: Dict[str, float] = {
    "enemy_z_velocity_min": -60.0,   # Enable gentle forward movement to enhance 3D feel
    "enemy_z_velocity_max": -30.0,   # Enemies slowly approach the camera
    "bullet_z_velocity": 150.0,      # Bullet depth movement speed
    "depth_oscillation_enabled": True,   # Slight depth oscillation for richer perspective
    "oscillation_amplitude_min": 5.0,   # Minimum oscillation amplitude
    "oscillation_amplitude_max": 20.0,  # Maximum oscillation amplitude
    "oscillation_frequency": 2.0,       # Oscillation frequency (Hz)
}

# Scale quantization buckets for caching optimization
# Dynamic scale buckets based on performance configuration
def get_scale_buckets() -> Tuple[float, ...]:
    """Get scale buckets based on current performance configuration."""
    try:
        from thunder_fighter.config.performance_config import get_cache_strategy_config
        config = get_cache_strategy_config()
        bucket_count = config["scale_buckets"]
        bucket_interval = config["bucket_interval"]
    except ImportError:
        # Fallback to original configuration
        bucket_count = 64
        bucket_interval = 0.015

    return tuple(
        round(0.05 + i * bucket_interval, 3) for i in range(bucket_count)
    )

# Default scale buckets (for backward compatibility)
SCALE_BUCKETS: Tuple[float, ...] = tuple(
    round(0.05 + i * 0.02, 3) for i in range(48)  # Conservative: 48 buckets with 0.02 interval
)

# Performance monitoring thresholds (optimized for realistic gameplay)
PERFORMANCE_THRESHOLDS: Dict[str, float] = {
    "fps_warning": 40.0,             # More realistic FPS warning threshold
    "fps_critical": 25.0,            # Critical performance threshold
    "cache_miss_rate_warning": 0.50, # More lenient cache miss rate (50% instead of 25%)
    "cache_miss_rate_critical": 0.70, # Critical cache miss rate threshold
    "memory_warning_mb": 150.0,      # Higher memory threshold
    "frame_time_warning_ms": 25.0,   # 40FPS standard (more realistic than 60FPS)
    "frame_time_critical_ms": 33.33, # 30FPS critical threshold
}

# Auto-performance mode switching thresholds
AUTO_PERFORMANCE_THRESHOLDS: Dict[str, Dict[str, float]] = {
    "high_to_medium": {
        "fps_threshold": 50.0,
        "cache_miss_rate": 0.30,
        "frame_time_ms": 18.0,
    },
    "medium_to_low": {
        "fps_threshold": 35.0,
        "cache_miss_rate": 0.40,
        "frame_time_ms": 25.0,
    },
    "low_to_medium": {
        "fps_threshold": 55.0,
        "cache_miss_rate": 0.20,
        "frame_time_ms": 15.0,
    },
    "medium_to_high": {
        "fps_threshold": 70.0,
        "cache_miss_rate": 0.15,
        "frame_time_ms": 12.0,
    },
}


def get_quantized_scale(scale: float) -> float:
    """
    Quantize scale to nearest bucket for cache optimization.

    Args:
        scale: Original scale value

    Returns:
        Quantized scale value from dynamic scale buckets
    """
    # Use dynamic scale buckets for better performance
    try:
        scale_buckets = get_scale_buckets()
    except Exception:
        # Fallback to static buckets
        scale_buckets = SCALE_BUCKETS

    if scale <= scale_buckets[0]:
        return scale_buckets[0]
    if scale >= scale_buckets[-1]:
        return scale_buckets[-1]

    # Find closest bucket
    for bucket in scale_buckets:
        if scale <= bucket:
            return bucket

    return scale_buckets[-1]


def get_lod_level(scale: float) -> str:
    """
    Determine LOD level based on scale.

    Args:
        scale: Current scale value

    Returns:
        LOD level string: "high", "medium", or "low"
    """
    thresholds = PERFORMANCE_CONFIG["lod_thresholds"]

    if scale >= thresholds["high"]:
        return "high"
    elif scale >= thresholds["medium"]:
        return "medium"
    else:
        return "low"


def get_update_frequency(scale: float) -> float:
    """
    Get update frequency multiplier based on scale.

    Args:
        scale: Current scale value

    Returns:
        Update frequency multiplier
    """
    lod_level = get_lod_level(scale)
    return PERFORMANCE_CONFIG["update_frequencies"][lod_level]


def should_render_entity(scale: float, visual_size: Tuple[int, int]) -> bool:
    """
    Determine if entity should be rendered based on scale and size.

    Args:
        scale: Current scale value
        visual_size: Visual size tuple (width, height)

    Returns:
        True if entity should be rendered
    """
    min_scale = DEPTH_SETTINGS["min_render_scale"]
    min_size = DEPTH_SETTINGS["min_render_size"]

    return (scale >= min_scale and
            visual_size[0] >= min_size and
            visual_size[1] >= min_size)


# Version and compatibility
PSEUDO_3D_VERSION = "1.0.0-phase1"
MIN_PYGAME_VERSION = "2.0.0"
