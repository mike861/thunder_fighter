import random
import pygame
from thunder_fighter.constants import WIDTH, HEIGHT

class Star:
    """背景星星类"""
    def __init__(self):
        self.x = random.randrange(WIDTH)
        self.y = random.randrange(HEIGHT)
        self.size = random.randrange(1, 3)
        self.speed = random.randrange(1, 3)
        self.color = random.choice([(200, 200, 200), (220, 220, 220), (255, 255, 255)])
        
    def update(self):
        """更新星星位置"""
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randrange(WIDTH)
            
    def draw(self, surf):
        """绘制星星"""
        pygame.draw.circle(surf, self.color, (self.x, self.y), self.size)

def create_stars(count=50):
    """创建指定数量的星星"""
    return [Star() for _ in range(count)] 