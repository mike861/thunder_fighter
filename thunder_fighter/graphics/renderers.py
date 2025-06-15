import pygame
import os
from thunder_fighter.constants import *

def load_image(name, with_alpha=True):
    """加载图片"""
    fullname = os.path.join('game_assets', name)
    try:
        if with_alpha:
            image = pygame.image.load(fullname).convert_alpha()
        else:
            image = pygame.image.load(fullname).convert()
            image.set_colorkey(BLACK)
        return image
    except pygame.error:
        print(f"无法加载图像: {fullname}")
        return pygame.Surface((30, 30))

def create_player_ship():
    """创建玩家飞机表面"""
    # 创建一个表面，大小为50x40
    ship_surface = pygame.Surface((50, 40), pygame.SRCALPHA)
    
    # 绘制飞机主体 (三角形)
    points = [(25, 0), (0, 40), (50, 40)]
    pygame.draw.polygon(ship_surface, LIGHT_BLUE, points)
    
    # 绘制飞机内部细节
    pygame.draw.polygon(ship_surface, BLUE, [(15, 25), (25, 10), (35, 25)])
    
    # 绘制机翼
    pygame.draw.polygon(ship_surface, CYAN, [(5, 30), (15, 20), (20, 30)])
    pygame.draw.polygon(ship_surface, CYAN, [(45, 30), (35, 20), (30, 30)])
    
    # 绘制发动机
    pygame.draw.rect(ship_surface, ORANGE, (20, 35, 10, 5))
    
    # 绘制驾驶舱
    pygame.draw.ellipse(ship_surface, WHITE, (20, 15, 10, 10))
    
    # 添加边缘线条
    pygame.draw.lines(ship_surface, DARK_BLUE, True, points, 2)
    
    return ship_surface

def create_enemy_ship(level=0):
    """创建敌人飞机表面，根据级别改变外观"""
    # 创建一个表面，大小为30x40
    ship_surface = pygame.Surface((30, 40), pygame.SRCALPHA)
    
    # 基础敌人飞机形状
    points = [(15, 0), (0, 25), (30, 25)]
    
    # 根据级别选择颜色
    if level < 3:
        # 低级敌人: 红色
        main_color = RED
        secondary_color = DARK_RED
        glow_color = None
    elif level < 6:
        # 中级敌人: 橙色
        main_color = ORANGE
        secondary_color = (200, 80, 0)  # 深橙色
        glow_color = (255, 200, 0, 100)  # 发光效果
    elif level < 9:
        # 高级敌人: 蓝色
        main_color = (30, 144, 255)  # 道奇蓝
        secondary_color = DARK_BLUE
        glow_color = (0, 191, 255, 120)  # 天蓝色发光
    else:
        # 超高级敌人: 紫色
        main_color = PURPLE
        secondary_color = (75, 0, 130)  # 靛蓝色
        glow_color = (186, 85, 211, 150)  # 紫色发光
    
    # 绘制敌人飞机主体
    pygame.draw.polygon(ship_surface, main_color, points)
    
    # 绘制飞机底部
    pygame.draw.rect(ship_surface, secondary_color, (5, 25, 20, 15))
    
    # 为高级敌人添加发光效果
    if level >= 4 and glow_color:
        # 创建一个发光表面
        glow_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(glow_surface, glow_color, 
                            [(20, 5), (5, 30), (35, 30)])
        
        # 将发光效果叠加到飞机上
        ship_surface.blit(glow_surface, (-5, -5), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    # 绘制机翼 (级别越高，机翼越大)
    wing_size = min(5 + level // 2, 10)
    pygame.draw.polygon(ship_surface, main_color, [(0, 15), (5, 20), (10, 15)])
    pygame.draw.polygon(ship_surface, main_color, [(30, 15), (25, 20), (20, 15)])
    
    # 高级敌人有额外的机翼装饰
    if level >= 5:
        pygame.draw.polygon(ship_surface, secondary_color, [(0, 12), (2, 17), (5, 12)])
        pygame.draw.polygon(ship_surface, secondary_color, [(30, 12), (28, 17), (25, 12)])
    
    # 绘制驾驶舱
    cockpit_color = DARK_GRAY if level < 6 else (200, 200, 200)
    pygame.draw.ellipse(ship_surface, cockpit_color, (10, 10, 10, 10))
    
    # 添加级别特有的装饰
    if level >= 7:
        # 高级敌人有额外的装甲
        pygame.draw.rect(ship_surface, secondary_color, (10, 5, 10, 5))
        pygame.draw.rect(ship_surface, main_color, (12, 3, 6, 5))
    
    if level >= 9:
        # 最高级敌人有发光的引擎和武器槽
        pygame.draw.rect(ship_surface, (255, 255, 0, 200), (10, 30, 10, 5))
        pygame.draw.rect(ship_surface, (255, 150, 0, 200), (5, 22, 5, 5))
        pygame.draw.rect(ship_surface, (255, 150, 0, 200), (20, 22, 5, 5))
    
    # 添加边缘线条
    pygame.draw.lines(ship_surface, BLACK, True, points, 1)
    pygame.draw.rect(ship_surface, BLACK, (5, 25, 20, 15), 1)
    
    # 添加级别指示器 (每3个级别显示一个小点)
    for i in range(min(3, (level + 2) // 3)):
        dot_size = 2
        dot_x = 5 + i * (dot_size * 2 + 2)
        pygame.draw.circle(ship_surface, WHITE, (dot_x, 28), dot_size)
    
    return ship_surface

def create_boss_ship(level=1):
    """创建BOSS飞机表面，根据等级不同外观也不同"""
    # 创建一个表面，大小为100x80
    ship_surface = pygame.Surface((100, 80), pygame.SRCALPHA)
    
    # 根据等级选择颜色
    if level == 1:
        # 1级Boss: 紫色系
        main_color = PURPLE
        secondary_color = MAGENTA
        detail_color = RED
        engine_color = ORANGE
        cockpit_color = CYAN
    elif level == 2:
        # 2级Boss: 蓝色系
        main_color = BLUE
        secondary_color = DARK_BLUE
        detail_color = CYAN
        engine_color = LIGHT_BLUE
        cockpit_color = WHITE
    else:
        # 3级Boss: 红色系
        main_color = RED
        secondary_color = DARK_RED
        detail_color = ORANGE
        engine_color = YELLOW
        cockpit_color = LIGHT_BLUE
    
    # 绘制BOSS飞机主体
    points = [(50, 10), (10, 50), (90, 50)]
    pygame.draw.polygon(ship_surface, main_color, points)
    
    # 绘制BOSS飞机下半部
    pygame.draw.rect(ship_surface, secondary_color, (20, 50, 60, 30))
    
    # 绘制多个机翼
    pygame.draw.polygon(ship_surface, detail_color, [(0, 40), (20, 35), (10, 55)])
    pygame.draw.polygon(ship_surface, detail_color, [(100, 40), (80, 35), (90, 55)])
    pygame.draw.polygon(ship_surface, engine_color, [(10, 60), (25, 50), (30, 70)])
    pygame.draw.polygon(ship_surface, engine_color, [(90, 60), (75, 50), (70, 70)])
    
    # 绘制多个发动机
    pygame.draw.rect(ship_surface, engine_color, (30, 75, 10, 5))
    pygame.draw.rect(ship_surface, engine_color, (60, 75, 10, 5))
    pygame.draw.rect(ship_surface, YELLOW, (45, 70, 10, 10))
    
    # 绘制主驾驶舱
    pygame.draw.ellipse(ship_surface, cockpit_color, (40, 20, 20, 20))
    pygame.draw.ellipse(ship_surface, WHITE, (45, 25, 10, 10))
    
    # 添加装饰细节
    pygame.draw.circle(ship_surface, YELLOW, (50, 50), 8)
    pygame.draw.circle(ship_surface, WHITE, (50, 50), 3)
    
    # 根据等级添加额外特征
    if level >= 2:
        # 2级以上Boss有额外机炮
        pygame.draw.rect(ship_surface, detail_color, (15, 45, 5, 10))
        pygame.draw.rect(ship_surface, detail_color, (80, 45, 5, 10))
        
    if level >= 3:
        # 3级Boss有额外装甲和能量核心
        pygame.draw.rect(ship_surface, secondary_color, (35, 30, 30, 5))
        pygame.draw.circle(ship_surface, YELLOW, (50, 50), 12)
        pygame.draw.circle(ship_surface, WHITE, (50, 50), 6)
        
        # 简化发光效果，避免透明度混合问题
        # 直接在当前表面上绘制圆形
        for radius in range(25, 15, -2):
            # 使用递减的alpha值创建渐变发光效果
            alpha = max(10, 70 - (25 - radius) * 5)
            glow_color = (255, 255, 0, alpha)
            # 创建一个单独的表面用于发光效果
            glow_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, glow_color, (radius, radius), radius)
            # 将发光效果绘制到主表面上，位置居中
            ship_surface.blit(glow_surf, (50 - radius, 50 - radius))
    
    # 添加边缘线条
    pygame.draw.lines(ship_surface, DARK_BLUE, True, points, 2)
    pygame.draw.rect(ship_surface, DARK_BLUE, (20, 50, 60, 30), 2)
    
    # 等级指示器
    for i in range(level):
        pygame.draw.circle(ship_surface, WHITE, (85 - i*7, 65), 3)
    
    return ship_surface

def create_bullet():
    """创建子弹表面"""
    # 创建一个表面，大小为5x15
    bullet_surface = pygame.Surface((5, 15), pygame.SRCALPHA)
    
    # 绘制子弹
    pygame.draw.rect(bullet_surface, YELLOW, (0, 0, 5, 10))
    pygame.draw.rect(bullet_surface, ORANGE, (0, 10, 5, 5))
    
    # 添加光效
    pygame.draw.line(bullet_surface, WHITE, (2, 0), (2, 7), 1)
    
    return bullet_surface

def create_boss_bullet():
    """创建BOSS子弹表面"""
    # 创建一个表面，大小为10x20
    bullet_surface = pygame.Surface((10, 20), pygame.SRCALPHA)
    
    # 绘制BOSS子弹
    pygame.draw.rect(bullet_surface, MAGENTA, (0, 0, 10, 15))
    pygame.draw.rect(bullet_surface, PURPLE, (0, 15, 10, 5))
    
    # 添加光效
    pygame.draw.line(bullet_surface, WHITE, (5, 0), (5, 10), 2)
    
    return bullet_surface

def create_health_item():
    """创建血量道具表面"""
    # 创建一个表面，大小为30x30
    item_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    
    # 绘制圆形背景
    pygame.draw.circle(item_surface, PINK, (15, 15), 15)
    
    # 绘制十字形
    pygame.draw.rect(item_surface, RED, (5, 12, 20, 6))
    pygame.draw.rect(item_surface, RED, (12, 5, 6, 20))
    
    # 添加白色边缘
    pygame.draw.circle(item_surface, WHITE, (15, 15), 15, 2)
    
    return item_surface

def create_bullet_speed_item():
    """创建子弹速度提升道具表面"""
    # 创建一个表面，大小为30x30
    item_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    
    # 绘制圆形背景
    pygame.draw.circle(item_surface, LIGHT_BLUE, (15, 15), 15)
    
    # 绘制内部图案 - 闪电形状
    lightning_points = [
        (10, 5), (20, 5), (15, 12), 
        (20, 12), (10, 25), (15, 18), 
        (10, 18)
    ]
    pygame.draw.polygon(item_surface, YELLOW, lightning_points)
    
    # 添加发光效果
    glow_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(glow_surface, (0, 191, 255, 70), (20, 20), 18)
    item_surface.blit(glow_surface, (-5, -5), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    # 添加白色边缘
    pygame.draw.circle(item_surface, WHITE, (15, 15), 15, 2)
    
    return item_surface

def create_bullet_path_item():
    """创建子弹弹道增加道具表面"""
    # 创建一个表面，大小为30x30
    item_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    
    # 绘制圆形背景
    pygame.draw.circle(item_surface, GREEN, (15, 15), 15)
    
    # 绘制内部图案 - 多弹道图案
    # 中心点
    pygame.draw.circle(item_surface, WHITE, (15, 20), 3)
    
    # 弹道线
    pygame.draw.line(item_surface, WHITE, (15, 20), (15, 5), 2)
    pygame.draw.line(item_surface, WHITE, (15, 20), (8, 5), 2)
    pygame.draw.line(item_surface, WHITE, (15, 20), (22, 5), 2)
    
    # 弹道终点
    pygame.draw.circle(item_surface, YELLOW, (15, 5), 2)
    pygame.draw.circle(item_surface, YELLOW, (8, 5), 2)
    pygame.draw.circle(item_surface, YELLOW, (22, 5), 2)
    
    # 添加发光效果
    glow_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(glow_surface, (100, 255, 100, 70), (20, 20), 18)
    item_surface.blit(glow_surface, (-5, -5), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    # 添加白色边缘
    pygame.draw.circle(item_surface, WHITE, (15, 15), 15, 2)
    
    return item_surface

def create_player_speed_item():
    """创建玩家速度提升道具表面"""
    item_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    
    # 绘制圆形背景 (绿色系)
    pygame.draw.circle(item_surface, (0, 200, 0), (15, 15), 15)
    
    # 绘制内部图案 - 向上箭头
    arrow_points = [
        (15, 5),  # 箭头顶部
        (22, 15), # 右肩
        (18, 15), # 右颈
        (18, 25), # 右底
        (12, 25), # 左底
        (12, 15), # 左颈
        (8, 15)   # 左肩
    ]
    pygame.draw.polygon(item_surface, WHITE, arrow_points)
    
    # 添加发光效果
    glow_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(glow_surface, (100, 255, 100, 70), (20, 20), 18)
    item_surface.blit(glow_surface, (-5, -5), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    # 添加白色边缘
    pygame.draw.circle(item_surface, WHITE, (15, 15), 15, 2)
    
    return item_surface

def create_wingman():
    """创建僚机表面"""
    wingman_surface = pygame.Surface((20, 25), pygame.SRCALPHA)
    
    # 主体
    pygame.draw.polygon(wingman_surface, (0, 180, 255), [(10, 0), (0, 25), (20, 25)])
    # 细节
    pygame.draw.polygon(wingman_surface, (200, 200, 200), [(10, 5), (5, 20), (15, 20)])
    
    return wingman_surface

def create_tracking_missile():
    """Creates the surface for a tracking missile."""
    missile_surface = pygame.Surface((6, 12), pygame.SRCALPHA)
    pygame.draw.rect(missile_surface, ORANGE, (0, 0, 6, 9))
    pygame.draw.polygon(missile_surface, RED, [(0, 9), (6, 9), (3, 12)])
    pygame.draw.line(missile_surface, YELLOW, (3, 0), (3, 7), 1)
    return missile_surface

def create_wingman_item():
    """Creates the surface for a wingman power-up item."""
    item_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    
    # 背景
    pygame.draw.circle(item_surface, (255, 255, 255), (15, 15), 15)
    pygame.draw.circle(item_surface, (0, 180, 255), (15, 15), 15, 2)

    # 绘制僚机的小图标
    wingman_icon = create_wingman()
    wingman_icon = pygame.transform.scale(wingman_icon, (18, 22))
    
    rect = wingman_icon.get_rect(center=(15, 15))
    item_surface.blit(wingman_icon, rect)
    
    return item_surface

def draw_health_bar(surface, x, y, width, height, health, max_health, border_color=WHITE):
    """绘制血条"""
    # 血条背景
    pygame.draw.rect(surface, DARK_GRAY, (x, y, width, height))
    
    # 计算当前血量对应的血条宽度
    health_width = int(health / max_health * width)
    
    # 根据血量变化血条颜色
    if health > max_health * 0.6:
        color = GREEN
    elif health > max_health * 0.3:
        color = YELLOW
    else:
        color = RED
        
    # 绘制血条
    pygame.draw.rect(surface, color, (x, y, health_width, height))
    
    # 绘制血条边框
    pygame.draw.rect(surface, border_color, (x, y, width, height), 1)

def draw_text(surface, text, size, x, y, color=WHITE, font_name='arial'):
    """绘制文本"""
    try:
        font = pygame.font.Font(pygame.font.match_font(font_name), size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        surface.blit(text_surface, text_rect)
    except pygame.error:
        print(f"找不到字体: {font_name}, 使用默认字体")
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        surface.blit(text_surface, text_rect)