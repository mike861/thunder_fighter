import os
from typing import Any, Dict

# Get the absolute path of the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the path to the assets directory
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

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

# ===== Player System Configuration =====
PLAYER_CONFIG: Dict[str, Any] = {
    "HEALTH": 100,
    "SHOOT_DELAY": 250,
    "SPEED": 6,
    "MAX_SPEED": 15,
    "SPEED_UPGRADE_AMOUNT": 1,
    "FLASH_FRAMES": 20,
    "HEAL_AMOUNT": 10,
    "INITIAL_WINGMEN": 0,
    "MAX_WINGMEN": 2,
    "WINGMAN_FORMATION_SPACING": 45,
}

# Backward compatibility aliases
PLAYER_HEALTH = PLAYER_CONFIG["HEALTH"]
PLAYER_SHOOT_DELAY = PLAYER_CONFIG["SHOOT_DELAY"]
PLAYER_SPEED = PLAYER_CONFIG["SPEED"]
PLAYER_MAX_SPEED = PLAYER_CONFIG["MAX_SPEED"]
PLAYER_SPEED_UPGRADE_AMOUNT = PLAYER_CONFIG["SPEED_UPGRADE_AMOUNT"]
PLAYER_FLASH_FRAMES = PLAYER_CONFIG["FLASH_FRAMES"]
PLAYER_HEAL_AMOUNT = PLAYER_CONFIG["HEAL_AMOUNT"]
PLAYER_INITIAL_WINGMEN = PLAYER_CONFIG["INITIAL_WINGMEN"]
PLAYER_MAX_WINGMEN = PLAYER_CONFIG["MAX_WINGMEN"]
WINGMAN_FORMATION_SPACING = PLAYER_CONFIG["WINGMAN_FORMATION_SPACING"]

# ===== Bullet System Configuration =====
BULLET_CONFIG: Dict[str, Any] = {
    "SPEED_DEFAULT": 10,
    "SPEED_MAX": 20,
    "PATHS_DEFAULT": 1,
    "PATHS_MAX": 4,
    "ANGLE_STRAIGHT": 0,
    "ANGLE_SPREAD_SMALL": 15,
    "ANGLE_SPREAD_LARGE": 25,
    "SPEED_UPGRADE_AMOUNT": 1,
    "DAMAGE_TO_BOSS": 5,
}

# Backward compatibility aliases
BULLET_SPEED_DEFAULT = BULLET_CONFIG["SPEED_DEFAULT"]
BULLET_SPEED_MAX = BULLET_CONFIG["SPEED_MAX"]
BULLET_PATHS_DEFAULT = BULLET_CONFIG["PATHS_DEFAULT"]
BULLET_PATHS_MAX = BULLET_CONFIG["PATHS_MAX"]
BULLET_ANGLE_STRAIGHT = BULLET_CONFIG["ANGLE_STRAIGHT"]
BULLET_ANGLE_SPREAD_SMALL = BULLET_CONFIG["ANGLE_SPREAD_SMALL"]
BULLET_ANGLE_SPREAD_LARGE = BULLET_CONFIG["ANGLE_SPREAD_LARGE"]
BULLET_SPEED_UPGRADE_AMOUNT = BULLET_CONFIG["SPEED_UPGRADE_AMOUNT"]
BULLET_DAMAGE_TO_BOSS = BULLET_CONFIG["DAMAGE_TO_BOSS"]

# ===== Enemy Configuration (Extended) =====
ENEMY_CONFIG: Dict[str, Any] = {
    "BASE_COUNT": 4,
    "MIN_SHOOT_DELAY": 500,
    "MAX_SHOOT_DELAY": 2000,
    "SHOOT_LEVEL": 2,
    "SPAWN_Y_MIN": -80,
    "SPAWN_Y_MAX": -20,
    "HORIZONTAL_MOVE_MIN": -3,
    "HORIZONTAL_MOVE_MAX": 4,
    "ROTATION_UPDATE": 50,
    "SCREEN_BOUNDS": 25,
}

# Backward compatibility aliases
BASE_ENEMY_COUNT = ENEMY_CONFIG["BASE_COUNT"]
ENEMY_MIN_SHOOT_DELAY = ENEMY_CONFIG["MIN_SHOOT_DELAY"]
ENEMY_MAX_SHOOT_DELAY = ENEMY_CONFIG["MAX_SHOOT_DELAY"]
ENEMY_SHOOT_LEVEL = ENEMY_CONFIG["SHOOT_LEVEL"]
ENEMY_SPAWN_Y_MIN = ENEMY_CONFIG["SPAWN_Y_MIN"]
ENEMY_SPAWN_Y_MAX = ENEMY_CONFIG["SPAWN_Y_MAX"]
ENEMY_HORIZONTAL_MOVE_MIN = ENEMY_CONFIG["HORIZONTAL_MOVE_MIN"]
ENEMY_HORIZONTAL_MOVE_MAX = ENEMY_CONFIG["HORIZONTAL_MOVE_MAX"]
ENEMY_ROTATION_UPDATE = ENEMY_CONFIG["ROTATION_UPDATE"]
ENEMY_SCREEN_BOUNDS = ENEMY_CONFIG["SCREEN_BOUNDS"]

# ===== Boss Configuration (Extended) =====
BOSS_CONFIG: Dict[str, Any] = {
    "MAX_HEALTH": 300,
    "SHOOT_DELAY": 1000,
    "SPAWN_INTERVAL": 30,
    "HEALTH_MULTIPLIER": 1.5,
    "BULLET_COUNT_BASE": 3,
    "BULLET_COUNT_INCREMENT": 1,
    "MAX_LEVEL": 5,
}

# Backward compatibility aliases
BOSS_MAX_HEALTH = BOSS_CONFIG["MAX_HEALTH"]
BOSS_SHOOT_DELAY = BOSS_CONFIG["SHOOT_DELAY"]
BOSS_SPAWN_INTERVAL = BOSS_CONFIG["SPAWN_INTERVAL"]
BOSS_HEALTH_MULTIPLIER = BOSS_CONFIG["HEALTH_MULTIPLIER"]
BOSS_BULLET_COUNT_BASE = BOSS_CONFIG["BULLET_COUNT_BASE"]
BOSS_BULLET_COUNT_INCREMENT = BOSS_CONFIG["BULLET_COUNT_INCREMENT"]
BOSS_MAX_LEVEL = BOSS_CONFIG["MAX_LEVEL"]

# ===== Boss Bullet Configuration =====
BOSS_BULLET_CONFIG: Dict[str, Any] = {
    "NORMAL_SPEED": 5,
    "AGGRESSIVE_SPEED": 6,
    "FINAL_SPEED": 7,
    "NORMAL_DAMAGE": 10,
    "AGGRESSIVE_DAMAGE": 15,
    "FINAL_DAMAGE": 20,
    "BASE_WIDTH": 10,
    "BASE_HEIGHT": 20,
    "TRACKING_HORIZONTAL_FACTOR": 0.3,
    "MINIMUM_VERTICAL_SPEED": 3,
    "GLOW_EFFECT_SIZE": 8,
    "GLOW_LAYERS": 3,
    "NORMAL_COLOR_PRIMARY": (255, 0, 255),
    "NORMAL_COLOR_SECONDARY": (128, 0, 128),
    "AGGRESSIVE_COLOR_PRIMARY": (255, 50, 0),
    "AGGRESSIVE_COLOR_SECONDARY": (200, 0, 0),
    "FINAL_COLOR_PRIMARY": (0, 200, 255),
    "FINAL_COLOR_SECONDARY": (255, 255, 255),
    "AGGRESSIVE_SIZE_MULTIPLIER": 1.2,
    "FINAL_SIZE_MULTIPLIER": 1.3,
}

# Backward compatibility aliases
BOSS_BULLET_NORMAL_SPEED = BOSS_BULLET_CONFIG["NORMAL_SPEED"]
BOSS_BULLET_AGGRESSIVE_SPEED = BOSS_BULLET_CONFIG["AGGRESSIVE_SPEED"]
BOSS_BULLET_FINAL_SPEED = BOSS_BULLET_CONFIG["FINAL_SPEED"]
BOSS_BULLET_NORMAL_DAMAGE = BOSS_BULLET_CONFIG["NORMAL_DAMAGE"]
BOSS_BULLET_AGGRESSIVE_DAMAGE = BOSS_BULLET_CONFIG["AGGRESSIVE_DAMAGE"]
BOSS_BULLET_FINAL_DAMAGE = BOSS_BULLET_CONFIG["FINAL_DAMAGE"]
BOSS_BULLET_BASE_WIDTH = BOSS_BULLET_CONFIG["BASE_WIDTH"]
BOSS_BULLET_BASE_HEIGHT = BOSS_BULLET_CONFIG["BASE_HEIGHT"]
BOSS_BULLET_TRACKING_HORIZONTAL_FACTOR = BOSS_BULLET_CONFIG["TRACKING_HORIZONTAL_FACTOR"]
BOSS_BULLET_MINIMUM_VERTICAL_SPEED = BOSS_BULLET_CONFIG["MINIMUM_VERTICAL_SPEED"]
BOSS_BULLET_GLOW_EFFECT_SIZE = BOSS_BULLET_CONFIG["GLOW_EFFECT_SIZE"]
BOSS_BULLET_GLOW_LAYERS = BOSS_BULLET_CONFIG["GLOW_LAYERS"]
BOSS_BULLET_NORMAL_COLOR_PRIMARY = BOSS_BULLET_CONFIG["NORMAL_COLOR_PRIMARY"]
BOSS_BULLET_NORMAL_COLOR_SECONDARY = BOSS_BULLET_CONFIG["NORMAL_COLOR_SECONDARY"]
BOSS_BULLET_AGGRESSIVE_COLOR_PRIMARY = BOSS_BULLET_CONFIG["AGGRESSIVE_COLOR_PRIMARY"]
BOSS_BULLET_AGGRESSIVE_COLOR_SECONDARY = BOSS_BULLET_CONFIG["AGGRESSIVE_COLOR_SECONDARY"]
BOSS_BULLET_FINAL_COLOR_PRIMARY = BOSS_BULLET_CONFIG["FINAL_COLOR_PRIMARY"]
BOSS_BULLET_FINAL_COLOR_SECONDARY = BOSS_BULLET_CONFIG["FINAL_COLOR_SECONDARY"]
BOSS_BULLET_AGGRESSIVE_SIZE_MULTIPLIER = BOSS_BULLET_CONFIG["AGGRESSIVE_SIZE_MULTIPLIER"]
BOSS_BULLET_FINAL_SIZE_MULTIPLIER = BOSS_BULLET_CONFIG["FINAL_SIZE_MULTIPLIER"]

# ===== Game Balance Configuration =====
GAME_CONFIG: Dict[str, Any] = {"SCORE_THRESHOLD": 200, "MAX_GAME_LEVEL": 8, "INITIAL_GAME_LEVEL": 1}

# Backward compatibility aliases
SCORE_THRESHOLD = GAME_CONFIG["SCORE_THRESHOLD"]
MAX_GAME_LEVEL = GAME_CONFIG["MAX_GAME_LEVEL"]
INITIAL_GAME_LEVEL = GAME_CONFIG["INITIAL_GAME_LEVEL"]

# Dynamic Item Weight System Configuration
ITEM_WEIGHT_SYSTEM = {
    # Base probabilities for each item type
    "BASE_WEIGHTS": {"health": 20, "bullet_speed": 18, "bullet_path": 15, "player_speed": 12, "wingman": 10},
    # Phase 1: Core intelligent weights
    "HEALTH_ADAPTATION": {
        "critical_threshold": 0.3,  # Below 30% health is critical
        "injured_threshold": 0.7,  # Below 70% health is injured
        "critical_multiplier": 2.5,  # 2.5x weight when critical
        "injured_multiplier": 1.5,  # 1.5x weight when injured
        "healthy_multiplier": 0.5,  # 0.5x weight when healthy
    },
    "LEVEL_GATING": {
        "wingman_min_level": 3,  # Wingman only available from level 3+
    },
    "ABILITY_CAPS": {
        "bullet_speed_max": BULLET_SPEED_MAX,
        "bullet_paths_max": BULLET_PATHS_MAX,
        "player_speed_max": PLAYER_MAX_SPEED,
        "wingman_max": PLAYER_MAX_WINGMEN,
    },
    # Phase 2: Duplicate prevention
    "DUPLICATE_PREVENTION": {
        "min_same_item_interval": 15,  # Minimum 15 seconds between same items
        "burst_penalty_multiplier": 0.2,  # Reduce weight to 20% if too recent
        "max_consecutive_same": 2,  # Maximum 2 consecutive same items
    },
}

# ===== Boss Combat System Configuration =====
BOSS_COMBAT: Dict[str, Any] = {
    "AGGRESSIVE_THRESHOLD": 0.5,  # Health percentage to enter aggressive mode
    "FINAL_THRESHOLD": 0.25,  # Health percentage to enter final mode
    "AGGRESSIVE_DELAY_MULTIPLIER": 0.7,  # Shooting delay multiplier in aggressive mode
    "FINAL_DELAY_MULTIPLIER": 0.8,  # Shooting delay multiplier in final mode
    "MIN_AGGRESSIVE_DELAY": 150,  # Minimum shooting delay in aggressive mode
    "MIN_FINAL_DELAY": 100,  # Minimum shooting delay in final mode
    "DAMAGE_FLASH_FRAMES": 12,  # Number of frames for damage flash effect
    "ENTRANCE_TARGET_Y": 50,  # Y position target during entrance animation
    "ENTRANCE_SPEED": 2,  # Speed of entrance animation
    "DIRECTION_CHANGE_INTERVAL": 100,  # Frames between direction changes
    "MOVE_MARGIN": 10,  # Minimum margin from screen edge
}

# ===== Enemy System Configuration =====
ENEMY_SYSTEM: Dict[str, Any] = {
    "MAX_SPEED_FACTOR": 3.0,  # Maximum speed factor based on time
    "BASE_SPEED_FACTOR": 1.0,  # Base speed factor
    "SPEED_TIME_DIVISOR": 60.0,  # Time divisor for speed calculation
    "LEVEL_SPEED_BONUS": 0.2,  # Speed bonus per enemy level
    "MIN_BASE_SPEED": 1,  # Minimum base speed
    "MAX_BASE_SPEED": 3,  # Maximum base speed
    "ROTATION_SPEED_MIN": -8,  # Minimum rotation speed
    "ROTATION_SPEED_MAX": 8,  # Maximum rotation speed
    "BASE_SHOOT_DELAY": 800,  # Base shooting delay
    "LEVEL_DELAY_REDUCTION": 50,  # Shooting delay reduction per level
}
