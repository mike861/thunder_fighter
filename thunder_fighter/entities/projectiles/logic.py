"""
Pure logic classes for projectile calculations.

This module contains business logic classes that are completely independent
of graphics, UI, or I/O systems, following the logic/interface separation principle.
"""

import math
from typing import Any, Dict, Optional, Tuple


class Vector2:
    """Simple 2D vector implementation for pure mathematical calculations."""

    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalize_ip(self):
        length = self.length()
        if length > 0:
            self.x /= length
            self.y /= length


class BulletLogic:
    """Pure mathematical logic for bullet movement and trajectory calculation.

    This class contains no graphics dependencies and can be tested in isolation.
    All calculations are pure mathematical operations.
    """

    def __init__(self, x: float, y: float, speed: float = 10.0, angle: float = 0.0):
        """Initialize bullet logic with position and movement parameters.

        Args:
            x: Initial X coordinate
            y: Initial Y coordinate
            speed: Movement speed (pixels per update)
            angle: Movement angle in degrees (0 = straight up, positive = clockwise)
        """
        self.x = float(x)
        self.y = float(y)
        self.speed = float(speed)
        self.angle = float(angle)

        # Calculate velocity components from angle and speed
        rad_angle = math.radians(angle)
        self.speed_y = -self.speed * math.cos(rad_angle)  # Negative for upward movement
        self.speed_x = self.speed * math.sin(rad_angle)

    def update_position(self) -> Tuple[float, float]:
        """Update position based on velocity and return new coordinates.

        Returns:
            Tuple of (new_x, new_y) coordinates
        """
        self.x += self.speed_x
        self.y += self.speed_y
        return (self.x, self.y)

    def is_out_of_bounds(self, width: int, height: int) -> bool:
        """Check if bullet position is outside the given boundaries.

        Args:
            width: Screen/area width
            height: Screen/area height

        Returns:
            True if bullet is outside boundaries
        """
        return (
            self.y < 0  # Top boundary
            or self.x < 0  # Left boundary
            or self.x > width
        )  # Right boundary

    def get_position(self) -> Tuple[float, float]:
        """Get current position coordinates.

        Returns:
            Tuple of (x, y) coordinates
        """
        return (self.x, self.y)

    def get_velocity(self) -> Tuple[float, float]:
        """Get current velocity components.

        Returns:
            Tuple of (speed_x, speed_y) velocity components
        """
        return (self.speed_x, self.speed_y)


class TrackingAlgorithm:
    """Pure mathematical logic for tracking missile movement and target pursuit.

    This class contains no graphics dependencies and implements the core
    tracking algorithm using mathematical vector operations.
    """

    def __init__(self, start_x: float, start_y: float, speed: float = 8.0):
        """Initialize tracking algorithm with starting position and speed.

        Args:
            start_x: Initial X coordinate
            start_y: Initial Y coordinate
            speed: Movement speed (pixels per update)
        """
        self.position = Vector2(start_x, start_y)
        self.speed = float(speed)
        self.last_target_position: Optional[Tuple[float, float]] = None

    def calculate_movement(self, target_position: Optional[Tuple[float, float]]) -> Dict[str, Any]:
        """Calculate movement towards target position.

        Args:
            target_position: Target coordinates as (x, y) tuple, or None if no target

        Returns:
            Dictionary containing movement result:
            - "action": "move", "destroy", or "continue"
            - "new_position": (x, y) tuple if action is "move"
            - "angle": rotation angle in degrees if action is "move"
            - "distance_to_target": remaining distance if action is "move"
        """
        # Update target tracking
        if target_position is not None:
            self.last_target_position = target_position
            current_target = target_position
        elif self.last_target_position is not None:
            current_target = self.last_target_position
        else:
            return {"action": "destroy", "reason": "no_target"}

        # Calculate direction vector
        target_vector = Vector2(current_target[0], current_target[1])
        direction_vector = target_vector - self.position
        distance = direction_vector.length()

        # Check if close enough to target
        if distance < self.speed:
            return {"action": "destroy", "reason": "target_reached", "final_distance": distance}

        # Calculate new position
        direction_vector.normalize_ip()
        new_position = self.position + direction_vector * self.speed

        # Calculate rotation angle for graphics (matching original implementation)
        angle = math.degrees(math.atan2(-direction_vector.x, -direction_vector.y))

        # Update internal position
        self.position = new_position

        return {
            "action": "move",
            "new_position": (new_position.x, new_position.y),
            "angle": angle,
            "distance_to_target": distance - self.speed,
            "direction": (direction_vector.x, direction_vector.y),
        }

    def is_out_of_bounds(self, width: int, height: int) -> bool:
        """Check if missile position is outside the given boundaries.

        Args:
            width: Screen/area width
            height: Screen/area height

        Returns:
            True if missile is outside boundaries
        """
        return self.position.y < 0 or self.position.y > height or self.position.x < 0 or self.position.x > width

    def get_position(self) -> Tuple[float, float]:
        """Get current position coordinates.

        Returns:
            Tuple of (x, y) coordinates
        """
        return (self.position.x, self.position.y)

    def set_position(self, x: float, y: float) -> None:
        """Set position coordinates (for testing or initialization).

        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.position.x = float(x)
        self.position.y = float(y)
