"""
Tests for pure projectile logic classes.

These tests validate the mathematical algorithms and business logic
without any pygame or graphics dependencies.
"""

import math

from thunder_fighter.entities.projectiles.logic import BulletLogic, TrackingAlgorithm


class TestBulletLogic:
    """Test BulletLogic pure mathematical calculations."""

    def test_initialization_straight_up(self):
        """Test bullet logic initializes correctly for straight upward movement."""
        logic = BulletLogic(x=100, y=200, speed=10, angle=0)

        assert logic.x == 100.0
        assert logic.y == 200.0
        assert logic.speed == 10.0
        assert logic.angle == 0.0
        assert logic.speed_x == 0.0
        assert logic.speed_y == -10.0  # Negative for upward movement

    def test_initialization_angled_movement(self):
        """Test bullet logic initializes correctly for angled movement."""
        logic = BulletLogic(x=50, y=100, speed=10, angle=45)

        assert logic.x == 50.0
        assert logic.y == 100.0
        assert logic.speed == 10.0
        assert logic.angle == 45.0

        # 45 degree angle should give equal x and y components
        expected_component = 10 * math.sin(math.radians(45))
        assert abs(logic.speed_x - expected_component) < 0.001
        assert abs(logic.speed_y - (-10 * math.cos(math.radians(45)))) < 0.001

    def test_position_update_straight(self):
        """Test position updates correctly for straight movement."""
        logic = BulletLogic(x=100, y=200, speed=5, angle=0)

        # Update position once
        new_x, new_y = logic.update_position()

        assert new_x == 100.0  # No horizontal movement
        assert new_y == 195.0  # Moved up by 5 pixels
        assert logic.x == 100.0
        assert logic.y == 195.0

    def test_position_update_angled(self):
        """Test position updates correctly for angled movement."""
        logic = BulletLogic(x=0, y=0, speed=10, angle=90)  # 90 degrees = right

        # Update position once
        new_x, new_y = logic.update_position()

        assert abs(new_x - 10.0) < 0.001  # Moved right by ~10 pixels
        assert abs(new_y - 0.0) < 0.001  # No vertical movement for 90 degrees

    def test_multiple_position_updates(self):
        """Test multiple position updates accumulate correctly."""
        logic = BulletLogic(x=0, y=100, speed=2, angle=0)

        # Update 3 times
        logic.update_position()  # y = 98
        logic.update_position()  # y = 96
        x, y = logic.update_position()  # y = 94

        assert x == 0.0
        assert y == 94.0

    def test_boundary_checking_inside(self):
        """Test boundary checking when bullet is inside bounds."""
        logic = BulletLogic(x=50, y=50, speed=5, angle=0)

        assert not logic.is_out_of_bounds(width=100, height=100)

    def test_boundary_checking_outside_top(self):
        """Test boundary checking when bullet goes above screen."""
        logic = BulletLogic(x=50, y=-1, speed=5, angle=0)

        assert logic.is_out_of_bounds(width=100, height=100)

    def test_boundary_checking_outside_left(self):
        """Test boundary checking when bullet goes left of screen."""
        logic = BulletLogic(x=-1, y=50, speed=5, angle=0)

        assert logic.is_out_of_bounds(width=100, height=100)

    def test_boundary_checking_outside_right(self):
        """Test boundary checking when bullet goes right of screen."""
        logic = BulletLogic(x=101, y=50, speed=5, angle=0)

        assert logic.is_out_of_bounds(width=100, height=100)

    def test_get_position(self):
        """Test position getter returns correct coordinates."""
        logic = BulletLogic(x=75, y=125, speed=3, angle=30)

        x, y = logic.get_position()
        assert x == 75.0
        assert y == 125.0

    def test_get_velocity(self):
        """Test velocity getter returns correct components."""
        logic = BulletLogic(x=0, y=0, speed=8, angle=60)

        speed_x, speed_y = logic.get_velocity()
        expected_x = 8 * math.sin(math.radians(60))
        expected_y = -8 * math.cos(math.radians(60))

        assert abs(speed_x - expected_x) < 0.001
        assert abs(speed_y - expected_y) < 0.001


class TestTrackingAlgorithm:
    """Test TrackingAlgorithm pure mathematical calculations."""

    def test_initialization(self):
        """Test tracking algorithm initializes correctly."""
        algorithm = TrackingAlgorithm(start_x=10, start_y=20, speed=5)

        assert algorithm.position.x == 10.0
        assert algorithm.position.y == 20.0
        assert algorithm.speed == 5.0
        assert algorithm.last_target_position is None

    def test_movement_with_target(self):
        """Test movement calculation when target is available."""
        algorithm = TrackingAlgorithm(start_x=0, start_y=0, speed=10)

        # Target at (10, 0) - straight right
        result = algorithm.calculate_movement(target_position=(10, 0))

        assert result["action"] == "move"
        assert abs(result["new_position"][0] - 10.0) < 0.001
        assert abs(result["new_position"][1] - 0.0) < 0.001
        # Original implementation uses atan2(-direction_vector.x, -direction_vector.y)
        # For direction (1, 0), this gives atan2(-1, 0) = -90 degrees
        assert abs(result["angle"] - (-90.0)) < 0.001

    def test_movement_diagonal_target(self):
        """Test movement calculation for diagonal target."""
        algorithm = TrackingAlgorithm(start_x=0, start_y=0, speed=5)

        # Target at (3, 4) - distance is 5, so should move exactly to target
        result = algorithm.calculate_movement(target_position=(3, 4))

        assert result["action"] == "move"
        # Should move exactly to target since distance equals speed
        assert abs(result["new_position"][0] - 3.0) < 0.001
        assert abs(result["new_position"][1] - 4.0) < 0.001

    def test_movement_close_target_destruction(self):
        """Test missile destroys when very close to target."""
        algorithm = TrackingAlgorithm(start_x=0, start_y=0, speed=10)

        # Target very close (distance < speed)
        result = algorithm.calculate_movement(target_position=(5, 0))

        assert result["action"] == "destroy"
        assert result["reason"] == "target_reached"
        assert result["final_distance"] == 5.0

    def test_movement_no_target_destruction(self):
        """Test missile destroys when no target available."""
        algorithm = TrackingAlgorithm(start_x=0, start_y=0, speed=5)

        result = algorithm.calculate_movement(target_position=None)

        assert result["action"] == "destroy"
        assert result["reason"] == "no_target"

    def test_last_target_position_tracking(self):
        """Test algorithm remembers last target position."""
        algorithm = TrackingAlgorithm(start_x=0, start_y=0, speed=3)

        # First movement with target
        result1 = algorithm.calculate_movement(target_position=(10, 0))
        assert result1["action"] == "move"

        # Second movement without target (should use last position)
        result2 = algorithm.calculate_movement(target_position=None)
        assert result2["action"] == "move"
        # Should continue toward last known position

    def test_boundary_checking_inside(self):
        """Test boundary checking when missile is inside bounds."""
        algorithm = TrackingAlgorithm(start_x=50, start_y=50, speed=5)

        assert not algorithm.is_out_of_bounds(width=100, height=100)

    def test_boundary_checking_outside(self):
        """Test boundary checking when missile is outside bounds."""
        algorithm = TrackingAlgorithm(start_x=-1, start_y=50, speed=5)

        assert algorithm.is_out_of_bounds(width=100, height=100)

    def test_position_getter_setter(self):
        """Test position getter and setter methods."""
        algorithm = TrackingAlgorithm(start_x=10, start_y=20, speed=5)

        # Test getter
        x, y = algorithm.get_position()
        assert x == 10.0
        assert y == 20.0

        # Test setter
        algorithm.set_position(30, 40)
        x, y = algorithm.get_position()
        assert x == 30.0
        assert y == 40.0

    def test_complex_tracking_scenario(self):
        """Test complex tracking scenario with multiple movements."""
        algorithm = TrackingAlgorithm(start_x=0, start_y=0, speed=2)

        # Move toward (6, 8) - distance 10, should take 5 steps
        target = (6, 8)

        for _ in range(4):  # Move 4 times, should not reach target yet
            result = algorithm.calculate_movement(target_position=target)
            assert result["action"] == "move"

        # 5th move should reach target
        result = algorithm.calculate_movement(target_position=target)
        assert result["action"] == "destroy"
        assert result["reason"] == "target_reached"

    def test_angle_calculation_accuracy(self):
        """Test angle calculation for various directions (matching original implementation)."""
        algorithm = TrackingAlgorithm(start_x=0, start_y=0, speed=1)

        # Test cases with expected angles based on atan2(-direction_vector.x, -direction_vector.y)
        test_cases = [
            ((0, -1), 0.0),  # Straight up: atan2(0, 1) = 0°
            ((1, 0), -90.0),  # Straight right: atan2(-1, 0) = -90°
            ((0, 1), 180.0),  # Straight down: atan2(0, -1) = ±180°
            ((-1, 0), 90.0),  # Straight left: atan2(1, 0) = 90°
        ]

        for target_pos, expected_angle in test_cases:
            algorithm.set_position(0, 0)  # Reset position
            result = algorithm.calculate_movement(target_position=target_pos)

            if result["action"] == "move":
                actual_angle = result["angle"]
                # Handle angle wraparound for comparison
                angle_diff = abs(actual_angle - expected_angle)
                if angle_diff > 180:
                    angle_diff = 360 - angle_diff
                assert angle_diff < 1.0, f"Target {target_pos}: expected {expected_angle}°, got {actual_angle}°"
