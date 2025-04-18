import pygame
import random
from thunder_fighter.sprites.explosion import Explosion
import math

def create_explosion(center, size=40):
    """创建爆炸效果"""
    return Explosion(center, size)

def create_hit_effect(x, y, size=20):
    """创建命中效果"""
    hit = Explosion((x, y), size)
    # 修改爆炸效果的颜色和表现以适合命中效果
    hit.draw_explosion = lambda: _draw_hit_effect(hit)
    hit.frame_rate = 40  # 命中效果稍快一些
    _draw_hit_effect(hit)  # 立即绘制第一帧
    return hit

def _draw_hit_effect(hit_obj):
    """自定义的命中效果绘制函数"""
    # 清除表面
    hit_obj.image.fill((0, 0, 0, 0))
    
    # 命中效果使用不同颜色
    radius = hit_obj.size // 2
    intensity = max(0, 5 - hit_obj.frame)
    
    # 绘制外部圆 - 白色发光
    pygame.draw.circle(hit_obj.image, (255, 255, 255, 150), (radius, radius), radius - hit_obj.frame * 3)
    
    # 绘制内部圆 - 蓝色闪光
    pygame.draw.circle(hit_obj.image, (100, 200, 255, 200), (radius, radius), radius - 3 - hit_obj.frame * 3)
    
    # 绘制命中粒子 - 蓝色
    for _ in range(intensity * 3):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, radius)
        x = radius + math.cos(angle) * distance
        y = radius + math.sin(angle) * distance
        size = random.randint(1, 3)
        pygame.draw.circle(hit_obj.image, (150, 230, 255, 200), (int(x), int(y)), size) 