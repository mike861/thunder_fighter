"""
Font Support for Localization

This module provides font management functionality that integrates with
the localization system to ensure proper rendering of all languages.
"""

import pygame
from typing import Optional, Dict, Tuple
from thunder_fighter.utils.logger import logger
from thunder_fighter.utils.resource_manager import get_resource_manager


class FontManager:
    """
    Manages fonts for different languages and text styles.
    
    This class ensures that the appropriate font is used for each language,
    particularly important for Chinese characters which require specific fonts.
    """
    
    def __init__(self):
        """Initialize the font manager."""
        self.resource_manager = get_resource_manager()
        self._font_cache: Dict[Tuple[str, int, str], pygame.font.Font] = {}
        
        # Language-specific font configurations
        self.language_fonts = {
            'zh': {
                'normal': 'PingFang SC',  # macOS Chinese font
                'bold': 'PingFang SC',
                'fallback': ['STHeiti', 'Heiti SC', 'Microsoft YaHei']
            },
            'en': {
                'normal': None,  # Use pygame default
                'bold': None,
                'fallback': []
            }
        }
        
        logger.info("FontManager initialized")
    
    def get_font(self, language: str, size: int, style: str = 'normal') -> pygame.font.Font:
        """
        Get the appropriate font for a language and style.
        
        Args:
            language: Language code (e.g., 'en', 'zh')
            size: Font size in points
            style: Font style ('normal' or 'bold')
            
        Returns:
            pygame.font.Font object
        """
        cache_key = (language, size, style)
        
        # Check cache first
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
        
        # Create font
        font = self._create_font(language, size, style)
        self._font_cache[cache_key] = font
        return font
    
    def _create_font(self, language: str, size: int, style: str) -> pygame.font.Font:
        """Create a font for the given parameters."""
        # Get font configuration for the language
        font_config = self.language_fonts.get(language, self.language_fonts['en'])
        
        # Try primary font
        font_name = font_config.get(style, None)
        if font_name:
            try:
                # Use resource manager's font loading with system font support
                font = self.resource_manager.load_font(font_name, size, system_font=True)
                logger.debug(f"Loaded font '{font_name}' for language '{language}'")
                return font
            except Exception as e:
                logger.warning(f"Failed to load font '{font_name}': {e}")
        
        # Try fallback fonts
        for fallback_name in font_config.get('fallback', []):
            try:
                font = self.resource_manager.load_font(fallback_name, size, system_font=True)
                logger.debug(f"Loaded fallback font '{fallback_name}' for language '{language}'")
                return font
            except Exception:
                continue
        
        # Ultimate fallback to pygame default
        logger.info(f"Using default font for language '{language}'")
        return self.resource_manager.load_font(None, size)
    
    def render_text(self, text: str, font: pygame.font.Font, 
                   color: Tuple[int, int, int], 
                   antialias: bool = True) -> pygame.Surface:
        """
        Render text with the given font and color.
        
        Args:
            text: Text to render
            font: Font to use
            color: RGB color tuple
            antialias: Whether to use antialiasing
            
        Returns:
            Rendered text surface
        """
        try:
            surface = font.render(text, antialias, color)
            return surface
        except Exception as e:
            logger.error(f"Error rendering text '{text}': {e}")
            # Return empty surface on error
            return pygame.Surface((1, 1))
    
    def check_rendering_support(self, text: str, font: pygame.font.Font) -> bool:
        """
        Check if the font can render the text without tofu blocks.
        
        Args:
            text: Text to check
            font: Font to test
            
        Returns:
            True if text can be rendered properly, False if tofu blocks detected
        """
        try:
            # Render the text
            surface = font.render(text, True, (255, 255, 255))
            
            # Check for tofu blocks by looking for the replacement character
            # This is a heuristic - a more sophisticated check would analyze pixels
            metrics = font.metrics(text)
            if metrics:
                # Check if any character has no width (might be tofu)
                for metric in metrics:
                    if metric is None or (len(metric) > 0 and metric[1] == 0):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking rendering support: {e}")
            return False
    
    def clear_cache(self):
        """Clear the font cache."""
        self._font_cache.clear()
        logger.debug("Font cache cleared")


# Global font manager instance
_font_manager: Optional[FontManager] = None


def get_font_manager() -> FontManager:
    """Get the global font manager instance."""
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager()
    return _font_manager


def get_localized_font(language: str, size: int, style: str = 'normal') -> pygame.font.Font:
    """
    Convenience function to get a font for a specific language.
    
    Args:
        language: Language code
        size: Font size
        style: Font style
        
    Returns:
        Appropriate font for the language
    """
    return get_font_manager().get_font(language, size, style)