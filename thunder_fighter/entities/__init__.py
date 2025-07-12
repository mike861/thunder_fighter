"""
Game Entity Module

Contains all game object definitions and factory classes.
Refactored entity system organized by type.
"""

# Base entity classes
from .base import Entity, EntityFactory, GameObject, LivingEntity, MovableEntity
from .enemies.boss_factory import BossFactory

# Factory classes
from .enemies.enemy_factory import EnemyFactory
from .items.item_factory import ItemFactory

# Primary entity classes (frequently used)
from .player.player import Player
from .projectiles.projectile_factory import ProjectileFactory

__all__ = [
    # Base entity classes
    'GameObject',
    'Entity',
    'EntityFactory',
    'MovableEntity',
    'LivingEntity',

    # Factory classes
    'EnemyFactory',
    'BossFactory',
    'ItemFactory',
    'ProjectileFactory',

    # Primary entity classes
    'Player',
]
