"""
Static 3D visual effects module for Thunder Fighter.

This module provides static 3D appearance enhancements without runtime
scaling or complex transformations. Focuses on pre-rendered visual depth
through shading, highlights, and artistic effects.
"""

from .background_3d import BackgroundVisual3D, create_3d_planet
from .cinematic_effects import Cinematic3DEffects
from .effect_config import Visual3DConfig
from .enemy_effects import EnemyVisualEnhancer, enhance_enemy_ship
from .ship_effects import ShipVisualEnhancer, enhance_player_ship

__all__ = [
    "Visual3DConfig",
    "ShipVisualEnhancer",
    "EnemyVisualEnhancer",
    "BackgroundVisual3D",
    "Cinematic3DEffects",
    "enhance_player_ship",
    "enhance_enemy_ship",
    "create_3d_planet",
]

__version__ = "1.0.0"
