import pygame
import random
import math

class Explosion(pygame.sprite.Sprite):
    """爆炸效果类"""
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        self.draw_explosion()
        
    def draw_explosion(self):
        """绘制爆炸效果"""
        # 清除表面
        self.image.fill((0, 0, 0, 0))
        
        # 根据当前帧绘制爆炸效果
        radius = self.size // 2
        intensity = max(0, 5 - self.frame)  # 爆炸强度随时间减弱
        
        # 绘制外部爆炸圆
        pygame.draw.circle(self.image, (255, 200, 0, 150), (radius, radius), radius - self.frame * 3)
        
        # 绘制内部爆炸圆
        pygame.draw.circle(self.image, (255, 255, 255, 200), (radius, radius), radius - 5 - self.frame * 3)
        
        # 绘制爆炸碎片
        for _ in range(intensity * 2):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, radius)
            x = radius + math.cos(angle) * distance
            y = radius + math.sin(angle) * distance
            size = random.randint(2, 4)
            pygame.draw.circle(self.image, (255, 255, 0, 200), (int(x), int(y)), size)
        
    def update(self):
        """更新爆炸帧"""
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            # 当帧数结束时，删除爆炸
            if self.frame > 6:  # 6帧，使爆炸效果更流畅
                self.kill()
            else:
                # 更新爆炸效果
                self.draw_explosion() 