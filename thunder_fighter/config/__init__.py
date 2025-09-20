"""
Configuration package for Thunder Fighter.

This package contains configuration modules for various game systems.
"""

from thunder_fighter.config.pseudo_3d_config import *

__all__ = [
    'PSEUDO_3D_CONFIG',
    'DEPTH_SETTINGS',
    'SPAWN_DEPTH_CONFIG',
    'PERFORMANCE_CONFIG',
    'VISUAL_EFFECTS_CONFIG',
    'DEBUG_3D_CONFIG',
    'GAMEPLAY_3D_CONFIG',
    'MOVEMENT_3D_CONFIG',
    'get_quantized_scale',
    'get_lod_level',
    'get_update_frequency',
    'should_render_entity',
]