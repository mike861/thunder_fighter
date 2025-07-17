"""
Base Entity Class Definitions

Defines the base class and common interfaces for all game objects.
"""

from abc import ABC, abstractmethod
from typing import Tuple

import pygame


class GameObject(pygame.sprite.Sprite, ABC):
    """Base Game Object Class"""

    def __init__(self, x: float, y: float, width: int, height: int):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.health = 1
        self.max_health = 1
        self.active = True

        # Create base rect
        self.rect = pygame.Rect(int(x), int(y), width, height)

        # Base image (subclasses need to set specific image)
        self.image = None

    @abstractmethod
    def update(self, dt: float):
        """Updates the game object's state."""
        pass

    @abstractmethod
    def render(self, screen: pygame.Surface):
        """Renders the game object."""
        pass

    def take_damage(self, damage: int) -> bool:
        """Takes damage, returns whether destroyed."""
        self.health -= damage
        return self.health <= 0

    def heal(self, amount: int):
        """Heals health points."""
        self.health = min(self.health + amount, self.max_health)

    def set_position(self, x: float, y: float):
        """Sets position."""
        self.x = x
        self.y = y
        self.rect.x = int(x)
        self.rect.y = int(y)

    def get_position(self) -> Tuple[float, float]:
        """Gets position."""
        return (self.x, self.y)

    def set_velocity(self, velocity_x: float, velocity_y: float):
        """Sets velocity."""
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y

    def get_velocity(self) -> Tuple[float, float]:
        """Gets velocity."""
        return (self.velocity_x, self.velocity_y)


class Entity(GameObject):
    """Concrete Entity Class, provides default implementation"""

    def update(self, dt: float):
        """Default update implementation."""
        # Update position
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Update sprite's built-in update (for animation, etc.)
        # Note: pygame.sprite.Sprite.update() doesn't require dt parameter
        if hasattr(pygame.sprite.Sprite, "update"):
            pygame.sprite.Sprite.update(self)

    def render(self, screen: pygame.Surface):
        """Default render implementation."""
        if hasattr(self, "image") and hasattr(self, "rect") and self.image:
            screen.blit(self.image, self.rect)


class EntityFactory(ABC):
    """Base Entity Factory Class"""

    @abstractmethod
    def create(self, *args, **kwargs) -> GameObject:
        """Creates an entity instance."""
        pass

    def create_batch(self, count: int, *args, **kwargs) -> list:
        """Creates entities in batch."""
        entities = []
        for _i in range(count):
            entity = self.create(*args, **kwargs)
            entities.append(entity)
        return entities


class MovableEntity(Entity):
    """Base class for movable entities"""

    def __init__(self, x: float, y: float, width: int, height: int, speed: float = 100.0):
        super().__init__(x, y, width, height)
        self.speed = speed
        self.direction_x = 0.0
        self.direction_y = 0.0

    def set_direction(self, direction_x: float, direction_y: float):
        """Sets movement direction (normalized vector)."""
        self.direction_x = direction_x
        self.direction_y = direction_y

        # Calculate velocity based on direction and speed
        self.velocity_x = self.direction_x * self.speed
        self.velocity_y = self.direction_y * self.speed

    def move_towards(self, target_x: float, target_y: float):
        """Moves towards a target."""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = (dx * dx + dy * dy) ** 0.5

        if distance > 0:
            self.set_direction(dx / distance, dy / distance)


class LivingEntity(MovableEntity):
    """Base class for living entities"""

    def __init__(self, x: float, y: float, width: int, height: int, speed: float = 100.0, max_health: int = 100):
        super().__init__(x, y, width, height, speed)
        self.max_health = max_health
        self.health = max_health
        self.is_alive = True

    def take_damage(self, damage: int) -> bool:
        """Takes damage, returns whether dead."""
        if not self.is_alive:
            return True

        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            self.on_death()
            return True

        self.on_damage_taken(damage)
        return False

    def heal(self, amount: int):
        """Heals health points."""
        if self.is_alive:
            self.health = min(self.health + amount, self.max_health)
            self.on_heal(amount)

    def on_damage_taken(self, damage: int):
        """Callback when damage is taken."""
        pass

    def on_heal(self, amount: int):
        """Callback when healed."""
        pass

    def on_death(self):
        """Callback when dead."""
        self.active = False
        if hasattr(self, "kill"):
            self.kill()

    def get_health_percentage(self) -> float:
        """Gets health percentage."""
        if self.max_health <= 0:
            return 0.0
        return self.health / self.max_health
