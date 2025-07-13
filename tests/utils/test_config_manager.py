"""
Tests for the configuration management system
"""

import json
import os
import tempfile
from unittest.mock import patch

from thunder_fighter.utils.config_manager import (
    ConfigManager,
    ControlsConfig,
    DebugConfig,
    DisplayConfig,
    GameplayConfig,
    SoundConfig,
)


class TestSoundConfig:
    """Test SoundConfig dataclass"""

    def test_default_values(self):
        """Test default configuration values"""
        config = SoundConfig()
        assert config.music_volume == 0.5
        assert config.sound_volume == 0.7
        assert config.music_enabled is True
        assert config.sound_enabled is True

    def test_custom_values(self):
        """Test custom configuration values"""
        config = SoundConfig(music_volume=0.8, sound_volume=0.9, music_enabled=False, sound_enabled=False)
        assert config.music_volume == 0.8
        assert config.sound_volume == 0.9
        assert config.music_enabled is False
        assert config.sound_enabled is False


class TestDisplayConfig:
    """Test DisplayConfig dataclass"""

    def test_default_values(self):
        """Test default display configuration"""
        config = DisplayConfig()
        assert config.fullscreen is False
        assert config.screen_scaling == 1.0
        assert config.width == 800
        assert config.height == 600


class TestGameplayConfig:
    """Test GameplayConfig dataclass"""

    def test_default_values(self):
        """Test default gameplay configuration"""
        config = GameplayConfig()
        assert config.difficulty == "normal"
        assert config.initial_lives == 3
        assert config.player_speed_multiplier == 1.0
        assert config.enemy_speed_multiplier == 1.0
        assert config.score_multiplier == 1.0


class TestControlsConfig:
    """Test ControlsConfig dataclass"""

    def test_default_values(self):
        """Test default controls configuration"""
        config = ControlsConfig()
        assert config.move_left == ["LEFT", "a"]
        assert config.move_right == ["RIGHT", "d"]
        assert config.move_up == ["UP", "w"]
        assert config.move_down == ["DOWN", "s"]
        assert config.shoot == ["SPACE"]
        assert config.pause == ["p"]


class TestDebugConfig:
    """Test DebugConfig dataclass"""

    def test_default_values(self):
        """Test default debug configuration"""
        config = DebugConfig()
        assert config.dev_mode is False
        assert config.log_level == "INFO"
        assert config.show_fps is False
        assert config.show_collision_boxes is False


class TestConfigManager:
    """Test ConfigManager class"""

    def test_init_with_temp_file(self):
        """Test initialization with temporary config file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            config_data = {"sound": {"music_volume": 0.8, "sound_volume": 0.9}, "debug": {"dev_mode": True}}
            json.dump(config_data, f)
            temp_file = f.name

        try:
            manager = ConfigManager(temp_file)
            assert manager.sound.music_volume == 0.8
            assert manager.sound.sound_volume == 0.9
            assert manager.debug.dev_mode is True
        finally:
            os.unlink(temp_file)

    def test_save_configuration(self):
        """Test saving configuration to file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_file = f.name

        try:
            manager = ConfigManager(temp_file)
            manager.sound.music_volume = 0.6
            manager.debug.dev_mode = True
            manager.save_configuration()

            # Load and verify
            with open(temp_file) as f:
                data = json.load(f)

            assert data["sound"]["music_volume"] == 0.6
            assert data["debug"]["dev_mode"] is True
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_update_sound_config(self):
        """Test updating sound configuration"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_file = f.name

        try:
            manager = ConfigManager(temp_file)
            manager.update_sound_config(music_volume=0.9, sound_enabled=False)

            assert manager.sound.music_volume == 0.9
            assert manager.sound.sound_enabled is False
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_update_gameplay_config(self):
        """Test updating gameplay configuration"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_file = f.name

        try:
            manager = ConfigManager(temp_file)
            manager.update_gameplay_config(difficulty="hard", initial_lives=5)

            assert manager.gameplay.difficulty == "hard"
            assert manager.gameplay.initial_lives == 5
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_get_difficulty_multipliers(self):
        """Test getting difficulty-based multipliers"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_file = f.name

        try:
            manager = ConfigManager(temp_file)

            # Test easy difficulty
            manager.gameplay.difficulty = "easy"
            multipliers = manager.get_difficulty_multipliers()
            assert multipliers["player_speed"] == 1.2
            assert multipliers["enemy_speed"] == 0.8

            # Test hard difficulty
            manager.gameplay.difficulty = "hard"
            multipliers = manager.get_difficulty_multipliers()
            assert multipliers["player_speed"] == 0.9
            assert multipliers["enemy_speed"] == 1.3

            # Test normal difficulty
            manager.gameplay.difficulty = "normal"
            multipliers = manager.get_difficulty_multipliers()
            assert multipliers["player_speed"] == 1.0
            assert multipliers["enemy_speed"] == 1.0
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_reset_to_defaults(self):
        """Test resetting configuration to defaults"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_file = f.name

        try:
            manager = ConfigManager(temp_file)

            # Modify some settings
            manager.sound.music_volume = 0.9
            manager.gameplay.difficulty = "hard"
            manager.debug.dev_mode = True

            # Reset to defaults
            manager.reset_to_defaults()

            # Verify defaults
            assert manager.sound.music_volume == 0.5
            assert manager.gameplay.difficulty == "normal"
            assert manager.debug.dev_mode is False
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    @patch("thunder_fighter.utils.config_manager.logger")
    def test_load_from_legacy_config(self, mock_logger):
        """Test loading from legacy config.py"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_file = f.name

        try:
            # Create manager and test that legacy config loading doesn't crash
            manager = ConfigManager(temp_file)

            # Call the method - it should handle import errors gracefully
            manager._load_from_legacy_config()

            # Since legacy config doesn't exist, values should remain defaults
            assert manager.sound.music_volume == 0.5
            assert manager.gameplay.difficulty == "normal"
            assert manager.debug.dev_mode is False

            # Verify logger was called (indicating the method attempted to load)
            mock_logger.info.assert_called()
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_load_from_nonexistent_legacy_config(self):
        """Test graceful handling when legacy config doesn't exist"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_file = f.name

        try:
            # Test that it falls back to defaults when legacy config fails
            manager = ConfigManager(temp_file)

            # Should use default values
            assert manager.sound.music_volume == 0.5
            assert manager.gameplay.difficulty == "normal"
            assert manager.debug.dev_mode is False
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
