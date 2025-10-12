"""
Configuration for static 3D visual effects.

This module contains simple configuration parameters for visual depth effects
without complex performance settings or dynamic scaling parameters.
"""

from typing import Dict, Tuple


# Core 3D visual effect settings - simple and clean
class Visual3DConfig:
    """Configuration class for static 3D visual effects."""

    # Player ship 3D appearance
    PLAYER_SHIP = {
        "shadow_offset": (4, 4),  # Bottom-right shadow offset in pixels
        "shadow_alpha": 180,  # Shadow transparency (0-255) - increased for visibility
        "shadow_color": (0, 0, 0),  # Shadow color (RGB)
        "highlight_intensity": 0.8,  # Highlight brightness multiplier - increased
        "highlight_color": (255, 255, 255),  # Highlight color (RGB)
        "highlight_positions": [  # Highlight positions as ratios (0.0-1.0)
            (0.3, 0.2),  # Left wing highlight
            (0.7, 0.2),  # Right wing highlight
            (0.5, 0.1),  # Nose highlight
        ],
        "metallic_sheen": True,  # Enable metallic surface effect
        "edge_lighting": True,  # Enable edge lighting effect
        "engine_glow": {
            "enabled": True,
            "color": (255, 150, 100),  # Orange-red glow
            "intensity": 0.9,  # Increased intensity
            "radius": 6,  # Larger glow radius
        },
    }

    # Enemy ship 3D appearance
    ENEMY_SHIP = {
        "organic_shading": True,  # Use organic/biological shading
        "shadow_offset": (3, 3),  # Increased shadow for visibility
        "shadow_alpha": 160,  # Increased alpha for more visible shadow
        "shadow_color": (40, 0, 0),  # Darker red shadow for organic feel
        "bio_highlights": [  # Organic highlight positions
            (0.5, 0.3),  # Center highlight
            (0.2, 0.6),  # Left bio-panel
            (0.8, 0.6),  # Right bio-panel
        ],
        "highlight_color": (220, 80, 80),  # Brighter reddish organic highlights
        "surface_texture": {
            "enabled": True,
            "roughness": 0.3,  # Surface roughness (0.0-1.0)
            "bio_pattern": True,  # Apply biological pattern
        },
    }

    # Background 3D elements
    BACKGROUND_3D = {
        "planets": {
            "sphere_gradient_steps": 32,  # Gradient smoothness for sphere effect
            "light_angle": 45,  # Light source angle in degrees
            "atmosphere_thickness": 0.15,  # Atmosphere rim thickness (0.0-1.0)
            "specular_intensity": 0.8,  # Specular highlight intensity
            "specular_size": 0.1,  # Specular highlight size ratio
        },
        "nebula": {
            "depth_layers": 3,  # Number of depth layers
            "opacity_gradient": True,  # Apply depth-based opacity
            "color_shift": True,  # Apply depth-based color shift
        },
    }

    # Performance settings - minimal and focused
    PERFORMANCE = {
        "enable_caching": True,  # Cache enhanced images
        "max_cache_size": 50,  # Maximum cached images
        "preload_player_variants": True,  # Preload player ship variants
        "preload_enemy_variants": False,  # Don't preload enemy variants to save memory
    }

    # Debug and development settings
    DEBUG = {
        "show_shadow_bounds": False,  # Visualize shadow boundaries
        "show_highlight_points": False,  # Show highlight point markers
        "show_enhancement_stats": False,  # Display enhancement statistics
        "wireframe_mode": False,  # Show wireframe overlays
    }

    @classmethod
    def get_player_config(cls) -> Dict:
        """Get player ship visual configuration."""
        return cls.PLAYER_SHIP.copy()

    @classmethod
    def get_enemy_config(cls) -> Dict:
        """Get enemy ship visual configuration."""
        return cls.ENEMY_SHIP.copy()

    @classmethod
    def get_background_config(cls) -> Dict:
        """Get background 3D visual configuration."""
        return cls.BACKGROUND_3D.copy()

    @classmethod
    def is_debug_enabled(cls) -> bool:
        """Check if any debug visualization is enabled."""
        return any(cls.DEBUG.values())


# Color utility functions
def blend_colors(
    base_color: Tuple[int, int, int], overlay_color: Tuple[int, int, int], alpha: float
) -> Tuple[int, int, int]:
    """
    Blend two colors with alpha transparency.

    Args:
        base_color: Base RGB color
        overlay_color: Overlay RGB color
        alpha: Alpha value (0.0-1.0)

    Returns:
        Blended RGB color
    """
    r = int(base_color[0] * (1 - alpha) + overlay_color[0] * alpha)
    g = int(base_color[1] * (1 - alpha) + overlay_color[1] * alpha)
    b = int(base_color[2] * (1 - alpha) + overlay_color[2] * alpha)

    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))


def adjust_brightness(color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    """
    Adjust color brightness by a factor.

    Args:
        color: RGB color
        factor: Brightness factor (0.0 = black, 1.0 = original, >1.0 = brighter)

    Returns:
        Brightness-adjusted RGB color
    """
    return (
        max(0, min(255, int(color[0] * factor))),
        max(0, min(255, int(color[1] * factor))),
        max(0, min(255, int(color[2] * factor))),
    )
