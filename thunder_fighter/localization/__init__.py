"""
Localization module for Thunder Fighter
Handles loading and managing text in different languages
"""
import json
import os
from typing import Optional, Dict
from thunder_fighter.utils.logger import logger
from .loader import LanguageLoader, FileLanguageLoader

try:
    # Try to import the config file
    from thunder_fighter.config import LANGUAGE as CONFIG_LANGUAGE
except ImportError:
    # Default to English if config file is missing
    CONFIG_LANGUAGE = 'en'
    logger.warning("Could not load config file, using default language: English")

class LanguageManager:
    """Manages text loading from language files with injectable loader."""
    
    def __init__(self, language_code: Optional[str] = None, 
                 loader: Optional[LanguageLoader] = None):
        """
        Initialize the language manager.
        
        Args:
            language_code: Initial language code. If None, uses CONFIG_LANGUAGE
            loader: Language loader implementation. If None, uses FileLanguageLoader
        """
        # Use the language from config if no specific language is provided
        self.language_code = language_code or CONFIG_LANGUAGE
        self.loader = loader or FileLanguageLoader()
        self.text: Dict[str, str] = {}
        # Track already warned missing keys to avoid log spam
        self.missing_keys_warned: set[str] = set()
        self.load_language(self.language_code)
    
    def load_language(self, language_code: str) -> bool:
        """Load a specific language using the configured loader.
        
        Args:
            language_code: Two-letter language code (e.g., 'en', 'zh')
        
        Returns:
            bool: True if language loaded successfully, False otherwise
        """
        # Use the loader to get language data
        language_data = self.loader.load(language_code)
        
        if language_data is not None:
            self.text = language_data
            self.missing_keys_warned.clear()
            self.language_code = language_code
            logger.info(f"Loaded language: {language_code}")
            return True
        else:
            # Try fallback to English if not already English
            if language_code != 'en':
                logger.info("Falling back to English")
                return self.load_language('en')
            
            # If even English fails, use empty dictionary
            logger.error("Failed to load any language data")
            self.text = {}
            return False
    
    def change_language(self, language_code):
        """Change the active language
        
        Args:
            language_code: Two-letter language code
            
        Returns:
            bool: True if language changed successfully
        """
        return self.load_language(language_code)
    
    def get_text(self, key, *args, **kwargs):
        """Get text by key with optional formatting
        
        Args:
            key: Text identifier (must match a constant in the language file)
            *args, **kwargs: Arguments for string formatting
            
        Returns:
            str: Formatted text string or key itself if not found
        """
        if key in self.text:
            try:
                # Apply string formatting if args/kwargs provided
                if args or kwargs:
                    return self.text[key].format(*args, **kwargs)
                return self.text[key]
            except Exception as e:
                logger.error(f"Error formatting text '{key}': {e}")
                return self.text[key]
        else:
            # Only log the warning once per key to avoid log spam
            if key not in self.missing_keys_warned:
                logger.warning(f"Missing text key: {key}")
                self.missing_keys_warned.add(key)
            return key
    
    def reset_warnings(self):
        """Reset the missing keys warning set. Useful for testing."""
        self.missing_keys_warned.clear()
        logger.debug("Reset missing key warnings")
    
    def get_available_languages(self) -> list[str]:
        """Get list of available languages from the loader."""
        return self.loader.available_languages()
    
    def get_font_for_current_language(self, size: int, style: str = 'normal'):
        """
        Get appropriate font for the current language.
        
        Args:
            size: Font size in points
            style: Font style ('normal' or 'bold')
            
        Returns:
            pygame.font.Font appropriate for current language
        """
        from .font_support import get_localized_font
        return get_localized_font(self.language_code, size, style)

# Create a singleton instance to be imported elsewhere
language_manager = LanguageManager()

# Export a simple function for getting text
def get_text(key, *args, **kwargs):
    """Get localized text string
    
    Args:
        key: Text key from language file
        *args, **kwargs: Optional formatting arguments
        
    Returns:
        str: Localized and formatted text
    """
    return language_manager.get_text(key, *args, **kwargs)
    
# For syntactic sugar, provide a shorter alias
_ = get_text

# Export a function to change language at runtime
def change_language(language_code):
    """Change the active language
    
    Args:
        language_code: Two-letter language code (e.g., 'en', 'zh')
        
    Returns:
        bool: True if language changed successfully
    """
    return language_manager.change_language(language_code)

# Export loader classes for testing
from .loader import LanguageLoader, FileLanguageLoader, MemoryLanguageLoader, CachedLanguageLoader

__all__ = [
    'language_manager',
    'get_text',
    '_',
    'change_language',
    'LanguageLoader',
    'FileLanguageLoader', 
    'MemoryLanguageLoader',
    'CachedLanguageLoader'
] 