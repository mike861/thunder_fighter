"""
Graphics Effects Module

Contains all visual effects related implementations.
"""

from .explosion import Explosion
from .stars import *
from .particles import (
    ParticleSystem,
    get_particle_system,
    create_particle_explosion,
    create_particle_trail,
    create_particle_sparks,
    create_particle_hit_effect,
    update_particles,
    render_particles,
    clear_particles,
)

# Import notification classes
from .notifications import (
    Notification,
    WarningNotification,
    AchievementNotification,
)

# Import explosion effects
from .explosions import (
    create_explosion,
    create_hit_effect,
)

# Import flash effects
from .flash_effects import (
    create_flash_effect,
    FlashEffect,
    FlashEffectManager,
    flash_manager,
)

__all__ = [
    'Explosion',
    'ParticleSystem',
    'get_particle_system',
    'create_particle_explosion',
    'create_particle_trail',
    'create_particle_sparks',
    'create_particle_hit_effect',
    'update_particles',
    'render_particles',
    'clear_particles',
    'create_explosion',
    'create_hit_effect',
    'create_flash_effect',
    'Notification',
    'WarningNotification',
    'AchievementNotification',
    'FlashEffect',
    'FlashEffectManager',
    'flash_manager',
]