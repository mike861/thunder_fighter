"""
Configuration management system for Thunder Fighter

This module provides a centralized way to manage all game configuration settings,
including sound, display, gameplay, and controls.
"""

import json
import os
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

from thunder_fighter.utils.logger import logger


@dataclass
class SoundConfig:
    """Sound and music configuration settings"""

    music_volume: float = 0.5
    sound_volume: float = 0.7
    music_enabled: bool = True
    sound_enabled: bool = True


@dataclass
class DisplayConfig:
    """Display and rendering configuration settings"""

    fullscreen: bool = False
    screen_scaling: float = 1.0
    width: int = 800
    height: int = 600


@dataclass
class GameplayConfig:
    """Gameplay mechanics configuration settings"""

    difficulty: str = "normal"  # "easy", "normal", "hard"
    initial_lives: int = 3
    player_speed_multiplier: float = 1.0
    enemy_speed_multiplier: float = 1.0
    score_multiplier: float = 1.0


@dataclass
class ControlsConfig:
    """Input controls configuration"""

    move_left: Optional[List[str]] = None
    move_right: Optional[List[str]] = None
    move_up: Optional[List[str]] = None
    move_down: Optional[List[str]] = None
    shoot: Optional[List[str]] = None
    pause: Optional[List[str]] = None

    def __post_init__(self):
        """Set default key mappings if none provided"""
        if self.move_left is None:
            self.move_left = ["LEFT", "a"]
        if self.move_right is None:
            self.move_right = ["RIGHT", "d"]
        if self.move_up is None:
            self.move_up = ["UP", "w"]
        if self.move_down is None:
            self.move_down = ["DOWN", "s"]
        if self.shoot is None:
            self.shoot = ["SPACE"]
        if self.pause is None:
            self.pause = ["p"]


@dataclass
class DebugConfig:
    """Debug and development configuration settings"""

    dev_mode: bool = False
    log_level: str = "INFO"
    show_fps: bool = False
    show_collision_boxes: bool = False


class ConfigManager:
    """
    Centralized configuration manager for Thunder Fighter

    Handles loading, saving, and runtime modification of all game settings.
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager

        Args:
            config_file: Path to configuration file. If None, uses default location.
        """
        self.config_file = config_file or self._get_default_config_path()

        # Initialize configuration sections
        self.sound = SoundConfig()
        self.display = DisplayConfig()
        self.gameplay = GameplayConfig()
        self.controls = ControlsConfig()
        self.debug = DebugConfig()

        # Load configuration from file or legacy config.py
        self._load_configuration()

        logger.info(f"Configuration manager initialized with file: {self.config_file}")

    def _get_default_config_path(self) -> str:
        """Get the default configuration file path"""
        # Use user's home directory for config file
        home_dir = os.path.expanduser("~")
        config_dir = os.path.join(home_dir, ".thunder_fighter")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "config.json")

    def _load_configuration(self):
        """Load configuration from file or fall back to legacy config.py"""
        # First try to load from JSON config file
        if os.path.exists(self.config_file):
            try:
                self._load_from_json()
                logger.info("Configuration loaded from JSON file")
                return
            except Exception as e:
                logger.warning(f"Failed to load JSON config: {e}, falling back to legacy config")

        # Fall back to legacy config.py
        try:
            self._load_from_legacy_config()
            logger.info("Configuration loaded from legacy config.py")
        except Exception as e:
            logger.warning(f"Failed to load legacy config: {e}, using defaults")

    def _load_from_json(self):
        """Load configuration from JSON file"""
        with open(self.config_file, encoding="utf-8") as f:
            data = json.load(f)

        # Update each configuration section
        if "sound" in data:
            self.sound = SoundConfig(**data["sound"])
        if "display" in data:
            self.display = DisplayConfig(**data["display"])
        if "gameplay" in data:
            self.gameplay = GameplayConfig(**data["gameplay"])
        if "controls" in data:
            self.controls = ControlsConfig(**data["controls"])
        if "debug" in data:
            self.debug = DebugConfig(**data["debug"])

    def _load_from_legacy_config(self):
        """Load configuration from legacy config.py file"""
        try:
            from thunder_fighter import config as legacy_config

            # Map legacy config to new structure
            self.sound.music_volume = getattr(legacy_config, "DEFAULT_MUSIC_VOLUME", 0.5)
            self.sound.sound_volume = getattr(legacy_config, "DEFAULT_SOUND_VOLUME", 0.7)
            self.sound.music_enabled = getattr(legacy_config, "MUSIC_ENABLED", True)
            self.sound.sound_enabled = getattr(legacy_config, "SOUND_ENABLED", True)

            self.display.fullscreen = getattr(legacy_config, "FULLSCREEN", False)
            self.display.screen_scaling = getattr(legacy_config, "SCREEN_SCALING", 1.0)

            self.gameplay.difficulty = getattr(legacy_config, "DIFFICULTY", "normal")

            self.debug.dev_mode = getattr(legacy_config, "DEV_MODE", False)

            # Handle key mapping
            key_mapping = getattr(legacy_config, "KEY_MAPPING", {})
            if key_mapping:
                self.controls.move_left = key_mapping.get("MOVE_LEFT", ["LEFT", "a"])
                self.controls.move_right = key_mapping.get("MOVE_RIGHT", ["RIGHT", "d"])
                self.controls.move_up = key_mapping.get("MOVE_UP", ["UP", "w"])
                self.controls.move_down = key_mapping.get("MOVE_DOWN", ["DOWN", "s"])
                self.controls.shoot = key_mapping.get("SHOOT", ["SPACE"])
                self.controls.pause = key_mapping.get("PAUSE", ["p"])

        except ImportError:
            logger.warning("Legacy config.py not found, using default values")

    def save_configuration(self):
        """Save current configuration to JSON file"""
        try:
            config_data = {
                "sound": asdict(self.sound),
                "display": asdict(self.display),
                "gameplay": asdict(self.gameplay),
                "controls": asdict(self.controls),
                "debug": asdict(self.debug),
            }

            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)

            logger.info(f"Configuration saved to {self.config_file}")

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")

    def update_sound_config(self, **kwargs):
        """Update sound configuration settings"""
        for key, value in kwargs.items():
            if hasattr(self.sound, key):
                setattr(self.sound, key, value)
                logger.debug(f"Updated sound.{key} = {value}")

    def update_display_config(self, **kwargs):
        """Update display configuration settings"""
        for key, value in kwargs.items():
            if hasattr(self.display, key):
                setattr(self.display, key, value)
                logger.debug(f"Updated display.{key} = {value}")

    def update_gameplay_config(self, **kwargs):
        """Update gameplay configuration settings"""
        for key, value in kwargs.items():
            if hasattr(self.gameplay, key):
                setattr(self.gameplay, key, value)
                logger.debug(f"Updated gameplay.{key} = {value}")

    def update_debug_config(self, **kwargs):
        """Update debug configuration settings"""
        for key, value in kwargs.items():
            if hasattr(self.debug, key):
                setattr(self.debug, key, value)
                logger.debug(f"Updated debug.{key} = {value}")

    def get_difficulty_multipliers(self) -> Dict[str, float]:
        """Get difficulty-based multipliers for game mechanics"""
        difficulty_settings = {
            "easy": {"player_speed": 1.2, "enemy_speed": 0.8, "enemy_health": 0.7, "score_multiplier": 0.8},
            "normal": {"player_speed": 1.0, "enemy_speed": 1.0, "enemy_health": 1.0, "score_multiplier": 1.0},
            "hard": {"player_speed": 0.9, "enemy_speed": 1.3, "enemy_health": 1.5, "score_multiplier": 1.5},
        }

        return difficulty_settings.get(self.gameplay.difficulty, difficulty_settings["normal"])

    def reset_to_defaults(self):
        """Reset all configuration to default values"""
        self.sound = SoundConfig()
        self.display = DisplayConfig()
        self.gameplay = GameplayConfig()
        self.controls = ControlsConfig()
        self.debug = DebugConfig()
        logger.info("Configuration reset to defaults")

    def __str__(self) -> str:
        """String representation of current configuration"""
        return (
            f"ConfigManager(\n"
            f"  sound={self.sound},\n"
            f"  display={self.display},\n"
            f"  gameplay={self.gameplay},\n"
            f"  controls={self.controls},\n"
            f"  debug={self.debug}\n"
            f")"
        )


# Global configuration manager instance
config_manager = ConfigManager()
