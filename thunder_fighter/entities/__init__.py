"""
Game Entity Module

Contains all game object definitions and factory classes.
Refactored entity system organized by type.
"""

# Base entity classes
from .base import GameObject, Entity, EntityFactory, MovableEntity, LivingEntity

# Compatibility imports (maintain backward compatibility)
from .entity_factory import EntityFactory as LegacyEntityFactory

# Import all factory classes
from .enemies.enemy_factory import EnemyFactory
from .enemies.boss_factory import BossFactory
from .items.item_factory import ItemFactory
from .projectiles.projectile_factory import ProjectileFactory

# Import entity classes
from .player.player import Player
from .enemies.enemy import Enemy
from .enemies.boss import Boss
from .projectiles.bullets import Bullet, BossBullet, EnemyBullet
from .projectiles.missile import TrackingMissile
from .items.items import HealthItem, BulletSpeedItem, BulletPathItem, PlayerSpeedItem, WingmanItem
from .player.wingman import Wingman

__all__ = [
    # New base entity classes
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
    
    # Entity classes
    'Player',
    'Enemy',
    'Boss',
    'Bullet',
    'BossBullet',
    'EnemyBullet',
    'TrackingMissile',
    'HealthItem',
    'BulletSpeedItem',
    'BulletPathItem',
    'PlayerSpeedItem',
    'WingmanItem',
    'Wingman',
    
    # backward compatibility
    'LegacyEntityFactory',
] 