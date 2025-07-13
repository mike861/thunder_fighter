"""
Projectile Factory

This module provides a factory for creating projectile entities (bullets, missiles).
"""

from typing import Any, Dict

from thunder_fighter.entities.projectiles.bullets import Bullet
from thunder_fighter.entities.projectiles.missile import TrackingMissile
from thunder_fighter.utils.logger import logger

from ..entity_factory import ConfigurableEntityFactory


class ProjectileFactory(ConfigurableEntityFactory):
    """Factory for creating projectile entities."""

    def __init__(self):
        """Initialize the projectile factory."""
        super().__init__(Bullet)  # Default type
        self._projectile_types = {"bullet": Bullet, "missile": TrackingMissile}
        self._setup_default_presets()

        logger.info("ProjectileFactory initialized")

    def _setup_default_presets(self):
        """Set up default projectile configuration presets."""
        self.add_preset("player_bullet", {"projectile_type": "bullet", "owner": "player"})

        self.add_preset("enemy_bullet", {"projectile_type": "bullet", "owner": "enemy"})

        self.add_preset("player_missile", {"projectile_type": "missile", "owner": "player"})

    def _create_entity(self, config: Dict[str, Any]):
        """Create a projectile entity."""
        projectile_type = config.get("projectile_type", "bullet")
        projectile_class = self._projectile_types.get(projectile_type, Bullet)

        # This is a simplified version - real implementation would need
        # proper parameter handling based on the projectile type
        return projectile_class()

    def create_bullet(self, owner: str = "player"):
        """Create a bullet."""
        preset = "player_bullet" if owner == "player" else "enemy_bullet"
        return self.create_from_preset(preset)

    def create_missile(self, owner: str = "player"):
        """Create a missile."""
        return self.create_from_preset("player_missile")
