"""
游戏实体模块

包含所有游戏对象的定义和工厂类。
重构后按类型组织的实体系统。
"""

# 基础实体类
from .base import GameObject, Entity, EntityFactory, MovableEntity, LivingEntity

# 兼容性导入（保持向后兼容）
from .entity_factory import EntityFactory as LegacyEntityFactory

# 导入所有工厂类
from .enemies.enemy_factory import EnemyFactory
from .enemies.boss_factory import BossFactory
from .items.item_factory import ItemFactory
from .projectiles.projectile_factory import ProjectileFactory

# 导入实体类
from .player.player import Player
from .enemies.enemy import Enemy
from .enemies.boss import Boss
from .projectiles.bullets import Bullet, BossBullet, EnemyBullet
from .projectiles.missile import TrackingMissile
from .items.items import HealthItem, BulletSpeedItem, BulletPathItem, PlayerSpeedItem, WingmanItem
from .player.wingman import Wingman

__all__ = [
    # 新的基础实体类
    'GameObject', 
    'Entity', 
    'EntityFactory',
    'MovableEntity',
    'LivingEntity',
    
    # 工厂类
    'EnemyFactory',
    'BossFactory',
    'ItemFactory',
    'ProjectileFactory',
    
    # 实体类
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
    
    # 向后兼容
    'LegacyEntityFactory',
] 