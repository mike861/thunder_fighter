"""
Entities Package

This package provides entity factories and creation patterns for the Thunder Fighter game.
It centralizes entity creation logic and provides consistent interfaces for creating
game objects like enemies, bosses, items, and projectiles.
"""

from .entity_factory import EntityFactory
from .enemy_factory import EnemyFactory
from .boss_factory import BossFactory
from .item_factory import ItemFactory
from .projectile_factory import ProjectileFactory

__all__ = [
    'EntityFactory',
    'EnemyFactory',
    'BossFactory', 
    'ItemFactory',
    'ProjectileFactory'
] 