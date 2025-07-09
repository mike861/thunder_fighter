"""
基础实体类定义

定义所有游戏对象的基类和通用接口。
"""

import pygame
from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict, Any


class GameObject(pygame.sprite.Sprite, ABC):
    """游戏对象基类"""
    
    def __init__(self, x: float, y: float, width: int, height: int):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.health = 1
        self.max_health = 1
        self.active = True
        
        # 创建基础rect
        self.rect = pygame.Rect(int(x), int(y), width, height)
        
        # 基础图像（子类需要设置具体图像）
        self.image = None
    
    @abstractmethod
    def update(self, dt: float):
        """更新游戏对象状态"""
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface):
        """渲染游戏对象"""
        pass
    
    def take_damage(self, damage: int) -> bool:
        """承受伤害，返回是否被摧毁"""
        self.health -= damage
        return self.health <= 0
    
    def heal(self, amount: int):
        """恢复生命值"""
        self.health = min(self.health + amount, self.max_health)
    
    def set_position(self, x: float, y: float):
        """设置位置"""
        self.x = x
        self.y = y
        self.rect.x = int(x)
        self.rect.y = int(y)
    
    def get_position(self) -> Tuple[float, float]:
        """获取位置"""
        return (self.x, self.y)
    
    def set_velocity(self, velocity_x: float, velocity_y: float):
        """设置速度"""
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
    
    def get_velocity(self) -> Tuple[float, float]:
        """获取速度"""
        return (self.velocity_x, self.velocity_y)


class Entity(GameObject):
    """具体实体类，提供默认实现"""
    
    def update(self, dt: float):
        """默认更新实现"""
        # 更新位置
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # 更新精灵的内置update（如果有动画等）
        if hasattr(super(), 'update') and callable(getattr(super(), 'update')):
            super().update()
    
    def render(self, screen: pygame.Surface):
        """默认渲染实现"""
        if hasattr(self, 'image') and hasattr(self, 'rect') and self.image:
            screen.blit(self.image, self.rect)


class EntityFactory(ABC):
    """实体工厂基类"""
    
    @abstractmethod
    def create(self, *args, **kwargs) -> GameObject:
        """创建实体实例"""
        pass
    
    def create_batch(self, count: int, *args, **kwargs) -> list:
        """批量创建实体"""
        entities = []
        for i in range(count):
            entity = self.create(*args, **kwargs)
            entities.append(entity)
        return entities


class MovableEntity(Entity):
    """可移动的实体基类"""
    
    def __init__(self, x: float, y: float, width: int, height: int, speed: float = 100.0):
        super().__init__(x, y, width, height)
        self.speed = speed
        self.direction_x = 0.0
        self.direction_y = 0.0
    
    def set_direction(self, direction_x: float, direction_y: float):
        """设置移动方向（归一化向量）"""
        self.direction_x = direction_x
        self.direction_y = direction_y
        
        # 根据方向和速度计算速度
        self.velocity_x = self.direction_x * self.speed
        self.velocity_y = self.direction_y * self.speed
    
    def move_towards(self, target_x: float, target_y: float):
        """朝向目标移动"""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = (dx * dx + dy * dy) ** 0.5
        
        if distance > 0:
            self.set_direction(dx / distance, dy / distance)


class LivingEntity(MovableEntity):
    """有生命的实体基类"""
    
    def __init__(self, x: float, y: float, width: int, height: int, 
                 speed: float = 100.0, max_health: int = 100):
        super().__init__(x, y, width, height, speed)
        self.max_health = max_health
        self.health = max_health
        self.is_alive = True
    
    def take_damage(self, damage: int) -> bool:
        """承受伤害，返回是否死亡"""
        if not self.is_alive:
            return True
        
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            self.on_death()
            return True
        
        self.on_damage_taken(damage)
        return False
    
    def heal(self, amount: int):
        """恢复生命值"""
        if self.is_alive:
            self.health = min(self.health + amount, self.max_health)
            self.on_heal(amount)
    
    def on_damage_taken(self, damage: int):
        """受伤时的回调"""
        pass
    
    def on_heal(self, amount: int):
        """治疗时的回调"""
        pass
    
    def on_death(self):
        """死亡时的回调"""
        self.active = False
        if hasattr(self, 'kill'):
            self.kill()
    
    def get_health_percentage(self) -> float:
        """获取生命值百分比"""
        if self.max_health <= 0:
            return 0.0
        return self.health / self.max_health