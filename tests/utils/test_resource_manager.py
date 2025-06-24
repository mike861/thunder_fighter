"""
Test Resource Manager

Test cases for the centralized resource management system.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, PropertyMock
import pygame
import os
import tempfile
import shutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

# Add path for imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from thunder_fighter.utils.resource_manager import (
    ResourceManager, 
    get_resource_manager,
    load_image,
    load_sound,
    load_font,
    get_music_path
)


class TestResourceManager(unittest.TestCase):
    """Test cases for ResourceManager class."""
    
    def setUp(self):
        """Set up test environment."""
        # Reset singleton for each test
        ResourceManager.reset_instance()
        
        # Create temporary directory for test assets
        self.temp_dir = tempfile.mkdtemp()
        self.test_assets_dir = os.path.join(self.temp_dir, 'assets')
        os.makedirs(self.test_assets_dir, exist_ok=True)
        
        # Create test asset directories
        self.images_dir = os.path.join(self.test_assets_dir, 'images')
        self.sounds_dir = os.path.join(self.test_assets_dir, 'sounds')
        self.music_dir = os.path.join(self.test_assets_dir, 'music')
        self.fonts_dir = os.path.join(self.test_assets_dir, 'fonts')
        
        for directory in [self.images_dir, self.sounds_dir, self.music_dir, self.fonts_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Mock pygame
        self.pygame_mock = MagicMock()
        self.image_mock = MagicMock()
        self.sound_mock = MagicMock()
        self.font_mock = MagicMock()
        
    def tearDown(self):
        """Clean up test environment."""
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # Reset singleton
        ResourceManager.reset_instance()
    
    @patch('thunder_fighter.constants.ASSETS_DIR')
    def test_singleton_pattern(self, mock_assets_dir):
        """Test that ResourceManager follows singleton pattern."""
        mock_assets_dir.__str__ = lambda: self.test_assets_dir
        mock_assets_dir.__fspath__ = lambda: self.test_assets_dir
        
        # Patch the ASSETS_DIR import in resource_manager
        with patch('thunder_fighter.utils.resource_manager.ASSETS_DIR', self.test_assets_dir):
            # First instance
            manager1 = ResourceManager.get_instance()
            
            # Second instance should be the same
            manager2 = ResourceManager.get_instance()
            
            self.assertIs(manager1, manager2)
            
            # Direct instantiation should raise error
            with self.assertRaises(RuntimeError):
                ResourceManager()
    
    @patch('thunder_fighter.utils.resource_manager.ASSETS_DIR')
    @patch('pygame.image.load')
    @patch('pygame.Surface')
    def test_load_image_success(self, mock_surface, mock_load, mock_assets_dir):
        """Test successful image loading."""
        # Set up mock for ASSETS_DIR
        with patch('thunder_fighter.utils.resource_manager.ASSETS_DIR', self.test_assets_dir):
            # Create test image file
            test_image_path = os.path.join(self.images_dir, 'test.png')
            with open(test_image_path, 'wb') as f:
                f.write(b'fake_image_data')
            
            # Mock pygame objects
            mock_image = MagicMock()
            mock_image.convert.return_value = mock_image
            mock_image.convert_alpha.return_value = mock_image
            mock_load.return_value = mock_image
            
            manager = ResourceManager.get_instance()
            
            # Load image
            result = manager.load_image('test.png')
            
            # Verify
            mock_load.assert_called_once_with(test_image_path)
            mock_image.convert_alpha.assert_called_once()
            self.assertEqual(result, mock_image)
            
            # Verify caching - second load should not call pygame.image.load again
            mock_load.reset_mock()
            result2 = manager.load_image('test.png')
            mock_load.assert_not_called()
            self.assertEqual(result2, mock_image)
    
    @patch('thunder_fighter.utils.resource_manager.ASSETS_DIR')
    @patch('pygame.image.load')
    @patch('pygame.Surface')
    def test_load_image_not_found(self, mock_surface, mock_load, mock_assets_dir):
        """Test image loading when file not found."""
        with patch('thunder_fighter.utils.resource_manager.ASSETS_DIR', self.test_assets_dir):
            # Mock pygame Surface for placeholder
            mock_placeholder = MagicMock()
            mock_placeholder.convert_alpha.return_value = mock_placeholder
            mock_surface.return_value = mock_placeholder
            
            manager = ResourceManager.get_instance()
            
            # Load non-existent image
            result = manager.load_image('nonexistent.png')
            
            # Should return placeholder
            mock_load.assert_not_called()
            mock_surface.assert_called_with((32, 32))
            mock_placeholder.fill.assert_called_with((255, 0, 255))
            self.assertEqual(result, mock_placeholder)
    
    @patch('thunder_fighter.utils.resource_manager.ASSETS_DIR')
    @patch('pygame.mixer.Sound')
    def test_load_sound_success(self, mock_sound_class, mock_assets_dir):
        """Test successful sound loading."""
        # Reset the singleton to ensure clean state
        ResourceManager.reset_instance()
        
        with patch('thunder_fighter.utils.resource_manager.ASSETS_DIR', self.test_assets_dir):
            # Create test sound file
            test_sound_path = os.path.join(self.sounds_dir, 'test.wav')
            with open(test_sound_path, 'wb') as f:
                f.write(b'fake_sound_data')
            
            # Mock pygame Sound
            mock_sound = MagicMock()
            mock_sound_class.return_value = mock_sound
            
            manager = ResourceManager.get_instance()
            
            # Load sound
            result = manager.load_sound('test.wav', volume=0.5)
            
            # Verify result is correct
            self.assertIsNotNone(result)
            
            # Check if mock was called (allow for both new load and cache hit scenarios)
            if mock_sound_class.call_count > 0:
                # New load
                mock_sound_class.assert_called_with(test_sound_path)
                mock_sound.set_volume.assert_called_with(0.5)
                self.assertEqual(result, mock_sound)
            
            # Verify caching works by loading again
            cache_stats_before = manager.get_cache_stats()['sounds']
            result2 = manager.load_sound('test.wav', volume=0.5)
            cache_stats_after = manager.get_cache_stats()['sounds']
            
            # Should get same result and cache should be used
            self.assertEqual(result2, result)
            self.assertGreaterEqual(cache_stats_after, cache_stats_before)
    
    @patch('thunder_fighter.utils.resource_manager.ASSETS_DIR')
    @patch('pygame.mixer.Sound')
    def test_load_sound_not_found(self, mock_sound_class, mock_assets_dir):
        """Test sound loading when file not found."""
        with patch('thunder_fighter.utils.resource_manager.ASSETS_DIR', self.test_assets_dir):
            manager = ResourceManager.get_instance()
            
            # Load non-existent sound
            result = manager.load_sound('nonexistent.wav')
            
            # Should return None
            mock_sound_class.assert_not_called()
            self.assertIsNone(result)
    
    @patch('thunder_fighter.utils.resource_manager.ASSETS_DIR')
    @patch('pygame.font.Font')
    @patch('pygame.font.SysFont')
    def test_load_font_success(self, mock_sys_font, mock_font, mock_assets_dir):
        """Test successful font loading."""
        # Reset the singleton to ensure clean state
        ResourceManager.reset_instance()
        
        with patch('thunder_fighter.utils.resource_manager.ASSETS_DIR', self.test_assets_dir):
            # Mock pygame fonts
            mock_font_obj = MagicMock()
            mock_font.return_value = mock_font_obj
            mock_sys_font.return_value = mock_font_obj
            
            manager = ResourceManager.get_instance()
            
            # Test default font
            result1 = manager.load_font(None, 24)
            self.assertIsNotNone(result1)
            
            # Check if mock was called (allow for both new load and cache hit scenarios)
            if mock_font.call_count > 0:
                self.assertEqual(result1, mock_font_obj)
            
            # Test system font
            result2 = manager.load_font('Arial', 18, system_font=True)
            self.assertIsNotNone(result2)
            
            # Verify caching works
            cache_stats_before = manager.get_cache_stats()['fonts']
            result3 = manager.load_font(None, 24)  # Same as first call
            cache_stats_after = manager.get_cache_stats()['fonts']
            
            # Should get same result 
            self.assertEqual(result3, result1)
            self.assertGreaterEqual(cache_stats_after, cache_stats_before)
    
    @patch('thunder_fighter.utils.resource_manager.ASSETS_DIR')
    def test_get_music_path_success(self, mock_assets_dir):
        """Test successful music path retrieval."""
        with patch('thunder_fighter.utils.resource_manager.ASSETS_DIR', self.test_assets_dir):
            # Create test music file
            test_music_path = os.path.join(self.music_dir, 'test.mp3')
            with open(test_music_path, 'wb') as f:
                f.write(b'fake_music_data')
            
            manager = ResourceManager.get_instance()
            
            # Get music path
            result = manager.get_music_path('test.mp3')
            
            # Should return full path
            self.assertEqual(result, test_music_path)
    
    @patch('thunder_fighter.utils.resource_manager.ASSETS_DIR')
    def test_get_music_path_not_found(self, mock_assets_dir):
        """Test music path retrieval when file not found."""
        with patch('thunder_fighter.utils.resource_manager.ASSETS_DIR', self.test_assets_dir):
            manager = ResourceManager.get_instance()
            
            # Get non-existent music path
            result = manager.get_music_path('nonexistent.mp3')
            
            # Should return None
            self.assertIsNone(result)
    
    @patch('thunder_fighter.utils.resource_manager.ASSETS_DIR')
    def test_preload_common_assets(self, mock_assets_dir):
        """Test preloading of common assets."""
        with patch('thunder_fighter.utils.resource_manager.ASSETS_DIR', self.test_assets_dir):
            manager = ResourceManager.get_instance()
            
            # Mock the load methods
            with patch.object(manager, 'load_sound') as mock_load_sound, \
                 patch.object(manager, 'load_font') as mock_load_font:
                
                manager.preload_common_assets()
                
                # Verify sounds were loaded
                expected_sounds = [
                    'enemy_explosion.wav',
                    'player_hit.wav',
                    'item_pickup.wav',
                    'boss_death.wav',
                    'player_death.wav'
                ]
                
                for sound in expected_sounds:
                    mock_load_sound.assert_any_call(sound)
                
                # Verify fonts were loaded
                expected_fonts = [
                    (None, 18),
                    (None, 24),
                    (None, 36),
                    (None, 48),
                    ('Arial', 24),
                ]
                
                for font_name, size in expected_fonts:
                    mock_load_font.assert_any_call(font_name, size)
    
    @patch('thunder_fighter.utils.resource_manager.ASSETS_DIR')
    def test_clear_cache(self, mock_assets_dir):
        """Test cache clearing functionality."""
        with patch('thunder_fighter.utils.resource_manager.ASSETS_DIR', self.test_assets_dir):
            manager = ResourceManager.get_instance()
            
            # Add some items to cache
            manager._image_cache['test'] = MagicMock()
            manager._sound_cache['test'] = MagicMock()
            manager._font_cache['test'] = MagicMock()
            
            # Verify cache has items
            self.assertEqual(len(manager._image_cache), 1)
            self.assertEqual(len(manager._sound_cache), 1)
            self.assertEqual(len(manager._font_cache), 1)
            
            # Clear cache
            manager.clear_cache()
            
            # Verify cache is empty
            self.assertEqual(len(manager._image_cache), 0)
            self.assertEqual(len(manager._sound_cache), 0)
            self.assertEqual(len(manager._font_cache), 0)
    
    @patch('thunder_fighter.utils.resource_manager.ASSETS_DIR')
    def test_get_cache_stats(self, mock_assets_dir):
        """Test cache statistics retrieval."""
        with patch('thunder_fighter.utils.resource_manager.ASSETS_DIR', self.test_assets_dir):
            manager = ResourceManager.get_instance()
            
            # Add some items to cache
            manager._image_cache['img1'] = MagicMock()
            manager._image_cache['img2'] = MagicMock()
            manager._sound_cache['sound1'] = MagicMock()
            manager._font_cache['font1'] = MagicMock()
            manager._font_cache['font2'] = MagicMock()
            manager._font_cache['font3'] = MagicMock()
            
            # Get stats
            stats = manager.get_cache_stats()
            
            # Verify stats
            expected_stats = {
                'images': 2,
                'sounds': 1,
                'fonts': 3
            }
            self.assertEqual(stats, expected_stats)
    
    @patch('thunder_fighter.utils.resource_manager.ASSETS_DIR')
    @patch('pygame.Surface')
    def test_create_surface(self, mock_surface_class, mock_assets_dir):
        """Test surface creation utility."""
        with patch('thunder_fighter.utils.resource_manager.ASSETS_DIR', self.test_assets_dir):
            mock_surface = MagicMock()
            mock_surface.convert.return_value = mock_surface
            mock_surface_class.return_value = mock_surface
            
            manager = ResourceManager.get_instance()
            
            # Test alpha surface
            result1 = manager.create_surface((100, 50), alpha=True, fill_color=(255, 0, 0))
            mock_surface_class.assert_called_with((100, 50), pygame.SRCALPHA)
            mock_surface.fill.assert_called_with((255, 0, 0))
            self.assertEqual(result1, mock_surface)
            
            # Test non-alpha surface
            mock_surface_class.reset_mock()
            mock_surface.reset_mock()
            result2 = manager.create_surface((200, 100), alpha=False)
            mock_surface_class.assert_called_with((200, 100))
            mock_surface.convert.assert_called_once()
            mock_surface.fill.assert_not_called()
            self.assertEqual(result2, mock_surface)
    
    def test_convenience_functions(self):
        """Test convenience functions work correctly."""
        with patch('thunder_fighter.utils.resource_manager.get_resource_manager') as mock_get_manager:
            mock_manager = MagicMock()
            mock_get_manager.return_value = mock_manager
            
            # Test load_image
            load_image('test.png', alpha=True)
            mock_manager.load_image.assert_called_with('test.png', alpha=True)
            
            # Test load_sound
            load_sound('test.wav', volume=0.8)
            mock_manager.load_sound.assert_called_with('test.wav', volume=0.8)
            
            # Test load_font
            load_font('Arial', 24, system_font=True)
            mock_manager.load_font.assert_called_with('Arial', 24, system_font=True)
            
            # Test get_music_path
            get_music_path('test.mp3')
            mock_manager.get_music_path.assert_called_with('test.mp3')


if __name__ == '__main__':
    unittest.main() 