import pygame
import pygame.time as ptime
import random
from thunder_fighter.constants import (
    WIDTH, BOSS_MAX_HEALTH, BOSS_SHOOT_DELAY,
    BOSS_HEALTH_MULTIPLIER, BOSS_BULLET_COUNT_BASE,
    BOSS_BULLET_COUNT_INCREMENT, BOSS_MAX_LEVEL
)
from thunder_fighter.graphics.renderers import create_boss_ship, draw_health_bar
from thunder_fighter.utils.logger import logger

class Boss(pygame.sprite.Sprite):
    """Boss类"""
    def __init__(self, all_sprites, boss_bullets_group, level=None):
        pygame.sprite.Sprite.__init__(self)
        
        # 确定Boss等级 - 如果未指定，根据游戏进度随机生成
        if level is None:
            self.level = random.randint(1, BOSS_MAX_LEVEL)
        else:
            self.level = min(level, BOSS_MAX_LEVEL)
        
        # 记录原始图像 - 用于闪烁效果时恢复
        self.original_image = create_boss_ship(self.level)
        
        # 根据等级调整属性
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.y = -self.rect.height
        self.speedx = 2
        self.speedy = 1
        
        # 创建碰撞掩码 - 用于更精确的碰撞检测
        self.mask = pygame.mask.from_surface(self.image)
        
        # 根据等级调整血量
        self.max_health = int(BOSS_MAX_HEALTH * (1 + (self.level - 1) * BOSS_HEALTH_MULTIPLIER))
        self.health = self.max_health
        
        # 根据等级调整射击
        self.shoot_delay = max(300, BOSS_SHOOT_DELAY - (self.level - 1) * 150)  # 等级越高，射击越快
        self.bullet_count = BOSS_BULLET_COUNT_BASE + (self.level - 1) * BOSS_BULLET_COUNT_INCREMENT
        
        self.last_shot = ptime.get_ticks()
        self.direction = 1  # 移动方向
        self.move_counter = 0
        self.damage_flash = 0
        
        # 预先创建闪烁图像
        self.flash_images = self._create_flash_images()
        
        # 精灵组
        self.all_sprites = all_sprites
        self.boss_bullets_group = boss_bullets_group
        
        logger.info(f"Boss level {self.level} initialized with {self.health} health")
    
    def _create_flash_images(self):
        """预先创建闪烁效果的图像序列"""
        flash_images = []
        
        # 创建原始图像的副本
        base_image = self.original_image.copy()
        flash_images.append(base_image)  # 第一帧是原始图像
        
        # 创建发光红色效果图像
        red_image = base_image.copy()
        # 创建叠加用的红色表面
        red_overlay = pygame.Surface(red_image.get_size(), pygame.SRCALPHA)
        red_overlay.fill((255, 0, 0, 100))  # 半透明红色
        # 应用叠加
        red_image.blit(red_overlay, (0, 0))
        flash_images.append(red_image)  # 第二帧是红色版本
        
        return flash_images
        
    def update(self):
        """更新Boss状态"""
        # Boss入场动画
        if self.rect.top < 50:
            self.rect.y += 2
        else:
            # 左右移动
            self.move_counter += 1
            if self.move_counter >= 100:
                self.direction *= -1
                self.move_counter = 0
            
            self.rect.x += self.speedx * self.direction
            
            # 防止Boss飞出屏幕
            if self.rect.left < 0:
                self.rect.left = 0
                self.direction = 1
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
                self.direction = -1
        
        # Boss射击
        now = ptime.get_ticks()
        if now - self.last_shot > self.shoot_delay and self.rect.top >= 0:
            self.last_shot = now
            self.shoot()
        
        # 受伤闪烁效果
        if self.damage_flash > 0:
            self.damage_flash -= 1
            
            # 使用预先创建的闪烁图像序列
            if self.damage_flash % 2 == 0:  # 每隔一帧闪烁
                self.image = self.flash_images[1]  # 红色版本
            else:
                self.image = self.flash_images[0]  # 原始版本
                
            # 当闪烁结束时确保恢复原始图像
            if self.damage_flash == 0:
                self.image = self.original_image
                
            # 每次更新图像后更新碰撞掩码
            self.mask = pygame.mask.from_surface(self.image)
    
    def shoot(self):
        """发射子弹"""
        # 由于循环引用，需要从外部导入BossBullet
        from thunder_fighter.sprites.bullets import BossBullet
        
        # 根据等级决定子弹数量和方式
        if self.level == 1:
            # 1级Boss: 3颗子弹，直线发射
            offsets = [-30, 0, 30]
        elif self.level == 2:
            # 2级Boss: 4颗子弹，扇形分布
            offsets = [-45, -15, 15, 45]
        else:
            # 3级Boss: 5颗子弹，更密集的扇形分布
            offsets = [-60, -30, 0, 30, 60]
            
        # 发射子弹
        for offset in offsets[:self.bullet_count]:
            boss_bullet = BossBullet(self.rect.centerx + offset, self.rect.bottom)
            self.all_sprites.add(boss_bullet)
            self.boss_bullets_group.add(boss_bullet)
    
    def draw_health_bar(self, surface):
        """绘制Boss血条"""
        # 绘制血条背景
        bar_width = self.rect.width
        bar_height = 8
        bar_x = self.rect.x
        bar_y = self.rect.y - 15
        
        # 防止血条超出屏幕顶部
        if bar_y < 10:
            bar_y = 10
            
        draw_health_bar(surface, bar_x, bar_y, bar_width, bar_height, 
                        self.health, self.max_health) 