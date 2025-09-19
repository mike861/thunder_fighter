"""
Projectile Factory

This module provides a factory for creating projectile entities (bullets, missiles).
Updated to support clean interfaces with logic/graphics separation.
"""

from typing import Any, Callable, Dict, Optional

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
        """Create a projectile entity with proper parameter handling."""
        projectile_type = config.get("projectile_type", "bullet")
        projectile_class = self._projectile_types.get(projectile_type, Bullet)

        # Extract required parameters
        x = config.get("x", 0)
        y = config.get("y", 0)

        # Create projectile based on type
        if projectile_type == "bullet":
            speed = config.get("speed", 10)
            angle = config.get("angle", 0)
            renderer = config.get("renderer", None)
            return projectile_class(x, y, speed, angle, renderer)
        elif projectile_type == "missile":
            target = config.get("target", None)
            renderer = config.get("renderer", None)
            return projectile_class(x, y, target, renderer)
        else:
            # Fallback for unknown types
            return projectile_class(x, y)

    def create_bullet(
        self,
        x: float,
        y: float,
        speed: float = 10,
        angle: float = 0,
        owner: str = "player",
        renderer: Optional[Callable] = None,
    ):
        """Create a bullet with clean interface.

        Args:
            x: Initial X position
            y: Initial Y position
            speed: Movement speed (default: 10)
            angle: Movement angle in degrees (default: 0)
            owner: Owner type for tracking (default: "player")
            renderer: Optional graphics renderer for testing

        Returns:
            Configured Bullet instance
        """
        config = {
            "projectile_type": "bullet",
            "x": x,
            "y": y,
            "speed": speed,
            "angle": angle,
            "owner": owner,
            "renderer": renderer,
        }
        return self._create_entity(config)

    def create_missile(
        self, x: float, y: float, target: Any, owner: str = "player", renderer: Optional[Callable] = None
    ):
        """Create a tracking missile with clean interface.

        Args:
            x: Initial X position
            y: Initial Y position
            target: Target object to track (must have rect.center attribute)
            owner: Owner type for tracking (default: "player")
            renderer: Optional graphics renderer for testing

        Returns:
            Configured TrackingMissile instance
        """
        config = {"projectile_type": "missile", "x": x, "y": y, "target": target, "owner": owner, "renderer": renderer}
        return self._create_entity(config)

    def create_from_preset(self, preset_name: str, x: float = 0, y: float = 0, **kwargs):
        """Create projectile from preset with position parameters.

        Args:
            preset_name: Name of the preset configuration
            x: Initial X position (required for clean interface)
            y: Initial Y position (required for clean interface)
            **kwargs: Additional parameters to override preset values

        Returns:
            Configured projectile instance
        """
        # Get base preset configuration
        preset = self.get_preset(preset_name)
        if preset is None:
            raise ValueError(f"Preset '{preset_name}' not found")
        preset_config = preset.copy()

        # Add position parameters
        preset_config.update({"x": x, "y": y})

        # Override with any additional parameters
        preset_config.update(kwargs)

        return self._create_entity(preset_config)
