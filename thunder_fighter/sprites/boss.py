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
    def __init__(self, all_sprites, boss_bullets_group, level=None, game_level=1, player=None):
        pygame.sprite.Sprite.__init__(self)
        
        # 确定Boss等级 - 如果未指定，根据游戏进度随机生成
        if level is None:
            self.level = random.randint(1, BOSS_MAX_LEVEL)
        else:
            self.level = min(level, BOSS_MAX_LEVEL)
            
        self.game_level = game_level # Store the overall game level
        self.player = player  # 存储玩家引用，用于追踪
        
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
        
        # 设置初始攻击模式
        self.shoot_pattern = "normal"
        
        self.last_shot = ptime.get_ticks()
        self.direction = 1  # 移动方向
        self.move_counter = 0
        self.damage_flash = 0
        
        # 预先创建闪烁图像
        self.flash_images = self._create_flash_images()
        
        # 定义基础移动速度和范围
        self.base_speedx = 2
        self.move_margin = 10 # Minimum margin from screen edge

        # 精灵组
        self.all_sprites = all_sprites
        self.boss_bullets_group = boss_bullets_group
        
        # Boss初始化信息应该显示在游戏UI中，而不仅仅是日志
        logger.debug(f"Boss level {self.level} initialized with {self.health} health")
    
    def _create_flash_images(self):
        """预先创建闪烁效果的图像序列"""
        flash_images = []
        
        # 创建原始图像的副本
        base_image = self.original_image.copy()
        flash_images.append(base_image)  # 第一帧是原始图像
        
        # 创建多种闪烁效果图像
        # 方法1: 强烈红色叠加
        red_image = self.original_image.copy()
        red_overlay = pygame.Surface(red_image.get_size())
        red_overlay.fill((255, 80, 80))  # 非常亮的红色
        red_image.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        flash_images.append(red_image)
        
        # 方法2: 纯白色高亮（最明显的闪烁效果）
        white_image = self.original_image.copy()
        white_overlay = pygame.Surface(white_image.get_size())
        white_overlay.fill((180, 180, 180))  # 非常亮的白色叠加
        white_image.blit(white_overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        flash_images.append(white_image)
        
        # 方法3: 黄色警告效果（额外的闪烁变化）
        yellow_image = self.original_image.copy()
        yellow_overlay = pygame.Surface(yellow_image.get_size())
        yellow_overlay.fill((200, 200, 0))  # 亮黄色
        yellow_image.blit(yellow_overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        flash_images.append(yellow_image)
        
        return flash_images
    
    def damage(self, amount):
        """处理Boss受到的伤害
        
        Args:
            amount: 伤害值
        
        Returns:
            bool: 如果Boss被摧毁返回True，否则返回False
        """
        self.health -= amount
        self.damage_flash = 12  # 增加闪烁帧数，使效果更明显
        
        # 根据Boss等级和血量百分比决定攻击模式转换
        health_percentage = self.health / self.max_health
        
        # 2级及以上Boss才能进入激进模式
        if (health_percentage <= 0.5 and 
            self.shoot_pattern == "normal" and 
            self.level >= 2):
            self.shoot_pattern = "aggressive"
            # 当生命值降低时，减少射击延迟，增加攻击频率
            self.shoot_delay = max(150, self.shoot_delay * 0.7)
            # Boss进入激进模式的信息应该在游戏UI中显示
            logger.debug(f"Level {self.level} Boss entered aggressive mode! Shoot delay: {self.shoot_delay}")
        
        # 3级及以上Boss才能进入最终模式
        if (health_percentage <= 0.25 and 
            self.shoot_pattern == "aggressive" and 
            self.level >= 3):
            self.shoot_pattern = "final"
            # 再次减少射击延迟
            self.shoot_delay = max(100, self.shoot_delay * 0.8)
            # Boss进入最终模式的信息应该在游戏UI中显示
            logger.debug(f"Level {self.level} Boss entered final mode! Shoot delay: {self.shoot_delay}")
        
        # 检查是否被摧毁
        if self.health <= 0:
            self.kill()
            return True
        
        return False
        
    def update(self):
        """更新Boss状态"""
        # Boss入场动画
        if self.rect.top < 50:
            self.rect.y += 2
        else:
            # 左右移动
            self.move_counter += 1
            if self.move_counter >= 100: # Change direction periodically
                self.direction *= -1
                self.move_counter = 0
            
            # Calculate dynamic movement boundaries based on game_level
            # Higher game_level allows moving closer to the edges
            max_movement_range = (WIDTH - self.rect.width - 2 * self.move_margin)
            # Reduce margin based on game level, but keep at least a small margin
            current_margin = max(5, self.move_margin + 50 - self.game_level * 5)
            
            left_boundary = current_margin
            right_boundary = WIDTH - self.rect.width - current_margin

            # Adjust speed slightly based on game level
            current_speedx = self.base_speedx + (self.game_level - 1) * 0.1

            self.rect.x += current_speedx * self.direction
            
            # 防止Boss飞出动态边界
            if self.rect.left < left_boundary:
                self.rect.left = left_boundary
                self.direction = 1 # Force move right
                self.move_counter = 0 # Reset move counter to prevent getting stuck
            if self.rect.right > right_boundary:
                self.rect.right = right_boundary
                self.direction = -1 # Force move left
                self.move_counter = 0 # Reset move counter
        
        # Boss射击
        now = ptime.get_ticks()
        if now - self.last_shot > self.shoot_delay and self.rect.top >= 0:
            self.last_shot = now
            self.shoot()
        
        # 受伤闪烁效果
        if self.damage_flash > 0:
            self.damage_flash -= 1
            
            # 使用更强烈和多样化的闪烁效果
            if self.damage_flash > 0:
                # 根据闪烁帧数选择不同的效果，创造更动态的闪烁
                flash_cycle = self.damage_flash % 6
                if flash_cycle == 0:
                    self.image = self.flash_images[2]  # 白色高亮版本（最明显）
                elif flash_cycle == 1:
                    self.image = self.flash_images[3]  # 黄色警告版本
                elif flash_cycle == 2:
                    self.image = self.flash_images[2]  # 再次白色高亮
                elif flash_cycle == 3:
                    self.image = self.flash_images[1]  # 红色版本
                elif flash_cycle == 4:
                    self.image = self.flash_images[0]  # 原始版本
                else:  # flash_cycle == 5
                    self.image = self.flash_images[1]  # 红色版本
            else:
                # 当闪烁结束时确保恢复原始图像
                self.image = self.original_image.copy()  # Use copy to avoid reference issues
    
    def shoot(self):
        """发射子弹"""
        # 由于循环引用，需要从外部导入BossBullet
        from thunder_fighter.sprites.bullets import BossBullet
        
        # 根据等级和攻击模式决定子弹数量和方式
        if self.shoot_pattern == "normal":
            if self.level == 1:
                # 1级Boss: 3颗子弹，直线发射
                offsets = [-30, 0, 30]
            elif self.level == 2:
                # 2级Boss: 4颗子弹，扇形分布
                offsets = [-45, -15, 15, 45]
            else:
                # 3级Boss: 5颗子弹，更密集的扇形分布
                offsets = [-60, -30, 0, 30, 60]
        elif self.shoot_pattern == "aggressive":
            # 激进模式下，增加子弹数量和分布范围
            if self.level == 1:
                # 1级Boss: 4颗子弹，更宽的扇形
                offsets = [-45, -15, 15, 45]
            elif self.level == 2:
                # 2级Boss: 5颗子弹，更宽的扇形
                offsets = [-60, -30, 0, 30, 60]
            else:
                # 3级Boss: 6颗子弹，更密集的扇形分布
                offsets = [-75, -45, -15, 15, 45, 75]
        else:  # "final" 模式
            # 最终模式下，最大范围和子弹数量
            if self.level == 1:
                # 1级Boss: 5颗子弹，宽扇形
                offsets = [-60, -30, 0, 30, 60]
            elif self.level == 2:
                # 2级Boss: 6颗子弹，宽扇形
                offsets = [-75, -45, -15, 15, 45, 75]
            else:
                # 3级Boss: 7颗子弹，几乎全屏扇形
                offsets = [-90, -60, -30, 0, 30, 60, 90]
            
        # 最终使用数量不超过设定的子弹数
        offsets = offsets[:self.bullet_count]
            
        # 获取玩家位置（用于Final模式追踪）
        target_pos = None
        if self.shoot_pattern == "final" and self.player and hasattr(self.player, 'rect'):
            target_pos = (self.player.rect.centerx, self.player.rect.centery)
        
        # 发射子弹
        for offset in offsets:
            boss_bullet = BossBullet(self.rect.centerx + offset, self.rect.bottom, self.shoot_pattern, target_pos)
            self.all_sprites.add(boss_bullet)
            self.boss_bullets_group.add(boss_bullet)
    
    def draw_health_bar(self, surface):
        """绘制Boss血条"""
        # 计算血条尺寸和位置
        bar_width = max(self.rect.width + 20, 120)  # 血条比boss稍宽一些，但至少120像素
        bar_height = 12  # 增加血条高度
        bar_x = self.rect.centerx - bar_width // 2  # 血条居中对齐boss
        bar_y = self.rect.y - 25  # 血条距离boss顶部25像素
        
        # 防止血条超出屏幕顶部
        if bar_y < 5:
            bar_y = 5
        
        # 防止血条超出屏幕左右边界  
        if bar_x < 5:
            bar_x = 5
        elif bar_x + bar_width > WIDTH - 5:
            bar_x = WIDTH - bar_width - 5
            
        # 绘制血条主体
        draw_health_bar(surface, bar_x, bar_y, bar_width, bar_height, 
                        self.health, self.max_health)
        
        # 根据攻击模式添加血条边框效果
        from thunder_fighter.constants import WHITE, RED, YELLOW, ORANGE
        import pygame
        
        if self.shoot_pattern == "aggressive":
            # 激进模式：黄色边框
            pygame.draw.rect(surface, YELLOW, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), 2)
        elif self.shoot_pattern == "final":
            # 最终模式：红色闪烁边框
            border_color = RED if (pygame.time.get_ticks() // 200) % 2 else ORANGE
            pygame.draw.rect(surface, border_color, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), 3)
        
        # 绘制boss等级标识和模式
        mode_indicators = {
            "normal": "",
            "aggressive": " [危险]",
            "final": " [极限]"
        }
        level_text = f"BOSS Lv.{self.level}{mode_indicators.get(self.shoot_pattern, '')}"
        
        font = pygame.font.Font(None, 20)
        
        # 根据模式改变文字颜色
        text_color = WHITE
        if self.shoot_pattern == "aggressive":
            text_color = YELLOW
        elif self.shoot_pattern == "final":
            text_color = RED
            
        level_surface = font.render(level_text, True, text_color)
        level_rect = level_surface.get_rect()
        level_rect.centerx = bar_x + bar_width // 2
        level_rect.bottom = bar_y - 2  # 显示在血条上方
        
        # 如果等级文本超出屏幕顶部，则显示在血条下方
        if level_rect.top < 0:
            level_rect.top = bar_y + bar_height + 2
            
        surface.blit(level_surface, level_rect)
        
        # 绘制血量数值
        health_text = f"{self.health}/{self.max_health}"
        health_surface = font.render(health_text, True, WHITE)
        health_rect = health_surface.get_rect()
        health_rect.center = (bar_x + bar_width // 2, bar_y + bar_height // 2)
        surface.blit(health_surface, health_rect) 