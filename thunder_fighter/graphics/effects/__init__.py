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

# Import from the parent effects.py file for backward compatibility
import sys
import os
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, parent_dir)

try:
    from thunder_fighter.graphics.effects import (
        create_explosion,
        create_hit_effect,
        create_flash_effect,
        Notification,
        WarningNotification,
        AchievementNotification,
        FlashEffect,
        FlashEffectManager,
        flash_manager,
    )
except ImportError:
    # If import fails, define dummy functions
    def create_explosion(center, size_str='md'):
        return Explosion(center)
    
    def create_hit_effect(x, y, size=20):
        return Explosion((x, y))
    
    def create_flash_effect(entity, color=(255, 255, 255), duration=200):
        pass
    
    class Notification:
        def __init__(self, *args, **kwargs):
            pass
    
    WarningNotification = Notification
    AchievementNotification = Notification
    FlashEffect = Notification
    FlashEffectManager = Notification
    flash_manager = FlashEffectManager()

finally:
    sys.path.pop(0)

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