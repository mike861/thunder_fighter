import pygame
import random
import math
import pygame.time as ptime
from thunder_fighter.constants import (
    WIDTH, HEIGHT, ENEMY_MIN_SHOOT_DELAY, ENEMY_MAX_SHOOT_DELAY,
    ENEMY_SHOOT_LEVEL, ENEMY_SPAWN_Y_MIN, ENEMY_SPAWN_Y_MAX,
    ENEMY_HORIZONTAL_MOVE_MIN, ENEMY_HORIZONTAL_MOVE_MAX,
    ENEMY_ROTATION_UPDATE, ENEMY_SCREEN_BOUNDS
)
from thunder_fighter.graphics.renderers import create_enemy_ship
from thunder_fighter.sprites.bullets import EnemyBullet
from thunder_fighter.utils.logger import logger
import traceback

class Enemy(pygame.sprite.Sprite):
    """Enemy class"""
    def __init__(self, game_time=0, game_level=1, all_sprites=None, enemy_bullets_group=None):
        pygame.sprite.Sprite.__init__(self)
        
        # Determine level based on game time and game level
        self.level = self._determine_level(game_time, game_level)
        
        # Create image based on level
        self.image = create_enemy_ship(self.level)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(ENEMY_SPAWN_Y_MIN, ENEMY_SPAWN_Y_MAX)
        
        # Adjust speed based on game time and level
        base_speed_factor = min(3.0, 1.0 + game_time / 60.0)
        level_speed_bonus = self.level * 0.2
        total_speed_factor = base_speed_factor + level_speed_bonus
        self.speedy = random.randrange(1, int(3 + 3 * total_speed_factor))
        self.speedx = random.randrange(ENEMY_HORIZONTAL_MOVE_MIN, ENEMY_HORIZONTAL_MOVE_MAX)
        
        # Rotation animation properties
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()
        self.original_image = self.image.copy()
        
        # Shooting capability
        self.can_shoot = self.level >= ENEMY_SHOOT_LEVEL
        logger.debug(f"Enemy ID:{id(self)} Level: {self.level}, Can Shoot: {self.can_shoot}")
        
        # Sprite groups for bullets
        self.all_sprites = all_sprites
        self.enemy_bullets_group = enemy_bullets_group
        
        # Shooting properties
        if self.can_shoot:
            base_delay = 800
            level_reduction = self.level * 50
            self.shoot_delay = max(ENEMY_MIN_SHOOT_DELAY, base_delay - level_reduction)
            if self.level >= 5:
                self.shoot_delay = max(300, self.shoot_delay - 100)
            self.last_shot = pygame.time.get_ticks() - self.shoot_delay + random.randint(0, 1000)
            logger.debug(f"Enemy ID:{id(self)} Level:{self.level} Ready to shoot, Delay:{self.shoot_delay}ms")
    
    def _determine_level(self, game_time, game_level):
        """根据游戏时间和关卡等级确定敌人等级"""
        # 基础概率（基于游戏时间）
        base_probs = [
            max(0, 0.35 - game_time * 0.05),  # 0级
            max(0, 0.25 - game_time * 0.03),  # 1级
            max(0, 0.15),                     # 2级
            max(0, 0.10 + game_time * 0.01),  # 3级
            max(0, 0.05 + game_time * 0.015), # 4级
            max(0, 0.05 + game_time * 0.015), # 5级
            max(0, 0.02 + game_time * 0.01),  # 6级
            max(0, 0.02 + game_time * 0.01),  # 7级
            max(0, 0.01 + game_time * 0.005), # 8级
            max(0, 0.00 + game_time * 0.003), # 9级
            max(0, 0.00 + game_time * 0.002)  # 10级
        ]

        # 关卡等级影响 - 增加高等级敌人的概率
        # 每增加一级关卡，高等级敌人出现概率轻微提升
        level_boost = (game_level - 1) * 0.02 # 每关增加2%的高级敌人倾向
        
        # 将提升的概率从低等级转移到高等级 (简单线性转移)
        transfer_prob = 0.0
        for i in range(len(base_probs)):
            # 从0-4级敌人转移概率
            if i < 5:
                reduction = base_probs[i] * level_boost * (5 - i) / 5 # 低等级减少更多
                reduction = min(base_probs[i], reduction) # 不能减少超过本身概率
                base_probs[i] -= reduction
                transfer_prob += reduction
            # 将概率添加到5-10级敌人
            elif i >= 5:
                # 按比例分配转移过来的概率
                boost_share = transfer_prob / max(1, len(base_probs) - 5) # 平均分配
                base_probs[i] += boost_share
                transfer_prob -= boost_share # 更新剩余转移概率
                
        # 确保概率不为负，并进行细微调整防止全0
        for i in range(len(base_probs)):
            base_probs[i] = max(0.001, base_probs[i]) # 保证每个等级都有极小概率出现

        # 归一化概率总和为1
        total = sum(base_probs)
        if total > 0:
            probs = [p / total for p in base_probs]
        else:
            probs = [1/len(base_probs)] * len(base_probs)
        
        # 根据最终概率选择等级
        chosen_level = random.choices(range(11), weights=probs, k=1)[0]
        logger.debug(f"Determined enemy level {chosen_level} (game_time: {game_time:.1f}, game_level: {game_level})")
        return chosen_level
        
    def update(self):
        """更新敌人状态"""
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        
        # 旋转动画（仅对快速移动的敌人）
        if abs(self.speedx) > 1:
            now = pygame.time.get_ticks()
            if now - self.last_update > ENEMY_ROTATION_UPDATE:
                self.last_update = now
                self.rot = (self.rot + self.rot_speed) % 360
                self.image = pygame.transform.rotate(self.original_image, self.rot)
                old_center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = old_center
        
        # If enemy goes off-screen, remove it
        if (self.rect.top > HEIGHT + ENEMY_SCREEN_BOUNDS or 
            self.rect.left < -ENEMY_SCREEN_BOUNDS or 
            self.rect.right > WIDTH + ENEMY_SCREEN_BOUNDS):
            logger.debug(f"Enemy ID:{id(self)} killed (off-screen).")
            self.kill()
        
        # Check if enemy can shoot
        time_now = ptime.get_ticks()
        if self.can_shoot and time_now - self.last_shot > self.shoot_delay:
            # Check if enemy is visible on screen
            if self.rect.bottom > 0 and self.rect.top < HEIGHT:
                if self.shoot():
                    self.last_shot = time_now
                    # Log shooting event (changed from print)
                    logger.debug(f"Enemy ID:{id(self)} Level:{self.level} Fired! Delay:{self.shoot_delay}ms")
    
    def shoot(self):
        """Fires a bullet"""
        try:
            # Ensure sprite groups exist
            if not hasattr(self, 'all_sprites') or not hasattr(self, 'enemy_bullets_group'):
                logger.error(f"Error: Enemy {id(self)} missing required sprite groups for shooting.")
                return False

            # Check shooting capability again (redundant but safe)
            if not self.can_shoot:
                return False
                
            # Create bullet
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom, self.level)
            
            # Add bullet to game sprite groups
            self.all_sprites.add(bullet)
            self.enemy_bullets_group.add(bullet)
            
            return True
            
        except Exception as e:
            # Log shooting error (changed from print)
            logger.error(f"Enemy shooting error: {str(e)}", exc_info=True)
            # traceback.print_exc() # Logger includes traceback with exc_info=True
            return False
    
    def get_level(self):
        """获取敌人等级"""
        return self.level 