import pytest

# Import the global instance, not the class
from thunder_fighter.utils.sound_manager import sound_manager


@pytest.fixture(autouse=True)
def clean_sound_manager_state():
    """Ensure the global sound_manager is in a predictable state."""
    # Store original state
    original_initialized = sound_manager._initialized
    original_sounds = sound_manager.sounds.copy()
    original_music_enabled = sound_manager.music_enabled

    # Reset for test
    sound_manager._initialized = False
    sound_manager.sounds.clear()
    sound_manager.music_enabled = False

    yield

    # Restore original state
    sound_manager._initialized = original_initialized
    sound_manager.sounds = original_sounds
    sound_manager.music_enabled = original_music_enabled


class TestSoundManager:
    """Test suite for the SoundManager."""

    def test_sound_manager_basic_functionality(self):
        """
        Tests basic sound manager functionality without relying on complex state management.
        """
        # Test that the global sound manager exists and can be imported
        assert sound_manager is not None
        assert hasattr(sound_manager, "play_sound")
        assert hasattr(sound_manager, "play_music")
        assert hasattr(sound_manager, "is_healthy")
        assert hasattr(sound_manager, "ensure_music_playing")

    def test_sound_manager_safe_operations(self):
        """
        Tests that sound manager operations don't raise exceptions even in edge cases.
        """
        # Test playing non-existent sound
        try:
            sound_manager.play_sound("non_existent_sound")
        except Exception as e:
            pytest.fail(f"Playing non-existent sound raised an exception: {e}")

        # Test music operations
        try:
            sound_manager.stop_music()
            sound_manager.set_sound_volume(0.5)
            sound_manager.set_music_volume(0.5)
            sound_manager.toggle_sound()
            sound_manager.toggle_music()
        except Exception as e:
            pytest.fail(f"Basic operations raised an exception: {e}")
