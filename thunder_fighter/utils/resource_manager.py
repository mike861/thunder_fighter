"""
Resource Manager

Centralized resource management system for Thunder Fighter.
Handles loading, caching, and managing game assets (images, sounds, fonts).
"""

import pygame
import os
from typing import Dict, Optional, Any
from thunder_fighter.constants import ASSETS_DIR
from thunder_fighter.utils.logger import logger


class ResourceManager:
    """
    Centralized resource manager for game assets.
    
    This class provides caching and centralized loading of all game resources
    including images, sounds, and fonts to improve performance and maintainability.
    """
    
    _instance: Optional['ResourceManager'] = None
    
    def __init__(self):
        """Initialize the resource manager."""
        if ResourceManager._instance is not None:
            raise RuntimeError("ResourceManager is a singleton. Use get_instance() instead.")
        
        # Asset caches
        self._image_cache: Dict[str, pygame.Surface] = {}
        self._sound_cache: Dict[str, pygame.mixer.Sound] = {}
        self._font_cache: Dict[str, pygame.font.Font] = {}
        
        # Asset directories
        self.assets_dir = ASSETS_DIR
        self.images_dir = os.path.join(self.assets_dir, 'images')
        self.sounds_dir = os.path.join(self.assets_dir, 'sounds')
        self.music_dir = os.path.join(self.assets_dir, 'music')
        self.fonts_dir = os.path.join(self.assets_dir, 'fonts')
        
        # Create directories if they don't exist
        for directory in [self.images_dir, self.sounds_dir, self.music_dir, self.fonts_dir]:
            os.makedirs(directory, exist_ok=True)
        
        logger.info("ResourceManager initialized")
    
    @classmethod
    def get_instance(cls) -> 'ResourceManager':
        """Get the singleton instance of ResourceManager."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance (for testing)."""
        cls._instance = None
    
    def load_image(self, filename: str, colorkey: Optional[Any] = None, 
                   alpha: bool = True, scale: Optional[tuple] = None) -> pygame.Surface:
        """
        Load an image with caching.
        
        Args:
            filename: Image filename (relative to images directory)
            colorkey: Color key for transparency (-1 for auto, or specific color)
            alpha: Whether to convert with alpha
            scale: Optional tuple (width, height) to scale the image
            
        Returns:
            pygame.Surface containing the image
            
        Raises:
            pygame.error: If the image cannot be loaded
        """
        cache_key = f"{filename}_{colorkey}_{alpha}_{scale}"
        
        if cache_key in self._image_cache:
            logger.debug(f"Image cache hit: {filename}")
            return self._image_cache[cache_key]
        
        # Try multiple paths for the image
        possible_paths = [
            os.path.join(self.images_dir, filename),
            os.path.join(self.assets_dir, filename),
            os.path.join('thunder_fighter', 'assets', filename),  # Legacy path
            filename  # Direct path
        ]
        
        image_path = None
        for path in possible_paths:
            if os.path.exists(path):
                image_path = path
                break
        
        if image_path is None:
            logger.error(f"Image not found: {filename} (searched: {possible_paths})")
            # Create a placeholder image
            image = pygame.Surface((32, 32))
            image.fill((255, 0, 255))  # Magenta placeholder
        else:
            try:
                image = pygame.image.load(image_path)
                logger.debug(f"Loaded image: {filename} from {image_path}")
            except pygame.error as e:
                logger.error(f"Failed to load image {filename}: {e}")
                # Create a placeholder image
                image = pygame.Surface((32, 32))
                image.fill((255, 0, 255))  # Magenta placeholder
        
        # Apply conversions
        if alpha:
            image = image.convert_alpha()
        else:
            image = image.convert()
        
        # Apply color key
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        
        # Apply scaling
        if scale is not None:
            image = pygame.transform.scale(image, scale)
        
        # Cache the processed image
        self._image_cache[cache_key] = image
        logger.debug(f"Cached image: {cache_key}")
        
        return image
    
    def load_sound(self, filename: str, volume: float = 1.0) -> Optional[pygame.mixer.Sound]:
        """
        Load a sound with caching.
        
        Args:
            filename: Sound filename (relative to sounds directory)
            volume: Initial volume (0.0 to 1.0)
            
        Returns:
            pygame.mixer.Sound or None if loading failed
        """
        cache_key = f"{filename}_{volume}"
        
        if cache_key in self._sound_cache:
            logger.debug(f"Sound cache hit: {filename}")
            return self._sound_cache[cache_key]
        
        # Try multiple paths for the sound
        possible_paths = [
            os.path.join(self.sounds_dir, filename),
            os.path.join(self.assets_dir, 'sounds', filename),
            filename  # Direct path
        ]
        
        sound_path = None
        for path in possible_paths:
            if os.path.exists(path):
                sound_path = path
                break
        
        if sound_path is None:
            logger.warning(f"Sound not found: {filename} (searched: {possible_paths})")
            return None
        
        try:
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(volume)
            self._sound_cache[cache_key] = sound
            logger.debug(f"Loaded and cached sound: {filename}")
            return sound
        except pygame.error as e:
            logger.error(f"Failed to load sound {filename}: {e}")
            return None
    
    def load_font(self, font_name: Optional[str] = None, size: int = 24, 
                  system_font: bool = True) -> pygame.font.Font:
        """
        Load a font with caching.
        
        Args:
            font_name: Font name or path (None for default)
            size: Font size
            system_font: Whether to use system font (vs. font file)
            
        Returns:
            pygame.font.Font object
        """
        cache_key = f"{font_name}_{size}_{system_font}"
        
        if cache_key in self._font_cache:
            logger.debug(f"Font cache hit: {font_name or 'default'}")
            return self._font_cache[cache_key]
        
        try:
            if font_name is None:
                # Default font - use Chinese-optimized font on macOS
                font = self._get_optimized_default_font(size)
            elif system_font:
                # System font - optimize for Chinese on macOS
                font = self._get_optimized_system_font(font_name, size)
            else:
                # Font file
                font_path = os.path.join(self.fonts_dir, font_name)
                if not os.path.exists(font_path):
                    logger.warning(f"Font file not found: {font_path}, using default")
                    font = self._get_optimized_default_font(size)
                else:
                    font = pygame.font.Font(font_path, size)
            
            self._font_cache[cache_key] = font
            logger.debug(f"Loaded and cached font: {font_name or 'default'} size {size}")
            return font
            
        except pygame.error as e:
            logger.error(f"Failed to load font {font_name}: {e}, using default")
            font = self._get_optimized_default_font(size)
            self._font_cache[cache_key] = font
            return font
    
    def _get_optimized_default_font(self, size: int) -> pygame.font.Font:
        """Get optimized default font for Chinese character support."""
        import platform
        import os
        
        if platform.system() == "Darwin":  # macOS
            # ONLY use TTF font files for Chinese support (SysFont doesn't work properly)
            font_files = [
                "/System/Library/Fonts/PingFang.ttc",
                "/System/Library/Fonts/STHeiti Medium.ttc",
                "/System/Library/Fonts/STHeiti Light.ttc"
            ]
            
            for font_path in font_files:
                if os.path.exists(font_path):
                    try:
                        font = pygame.font.Font(font_path, size)
                        # Test if font can render Chinese characters
                        test_surface = font.render("雷", True, (255, 255, 255))
                        if test_surface.get_width() > 1:  # Successfully rendered
                            logger.debug(f"Using TTF font file: {font_path}")
                            return font
                    except Exception as e:
                        logger.debug(f"Failed to load font {font_path}: {e}")
                        continue
            
            logger.warning("No TTF Chinese fonts found on macOS, using pygame default")
        
        # Fallback to pygame default (will show tofu blocks for Chinese)
        logger.debug("Using pygame default font - Chinese may not display correctly")
        return pygame.font.Font(None, size)
    
    def _get_optimized_system_font(self, font_name: str, size: int) -> pygame.font.Font:
        """Get optimized system font for Chinese character support."""
        import platform
        import os
        
        if platform.system() == "Darwin":  # macOS
            # ALWAYS use TTF files for Chinese support (SysFont doesn't work)
            font_file_mapping = {
                "Arial": "/System/Library/Fonts/PingFang.ttc",
                "Helvetica": "/System/Library/Fonts/PingFang.ttc", 
                "Sans": "/System/Library/Fonts/PingFang.ttc",
                "Default": "/System/Library/Fonts/PingFang.ttc",
                "PingFang SC": "/System/Library/Fonts/PingFang.ttc",
                "Heiti SC": "/System/Library/Fonts/STHeiti Medium.ttc",
                "STHeiti": "/System/Library/Fonts/STHeiti Medium.ttc"
            }
            
            # Try TTF file first
            ttf_path = font_file_mapping.get(font_name)
            if ttf_path and os.path.exists(ttf_path):
                try:
                    font = pygame.font.Font(ttf_path, size)
                    # Test if font can render Chinese characters
                    test_surface = font.render("雷", True, (255, 255, 255))
                    if test_surface.get_width() > 1:  # Successfully rendered
                        logger.debug(f"Using TTF file for {font_name}: {ttf_path}")
                        return font
                except Exception as e:
                    logger.debug(f"Failed to load TTF file {ttf_path}: {e}")
            
            # If specific font not mapped, try default TTF fonts
            return self._get_optimized_default_font(size)
        
        # For non-macOS systems, use system fonts (may not support Chinese properly)
        try:
            return pygame.font.SysFont(font_name, size)
        except:
            # Final fallback
            return self._get_optimized_default_font(size)
    
    def get_music_path(self, filename: str) -> Optional[str]:
        """
        Get the full path to a music file.
        
        Args:
            filename: Music filename
            
        Returns:
            Full path to the music file or None if not found
        """
        possible_paths = [
            os.path.join(self.music_dir, filename),
            os.path.join(self.assets_dir, 'music', filename),
            filename  # Direct path
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.debug(f"Found music file: {filename} at {path}")
                return path
        
        logger.warning(f"Music file not found: {filename}")
        return None
    
    def preload_common_assets(self):
        """Preload commonly used assets to improve performance."""
        logger.info("Preloading common assets...")
        
        # Common sounds
        common_sounds = [
            'enemy_explosion.wav',
            'player_hit.wav',
            'item_pickup.wav',
            'boss_death.wav',
            'player_death.wav'
        ]
        
        for sound_file in common_sounds:
            self.load_sound(sound_file)
        
        # Common fonts
        common_fonts = [
            (None, 16),  # Default small
            (None, 20),  # Default medium
            (None, 28),  # Default large
            (None, 32),  # Default extra large
            ('Arial', 20),  # System Arial
        ]
        
        for font_name, size in common_fonts:
            self.load_font(font_name, size)
        
        logger.info("Common assets preloaded")
    
    def clear_cache(self):
        """Clear all cached resources."""
        self._image_cache.clear()
        self._sound_cache.clear()
        self._font_cache.clear()
        logger.info("Resource cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache sizes
        """
        return {
            'images': len(self._image_cache),
            'sounds': len(self._sound_cache),
            'fonts': len(self._font_cache)
        }
    
    def create_surface(self, size: tuple, alpha: bool = True, 
                      fill_color: Optional[tuple] = None) -> pygame.Surface:
        """
        Create a new surface with optional initial fill.
        
        Args:
            size: Surface size (width, height)
            alpha: Whether to use alpha channel
            fill_color: Optional color to fill the surface
            
        Returns:
            New pygame.Surface
        """
        if alpha:
            surface = pygame.Surface(size, pygame.SRCALPHA)
        else:
            surface = pygame.Surface(size)
            surface = surface.convert()
        
        if fill_color is not None:
            surface.fill(fill_color)
        
        return surface


# Global instance accessor
def get_resource_manager() -> ResourceManager:
    """Get the global ResourceManager instance."""
    return ResourceManager.get_instance()


# Convenience functions for common operations
def load_image(filename: str, **kwargs) -> pygame.Surface:
    """Load an image using the global resource manager."""
    return get_resource_manager().load_image(filename, **kwargs)


def load_sound(filename: str, **kwargs) -> Optional[pygame.mixer.Sound]:
    """Load a sound using the global resource manager."""
    return get_resource_manager().load_sound(filename, **kwargs)


def load_font(font_name: Optional[str] = None, size: int = 24, **kwargs) -> pygame.font.Font:
    """Load a font using the global resource manager."""
    return get_resource_manager().load_font(font_name, size, **kwargs)


def get_music_path(filename: str) -> Optional[str]:
    """Get music file path using the global resource manager."""
    return get_resource_manager().get_music_path(filename) 