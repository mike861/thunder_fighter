import pytest
from unittest.mock import patch, MagicMock
import pygame

# Import the global instance, not the class
from thunder_fighter.utils.sound_manager import sound_manager, SoundManager

@pytest.fixture(autouse=True)
def clean_sound_manager_state():
    """Ensure the global sound_manager is in a predictable state."""
    # This allows each test to apply its own specific mocks without interference.
    sound_manager._initialized = False
    sound_manager.sounds.clear()
    yield

class TestSoundManager:
    """Test suite for the SoundManager."""

    def test_auto_recovery_from_failure(self):
        """
        Tests the sound manager's ability to detect and attempt recovery from failure.
        """
        # Arrange: Set up a scenario where the sound manager detects it's unhealthy
        sound_manager._initialized = True
        sound_manager.music_enabled = True
        sound_manager.sounds = {'test_sound': MagicMock()}
        
        # Mock pygame.mixer.music.get_busy to return False (music not playing)
        with patch('pygame.mixer.music.get_busy', return_value=False):
            # Act: Check if the system is healthy
            is_healthy = sound_manager.is_healthy()
            
            # Assert: Should detect the problem
            assert is_healthy is False, "Sound manager should detect that music is not playing when it should be"
        
        # Test that ensure_music_playing attempts to restart music
        with patch.object(sound_manager, 'play_music') as mock_play_music:
            with patch('pygame.mixer.music.get_busy', return_value=False):
                # Act
                sound_manager.ensure_music_playing()
                
                # Assert
                mock_play_music.assert_called_once_with('background_music.mp3')

    @patch('pygame.mixer.init', side_effect=pygame.error("Mixer init failed"))
    @patch('pygame.mixer.get_init', return_value=False)
    def test_graceful_failure_on_init(self, mock_get_init, mock_mixer_init):
        """
        Tests that the SoundManager handles initialization failure gracefully.
        """
        # Arrange / Act
        sound_manager.__init__() # This will fail internally

        # Assert
        assert sound_manager._initialized is False
        
        # Act 2
        try:
            # This should not raise an exception
            sound_manager.play_sound('any_sound')
        except Exception as e:
            pytest.fail(f"Playing sound on a failed manager raised an exception: {e}") 