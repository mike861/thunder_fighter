"""
Localization module for Thunder Fighter
Handles loading and managing text in different languages
"""
import json
import os
from thunder_fighter.utils.logger import logger

try:
    # Try to import the config file
    from thunder_fighter.config import LANGUAGE as CONFIG_LANGUAGE
except ImportError:
    # Default to English if config file is missing
    CONFIG_LANGUAGE = 'en'
    logger.warning("Could not load config file, using default language: English")

class LanguageManager:
    """Manages text loading from language files"""
    
    def __init__(self, language_code=None):
        # Use the language from config if no specific language is provided
        self.language_code = language_code or CONFIG_LANGUAGE
        self.text = {}
        # Track already warned missing keys to avoid log spam
        self.missing_keys_warned = set()
        self.load_language(self.language_code)
    
    def load_language(self, language_code):
        """Load a specific language file from JSON
        
        Args:
            language_code: Two-letter language code (e.g., 'en', 'zh')
        
        Returns:
            bool: True if language loaded successfully, False otherwise
        """
        try:
            # Construct the path to the JSON file
            # Note: This assumes the script runs from the project root.
            # A more robust solution might use __file__ to get the package path.
            file_path = os.path.join(os.path.dirname(__file__), f'{language_code}.json')

            with open(file_path, 'r', encoding='utf-8') as f:
                self.text = json.load(f)
            
            self.missing_keys_warned = set()
            self.language_code = language_code
            logger.info(f"Loaded language: {language_code}")
            return True
            
        except FileNotFoundError:
            logger.error(f"Language file not found: {file_path}")
            if language_code != 'en':
                logger.info("Falling back to English")
                return self.load_language('en')
            return False
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from language file: {file_path}")
            return False
        except Exception as e:
            logger.error(f"Error loading language file: {e}")
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