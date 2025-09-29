"""
Static 3D visual effects module for Thunder Fighter.

This module provides static 3D appearance enhancements without runtime
scaling or complex transformations. Focuses on pre-rendered visual depth
through shading, highlights, and artistic effects.
"""

from .effect_config import Visual3DConfig
from .ship_effects import ShipVisualEnhancer
from .enemy_effects import EnemyVisualEnhancer
from .background_3d import BackgroundVisual3D

__all__ = [
    'Visual3DConfig',
    'ShipVisualEnhancer',
    'EnemyVisualEnhancer',
    'BackgroundVisual3D',
]

__version__ = "1.0.0"