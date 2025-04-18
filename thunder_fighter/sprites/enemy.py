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
    def __init__(self, game_time=0, all_sprites=None, enemy_bullets_group=None):
        pygame.sprite.Sprite.__init__(self)
        
        # Determine level
        self.level = self._determine_level(game_time)
        
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
    
    def _determine_level(self, game_time):
        """根据游戏时间确定敌人等级"""
        # 计算每个等级的基础概率
        base_probs = [
            0.35 - game_time * 0.05,  # 0级，随时间降低概率
            0.25 - game_time * 0.03,  # 1级，随时间略微降低概率
            0.15,                     # 2级，基础概率保持不变
            0.10 + game_time * 0.01,  # 3级，随时间增加概率
            0.05 + game_time * 0.015, # 4级
            0.05 + game_time * 0.015, # 5级
            0.02 + game_time * 0.01,  # 6级
            0.02 + game_time * 0.01,  # 7级
            0.01 + game_time * 0.005, # 8级
            0.00 + game_time * 0.003, # 9级
            0.00 + game_time * 0.002  # 10级
        ]
        
        # 确保概率范围在0-1之间
        for i in range(len(base_probs)):
            base_probs[i] = max(0, min(base_probs[i], 1))
        
        # 归一化概率总和为1
        total = sum(base_probs)
        if total > 0:
            probs = [p / total for p in base_probs]
        else:
            probs = [1/len(base_probs)] * len(base_probs)
        
        # 游戏前3分钟，提高2-4级敌人的生成几率，确保玩家能看到射击效果
        if game_time < 3:
            # 强制至少30%的敌人是2级及以上
            shooting_enemies_prob = sum(probs[2:5])
            if shooting_enemies_prob < 0.3:
                # 提高2-4级敌人概率
                boost_factor = 0.3 / max(0.01, shooting_enemies_prob)
                for i in range(2, 5):
                    probs[i] *= boost_factor
                # 重新归一化
                total = sum(probs)
                probs = [p / total for p in probs]
        
        # 根据概率选择等级
        return random.choices(range(11), weights=probs, k=1)[0]
        
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