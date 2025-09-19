"""
Language Loader Abstraction

This module provides abstract interfaces and implementations for loading
language data, enabling better testability and flexibility.
"""

import json
import os
from abc import ABC, abstractmethod
from typing import Dict, Optional

from thunder_fighter.utils.logger import logger


class LanguageLoader(ABC):
    """Abstract base class for language loading strategies."""

    @abstractmethod
    def load(self, language_code: str) -> Optional[Dict[str, str]]:
        """
        Load language data for the given code.

        Args:
            language_code: Two-letter language code (e.g., 'en', 'zh')

        Returns:
            Dictionary of text keys to translations, or None if loading fails
        """
        pass

    @abstractmethod
    def available_languages(self) -> list[str]:
        """
        Get list of available language codes.

        Returns:
            List of available language codes
        """
        pass


class FileLanguageLoader(LanguageLoader):
    """
    Loads language data from JSON files in the filesystem.

    This is the production implementation that reads from actual files.
    """

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the file loader.

        Args:
            base_path: Base directory for language files. If None, uses module directory.
        """
        if base_path is None:
            # Default to the localization module directory
            base_path = os.path.dirname(os.path.abspath(__file__))
        self.base_path = base_path
        logger.debug(f"FileLanguageLoader initialized with base path: {base_path}")

    def load(self, language_code: str) -> Optional[Dict[str, str]]:
        """Load language data from a JSON file."""
        file_path = os.path.join(self.base_path, f"{language_code}.json")

        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Loaded language file: {file_path}")
            return data if isinstance(data, dict) else None

        except FileNotFoundError:
            logger.error(f"Language file not found: {file_path}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading language file {file_path}: {e}")
            return None

    def available_languages(self) -> list[str]:
        """Get available languages by scanning for JSON files."""
        try:
            files = os.listdir(self.base_path)
            languages = []

            for file in files:
                if file.endswith(".json") and not file.startswith("_"):
                    # Extract language code from filename
                    lang_code = file[:-5]  # Remove .json extension
                    languages.append(lang_code)

            return sorted(languages)
        except Exception as e:
            logger.error(f"Error scanning for language files: {e}")
            return []


class MemoryLanguageLoader(LanguageLoader):
    """
    Loads language data from in-memory dictionaries.

    This implementation is useful for testing without filesystem dependencies.
    """

    def __init__(self, languages: Optional[Dict[str, Dict[str, str]]] = None):
        """
        Initialize the memory loader.

        Args:
            languages: Dictionary mapping language codes to translation dictionaries
        """
        self.languages = languages or {}
        logger.debug(f"MemoryLanguageLoader initialized with {len(self.languages)} languages")

    def load(self, language_code: str) -> Optional[Dict[str, str]]:
        """Load language data from memory."""
        if language_code in self.languages:
            logger.info(f"Loaded language from memory: {language_code}")
            return self.languages[language_code].copy()  # Return a copy to prevent mutations
        else:
            logger.error(f"Language not found in memory: {language_code}")
            return None

    def available_languages(self) -> list[str]:
        """Get available languages from memory."""
        return sorted(self.languages.keys())

    def add_language(self, language_code: str, translations: Dict[str, str]):
        """
        Add or update a language in memory.

        Args:
            language_code: Language code to add/update
            translations: Dictionary of translations
        """
        self.languages[language_code] = translations.copy()
        logger.debug(f"Added language to memory: {language_code}")


class CachedLanguageLoader(LanguageLoader):
    """
    Wrapper that adds caching to any language loader.

    This decorator pattern improves performance by caching loaded languages.
    """

    def __init__(self, base_loader: LanguageLoader):
        """
        Initialize the cached loader.

        Args:
            base_loader: The underlying loader to cache
        """
        self.base_loader = base_loader
        self._cache: Dict[str, Dict[str, str]] = {}
        logger.debug("CachedLanguageLoader initialized")

    def load(self, language_code: str) -> Optional[Dict[str, str]]:
        """Load language data with caching."""
        # Check cache first
        if language_code in self._cache:
            logger.debug(f"Loaded language from cache: {language_code}")
            return self._cache[language_code].copy()

        # Load from base loader
        data = self.base_loader.load(language_code)
        if data is not None:
            # Cache the result
            self._cache[language_code] = data
            logger.debug(f"Cached language: {language_code}")

        return data

    def available_languages(self) -> list[str]:
        """Get available languages from base loader."""
        return self.base_loader.available_languages()

    def clear_cache(self):
        """Clear the language cache."""
        self._cache.clear()
        logger.debug("Language cache cleared")
