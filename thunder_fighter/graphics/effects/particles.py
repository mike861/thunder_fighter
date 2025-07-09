"""
粒子效果系统

统一管理各种粒子特效：爆炸、尾迹、闪光等。
"""

import pygame
import random
import math
from typing import List, Tuple, Optional
from thunder_fighter.utils.logger import logger


class Particle:
    """单个粒子类"""
    
    def __init__(self, x: float, y: float, velocity: Tuple[float, float], 
                 color: Tuple[int, int, int], lifetime: float, size: int = 2):
        self.x = x
        self.y = y
        self.velocity_x, self.velocity_y = velocity
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.active = True
    
    def update(self, dt: float):
        """更新粒子状态"""
        if not self.active:
            return
        
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.lifetime -= dt
        
        if self.lifetime <= 0:
            self.active = False
    
    def render(self, screen: pygame.Surface):
        """渲染粒子"""
        if not self.active:
            return
        
        # 计算透明度（基于剩余生命时间）
        alpha_ratio = self.lifetime / self.max_lifetime
        alpha = int(255 * alpha_ratio)
        
        # 创建带透明度的表面
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        color_with_alpha = (*self.color, alpha)
        pygame.draw.circle(surf, color_with_alpha, (self.size, self.size), self.size)
        
        screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))


class ParticleSystem:
    """粒子系统管理器"""
    
    def __init__(self):
        self.particles: List[Particle] = []
    
    def create_explosion(self, x: float, y: float, particle_count: int = 20):
        """创建爆炸效果"""
        colors = [(255, 255, 0), (255, 128, 0), (255, 0, 0)]  # 黄、橙、红
        
        for _ in range(particle_count):
            # 随机方向和速度
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            
            color = random.choice(colors)
            lifetime = random.uniform(0.5, 1.5)
            size = random.randint(2, 4)
            
            particle = Particle(x, y, velocity, color, lifetime, size)
            self.particles.append(particle)
    
    def create_trail(self, x: float, y: float, direction: Tuple[float, float], 
                     particle_count: int = 5):
        """创建尾迹效果"""
        colors = [(255, 255, 255), (200, 200, 255), (150, 150, 255)]  # 白到蓝
        
        for i in range(particle_count):
            # 在方向的反方向创建粒子
            speed = random.uniform(20, 50)
            spread = 0.3  # 扩散角度
            
            # 添加随机扩散
            dir_x = direction[0] + random.uniform(-spread, spread)
            dir_y = direction[1] + random.uniform(-spread, spread)
            
            velocity = (-dir_x * speed, -dir_y * speed)
            
            color = random.choice(colors)
            lifetime = random.uniform(0.2, 0.8)
            size = random.randint(1, 2)
            
            particle = Particle(x, y, velocity, color, lifetime, size)
            self.particles.append(particle)
    
    def create_sparks(self, x: float, y: float, particle_count: int = 10):
        """创建火花效果"""
        colors = [(255, 255, 100), (255, 200, 50), (255, 150, 0)]  # 黄到橙
        
        for _ in range(particle_count):
            # 向上的火花
            angle = random.uniform(-math.pi/3, -2*math.pi/3)  # 向上60度范围
            speed = random.uniform(80, 120)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            
            color = random.choice(colors)
            lifetime = random.uniform(0.3, 1.0)
            size = random.randint(1, 3)
            
            particle = Particle(x, y, velocity, color, lifetime, size)
            self.particles.append(particle)
    
    def create_hit_effect(self, x: float, y: float, color: Tuple[int, int, int] = (255, 255, 255)):
        """创建击中效果"""
        particle_count = 8
        
        for _ in range(particle_count):
            # 放射状扩散
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 80)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            
            lifetime = random.uniform(0.2, 0.6)
            size = random.randint(1, 2)
            
            particle = Particle(x, y, velocity, color, lifetime, size)
            self.particles.append(particle)
    
    def update(self, dt: float):
        """更新所有粒子"""
        for particle in self.particles[:]:  # 使用切片复制以便安全删除
            particle.update(dt)
            if not particle.active:
                self.particles.remove(particle)
    
    def render(self, screen: pygame.Surface):
        """渲染所有粒子"""
        for particle in self.particles:
            particle.render(screen)
    
    def clear(self):
        """清空所有粒子"""
        self.particles.clear()
    
    def get_particle_count(self) -> int:
        """获取当前粒子数量"""
        return len(self.particles)


# 全局粒子系统实例
_global_particle_system = None


def get_particle_system() -> ParticleSystem:
    """获取全局粒子系统实例"""
    global _global_particle_system
    if _global_particle_system is None:
        _global_particle_system = ParticleSystem()
    return _global_particle_system


def create_particle_explosion(x: float, y: float, particle_count: int = 20):
    """便捷函数：创建爆炸粒子效果"""
    get_particle_system().create_explosion(x, y, particle_count)


def create_particle_trail(x: float, y: float, direction: Tuple[float, float], 
                         particle_count: int = 5):
    """便捷函数：创建尾迹粒子效果"""
    get_particle_system().create_trail(x, y, direction, particle_count)


def create_particle_sparks(x: float, y: float, particle_count: int = 10):
    """便捷函数：创建火花粒子效果"""
    get_particle_system().create_sparks(x, y, particle_count)


def create_particle_hit_effect(x: float, y: float, color: Tuple[int, int, int] = (255, 255, 255)):
    """便捷函数：创建击中粒子效果"""
    get_particle_system().create_hit_effect(x, y, color)


def update_particles(dt: float):
    """便捷函数：更新粒子系统"""
    get_particle_system().update(dt)


def render_particles(screen: pygame.Surface):
    """便捷函数：渲染粒子系统"""
    get_particle_system().render(screen)


def clear_particles():
    """便捷函数：清空所有粒子"""
    get_particle_system().clear()