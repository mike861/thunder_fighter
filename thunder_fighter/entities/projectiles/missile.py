from typing import Callable, Optional

import pygame

from thunder_fighter.constants import HEIGHT, WIDTH
from thunder_fighter.entities.projectiles.logic import TrackingAlgorithm
from thunder_fighter.graphics.renderers import create_tracking_missile


class TrackingMissile(pygame.sprite.Sprite):
    """
    A missile that tracks a designated enemy with logic/graphics separation.
    """

    def __init__(self, x, y, target, renderer: Optional[Callable[[], pygame.Surface]] = None):
        """Initialize tracking missile with optional renderer injection.

        Args:
            x: Initial X position
            y: Initial Y position
            target: Target object to track (must have rect.center attribute)
            renderer: Optional graphics renderer function (for testing/injection)
        """
        super().__init__()

        # Initialize pure business logic
        self.algorithm = TrackingAlgorithm(x, y, speed=8)

        # Initialize graphics (with optional injection for testing)
        self._setup_graphics(x, y, renderer)

        # Target tracking
        self.target = target
        self.angle = 0.0

        # Initialize target position in algorithm
        if self.target and hasattr(self.target, "rect"):
            initial_target_pos = self.target.rect.center
            self.algorithm.last_target_position = initial_target_pos

    def _setup_graphics(self, x: float, y: float, renderer: Optional[Callable[[], pygame.Surface]] = None) -> None:
        """Setup graphics components with optional renderer injection."""
        # Use injected renderer or default
        graphics_renderer = renderer or create_tracking_missile
        self.image = graphics_renderer()
        self.original_image = self.image
        self.rect = self.image.get_rect(center=(int(x), int(y)))

    def update(self):
        """
        Update missile position and angle using algorithm layer.
        It will track a living target, or continue towards the target's
        last known position if it has been destroyed.
        """
        # Determine current target position
        target_pos = None
        if self.target and hasattr(self.target, "alive") and self.target.alive():
            # If target is alive, use its current position
            target_pos = self.target.rect.center

        # Calculate movement using pure algorithm
        movement_result = self.algorithm.calculate_movement(target_pos)

        # Handle movement result
        if movement_result["action"] == "destroy":
            self.kill()
            return
        elif movement_result["action"] == "move":
            # Update graphics position
            new_x, new_y = movement_result["new_position"]
            self.rect.centerx = int(new_x)
            self.rect.centery = int(new_y)

            # Update graphics rotation
            self.angle = movement_result["angle"]
            self.image = pygame.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)

        # Kill if it goes off-screen using algorithm boundary check
        if self.algorithm.is_out_of_bounds(WIDTH, HEIGHT):
            self.kill()
