import pygame
import os

# Get the absolute path of the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the path to the assets directory
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

# Game window size
WIDTH = 480
HEIGHT = 600
FPS = 60

# Define colors
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

# Font settings
FONT_NAME = "Arial"  # Use system common font
FONT_SIZE_LARGE = 28
FONT_SIZE_MEDIUM = 20
FONT_SIZE_SMALL = 16

# Game text
# UI display text
TEXT_SCORE = "Score: {}"
TEXT_TIME = "Time: {}m"
TEXT_ENEMIES = "Enemies: {}/{}"
TEXT_HIGH_LEVEL_ENEMIES = "High-Level Enemies: {}"
TEXT_BULLET_INFO = "Paths: {}  Speed: {}"
TEXT_ENEMY_LEVEL_DETAIL = "Level {}: {} units"
TEXT_GAME_TITLE = "Thunder Fighter"

# Player settings
PLAYER_HEALTH = 100
PLAYER_SHOOT_DELAY = 250
PLAYER_SPEED = 6 # Player movement speed
PLAYER_MAX_SPEED = 15 # Player max movement speed
PLAYER_SPEED_UPGRADE_AMOUNT = 1 # Player speed upgrade increment
PLAYER_FLASH_FRAMES = 20  # Player damage flash frames
PLAYER_HEAL_AMOUNT = 10  # Player heal amount

# Wingman settings
PLAYER_INITIAL_WINGMEN = 0  # Initial number of wingmen at game start
PLAYER_MAX_WINGMEN = 2  # Maximum number of wingmen allowed
WINGMAN_FORMATION_SPACING = 45  # Distance between wingmen in formation

# Bullet settings
BULLET_SPEED_DEFAULT = 10  # Default bullet speed
BULLET_SPEED_MAX = 20  # Bullet speed limit
BULLET_PATHS_DEFAULT = 1  # Default bullet paths
BULLET_PATHS_MAX = 4  # Bullet paths limit
BULLET_ANGLE_STRAIGHT = 0  # Straight shooting angle
BULLET_ANGLE_SPREAD_SMALL = 15  # Small angle spread
BULLET_ANGLE_SPREAD_LARGE = 25  # Large angle spread
BULLET_SPEED_UPGRADE_AMOUNT = 1  # Bullet speed upgrade increment
BULLET_DAMAGE_TO_BOSS = 5  # Player bullet damage to boss

# Enemy settings
BASE_ENEMY_COUNT = 4
ENEMY_MIN_SHOOT_DELAY = 500  # Enemy minimum shoot delay
ENEMY_MAX_SHOOT_DELAY = 2000  # Enemy maximum shoot delay reduced to 2000ms
ENEMY_SHOOT_LEVEL = 2  # Lower shooting level requirement, can shoot from level 2
ENEMY_SPAWN_Y_MIN = -80  # Reduce enemy spawn min Y coordinate for faster screen entry
ENEMY_SPAWN_Y_MAX = -20  # Reduce enemy spawn max Y coordinate for faster screen entry
ENEMY_HORIZONTAL_MOVE_MIN = -3  # Enemy horizontal movement min speed
ENEMY_HORIZONTAL_MOVE_MAX = 4   # Enemy horizontal movement max speed
ENEMY_ROTATION_UPDATE = 50  # Enemy rotation animation update interval (ms)
ENEMY_SCREEN_BOUNDS = 25  # Distance from screen edge for enemy removal

# Boss settings
BOSS_MAX_HEALTH = 300
BOSS_SHOOT_DELAY = 1000
BOSS_SPAWN_INTERVAL = 30  # Boss spawn interval (seconds), 120 seconds = 2 minutes
BOSS_HEALTH_MULTIPLIER = 1.5  # Boss health multiplier per level
BOSS_BULLET_COUNT_BASE = 3  # Base bullet count
BOSS_BULLET_COUNT_INCREMENT = 1  # Bullet count increment per level
BOSS_MAX_LEVEL = 5  # Boss max level

# Boss bullet settings
BOSS_BULLET_NORMAL_SPEED = 5  # Normal mode bullet speed
BOSS_BULLET_AGGRESSIVE_SPEED = 6  # Aggressive mode bullet speed
BOSS_BULLET_FINAL_SPEED = 7  # Final mode bullet speed
BOSS_BULLET_NORMAL_DAMAGE = 10  # Normal mode bullet damage
BOSS_BULLET_AGGRESSIVE_DAMAGE = 15  # Aggressive mode bullet damage
BOSS_BULLET_FINAL_DAMAGE = 20  # Final mode bullet damage
BOSS_BULLET_BASE_WIDTH = 10  # Base bullet width
BOSS_BULLET_BASE_HEIGHT = 20  # Base bullet height
BOSS_BULLET_TRACKING_HORIZONTAL_FACTOR = 0.3  # Horizontal tracking speed factor
BOSS_BULLET_MINIMUM_VERTICAL_SPEED = 3  # Minimum vertical speed for tracking bullets
BOSS_BULLET_GLOW_EFFECT_SIZE = 8  # Glow effect additional size
BOSS_BULLET_GLOW_LAYERS = 3  # Number of glow layers
BOSS_BULLET_NORMAL_COLOR_PRIMARY = (255, 0, 255)  # Normal bullet primary color (Magenta)
BOSS_BULLET_NORMAL_COLOR_SECONDARY = (128, 0, 128)  # Normal bullet secondary color (Dark Magenta)
BOSS_BULLET_AGGRESSIVE_COLOR_PRIMARY = (255, 50, 0)  # Aggressive bullet primary color (Orange-Red)
BOSS_BULLET_AGGRESSIVE_COLOR_SECONDARY = (200, 0, 0)  # Aggressive bullet secondary color (Dark Red)
BOSS_BULLET_FINAL_COLOR_PRIMARY = (0, 200, 255)  # Final bullet primary color (Cyan)
BOSS_BULLET_FINAL_COLOR_SECONDARY = (255, 255, 255)  # Final bullet secondary color (White)
BOSS_BULLET_AGGRESSIVE_SIZE_MULTIPLIER = 1.2  # Size multiplier for aggressive bullets
BOSS_BULLET_FINAL_SIZE_MULTIPLIER = 1.3  # Size multiplier for final bullets

# Score settings
SCORE_THRESHOLD = 200  # Generate an item every 200 points

# Game balance
MAX_GAME_LEVEL = 5 # Maximum game level 
INITIAL_GAME_LEVEL = 1  # Starting game level 