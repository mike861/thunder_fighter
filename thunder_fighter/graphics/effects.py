import pygame
import random
from thunder_fighter.sprites.explosion import Explosion
import math
from thunder_fighter.constants import WIDTH, HEIGHT, WHITE, YELLOW, RED, GREEN

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

class Notification:
    """用于显示临时通知消息的类"""
    def __init__(self, text, duration=2000, color=WHITE, size=30, position='center'):
        try:
            self.font = pygame.font.SysFont(None, size)
        except (pygame.error, AttributeError):
            # If pygame font is not initialized or available (test environment)
            # Create a dummy font interface
            class DummyFont:
                def render(self, text, antialias=True, color=(255, 255, 255)):
                    # Create a dummy surface with the essential methods
                    if hasattr(pygame, 'Surface'):
                        surf = pygame.Surface((len(text) * 10, size))
                        rect = surf.get_rect()
                        return surf
                    else:
                        # Pure mock for extreme cases
                        mock_surf = type('MockSurface', (), {
                            'get_rect': lambda: type('MockRect', (), {
                                'center': (0, 0),
                                'centerx': 0,
                                'centery': 0
                            })()
                        })()
                        return mock_surf
            self.font = DummyFont()
            
        self.text = text
        self.color = color
        self.creation_time = pygame.time.get_ticks() if hasattr(pygame, 'time') else 0
        self.duration = duration  # 持续时间（毫秒）
        self.alpha = 255  # 完全不透明
        self.position = position
        
        # Create the text surface
        try:
            self.surface = self.font.render(text, True, color)
            self.rect = self.surface.get_rect()
        except (pygame.error, AttributeError):
            # Create dummy surface and rect for test environments
            if hasattr(pygame, 'Surface'):
                self.surface = pygame.Surface((len(text) * 10, size))
            else:
                self.surface = type('MockSurface', (), {})()
            self.rect = type('MockRect', (), {
                'center': (WIDTH // 2, HEIGHT // 2),
                'centerx': WIDTH // 2,
                'centery': HEIGHT // 2
            })()
        
        # 根据position设置位置
        if position == 'center':
            self.rect.center = (WIDTH // 2, HEIGHT // 2)
        elif position == 'top':
            self.rect.center = (WIDTH // 2, 100)
        elif position == 'bottom':
            self.rect.center = (WIDTH // 2, HEIGHT - 100)
            
        # 添加垂直偏移量，用于多条消息堆叠显示
        self.y_offset = 0
    
    def update(self):
        """更新通知状态，检查是否应该消失"""
        if hasattr(pygame, 'time'):
            current_time = pygame.time.get_ticks()
        else:
            # For test environments without pygame.time
            return True  # Just keep notifications alive in tests
            
        time_passed = current_time - self.creation_time
        
        # 如果超过持续时间，返回False表示通知应该被移除
        if time_passed > self.duration:
            return False
        
        # 在最后500毫秒逐渐淡出
        if time_passed > self.duration - 500:
            # 计算淡出效果的alpha值
            self.alpha = max(0, int(255 * (self.duration - time_passed) / 500))
        
        return True
    
    def set_y_position(self, y):
        """设置通知的Y坐标位置，保持X坐标不变"""
        old_center_x = self.rect.centerx
        self.rect.centery = y
        self.rect.centerx = old_center_x
    
    def draw(self, surface):
        """在屏幕上绘制通知"""
        try:
            # 创建一个带有alpha通道的临时surface
            temp_surface = pygame.Surface(self.surface.get_size(), pygame.SRCALPHA)
            temp_surface.fill((0, 0, 0, 0))  # 完全透明填充
            temp_surface.blit(self.surface, (0, 0))
            
            # 应用alpha值
            temp_surface.set_alpha(self.alpha)
            
            # 绘制到屏幕上
            surface.blit(temp_surface, self.rect)
        except (pygame.error, AttributeError):
            # In test environment, just pass
            pass


class WarningNotification(Notification):
    """特殊的警告通知，有闪烁效果和更长的持续时间"""
    def __init__(self, text, duration=3000, color=YELLOW, size=36, position='top'):
        super().__init__(text, duration, color, size, position)
        self.flash_speed = 200  # 闪烁速度（毫秒）
        self.flash_colors = [YELLOW, RED]  # 闪烁颜色
        self.current_color_index = 0
        self.last_flash = self.creation_time
    
    def update(self):
        """更新警告通知状态，增加闪烁效果"""
        current_time = pygame.time.get_ticks()
        
        # 处理闪烁效果
        if current_time - self.last_flash > self.flash_speed:
            self.last_flash = current_time
            self.current_color_index = (self.current_color_index + 1) % len(self.flash_colors)
            self.surface = self.font.render(self.text, True, self.flash_colors[self.current_color_index])
        
        # 调用父类的update来处理淡出和时间检查
        return super().update()


class AchievementNotification(Notification):
    """成就或积极事件通知，带有绿色和特殊效果"""
    def __init__(self, text, duration=2500, color=GREEN, size=32, position='bottom'):
        super().__init__(text, duration, color, size, position)
        # 添加任何特殊效果或自定义逻辑 