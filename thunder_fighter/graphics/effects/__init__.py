"""
Graphics Effects Module

Contains all visual effects related implementations.
"""

from .explosion import Explosion

# Import explosion effects
from .explosions import (
    create_explosion,
    create_hit_effect,
)

# Import flash effects
from .flash_effects import (
    FlashEffect,
    FlashEffectManager,
    create_flash_effect,
    flash_manager,
)

# Import notification classes
from .notifications import (
    AchievementNotification,
    Notification,
    WarningNotification,
)
from .particles import (
    ParticleSystem,
    clear_particles,
    create_particle_explosion,
    create_particle_hit_effect,
    create_particle_sparks,
    create_particle_trail,
    get_particle_system,
    render_particles,
    update_particles,
)
from .stars import Star, create_stars

__all__ = [
    "Explosion",
    "ParticleSystem",
    "get_particle_system",
    "create_particle_explosion",
    "create_particle_trail",
    "create_particle_sparks",
    "create_particle_hit_effect",
    "update_particles",
    "render_particles",
    "clear_particles",
    "create_explosion",
    "create_hit_effect",
    "create_flash_effect",
    "Notification",
    "WarningNotification",
    "AchievementNotification",
    "FlashEffect",
    "FlashEffectManager",
    "flash_manager",
    "Star",
    "create_stars",
]
