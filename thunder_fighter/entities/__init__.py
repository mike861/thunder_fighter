"""
游戏实体模块

包含所有游戏对象的定义和工厂类。
重构后按类型组织的实体系统。
"""

# 基础实体类
from .base import GameObject, Entity, EntityFactory, MovableEntity, LivingEntity

# 兼容性导入（保持向后兼容）
from .entity_factory import EntityFactory as LegacyEntityFactory

__all__ = [
    # 新的基础实体类
    'GameObject', 
    'Entity', 
    'EntityFactory',
    'MovableEntity',
    'LivingEntity',
    
    # 向后兼容
    'LegacyEntityFactory',
] 