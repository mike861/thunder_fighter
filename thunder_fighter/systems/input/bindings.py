"""
Key Bindings System

This module manages configurable key bindings for the Thunder Fighter game.
It allows for customizable controls and easy remapping of keys.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

import pygame

from thunder_fighter.utils.logger import logger


@dataclass
class KeyBinding:
    """Represents a key binding with metadata."""

    key: int
    action: str
    description: str = ""
    category: str = "general"
    modifiers: Set[int] = field(default_factory=set)

    def matches(self, key: int, modifiers: Optional[Set[int]] = None) -> bool:
        """
        Check if this binding matches the given key and modifiers.

        Args:
            key: The key code to check
            modifiers: Set of modifier keys (Ctrl, Shift, Alt)

        Returns:
            True if the binding matches
        """
        if modifiers is None:
            modifiers = set()

        return self.key == key and self.modifiers == modifiers


class KeyBindings:
    """
    Manages configurable key bindings for the game.

    This class provides a centralized way to manage key mappings,
    allowing for easy customization and conflict detection.
    """

    def __init__(self):
        """Initialize with default key bindings."""
        self._bindings: Dict[str, KeyBinding] = {}
        self._key_to_action: Dict[int, str] = {}
        self._setup_default_bindings()

        logger.info("KeyBindings initialized with default mappings")

    def _setup_default_bindings(self):
        """Set up the default key bindings."""
        default_bindings = [
            # Movement
            KeyBinding(pygame.K_w, "move_up", "Move up", "movement"),
            KeyBinding(pygame.K_UP, "move_up", "Move up (arrow)", "movement"),
            KeyBinding(pygame.K_s, "move_down", "Move down", "movement"),
            KeyBinding(pygame.K_DOWN, "move_down", "Move down (arrow)", "movement"),
            KeyBinding(pygame.K_a, "move_left", "Move left", "movement"),
            KeyBinding(pygame.K_LEFT, "move_left", "Move left (arrow)", "movement"),
            KeyBinding(pygame.K_d, "move_right", "Move right", "movement"),
            KeyBinding(pygame.K_RIGHT, "move_right", "Move right (arrow)", "movement"),
            # Actions
            KeyBinding(pygame.K_SPACE, "shoot", "Shoot", "action"),
            KeyBinding(pygame.K_j, "shoot", "Shoot (J)", "action"),
            KeyBinding(pygame.K_x, "launch_missile", "Launch missile", "action"),
            KeyBinding(pygame.K_k, "launch_missile", "Launch missile (K)", "action"),
            # Game controls
            KeyBinding(pygame.K_p, "pause", "Pause/Resume", "game"),
            KeyBinding(pygame.K_ESCAPE, "quit", "Quit game", "game"),
            KeyBinding(pygame.K_r, "restart", "Restart game", "game"),
            # Audio controls
            KeyBinding(pygame.K_m, "toggle_music", "Toggle music", "audio"),
            KeyBinding(pygame.K_n, "toggle_sound", "Toggle sound effects", "audio"),
            KeyBinding(pygame.K_PLUS, "volume_up", "Volume up", "audio"),
            KeyBinding(pygame.K_EQUALS, "volume_up", "Volume up (=)", "audio"),
            KeyBinding(pygame.K_MINUS, "volume_down", "Volume down", "audio"),
            # UI controls
            KeyBinding(pygame.K_l, "change_language", "Change language", "ui"),
            KeyBinding(pygame.K_F3, "toggle_dev_mode", "Toggle developer mode", "ui"),
            KeyBinding(pygame.K_F1, "reset_input_state", "Reset input state (macOS fix)", "debug"),
            # Special
            KeyBinding(pygame.K_RETURN, "skip_animation", "Skip animation", "special"),
            KeyBinding(pygame.K_KP_ENTER, "skip_animation", "Skip animation (numpad)", "special"),
        ]

        for binding in default_bindings:
            self.add_binding(binding)

    def add_binding(self, binding: KeyBinding):
        """
        Add a key binding.

        Args:
            binding: The KeyBinding to add
        """
        # Create a unique key for bindings that might have the same action
        binding_key = f"{binding.action}_{binding.key}"
        self._bindings[binding_key] = binding

        # Update reverse lookup (key to action)
        if binding.key not in self._key_to_action:
            self._key_to_action[binding.key] = binding.action

        logger.debug(f"Added key binding: {pygame.key.name(binding.key)} -> {binding.action}")

    def remove_binding(self, action: str, key: int):
        """
        Remove a key binding.

        Args:
            action: The action name
            key: The key code
        """
        binding_key = f"{action}_{key}"
        if binding_key in self._bindings:
            del self._bindings[binding_key]

            # Update reverse lookup
            if key in self._key_to_action and self._key_to_action[key] == action:
                del self._key_to_action[key]

            logger.debug(f"Removed key binding: {pygame.key.name(key)} -> {action}")

    def get_action(self, key: int, modifiers: Optional[Set[int]] = None) -> Optional[str]:
        """
        Get the action for a given key and modifiers.

        Args:
            key: The key code
            modifiers: Set of modifier keys

        Returns:
            The action name or None if no binding found
        """
        if modifiers is None:
            modifiers = set()

        # Find matching binding
        for binding in self._bindings.values():
            if binding.matches(key, modifiers):
                return binding.action

        return None

    def get_keys_for_action(self, action: str) -> List[int]:
        """
        Get all keys bound to an action.

        Args:
            action: The action name

        Returns:
            List of key codes bound to the action
        """
        keys = []
        for binding in self._bindings.values():
            if binding.action == action:
                keys.append(binding.key)
        return keys

    def get_key_for_action(self, action: str) -> Optional[int]:
        """
        Get the first key bound to an action.

        Args:
            action: The action name

        Returns:
            First key code bound to the action, or None if not found
        """
        for binding in self._bindings.values():
            if binding.action == action:
                return binding.key
        return None

    def get_bindings_by_category(self, category: str) -> List[KeyBinding]:
        """
        Get all bindings in a category.

        Args:
            category: The category name

        Returns:
            List of KeyBinding objects in the category
        """
        return [binding for binding in self._bindings.values() if binding.category == category]

    def get_all_categories(self) -> Set[str]:
        """
        Get all binding categories.

        Returns:
            Set of category names
        """
        return {binding.category for binding in self._bindings.values()}

    def has_conflict(self, key: int, modifiers: Optional[Set[int]] = None) -> bool:
        """
        Check if a key binding would conflict with existing bindings.

        Args:
            key: The key code to check
            modifiers: Set of modifier keys

        Returns:
            True if there would be a conflict
        """
        if modifiers is None:
            modifiers = set()

        for binding in self._bindings.values():
            if binding.matches(key, modifiers):
                return True

        return False

    def get_conflicts(self, key: int, modifiers: Optional[Set[int]] = None) -> List[KeyBinding]:
        """
        Get all bindings that conflict with the given key.

        Args:
            key: The key code to check
            modifiers: Set of modifier keys

        Returns:
            List of conflicting KeyBinding objects
        """
        if modifiers is None:
            modifiers = set()

        conflicts = []
        for binding in self._bindings.values():
            if binding.matches(key, modifiers):
                conflicts.append(binding)

        return conflicts

    def rebind_key(self, action: str, old_key: int, new_key: int, modifiers: Optional[Set[int]] = None) -> bool:
        """
        Rebind an action from one key to another.

        Args:
            action: The action to rebind
            old_key: The current key
            new_key: The new key
            modifiers: Set of modifier keys for the new binding

        Returns:
            True if rebinding was successful
        """
        if modifiers is None:
            modifiers = set()

        # Check for conflicts
        if self.has_conflict(new_key, modifiers):
            logger.warning(f"Cannot rebind {action}: key {pygame.key.name(new_key)} already bound")
            return False

        # Find and update the binding
        binding_key = f"{action}_{old_key}"
        if binding_key in self._bindings:
            old_binding = self._bindings[binding_key]

            # Remove old binding
            self.remove_binding(action, old_key)

            # Add new binding
            new_binding = KeyBinding(
                key=new_key,
                action=action,
                description=old_binding.description,
                category=old_binding.category,
                modifiers=modifiers,
            )
            self.add_binding(new_binding)

            logger.info(f"Rebound {action}: {pygame.key.name(old_key)} -> {pygame.key.name(new_key)}")
            return True

        logger.warning(f"Cannot rebind {action}: binding not found for key {pygame.key.name(old_key)}")
        return False

    def reset_to_defaults(self):
        """Reset all bindings to default values."""
        self._bindings.clear()
        self._key_to_action.clear()
        self._setup_default_bindings()
        logger.info("Key bindings reset to defaults")

    def get_binding_info(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get formatted binding information for display.

        Returns:
            Dictionary with categories as keys and binding info as values
        """
        info = {}

        for category in self.get_all_categories():
            bindings = self.get_bindings_by_category(category)
            info[category] = []

            for binding in bindings:
                info[category].append(
                    {"key": pygame.key.name(binding.key), "action": binding.action, "description": binding.description}
                )

        return info

    def __str__(self):
        return f"KeyBindings({len(self._bindings)} bindings, {len(self.get_all_categories())} categories)"
