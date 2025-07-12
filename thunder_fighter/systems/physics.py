"""
Physics System

Manages physics-related logic in the game: movement, boundary detection, velocity control, etc.
"""

from typing import Dict, List, Tuple

from thunder_fighter.utils.logger import logger


class PhysicsSystem:
    """Physics System Class"""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.gravity = 0  # Space games usually have no gravity

        # Boundary settings
        self.boundary_margins = {"left": -50, "right": screen_width + 50, "top": -100, "bottom": screen_height + 50}

        logger.info(f"Physics system initialized: {screen_width}x{screen_height}")

    def update_movement(self, entities: List, dt: float):
        """Updates the movement of all entities."""
        for entity in entities:
            if hasattr(entity, "rect") and hasattr(entity, "velocity_x"):
                self._update_entity_movement(entity, dt)
                self._check_boundaries(entity)

    def _update_entity_movement(self, entity, dt: float):
        """Updates the movement of a single entity."""
        try:
            # Update position
            if hasattr(entity, "velocity_x"):
                entity.rect.x += entity.velocity_x * dt
            if hasattr(entity, "velocity_y"):
                entity.rect.y += entity.velocity_y * dt

            # If the entity has a custom physics update method, call it
            if hasattr(entity, "update_physics"):
                entity.update_physics(dt)

        except Exception as e:
            logger.error(f"Error updating entity movement: {e}")

    def _check_boundaries(self, entity):
        """Checks boundaries."""
        try:
            if not hasattr(entity, "rect"):
                return

            # Check if out of bounds
            out_of_bounds = False

            if entity.rect.right < self.boundary_margins["left"]:
                out_of_bounds = True
            elif entity.rect.left > self.boundary_margins["right"]:
                out_of_bounds = True
            elif entity.rect.bottom < self.boundary_margins["top"]:
                out_of_bounds = True
            elif entity.rect.top > self.boundary_margins["bottom"]:
                out_of_bounds = True

            # If out of bounds, mark for deletion
            if out_of_bounds:
                if hasattr(entity, "kill"):
                    entity.kill()
                elif hasattr(entity, "active"):
                    entity.active = False

        except Exception as e:
            logger.error(f"Error checking boundaries for entity: {e}")

    def apply_force(self, entity, force_x: float, force_y: float):
        """Applies a force to an entity."""
        try:
            if hasattr(entity, "velocity_x"):
                entity.velocity_x += force_x
            if hasattr(entity, "velocity_y"):
                entity.velocity_y += force_y

        except Exception as e:
            logger.error(f"Error applying force to entity: {e}")

    def set_velocity(self, entity, velocity_x: float, velocity_y: float):
        """Sets the velocity of an entity."""
        try:
            if hasattr(entity, "velocity_x"):
                entity.velocity_x = velocity_x
            if hasattr(entity, "velocity_y"):
                entity.velocity_y = velocity_y

        except Exception as e:
            logger.error(f"Error setting velocity for entity: {e}")

    def check_collision_with_boundaries(self, entity) -> Dict[str, bool]:
        """Checks for collisions with boundaries."""
        collisions = {"left": False, "right": False, "top": False, "bottom": False}

        try:
            if not hasattr(entity, "rect"):
                return collisions

            if entity.rect.left <= 0:
                collisions["left"] = True
            if entity.rect.right >= self.screen_width:
                collisions["right"] = True
            if entity.rect.top <= 0:
                collisions["top"] = True
            if entity.rect.bottom >= self.screen_height:
                collisions["bottom"] = True

        except Exception as e:
            logger.error(f"Error checking boundary collisions: {e}")

        return collisions

    def constrain_to_screen(self, entity):
        """Constrains an entity within the screen."""
        try:
            if not hasattr(entity, "rect"):
                return

            # Constrain within screen boundaries
            if entity.rect.left < 0:
                entity.rect.left = 0
            if entity.rect.right > self.screen_width:
                entity.rect.right = self.screen_width
            if entity.rect.top < 0:
                entity.rect.top = 0
            if entity.rect.bottom > self.screen_height:
                entity.rect.bottom = self.screen_height

        except Exception as e:
            logger.error(f"Error constraining entity to screen: {e}")

    def calculate_distance(self, entity1, entity2) -> float:
        """Calculates the distance between two entities."""
        try:
            if not (hasattr(entity1, "rect") and hasattr(entity2, "rect")):
                return float("inf")

            center1 = entity1.rect.center
            center2 = entity2.rect.center

            dx = center1[0] - center2[0]
            dy = center1[1] - center2[1]

            return (dx * dx + dy * dy) ** 0.5

        except Exception as e:
            logger.error(f"Error calculating distance: {e}")
            return float("inf")

    def get_direction_vector(self, from_entity, to_entity) -> Tuple[float, float]:
        """Gets the direction vector from one entity to another."""
        try:
            if not (hasattr(from_entity, "rect") and hasattr(to_entity, "rect")):
                return (0.0, 0.0)

            from_center = from_entity.rect.center
            to_center = to_entity.rect.center

            dx = to_center[0] - from_center[0]
            dy = to_center[1] - from_center[1]

            # Normalize
            distance = (dx * dx + dy * dy) ** 0.5
            if distance > 0:
                return (dx / distance, dy / distance)
            else:
                return (0.0, 0.0)

        except Exception as e:
            logger.error(f"Error calculating direction vector: {e}")
            return (0.0, 0.0)

    def update_screen_size(self, width: int, height: int):
        """Updates the screen size."""
        self.screen_width = width
        self.screen_height = height

        # Update boundaries
        self.boundary_margins.update({"right": width + 50, "bottom": height + 50})

        logger.info(f"Physics system screen size updated: {width}x{height}")

    def reset(self):
        """Resets the physics system."""
        logger.info("Physics system reset")
