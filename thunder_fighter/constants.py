import pygame

# 游戏窗口大小
WIDTH = 480
HEIGHT = 600
FPS = 60

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
DARK_BLUE = (0, 0, 128)
LIGHT_BLUE = (135, 206, 250)
ORANGE = (255, 165, 0)
DARK_RED = (139, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
PURPLE = (128, 0, 128)
MAGENTA = (255, 0, 255)
PINK = (255, 182, 193)

# 字体设置
FONT_NAME = "Arial"  # 使用系统通用字体
FONT_SIZE_LARGE = 28
FONT_SIZE_MEDIUM = 20
FONT_SIZE_SMALL = 16

# 游戏文本
# 界面显示文本
TEXT_SCORE = "Score: {}"
TEXT_TIME = "Time: {}m"
TEXT_ENEMIES = "Enemies: {}/{}"
TEXT_HIGH_LEVEL_ENEMIES = "High-Level Enemies: {}"
TEXT_BULLET_INFO = "Paths: {}  Speed: {}"
TEXT_ENEMY_LEVEL_DETAIL = "Level {}: {} units"
TEXT_GAME_TITLE = "Thunder Fighter"

# 玩家设置
PLAYER_HEALTH = 100
PLAYER_SHOOT_DELAY = 250
PLAYER_SPEED = 8  # 玩家移动速度
PLAYER_MAX_SPEED = 15 # 玩家最大移动速度
PLAYER_SPEED_UPGRADE_AMOUNT = 1 # 玩家速度升级增量
PLAYER_FLASH_FRAMES = 20  # 玩家受伤闪烁帧数
PLAYER_HEAL_AMOUNT = 10  # 玩家回血量

# 子弹设置
BULLET_SPEED_DEFAULT = 10  # 默认子弹速度
BULLET_SPEED_MAX = 20  # 子弹速度上限
BULLET_PATHS_DEFAULT = 1  # 默认弹道数量
BULLET_PATHS_MAX = 4  # 弹道数量上限
BULLET_ANGLE_STRAIGHT = 0  # 直射角度
BULLET_ANGLE_SPREAD_SMALL = 15  # 小角度扩散
BULLET_ANGLE_SPREAD_LARGE = 25  # 大角度扩散
BULLET_SPEED_UPGRADE_AMOUNT = 1  # 子弹速度升级增量

# 敌人设置
BASE_ENEMY_COUNT = 8
ENEMY_MIN_SHOOT_DELAY = 200  # 敌人最小射击延迟
ENEMY_MAX_SHOOT_DELAY = 800  # 敌人最大射击延迟降低到800ms
ENEMY_SHOOT_LEVEL = 2  # 降低射击等级要求，从1级开始就能射击
ENEMY_SPAWN_Y_MIN = -80  # 减少敌人生成的最小Y坐标，使其更快进入屏幕
ENEMY_SPAWN_Y_MAX = -20  # 减少敌人生成的最大Y坐标，使其更快进入屏幕
ENEMY_HORIZONTAL_MOVE_MIN = -3  # 敌人水平移动最小速度
ENEMY_HORIZONTAL_MOVE_MAX = 4   # 敌人水平移动最大速度
ENEMY_ROTATION_UPDATE = 50  # 敌人旋转动画更新间隔(ms)
ENEMY_SCREEN_BOUNDS = 25  # 敌人离开屏幕边界的距离

# Boss设置
BOSS_MAX_HEALTH = 300
BOSS_SHOOT_DELAY = 1000
BOSS_SPAWN_INTERVAL = 30  # 生成间隔
BOSS_HEALTH_MULTIPLIER = 1.5  # 每级Boss血量增加倍数
BOSS_BULLET_COUNT_BASE = 3  # 基础子弹数量
BOSS_BULLET_COUNT_INCREMENT = 1  # 每级增加的子弹数量
BOSS_MAX_LEVEL = 5  # Boss最大等级

# 得分设置
SCORE_THRESHOLD = 100  # 每200分可能生成一个道具 