"""
Item Factory

This module provides a factory for creating item entities with different
types and configurations, featuring intelligent weight-based selection.
"""

import random
import time
from typing import Any, Dict

import pygame

from thunder_fighter.constants import ITEM_WEIGHT_SYSTEM, PLAYER_HEALTH
from thunder_fighter.entities.items.items import (
    BulletPathItem,
    BulletSpeedItem,
    HealthItem,
    PlayerSpeedItem,
    WingmanItem,
)
from thunder_fighter.utils.logger import logger

from ..entity_factory import ConfigurableEntityFactory


class ItemFactory(ConfigurableEntityFactory):
    """Factory for creating item entities."""

    def __init__(self):
        """Initialize the item factory."""
        super().__init__(HealthItem)  # Default type, will be overridden
        self._item_types = {
            "health": HealthItem,
            "bullet_speed": BulletSpeedItem,
            "bullet_path": BulletPathItem,
            "player_speed": PlayerSpeedItem,
            "wingman": WingmanItem,
        }
        self._setup_default_presets()

        # Phase 2: Duplicate prevention tracking
        self._last_spawn_times = dict.fromkeys(self._item_types.keys(), 0)
        self._last_item_type = None
        self._consecutive_count = 0

        logger.info("ItemFactory initialized with intelligent weight system")

    def _setup_default_presets(self):
        """Set up default item configuration presets."""
        for item_type in self._item_types.keys():
            self.add_preset(item_type, {"item_type": item_type, "spawn_position": None})

    def _get_required_fields(self) -> list:
        """Get required fields for item creation."""
        return ["all_sprites", "items", "player"]

    def _create_entity(self, config: Dict[str, Any]):
        """Create an item entity."""
        item_type = config.get("item_type", "health")
        all_sprites = config["all_sprites"]
        items = config["items"]

        item_class = self._item_types.get(item_type, HealthItem)
        # Create item instance without parameters
        item = item_class()

        # Add to sprite groups
        all_sprites.add(item)
        items.add(item)

        return item

    def create_random_item(
        self, all_sprites: pygame.sprite.Group, items: pygame.sprite.Group, player, game_level: int = 1
    ):
        """Create a weighted random item based on game state."""
        weights = self._calculate_dynamic_weights(player, game_level)
        item_type = self._weighted_choice(weights)

        if item_type:
            # Update tracking for duplicate prevention
            current_time = time.time()
            self._last_spawn_times[item_type] = current_time

            if self._last_item_type == item_type:
                self._consecutive_count += 1
            else:
                self._consecutive_count = 1
            self._last_item_type = item_type

            logger.debug(f"Selected item type '{item_type}' with intelligent weights")
            return self.create_from_preset(item_type, all_sprites=all_sprites, items=items, player=player)

        logger.debug("No item selected (weighted randomization)")
        return None

    def _calculate_dynamic_weights(self, player, game_level: int) -> Dict[str, float]:
        """Calculate dynamic weights based on game state."""
        config = ITEM_WEIGHT_SYSTEM
        base_weights = config["BASE_WEIGHTS"].copy()

        # Phase 1: Health-based adaptation
        health_ratio = player.health / PLAYER_HEALTH
        health_config = config["HEALTH_ADAPTATION"]

        if health_ratio <= health_config["critical_threshold"]:
            base_weights["health"] *= health_config["critical_multiplier"]
        elif health_ratio <= health_config["injured_threshold"]:
            base_weights["health"] *= health_config["injured_multiplier"]
        else:
            base_weights["health"] *= health_config["healthy_multiplier"]

        # Phase 1: Level-based gating
        level_config = config["LEVEL_GATING"]
        if game_level < level_config["wingman_min_level"]:
            base_weights["wingman"] = 0

        # Phase 1: Ability cap detection
        ability_caps = config["ABILITY_CAPS"]
        if hasattr(player, "bullet_speed") and player.bullet_speed >= ability_caps["bullet_speed_max"]:
            base_weights["bullet_speed"] = 0
        if hasattr(player, "bullet_paths") and player.bullet_paths >= ability_caps["bullet_paths_max"]:
            base_weights["bullet_path"] = 0
        if hasattr(player, "speed") and player.speed >= ability_caps["player_speed_max"]:
            base_weights["player_speed"] = 0
        if hasattr(player, "wingmen_list") and len(player.wingmen_list) >= ability_caps["wingman_max"]:
            base_weights["wingman"] = 0

        # Phase 2: Duplicate prevention
        current_time = time.time()
        duplicate_config = config["DUPLICATE_PREVENTION"]

        for item_type in base_weights:
            time_since_last = current_time - self._last_spawn_times.get(item_type, 0)
            if time_since_last < duplicate_config["min_same_item_interval"]:
                base_weights[item_type] *= duplicate_config["burst_penalty_multiplier"]

        # Prevent too many consecutive same items
        if self._last_item_type and self._consecutive_count >= duplicate_config["max_consecutive_same"]:
            if self._last_item_type in base_weights:
                base_weights[self._last_item_type] *= duplicate_config["burst_penalty_multiplier"]

        return base_weights

    def _weighted_choice(self, weights: Dict[str, float]) -> str:
        """Select item type based on weights."""
        # Filter out zero weights
        valid_items = {k: v for k, v in weights.items() if v > 0}

        if not valid_items:
            logger.warning("No valid items available for selection")
            return None

        # Calculate total weight
        total_weight = sum(valid_items.values())

        if total_weight <= 0:
            logger.warning("Total weight is zero or negative")
            return None

        # Random selection based on weights
        random_value = random.uniform(0, total_weight)
        cumulative = 0

        for item_type, weight in valid_items.items():
            cumulative += weight
            if random_value <= cumulative:
                return item_type

        # Fallback to last item (shouldn't happen)
        return list(valid_items.keys())[-1]
