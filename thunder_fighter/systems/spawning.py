"""
Entity Spawning System

Manages the spawning logic for enemies, items, bosses, etc. in a unified way.
Integrates calls to various factory classes.
"""

import random
from typing import Any, Dict

from thunder_fighter.utils.logger import logger


class SpawningSystem:
    """Entity Spawning System Class"""

    def __init__(self):
        self.enemy_factory = None
        self.boss_factory = None
        self.item_factory = None
        self.spawn_timers = {}
        self.spawn_rates = {}
        self.last_spawn_times = {}

        # Initialize spawn parameters
        self._setup_spawn_parameters()

        # Lazily initialize factories (to avoid circular imports)
        self._factories_initialized = False

    def _setup_spawn_parameters(self):
        """Sets up spawn parameters."""
        self.spawn_rates = {
            "enemy": 2.0,  # Spawn an enemy every 2 seconds
            "boss": 30.0,  # Spawn a boss every 30 seconds
            "item": 10.0,  # Potentially spawn an item every 10 seconds
        }

        # Reset last spawn times
        self.last_spawn_times = {
            "enemy": 0.0,
            "boss": 0.0,
            "item": 0.0,
        }

    def _init_factories(self):
        """Initializes factory classes."""
        if not self._factories_initialized:
            try:
                from thunder_fighter.entities.enemies.boss_factory import BossFactory
                from thunder_fighter.entities.enemies.enemy_factory import EnemyFactory
                from thunder_fighter.entities.items.item_factory import ItemFactory

                self.enemy_factory = EnemyFactory()
                self.boss_factory = BossFactory()
                self.item_factory = ItemFactory()

                self._factories_initialized = True
                logger.info("Spawning system factories initialized")
            except ImportError as e:
                logger.error(f"Failed to initialize factories: {e}")

    def update(self, dt: float, game_state: Dict[str, Any]):
        """Updates the spawning logic."""
        if not self._factories_initialized:
            self._init_factories()

        current_time = game_state.get("game_time", 0.0)

        self._update_enemy_spawning(dt, current_time, game_state)
        self._update_boss_spawning(dt, current_time, game_state)
        self._update_item_spawning(dt, current_time, game_state)

    def _update_enemy_spawning(self, dt: float, current_time: float, game_state: Dict[str, Any]):
        """Updates enemy spawning."""
        if not self.enemy_factory:
            return

        # Check if it's time to spawn
        if current_time - self.last_spawn_times["enemy"] >= self.spawn_rates["enemy"]:
            try:
                # Adjust enemy difficulty based on game level
                game_level = game_state.get("level", 1)
                enemy_level = min(game_level, 5)  # Max level 5

                # Spawn enemy
                enemy = self.enemy_factory.create_enemy(
                    level=enemy_level, x=random.randint(50, game_state.get("screen_width", 800) - 50), y=-50
                )

                # Add to sprite groups
                enemies_group = game_state.get("enemies_group")
                all_sprites = game_state.get("all_sprites")

                if enemies_group and all_sprites:
                    enemies_group.add(enemy)
                    all_sprites.add(enemy)

                self.last_spawn_times["enemy"] = current_time
                logger.debug(f"Enemy spawned at level {enemy_level}")

            except Exception as e:
                logger.error(f"Error spawning enemy: {e}")

    def _update_boss_spawning(self, dt: float, current_time: float, game_state: Dict[str, Any]):
        """Updates boss spawning."""
        if not self.boss_factory:
            return

        # Check if it's time to spawn and there is no active boss
        if current_time - self.last_spawn_times["boss"] >= self.spawn_rates["boss"] and not game_state.get(
            "boss_active", False
        ):
            try:
                # Adjust boss difficulty based on game level
                game_level = game_state.get("level", 1)
                boss_level = min(game_level // 2 + 1, 3)  # Boss level is slightly lower but not exceeding 3

                # Spawn boss
                boss = self.boss_factory.create_boss(
                    level=boss_level, x=game_state.get("screen_width", 800) // 2, y=100
                )

                # Add to sprite groups
                bosses_group = game_state.get("bosses_group")
                all_sprites = game_state.get("all_sprites")

                if bosses_group and all_sprites:
                    bosses_group.add(boss)
                    all_sprites.add(boss)

                self.last_spawn_times["boss"] = current_time
                logger.info(f"Boss spawned at level {boss_level}")

            except Exception as e:
                logger.error(f"Error spawning boss: {e}")

    def _update_item_spawning(self, dt: float, current_time: float, game_state: Dict[str, Any]):
        """Updates item spawning."""
        if not self.item_factory:
            return

        # Randomly spawn items (probabilistically)
        if (
            current_time - self.last_spawn_times["item"] >= self.spawn_rates["item"] and random.random() < 0.3
        ):  # 30% chance to spawn an item
            try:
                # Randomly select an item type
                item_types = ["health", "bullet_speed", "bullet_path", "player_speed"]
                item_type = random.choice(item_types)

                # Spawn item
                item = self.item_factory.create_item(
                    item_type=item_type, x=random.randint(50, game_state.get("screen_width", 800) - 50), y=-30
                )

                # Add to sprite groups
                items_group = game_state.get("items_group")
                all_sprites = game_state.get("all_sprites")

                if items_group and all_sprites:
                    items_group.add(item)
                    all_sprites.add(item)

                self.last_spawn_times["item"] = current_time
                logger.debug(f"Item spawned: {item_type}")

            except Exception as e:
                logger.error(f"Error spawning item: {e}")

    def set_spawn_rate(self, entity_type: str, rate: float):
        """Sets the spawn rate."""
        if entity_type in self.spawn_rates:
            self.spawn_rates[entity_type] = rate
            logger.info(f"Spawn rate for {entity_type} set to {rate}")

    def reset_spawn_times(self):
        """Resets spawn times."""
        current_time = 0.0
        for entity_type in self.last_spawn_times:
            self.last_spawn_times[entity_type] = current_time
        logger.info("Spawn times reset")

    def get_spawn_statistics(self) -> Dict[str, Any]:
        """Gets spawn statistics."""
        return {
            "spawn_rates": self.spawn_rates.copy(),
            "last_spawn_times": self.last_spawn_times.copy(),
            "factories_initialized": self._factories_initialized,
        }
