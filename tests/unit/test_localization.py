"""
Tests for Improved Localization System

Tests the enhanced localization system with loader abstraction,
dependency injection, and better testability.
"""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from thunder_fighter.localization import (
    CachedLanguageLoader,
    FileLanguageLoader,
    LanguageLoader,
    LanguageManager,
    MemoryLanguageLoader,
)


class TestLanguageLoader:
    """Test the abstract LanguageLoader interface."""

    def test_abstract_interface(self):
        """Test that LanguageLoader cannot be instantiated directly."""
        with pytest.raises(TypeError):
            LanguageLoader()


class TestFileLanguageLoader:
    """Test FileLanguageLoader functionality."""

    def test_initialization_with_default_path(self):
        """Test initialization with default path."""
        loader = FileLanguageLoader()
        assert loader.base_path is not None
        assert os.path.exists(loader.base_path)

    def test_initialization_with_custom_path(self):
        """Test initialization with custom path."""
        custom_path = "/custom/path"
        loader = FileLanguageLoader(custom_path)
        assert loader.base_path == custom_path

    def test_load_existing_language(self):
        """Test loading an existing language file."""
        loader = FileLanguageLoader()

        # Should be able to load English
        en_data = loader.load("en")
        assert en_data is not None
        assert isinstance(en_data, dict)
        assert len(en_data) > 0
        assert "GAME_TITLE" in en_data

    def test_load_nonexistent_language(self):
        """Test loading a non-existent language file."""
        loader = FileLanguageLoader()

        # Should return None for non-existent language
        fake_data = loader.load("nonexistent")
        assert fake_data is None

    def test_available_languages(self):
        """Test getting available languages."""
        loader = FileLanguageLoader()

        languages = loader.available_languages()
        assert isinstance(languages, list)
        assert "en" in languages
        assert "zh" in languages
        assert len(languages) >= 2

    def test_available_languages_empty_directory(self):
        """Test available languages with empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = FileLanguageLoader(temp_dir)
            languages = loader.available_languages()
            assert languages == []

    def test_load_malformed_json(self):
        """Test loading malformed JSON file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create malformed JSON file
            bad_file = os.path.join(temp_dir, "bad.json")
            with open(bad_file, "w") as f:
                f.write("{ invalid json }")

            loader = FileLanguageLoader(temp_dir)
            result = loader.load("bad")
            assert result is None

    def test_load_with_io_error(self):
        """Test loading with IO errors."""
        loader = FileLanguageLoader("/nonexistent/path")
        result = loader.load("en")
        assert result is None


class TestMemoryLanguageLoader:
    """Test MemoryLanguageLoader functionality."""

    def test_empty_initialization(self):
        """Test initialization with no languages."""
        loader = MemoryLanguageLoader()
        assert loader.languages == {}
        assert loader.available_languages() == []

    def test_initialization_with_languages(self):
        """Test initialization with pre-loaded languages."""
        languages = {"en": {"hello": "Hello", "goodbye": "Goodbye"}, "es": {"hello": "Hola", "goodbye": "Adiós"}}
        loader = MemoryLanguageLoader(languages)

        assert loader.available_languages() == ["en", "es"]
        assert loader.load("en") == {"hello": "Hello", "goodbye": "Goodbye"}
        assert loader.load("es") == {"hello": "Hola", "goodbye": "Adiós"}

    def test_load_existing_language(self):
        """Test loading existing language from memory."""
        loader = MemoryLanguageLoader({"test": {"key1": "value1", "key2": "value2"}})

        result = loader.load("test")
        assert result == {"key1": "value1", "key2": "value2"}

        # Should return a copy, not the original
        result["key1"] = "modified"
        original = loader.load("test")
        assert original["key1"] == "value1"  # Original unchanged

    def test_load_nonexistent_language(self):
        """Test loading non-existent language from memory."""
        loader = MemoryLanguageLoader({"en": {"hello": "Hello"}})

        result = loader.load("nonexistent")
        assert result is None

    def test_add_language(self):
        """Test adding language to memory loader."""
        loader = MemoryLanguageLoader()

        # Add language
        loader.add_language("fr", {"hello": "Bonjour", "goodbye": "Au revoir"})

        assert "fr" in loader.available_languages()
        result = loader.load("fr")
        assert result == {"hello": "Bonjour", "goodbye": "Au revoir"}

    def test_update_existing_language(self):
        """Test updating existing language in memory."""
        loader = MemoryLanguageLoader({"en": {"hello": "Hello"}})

        # Update language
        loader.add_language("en", {"hello": "Hi", "new_key": "New Value"})

        result = loader.load("en")
        assert result == {"hello": "Hi", "new_key": "New Value"}


class TestCachedLanguageLoader:
    """Test CachedLanguageLoader functionality."""

    def test_initialization(self):
        """Test initialization with base loader."""
        base_loader = Mock(spec=LanguageLoader)
        cached_loader = CachedLanguageLoader(base_loader)

        assert cached_loader.base_loader is base_loader
        assert cached_loader._cache == {}

    def test_load_from_base_loader(self):
        """Test loading from base loader (cache miss)."""
        base_loader = Mock(spec=LanguageLoader)
        base_loader.load.return_value = {"hello": "Hello"}

        cached_loader = CachedLanguageLoader(base_loader)
        result = cached_loader.load("en")

        assert result == {"hello": "Hello"}
        base_loader.load.assert_called_once_with("en")
        assert "en" in cached_loader._cache

    def test_load_from_cache(self):
        """Test loading from cache (cache hit)."""
        base_loader = Mock(spec=LanguageLoader)
        base_loader.load.return_value = {"hello": "Hello"}

        cached_loader = CachedLanguageLoader(base_loader)

        # First load - should call base loader
        result1 = cached_loader.load("en")
        assert base_loader.load.call_count == 1

        # Second load - should use cache
        result2 = cached_loader.load("en")
        assert base_loader.load.call_count == 1  # Not called again
        assert result1 == result2

    def test_load_returns_copy_from_cache(self):
        """Test that cached data returns copies, not references."""
        base_loader = Mock(spec=LanguageLoader)
        base_loader.load.return_value = {"hello": "Hello"}

        cached_loader = CachedLanguageLoader(base_loader)

        result1 = cached_loader.load("en")
        result2 = cached_loader.load("en")

        # Modify one result
        result1["hello"] = "Modified"

        # Other result should be unchanged
        assert result2["hello"] == "Hello"

    def test_load_none_result(self):
        """Test loading when base loader returns None."""
        base_loader = Mock(spec=LanguageLoader)
        base_loader.load.return_value = None

        cached_loader = CachedLanguageLoader(base_loader)
        result = cached_loader.load("nonexistent")

        assert result is None
        # Should not cache None results
        assert "nonexistent" not in cached_loader._cache

    def test_available_languages_delegation(self):
        """Test that available_languages delegates to base loader."""
        base_loader = Mock(spec=LanguageLoader)
        base_loader.available_languages.return_value = ["en", "zh"]

        cached_loader = CachedLanguageLoader(base_loader)
        result = cached_loader.available_languages()

        assert result == ["en", "zh"]
        base_loader.available_languages.assert_called_once()

    def test_clear_cache(self):
        """Test cache clearing functionality."""
        base_loader = Mock(spec=LanguageLoader)
        base_loader.load.return_value = {"hello": "Hello"}

        cached_loader = CachedLanguageLoader(base_loader)

        # Load and cache data
        cached_loader.load("en")
        assert "en" in cached_loader._cache

        # Clear cache
        cached_loader.clear_cache()
        assert cached_loader._cache == {}


class TestLanguageManager:
    """Test enhanced LanguageManager with dependency injection."""

    def test_initialization_with_defaults(self):
        """Test initialization with default parameters."""
        with patch("thunder_fighter.localization.CONFIG_LANGUAGE", "en"):
            manager = LanguageManager()

            assert manager.language_code == "en"
            assert isinstance(manager.loader, FileLanguageLoader)
            assert isinstance(manager.text, dict)

    def test_initialization_with_custom_loader(self):
        """Test initialization with custom loader."""
        custom_loader = MemoryLanguageLoader({"test": {"hello": "Hello World"}})

        manager = LanguageManager("test", custom_loader)

        assert manager.language_code == "test"
        assert manager.loader is custom_loader
        assert manager.text == {"hello": "Hello World"}

    def test_load_language_success(self):
        """Test successful language loading."""
        mock_loader = Mock(spec=LanguageLoader)
        mock_loader.load.return_value = {"key1": "value1", "key2": "value2"}

        manager = LanguageManager(loader=mock_loader)
        result = manager.load_language("test")

        assert result is True
        assert manager.language_code == "test"
        assert manager.text == {"key1": "value1", "key2": "value2"}
        mock_loader.load.assert_called_with("test")

    def test_load_language_failure_with_fallback(self):
        """Test language loading failure with fallback to English."""
        mock_loader = Mock(spec=LanguageLoader)

        def mock_load_side_effect(lang):
            if lang == "invalid":
                return None  # First call (for 'invalid') returns None
            elif lang == "en":
                return {"fallback": "English"}  # Second call (for 'en') returns data
            return None

        mock_loader.load.side_effect = mock_load_side_effect

        manager = LanguageManager("en", loader=mock_loader)  # Start with 'en' to have working initial state
        result = manager.load_language("invalid")

        assert result is True  # Should succeed due to fallback
        assert manager.language_code == "en"  # Should fall back to English
        assert manager.text == {"fallback": "English"}
        assert mock_loader.load.call_count == 3  # Initial 'en', 'invalid', fallback 'en'

    def test_load_language_complete_failure(self):
        """Test language loading complete failure."""
        mock_loader = Mock(spec=LanguageLoader)
        mock_loader.load.return_value = None

        manager = LanguageManager(loader=mock_loader)
        result = manager.load_language("en")  # Even English fails

        assert result is False
        assert manager.text == {}

    def test_change_language(self):
        """Test language changing functionality."""
        mock_loader = Mock(spec=LanguageLoader)
        mock_loader.load.return_value = {"new_lang": "New Language"}

        manager = LanguageManager(loader=mock_loader)
        result = manager.change_language("new")

        assert result is True
        assert manager.language_code == "new"
        assert manager.text == {"new_lang": "New Language"}

    def test_get_text_existing_key(self):
        """Test getting text for existing key."""
        manager = LanguageManager(
            loader=MemoryLanguageLoader({"test": {"hello": "Hello World", "greeting": "Hi {name}!"}})
        )
        manager.load_language("test")

        # Simple text
        result = manager.get_text("hello")
        assert result == "Hello World"

        # Text with formatting
        result = manager.get_text("greeting", name="Alice")
        assert result == "Hi Alice!"

    def test_get_text_missing_key(self):
        """Test getting text for missing key."""
        manager = LanguageManager(loader=MemoryLanguageLoader({"test": {"hello": "Hello World"}}))
        manager.load_language("test")

        # First time - should log warning
        result = manager.get_text("missing_key")
        assert result == "missing_key"
        assert "missing_key" in manager.missing_keys_warned

        # Second time - should not log warning again
        result = manager.get_text("missing_key")
        assert result == "missing_key"

    def test_get_text_formatting_error(self):
        """Test getting text with formatting error."""
        manager = LanguageManager(loader=MemoryLanguageLoader({"test": {"bad_format": "Hello {missing_arg}!"}}))
        manager.load_language("test")

        # Should return original text even if formatting fails
        result = manager.get_text("bad_format", name="Alice")
        assert result == "Hello {missing_arg}!"

    def test_reset_warnings(self):
        """Test resetting missing key warnings."""
        manager = LanguageManager(loader=MemoryLanguageLoader({"test": {"hello": "Hello"}}))
        manager.load_language("test")

        # Generate warning
        manager.get_text("missing_key")
        assert "missing_key" in manager.missing_keys_warned

        # Reset warnings
        manager.reset_warnings()
        assert len(manager.missing_keys_warned) == 0

    def test_get_available_languages(self):
        """Test getting available languages from loader."""
        mock_loader = Mock(spec=LanguageLoader)
        mock_loader.available_languages.return_value = ["en", "zh", "es"]

        manager = LanguageManager(loader=mock_loader)
        result = manager.get_available_languages()

        assert result == ["en", "zh", "es"]
        mock_loader.available_languages.assert_called_once()

    def test_get_font_for_current_language(self):
        """Test getting font for current language."""
        manager = LanguageManager(loader=MemoryLanguageLoader({"zh": {"hello": "你好"}}))
        manager.load_language("zh")

        with patch("thunder_fighter.localization.font_support.get_localized_font") as mock_get_font:
            mock_font = Mock()
            mock_get_font.return_value = mock_font

            result = manager.get_font_for_current_language(24, "bold")

            assert result is mock_font
            mock_get_font.assert_called_once_with("zh", 24, "bold")


class TestLocalizationIntegration:
    """Integration tests for the localization system."""

    def test_file_to_memory_migration(self):
        """Test migrating from file-based to memory-based loader."""
        # Start with file loader
        file_loader = FileLanguageLoader()
        manager = LanguageManager("en", file_loader)

        # Get some text
        title = manager.get_text("GAME_TITLE")
        assert title is not None

        # Migrate to memory loader with custom data
        memory_loader = MemoryLanguageLoader({"custom": {"GAME_TITLE": "Custom Game Title"}})
        manager.loader = memory_loader
        manager.change_language("custom")

        # Should now use custom data
        custom_title = manager.get_text("GAME_TITLE")
        assert custom_title == "Custom Game Title"

    def test_caching_performance(self):
        """Test that caching improves performance."""
        # Create loader that tracks call count
        base_loader = Mock(spec=LanguageLoader)
        base_loader.load.return_value = {"test": "Test Value"}

        cached_loader = CachedLanguageLoader(base_loader)
        manager = LanguageManager("test", cached_loader)

        # Load language multiple times
        for _ in range(5):
            manager.change_language("test")

        # Base loader should only be called once due to caching
        assert base_loader.load.call_count == 1

    def test_fallback_chain(self):
        """Test language fallback chain."""
        # Create loader that fails for non-English languages
        loader = Mock(spec=LanguageLoader)
        loader.load.side_effect = lambda lang: ({"GAME_TITLE": "Thunder Fighter"} if lang == "en" else None)

        manager = LanguageManager("nonexistent", loader)

        # Should fall back to English
        assert manager.language_code == "en"
        assert manager.get_text("GAME_TITLE") == "Thunder Fighter"

    def test_real_file_loading(self):
        """Test loading real language files."""
        # This test uses actual files in the project
        manager = LanguageManager("en")

        # Should be able to load and use real English data
        title = manager.get_text("GAME_TITLE")
        assert title is not None
        assert len(title) > 0

        # Try switching to Chinese
        success = manager.change_language("zh")
        if success:  # Only test if Chinese file exists
            zh_title = manager.get_text("GAME_TITLE")
            assert zh_title is not None
            assert zh_title != title  # Should be different from English

    def test_concurrent_access_safety(self):
        """Test that the system is safe for concurrent access."""
        import threading
        import time

        manager = LanguageManager(
            loader=MemoryLanguageLoader({"en": {"counter": "English {count}"}, "zh": {"counter": "Chinese {count}"}})
        )

        results = []

        def worker(thread_id):
            for i in range(10):
                lang = "en" if i % 2 == 0 else "zh"
                manager.change_language(lang)
                text = manager.get_text("counter", count=f"{thread_id}-{i}")
                results.append((thread_id, text))
                time.sleep(0.001)  # Small delay to increase contention

        # Run multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All operations should complete without errors
        assert len(results) == 30  # 3 threads * 10 operations each
