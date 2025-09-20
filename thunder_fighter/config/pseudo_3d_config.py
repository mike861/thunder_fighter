"""
Configuration constants for pseudo-3D rendering system.

This module contains all configuration parameters for the depth scaling system,
performance settings, and visual effects parameters.
"""

from typing import Dict, Tuple, Any

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
    "depth_factor": 0.002,           # Perspective scaling factor
    "vanish_point_x": 0.5,           # Vanishing point X (0.0-1.0 screen ratio)
    "vanish_point_y": 0.6,           # Vanishing point Y (0.0-1.0 screen ratio) - moved down for screen entry
    "perspective_x_factor": 0.2,     # Horizontal perspective strength
    "perspective_y_factor": 1.2,     # Vertical perspective strength (increased for fast screen entry)
    "min_render_scale": 0.05,        # Minimum scale before culling
    "min_render_size": 2,            # Minimum pixel size before culling
}

# Spawning depth ranges
SPAWN_DEPTH_CONFIG: Dict[str, float] = {
    "enemy_min_depth": 200,          # Minimum enemy spawn depth (reduced for larger sprites)
    "enemy_max_depth": 400,          # Maximum enemy spawn depth (reduced for larger sprites)
    "enemy_depth_variation": 100,    # Random depth variation (reduced)
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
    "fog_enabled": True,             # Enable distance fog effects
    "fog_color": (20, 30, 50),       # RGB color for distance fog
    "fog_intensity_max": 80,         # Maximum fog alpha value
    "fog_start_distance": 0.8,       # Scale value where fog starts
    "depth_color_shift": True,       # Enable color shifting by depth
    "particle_depth_scaling": True,  # Scale particle effects by depth
    "depth_blur_enabled": False,     # Disable blur effects for Phase 1
    "glow_effects_enabled": True,    # Enable glow for near objects
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
    "enemy_z_velocity_min": 0.0,     # Disabled enemy Z movement for stable 2D gameplay
    "enemy_z_velocity_max": 0.0,     # Disabled enemy Z movement for stable 2D gameplay
    "bullet_z_velocity": 150.0,      # Bullet depth movement speed
    "depth_oscillation_enabled": False,  # Disable depth oscillation for stable movement
    "oscillation_amplitude_min": 5.0,   # Minimum oscillation amplitude
    "oscillation_amplitude_max": 20.0,  # Maximum oscillation amplitude
    "oscillation_frequency": 2.0,       # Oscillation frequency (Hz)
}

# Scale quantization buckets for caching optimization
SCALE_BUCKETS: Tuple[float, ...] = tuple(
    round(0.05 + i * 0.015, 3) for i in range(64)  # 64 buckets from 0.05 to ~1.0
)

# Performance monitoring thresholds
PERFORMANCE_THRESHOLDS: Dict[str, float] = {
    "fps_warning": 45.0,             # Warn if FPS drops below this
    "fps_critical": 30.0,            # Critical performance threshold
    "cache_miss_rate_warning": 0.25, # Warn if cache miss rate exceeds this
    "memory_warning_mb": 100.0,      # Warn if cache memory exceeds this
    "frame_time_warning_ms": 16.67,  # Warn if frame time exceeds this (60 FPS)
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
        Quantized scale value from SCALE_BUCKETS
    """
    if scale <= SCALE_BUCKETS[0]:
        return SCALE_BUCKETS[0]
    if scale >= SCALE_BUCKETS[-1]:
        return SCALE_BUCKETS[-1]

    # Find closest bucket
    for bucket in SCALE_BUCKETS:
        if scale <= bucket:
            return bucket

    return SCALE_BUCKETS[-1]


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