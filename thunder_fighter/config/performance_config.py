"""
Performance optimization configuration for Thunder Fighter.

This module provides configurable performance optimization settings
to balance visual quality with rendering performance.
"""

from typing import Any, Dict

# Performance optimization modes
PERFORMANCE_MODES = {
    "high_quality": {
        "description": "Prioritize visual quality, minimal performance optimization",
        "player_animation": {
            "visual_update_interval": 1,      # Every frame
            "depth_quantization": 0.05,       # Very fine quantization
            "position_quantization": 0.2,     # Fine position quantization
            "preserve_oscillation": True,
            "amplitude_reduction": 1.0,       # No reduction
            "frequency_reduction": 1.0,       # No reduction
        },
        "cache_strategy": {
            "scale_buckets": 64,              # Maximum precision
            "bucket_interval": 0.015,         # Original precision
            "min_change_threshold": 0.02,
        },
        "expected_performance_gain": "5-10%"
    },

    "balanced": {
        "description": "Balance between visual quality and performance",
        "player_animation": {
            "visual_update_interval": 2,      # Every 2 frames
            "depth_quantization": 0.1,        # Moderate quantization
            "position_quantization": 0.5,     # Moderate position quantization
            "preserve_oscillation": True,
            "amplitude_reduction": 0.8,       # Slight reduction
            "frequency_reduction": 0.8,       # Slight reduction
        },
        "cache_strategy": {
            "scale_buckets": 48,              # Moderate precision
            "bucket_interval": 0.02,          # Slightly coarser
            "min_change_threshold": 0.03,
        },
        "expected_performance_gain": "30-40%"
    },

    "performance": {
        "description": "Prioritize performance, acceptable visual quality",
        "player_animation": {
            "visual_update_interval": 3,      # Every 3 frames
            "depth_quantization": 0.2,        # Coarse quantization
            "position_quantization": 1.0,     # Coarse position quantization
            "preserve_oscillation": True,
            "amplitude_reduction": 0.6,       # Moderate reduction
            "frequency_reduction": 0.6,       # Moderate reduction
        },
        "cache_strategy": {
            "scale_buckets": 32,              # Reduced precision
            "bucket_interval": 0.03,          # Coarser intervals
            "min_change_threshold": 0.05,
        },
        "expected_performance_gain": "50-70%"
    }
}

# Current active performance mode
CURRENT_PERFORMANCE_MODE = "balanced"

# UI Animation optimization settings
UI_ANIMATION_CONFIG = {
    "adaptive_quality": True,
    "max_concurrent_animations": 3,
    "performance_throttle": True,
    "warning_flash_reduction": {
        "high_performance": 1000,    # 1 flash per second
        "medium_performance": 500,   # 2 flashes per second
        "low_performance": 200,      # 5 flashes per second (original)
    }
}

# Performance monitoring thresholds (more realistic)
REALISTIC_PERFORMANCE_THRESHOLDS = {
    "cache_miss_rate_warning": 0.50,        # 50% instead of 25%
    "cache_miss_rate_critical": 0.70,       # 70% critical threshold
    "frame_time_warning_ms": 25.0,          # 40FPS standard instead of 60FPS
    "frame_time_critical_ms": 33.33,        # 30FPS critical threshold
    "warning_cooldown": 10.0,               # 10 seconds instead of 5
    "fps_warning": 40.0,                    # 40FPS warning
    "fps_critical": 25.0,                   # 25FPS critical
}

# Performance optimization flags
OPTIMIZATION_FLAGS = {
    "enable_player_animation_optimization": True,
    "enable_cache_optimization": True,
    "enable_ui_animation_optimization": True,
    "enable_performance_monitoring_optimization": True,
    "enable_debug_logging": False,
}

def get_current_config() -> Dict[str, Any]:
    """Get current performance configuration."""
    return PERFORMANCE_MODES[CURRENT_PERFORMANCE_MODE]

def get_player_animation_config() -> Dict[str, Any]:
    """Get current player animation configuration."""
    return get_current_config()["player_animation"]

def get_cache_strategy_config() -> Dict[str, Any]:
    """Get current cache strategy configuration."""
    return get_current_config()["cache_strategy"]

def set_performance_mode(mode: str) -> bool:
    """
    Set performance mode.

    Args:
        mode: One of 'high_quality', 'balanced', 'performance'

    Returns:
        True if mode was set successfully
    """
    global CURRENT_PERFORMANCE_MODE
    if mode in PERFORMANCE_MODES:
        CURRENT_PERFORMANCE_MODE = mode
        return True
    return False

def quantize_value(value: float, quantization: float) -> float:
    """
    Quantize a value to reduce cache fragmentation.

    Args:
        value: Original value
        quantization: Quantization step size

    Returns:
        Quantized value
    """
    if quantization <= 0:
        return value
    return round(value / quantization) * quantization

def should_update_visuals(frame_count: int, interval: int) -> bool:
    """
    Determine if visual effects should be updated this frame.

    Args:
        frame_count: Current frame number
        interval: Update interval (1 = every frame, 2 = every 2 frames, etc.)

    Returns:
        True if visuals should be updated
    """
    return frame_count % interval == 0
