import pygame
import random
import math
from thunder_fighter.constants import HEIGHT, WIDTH
from thunder_fighter.graphics.renderers import create_bullet, create_boss_bullet
from thunder_fighter.utils.logger import logger

class Bullet(pygame.sprite.Sprite):
    """玩家子弹类"""
    def __init__(self, x, y, speed=10, angle=0):
        pygame.sprite.Sprite.__init__(self)
        # 使用自绘图形代替矩形
        self.image = create_bullet()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        
        # 子弹速度和角度
        self.speed = speed
        self.angle = angle
        
        # 角度不为0时需要旋转图像
        if angle != 0:
            self.image = pygame.transform.rotate(self.image, -angle)
            self.rect = self.image.get_rect(center=self.rect.center)
        
        # 计算x和y方向的速度分量
        rad_angle = math.radians(angle)
        self.speedy = -self.speed * math.cos(rad_angle)
        self.speedx = self.speed * math.sin(rad_angle)
        
    def update(self):
        """更新子弹位置"""
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        
        # 如果子弹飞出屏幕则删除
        if (self.rect.bottom < 0 or 
            self.rect.right < 0 or 
            self.rect.left > WIDTH):
            self.kill()
            
class BossBullet(pygame.sprite.Sprite):
    """Boss子弹类"""
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = create_boss_bullet()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speedy = 5
        
    def update(self):
        """更新子弹位置"""
        self.rect.y += self.speedy
        # 如果子弹飞出屏幕底部则删除
        if self.rect.top > HEIGHT:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    """敌人子弹类"""
    def __init__(self, x, y, enemy_level=0):
        pygame.sprite.Sprite.__init__(self)
        # 根据敌人等级创建不同外观的子弹
        self.enemy_level = enemy_level
        self.image = self._create_enemy_bullet()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        # 将子弹生成位置稍微往下移动一点，确保不被敌机挡住
        self.rect.top = y + 5
        
        # 子弹速度与敌人等级关联，调整为更合理的数值
        base_speed = 5  # 降低基础速度
        level_bonus = min(3, enemy_level * 0.5)  # 降低等级加成
        self.speedy = base_speed + level_bonus
        
        # 高等级敌人子弹可能有水平速度
        if enemy_level >= 5:
            # 5级以上有25%概率有水平移动（降低概率）
            if random.random() < 0.25:
                self.speedx = random.choice([-2, -1, 1, 2])  # 降低水平速度
                # 8级以上可能有额外的曲线移动
                if enemy_level >= 8:
                    self.curve = True
                    self.angle = 0
                    self.curve_amplitude = random.uniform(0.5, 1.5)  # 降低曲线幅度
                else:
                    self.curve = False
            else:
                self.speedx = 0
                self.curve = False
        else:
            self.speedx = 0
            self.curve = False
            
        # Log bullet creation
        logger.debug(f"EnemyBullet created: Pos=({x}, {self.rect.top}), SpeedY={self.speedy:.2f}, SpeedX={getattr(self, 'speedx', 0)}, Level={enemy_level}")
    
    def _create_enemy_bullet(self):
        """根据敌人等级创建子弹外观"""
        # 减小子弹尺寸，降低与等级的关联度
        bullet_size = 4 + min(3, self.enemy_level // 2)  # 降低基础尺寸和等级增长系数
        
        # 创建子弹表面，整体尺寸减小
        bullet_surface = pygame.Surface((bullet_size * 1.5, bullet_size * 2), pygame.SRCALPHA)
        
        # 颜色根据敌人等级变化
        if self.enemy_level < 3:
            # 低级敌人子弹：红色
            bullet_color = (255, 50, 50)  # 更亮的红色
            glow_color = (255, 100, 100, 120)  # 降低发光不透明度
        elif self.enemy_level < 6:
            # 中级敌人子弹：橙色
            bullet_color = (255, 160, 0)  # 更亮的橙色
            glow_color = (255, 220, 0, 120)  # 降低发光不透明度
        elif self.enemy_level < 9:
            # 高级敌人子弹：蓝色
            bullet_color = (50, 170, 255)  # 更亮的蓝色
            glow_color = (100, 200, 255, 120)  # 降低发光不透明度
        else:
            # 超高级敌人子弹：紫色
            bullet_color = (200, 50, 250)  # 更亮的紫色
            glow_color = (220, 100, 250, 120)  # 降低发光不透明度
        
        # 绘制子弹核心，减小尺寸
        pygame.draw.rect(bullet_surface, bullet_color, (bullet_size/2, 0, bullet_size/1.5, bullet_size * 1.5))
        
        # 绘制子弹尾部，减小尺寸
        pygame.draw.rect(bullet_surface, (200, 200, 200), (bullet_size/2, bullet_size * 1.5, bullet_size/1.5, bullet_size/2))
        
        # 添加白色边框增加可见度
        pygame.draw.rect(bullet_surface, (255, 255, 255), (bullet_size/2, 0, bullet_size/1.5, bullet_size * 1.5), 1)
        
        # 减小发光效果
        # 创建一个小一些的发光圆
        glow_size = bullet_size * 3  # 原来是 * 5，降低发光范围
        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, glow_color, (glow_size/2, glow_size/2), bullet_size * 1)  # 原来是 * 1.5
        
        # 将发光效果绘制到子弹表面，调整偏移量适应新尺寸
        bullet_surface.blit(glow_surface, (-glow_size/2 + bullet_size/2, -bullet_size/2), special_flags=pygame.BLEND_ALPHA_SDL2)
            
        return bullet_surface
        
    def update(self):
        """更新子弹位置"""
        try:
            # 垂直移动
            self.rect.y += self.speedy
            
            # 水平移动
            if hasattr(self, 'speedx') and self.speedx != 0:
                self.rect.x += self.speedx
                
                # 曲线移动 (只有高等级敌人的子弹)
                if hasattr(self, 'curve') and self.curve:
                    if not hasattr(self, 'angle'):
                        self.angle = 0
                    self.angle = (self.angle + 5) % 360
                    curve_offset = int(self.curve_amplitude * pygame.math.Vector2(1, 0).rotate(self.angle).x)
                    self.rect.x += curve_offset
            
            # Remove bullet if it goes off screen
            if (self.rect.top > HEIGHT or 
                self.rect.right < 0 or 
                self.rect.left > WIDTH):
                logger.debug(f"EnemyBullet {id(self)} killed (off-screen).")
                self.kill()
        except Exception as e:
            # Log update error
            logger.error(f"EnemyBullet update error: {str(e)}", exc_info=True)
            self.kill() # Remove bullet on error 