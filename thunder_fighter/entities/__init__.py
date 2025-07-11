"""
Game Entity Module

Contains all game object definitions and factory classes.
Refactored entity system organized by type.
"""

# Base entity classes
from .base import GameObject, Entity, EntityFactory, MovableEntity, LivingEntity

# Factory classes
from .enemies.enemy_factory import EnemyFactory
from .enemies.boss_factory import BossFactory
from .items.item_factory import ItemFactory
from .projectiles.projectile_factory import ProjectileFactory

# Primary entity classes (frequently used)
from .player.player import Player

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