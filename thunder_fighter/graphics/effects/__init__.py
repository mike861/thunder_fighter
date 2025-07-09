"""
图形效果模块

包含所有视觉效果相关的实现。
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
]