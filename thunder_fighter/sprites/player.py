import pygame
import pygame.time as ptime
import random
import math
from thunder_fighter.constants import (
    WIDTH, HEIGHT, PLAYER_HEALTH, PLAYER_SHOOT_DELAY, WHITE, RED,
<<<<<<< HEAD
    PLAYER_SPEED, PLAYER_FLASH_FRAMES, PLAYER_HEAL_AMOUNT,
=======
    PLAYER_SPEED, PLAYER_MAX_SPEED, PLAYER_SPEED_UPGRADE_AMOUNT, PLAYER_FLASH_FRAMES, PLAYER_HEAL_AMOUNT,
>>>>>>> origin/init
    BULLET_SPEED_DEFAULT, BULLET_SPEED_MAX, BULLET_PATHS_DEFAULT, BULLET_PATHS_MAX,
    BULLET_ANGLE_STRAIGHT, BULLET_ANGLE_SPREAD_SMALL, BULLET_ANGLE_SPREAD_LARGE,
    BULLET_SPEED_UPGRADE_AMOUNT
)
from thunder_fighter.graphics.renderers import create_player_ship
from thunder_fighter.sprites.bullets import Bullet
from thunder_fighter.graphics.effects import create_explosion, create_hit_effect
# 导入音效管理器
from thunder_fighter.utils.sound_manager import sound_manager
from thunder_fighter.utils.logger import logger

class Player(pygame.sprite.Sprite):
    """玩家类"""
    def __init__(self, all_sprites, bullets_group):
        pygame.sprite.Sprite.__init__(self)
        # 使用自绘图形代替矩形
        self.image = create_player_ship()
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
<<<<<<< HEAD
=======
        self.speed = PLAYER_SPEED # Use self.speed for current player speed
        self.max_speed = PLAYER_MAX_SPEED
>>>>>>> origin/init
        self.speedx = 0
        self.speedy = 0
        self.health = PLAYER_HEALTH
        self.shoot_delay = PLAYER_SHOOT_DELAY
        self.last_shot = ptime.get_ticks()
        # 添加推进器动画效果
        self.thrust = 0
        
        # 子弹属性
        self.bullet_speed = BULLET_SPEED_DEFAULT
        self.max_bullet_speed = BULLET_SPEED_MAX
        self.bullet_paths = BULLET_PATHS_DEFAULT
        self.max_bullet_paths = BULLET_PATHS_MAX
        
        # 精灵组
        self.all_sprites = all_sprites
        self.bullets_group = bullets_group
        
        # 视觉效果
        self.flash_timer = 0
        self.flash_duration = 0
        self.original_image = self.image.copy()
        
        # 动画效果
        self.angle = 0  # 用于旋转动画
        
    def update(self):
        """更新玩家状态"""
        # 移动速度重置
        self.speedx = 0
        self.speedy = 0
        
        # 获取按键
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT] or keystate[pygame.K_a]:
<<<<<<< HEAD
            self.speedx = -PLAYER_SPEED
        if keystate[pygame.K_RIGHT] or keystate[pygame.K_d]:
            self.speedx = PLAYER_SPEED
        if keystate[pygame.K_UP] or keystate[pygame.K_w]:
            self.speedy = -PLAYER_SPEED
        if keystate[pygame.K_DOWN] or keystate[pygame.K_s]:
            self.speedy = PLAYER_SPEED
=======
            self.speedx = -self.speed # Use current speed
        if keystate[pygame.K_RIGHT] or keystate[pygame.K_d]:
            self.speedx = self.speed # Use current speed
        if keystate[pygame.K_UP] or keystate[pygame.K_w]:
            self.speedy = -self.speed # Use current speed
        if keystate[pygame.K_DOWN] or keystate[pygame.K_s]:
            self.speedy = self.speed # Use current speed
>>>>>>> origin/init
        
        # 射击
        if keystate[pygame.K_SPACE]:
            self.shoot()
            
        # 移动玩家
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        
        # 限制玩家不要出界
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            
        # 更新推进器动画
        self.thrust = (self.thrust + 1) % 10
        
        # 闪烁效果
        current_time = ptime.get_ticks()
        if self.flash_timer > 0:
            # 每100毫秒切换一次可见性
            if (current_time // 100) % 2 == 0:
                self.image = self.original_image.copy()
            else:
                self.image = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
                self.image.fill((0, 0, 0, 0))  # 完全透明
            
            # 减少计时器
            self.flash_timer -= 1
        
        # 飞机轻微的浮动动画
        self.angle = (self.angle + 1) % 360
        dy = math.sin(math.radians(self.angle)) * 0.5  # 微小的上下浮动
        self.rect.y += dy
            
    def shoot(self):
        """发射子弹"""
        now = ptime.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            
            # 播放射击音效
            sound_manager.play_sound('player_shoot')
            
            # 根据弹道数量创建不同数量和角度的子弹
            if self.bullet_paths == 1:
                # 单发直射
                bullet = Bullet(self.rect.centerx, self.rect.top, self.bullet_speed, BULLET_ANGLE_STRAIGHT)
                self.all_sprites.add(bullet)
                self.bullets_group.add(bullet)
            elif self.bullet_paths == 2:
                # 双发平行
                bullet1 = Bullet(self.rect.left + 5, self.rect.top, self.bullet_speed, BULLET_ANGLE_STRAIGHT)
                bullet2 = Bullet(self.rect.right - 5, self.rect.top, self.bullet_speed, BULLET_ANGLE_STRAIGHT)
                self.all_sprites.add(bullet1, bullet2)
                self.bullets_group.add(bullet1, bullet2)
            elif self.bullet_paths == 3:
                # 三发：一直射，两斜射
                bullet1 = Bullet(self.rect.centerx, self.rect.top, self.bullet_speed, BULLET_ANGLE_STRAIGHT)  # 中间直射
                bullet2 = Bullet(self.rect.left + 5, self.rect.top, self.bullet_speed, -BULLET_ANGLE_SPREAD_SMALL)  # 左斜射
                bullet3 = Bullet(self.rect.right - 5, self.rect.top, self.bullet_speed, BULLET_ANGLE_SPREAD_SMALL)  # 右斜射
                self.all_sprites.add(bullet1, bullet2, bullet3)
                self.bullets_group.add(bullet1, bullet2, bullet3)
            elif self.bullet_paths >= 4:
                # 四发或更多（最大限制为4）：两直射，两斜射
                bullet1 = Bullet(self.rect.centerx - 8, self.rect.top, self.bullet_speed, BULLET_ANGLE_STRAIGHT)  # 左中直射
                bullet2 = Bullet(self.rect.centerx + 8, self.rect.top, self.bullet_speed, BULLET_ANGLE_STRAIGHT)  # 右中直射
                bullet3 = Bullet(self.rect.left + 5, self.rect.top, self.bullet_speed, -BULLET_ANGLE_SPREAD_LARGE)  # 左斜射
                bullet4 = Bullet(self.rect.right - 5, self.rect.top, self.bullet_speed, BULLET_ANGLE_SPREAD_LARGE)  # 右斜射
                self.all_sprites.add(bullet1, bullet2, bullet3, bullet4)
                self.bullets_group.add(bullet1, bullet2, bullet3, bullet4)
    
    def take_damage(self, damage=10):
        """玩家受到伤害"""
        self.health -= damage
        
        # 受伤闪烁效果
        self.flash_timer = PLAYER_FLASH_FRAMES
        
        # 创建受伤特效
        hit_effect = create_hit_effect(self.rect.centerx, self.rect.centery)
        self.all_sprites.add(hit_effect)
        
        # 播放受伤音效
        sound_manager.play_sound('player_hit')
        
        return self.health <= 0  # 返回是否死亡
    
    def heal(self, amount=PLAYER_HEAL_AMOUNT):
        """玩家回血"""
        self.health = min(PLAYER_HEALTH, self.health + amount)
    
    def increase_bullet_speed(self, amount=BULLET_SPEED_UPGRADE_AMOUNT):
        """增加子弹速度"""
        self.bullet_speed = min(self.max_bullet_speed, self.bullet_speed + amount)
        return self.bullet_speed
        
    def increase_bullet_paths(self):
        """增加弹道数量"""
        if self.bullet_paths < self.max_bullet_paths:
            self.bullet_paths += 1
<<<<<<< HEAD
        return self.bullet_paths 
=======
        return self.bullet_paths

    def increase_player_speed(self, amount=PLAYER_SPEED_UPGRADE_AMOUNT):
        """增加玩家移动速度"""
        self.speed = min(self.max_speed, self.speed + amount)
        logger.info(f"Player speed increased to: {self.speed}")
        return self.speed 
>>>>>>> origin/init
