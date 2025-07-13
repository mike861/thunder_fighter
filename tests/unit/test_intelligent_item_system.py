"""
Tests for the intelligent item weight system.

This module tests the dynamic item weight calculation and selection logic
implemented in the ItemFactory.
"""

import unittest
from unittest.mock import Mock, patch

from thunder_fighter.constants import ITEM_WEIGHT_SYSTEM, PLAYER_HEALTH
from thunder_fighter.entities.items.item_factory import ItemFactory


class TestIntelligentItemSystem(unittest.TestCase):
    """Test intelligent item weight system functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = ItemFactory()
        self.mock_all_sprites = Mock()
        self.mock_items = Mock()

        # Create a mock player with configurable attributes
        self.mock_player = Mock()
        self.mock_player.health = PLAYER_HEALTH  # Full health by default
        self.mock_player.bullet_speed = 10
        self.mock_player.bullet_paths = 1
        self.mock_player.speed = 6
        self.mock_player.wingmen_list = []

    def test_health_based_weight_adaptation_critical(self):
        """Test health-based weight adaptation for critical health."""
        # Set player to critical health (20%)
        self.mock_player.health = PLAYER_HEALTH * 0.2

        weights = self.factory._calculate_dynamic_weights(self.mock_player, game_level=1)

        # Health item weight should be boosted significantly
        base_health_weight = ITEM_WEIGHT_SYSTEM["BASE_WEIGHTS"]["health"]
        critical_multiplier = ITEM_WEIGHT_SYSTEM["HEALTH_ADAPTATION"]["critical_multiplier"]
        expected_health_weight = base_health_weight * critical_multiplier

        self.assertEqual(weights["health"], expected_health_weight)

    def test_health_based_weight_adaptation_injured(self):
        """Test health-based weight adaptation for injured state."""
        # Set player to injured health (50%)
        self.mock_player.health = PLAYER_HEALTH * 0.5

        weights = self.factory._calculate_dynamic_weights(self.mock_player, game_level=1)

        # Health item weight should be moderately boosted
        base_health_weight = ITEM_WEIGHT_SYSTEM["BASE_WEIGHTS"]["health"]
        injured_multiplier = ITEM_WEIGHT_SYSTEM["HEALTH_ADAPTATION"]["injured_multiplier"]
        expected_health_weight = base_health_weight * injured_multiplier

        self.assertEqual(weights["health"], expected_health_weight)

    def test_health_based_weight_adaptation_healthy(self):
        """Test health-based weight adaptation for healthy state."""
        # Set player to healthy health (90%)
        self.mock_player.health = PLAYER_HEALTH * 0.9

        weights = self.factory._calculate_dynamic_weights(self.mock_player, game_level=1)

        # Health item weight should be reduced
        base_health_weight = ITEM_WEIGHT_SYSTEM["BASE_WEIGHTS"]["health"]
        healthy_multiplier = ITEM_WEIGHT_SYSTEM["HEALTH_ADAPTATION"]["healthy_multiplier"]
        expected_health_weight = base_health_weight * healthy_multiplier

        self.assertEqual(weights["health"], expected_health_weight)

    def test_level_based_wingman_gating_early_levels(self):
        """Test wingman item gating for early levels."""
        weights = self.factory._calculate_dynamic_weights(self.mock_player, game_level=1)

        # Wingman should be disabled for levels below minimum
        self.assertEqual(weights["wingman"], 0)

        weights = self.factory._calculate_dynamic_weights(self.mock_player, game_level=2)
        self.assertEqual(weights["wingman"], 0)

    def test_level_based_wingman_gating_eligible_levels(self):
        """Test wingman item availability for eligible levels."""
        weights = self.factory._calculate_dynamic_weights(self.mock_player, game_level=3)

        # Wingman should be available from level 3+
        base_wingman_weight = ITEM_WEIGHT_SYSTEM["BASE_WEIGHTS"]["wingman"]
        self.assertEqual(weights["wingman"], base_wingman_weight)

    def test_ability_cap_detection_bullet_speed(self):
        """Test ability cap detection for bullet speed."""
        # Set bullet speed to maximum
        self.mock_player.bullet_speed = ITEM_WEIGHT_SYSTEM["ABILITY_CAPS"]["bullet_speed_max"]

        weights = self.factory._calculate_dynamic_weights(self.mock_player, game_level=1)

        # Bullet speed item should be disabled
        self.assertEqual(weights["bullet_speed"], 0)

    def test_ability_cap_detection_bullet_paths(self):
        """Test ability cap detection for bullet paths."""
        # Set bullet paths to maximum
        self.mock_player.bullet_paths = ITEM_WEIGHT_SYSTEM["ABILITY_CAPS"]["bullet_paths_max"]

        weights = self.factory._calculate_dynamic_weights(self.mock_player, game_level=1)

        # Bullet path item should be disabled
        self.assertEqual(weights["bullet_path"], 0)

    def test_ability_cap_detection_wingmen(self):
        """Test ability cap detection for wingmen."""
        # Set wingmen to maximum
        self.mock_player.wingmen_list = [Mock(), Mock()]  # Maximum is 2

        weights = self.factory._calculate_dynamic_weights(self.mock_player, game_level=3)

        # Wingman item should be disabled
        self.assertEqual(weights["wingman"], 0)

    @patch("time.time")
    def test_duplicate_prevention_recent_item(self, mock_time):
        """Test duplicate prevention for recently spawned items."""
        # Set up time sequence
        base_time = 1000.0
        mock_time.return_value = base_time

        # Simulate recent health item spawn
        self.factory._last_spawn_times["health"] = base_time - 5  # 5 seconds ago

        # Advance time slightly
        mock_time.return_value = base_time

        weights = self.factory._calculate_dynamic_weights(self.mock_player, game_level=1)

        # Health item weight should be penalized by both health state and duplicate prevention
        base_health_weight = ITEM_WEIGHT_SYSTEM["BASE_WEIGHTS"]["health"]
        healthy_multiplier = ITEM_WEIGHT_SYSTEM["HEALTH_ADAPTATION"]["healthy_multiplier"]  # Player is at full health
        penalty_multiplier = ITEM_WEIGHT_SYSTEM["DUPLICATE_PREVENTION"]["burst_penalty_multiplier"]
        expected_health_weight = base_health_weight * healthy_multiplier * penalty_multiplier

        self.assertAlmostEqual(weights["health"], expected_health_weight, places=5)

    def test_consecutive_item_prevention(self):
        """Test prevention of too many consecutive same items."""
        # Set up consecutive item scenario
        self.factory._last_item_type = "bullet_speed"
        self.factory._consecutive_count = 2  # At limit

        weights = self.factory._calculate_dynamic_weights(self.mock_player, game_level=1)

        # Bullet speed weight should be penalized
        base_bullet_speed_weight = ITEM_WEIGHT_SYSTEM["BASE_WEIGHTS"]["bullet_speed"]
        penalty_multiplier = ITEM_WEIGHT_SYSTEM["DUPLICATE_PREVENTION"]["burst_penalty_multiplier"]
        expected_bullet_speed_weight = base_bullet_speed_weight * penalty_multiplier

        self.assertEqual(weights["bullet_speed"], expected_bullet_speed_weight)

    def test_weighted_choice_basic_functionality(self):
        """Test weighted choice selection logic."""
        weights = {"health": 50, "bullet_speed": 30, "bullet_path": 20}

        # Test multiple selections to verify distribution (basic smoke test)
        results = []
        for _ in range(100):
            result = self.factory._weighted_choice(weights)
            self.assertIn(result, weights.keys())
            results.append(result)

        # Should have results from all categories
        unique_results = set(results)
        self.assertTrue(len(unique_results) > 1, "Should select from multiple categories")

    def test_weighted_choice_zero_weights(self):
        """Test weighted choice with zero weights."""
        weights = {"health": 0, "bullet_speed": 0, "bullet_path": 0}

        result = self.factory._weighted_choice(weights)
        self.assertIsNone(result)

    def test_weighted_choice_single_valid_item(self):
        """Test weighted choice with single valid item."""
        weights = {"health": 50, "bullet_speed": 0, "bullet_path": 0}

        result = self.factory._weighted_choice(weights)
        self.assertEqual(result, "health")

    @patch("thunder_fighter.entities.items.item_factory.time.time")
    def test_create_random_item_with_tracking(self, mock_time):
        """Test create_random_item with tracking updates."""
        mock_time.return_value = 1000.0

        # Mock the preset creation to return a mock item
        mock_item = Mock()
        with patch.object(self.factory, "create_from_preset", return_value=mock_item):
            result = self.factory.create_random_item(
                self.mock_all_sprites, self.mock_items, self.mock_player, game_level=1
            )

        # Should return an item
        self.assertIsNotNone(result)

        # Should update tracking data
        self.assertIsNotNone(self.factory._last_item_type)
        self.assertEqual(self.factory._consecutive_count, 1)

    def test_comprehensive_weight_calculation_scenario(self):
        """Test comprehensive scenario with multiple factors."""
        # Set up complex scenario: low health, high level, some maxed abilities
        self.mock_player.health = PLAYER_HEALTH * 0.25  # Critical health
        self.mock_player.bullet_speed = ITEM_WEIGHT_SYSTEM["ABILITY_CAPS"]["bullet_speed_max"]  # Maxed
        self.mock_player.wingmen_list = []  # No wingmen

        weights = self.factory._calculate_dynamic_weights(self.mock_player, game_level=5)

        # Health should be heavily boosted
        base_health_weight = ITEM_WEIGHT_SYSTEM["BASE_WEIGHTS"]["health"]
        critical_multiplier = ITEM_WEIGHT_SYSTEM["HEALTH_ADAPTATION"]["critical_multiplier"]
        expected_health_weight = base_health_weight * critical_multiplier
        self.assertEqual(weights["health"], expected_health_weight)

        # Bullet speed should be disabled (maxed out)
        self.assertEqual(weights["bullet_speed"], 0)

        # Wingman should be available (level 5 > 3)
        self.assertEqual(weights["wingman"], ITEM_WEIGHT_SYSTEM["BASE_WEIGHTS"]["wingman"])


if __name__ == "__main__":
    unittest.main()
