"""
Game configuration settings
"""

# Display settings
FULLSCREEN = False
SCREEN_SCALING = 1.0  # For high DPI displays

# Sound settings
DEFAULT_MUSIC_VOLUME = 0.5
DEFAULT_SOUND_VOLUME = 0.7
MUSIC_ENABLED = True
SOUND_ENABLED = True

# Game difficulty
DIFFICULTY = "normal"  # "easy", "normal", "hard"

# Language settings
LANGUAGE = "en"  # Available: "en", "zh"

# Controls
KEY_MAPPING = {
    "MOVE_LEFT": ["LEFT", "a"],
    "MOVE_RIGHT": ["RIGHT", "d"],
    "MOVE_UP": ["UP", "w"],
    "MOVE_DOWN": ["DOWN", "s"],
    "SHOOT": ["SPACE"],
    "PAUSE": ["p"],
}

# Debug settings
# For developer use, to show additional debug info
DEV_MODE = False