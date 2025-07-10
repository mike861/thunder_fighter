import unittest
from unittest.mock import MagicMock, patch
import pygame

# Since the test runner has path issues, we add the root manually.
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from thunder_fighter.entities.items.items import create_random_item, HealthItem, BulletSpeedItem, BulletPathItem, PlayerSpeedItem, WingmanItem
from thunder_fighter.graphics.renderers import create_wingman_item

# A real pygame surface to be returned by mocks
MOCK_SURFACE = pygame.Surface((10, 10))

class TestItems(unittest.TestCase):

    def setUp(self):
        """Set up common mock objects for tests."""
        self.mock_player = MagicMock()
        self.mock_player.health = 50
        self.mock_player.speed = 5
        self.mock_player.bullet_speed = 10
        self.mock_player.bullet_paths = 1
        self.mock_player.wingmen_list = []
        
        self.mock_sprites_group = MagicMock()
        self.mock_items_group = MagicMock()

    @patch('random.choices')
    @patch('thunder_fighter.sprites.items.create_health_item', return_value=MOCK_SURFACE)
    @patch('thunder_fighter.sprites.items.create_bullet_speed_item', return_value=MOCK_SURFACE)
    @patch('thunder_fighter.sprites.items.create_bullet_path_item', return_value=MOCK_SURFACE)
    @patch('thunder_fighter.sprites.items.create_player_speed_item', return_value=MOCK_SURFACE)
    @patch('thunder_fighter.sprites.items.create_wingman_item', return_value=MOCK_SURFACE)
    def test_create_random_item_logic(self, mock_create_wingman, mock_create_player_speed, mock_create_bullet_path, mock_create_bullet_speed, mock_create_health, mock_choices):
        """Test that create_random_item correctly creates items based on weighted choices."""
        
        def run_test(item_class, game_time, game_level):
            mock_choices.return_value = [item_class]
            item = create_random_item(game_time, game_level, self.mock_sprites_group, self.mock_items_group, self.mock_player)
            
            self.assertIsInstance(item, item_class)
            self.mock_sprites_group.add.assert_called_with(item)
            self.mock_items_group.add.assert_called_with(item)

        # Test creation for each item type
        run_test(HealthItem, game_time=1, game_level=1)
        run_test(PlayerSpeedItem, game_time=3, game_level=2)
        run_test(BulletSpeedItem, game_time=5, game_level=3)
        run_test(BulletPathItem, game_time=8, game_level=4)
        run_test(WingmanItem, game_time=10, game_level=5)

    def test_wingman_item_creation_level_gate(self):
        """Test that WingmanItem is only created at or after game level 3."""
        
        # At level 2, it should NOT be created. 
        # The internal logic should now correctly assign a weight of 0.
        item = create_random_item(5, 2, self.mock_sprites_group, self.mock_items_group, self.mock_player)
        self.assertNotIsInstance(item, WingmanItem, "WingmanItem was created at game level 2")

        # At level 3, it SHOULD be possible to create one.
        # We patch the item creation function to avoid rendering issues.
        with patch('thunder_fighter.sprites.items.create_wingman_item', return_value=MOCK_SURFACE):
            # To guarantee a WingmanItem, we can temporarily rig the weights
            with patch('random.choices', return_value=[WingmanItem]):
                 item = create_random_item(5, 3, self.mock_sprites_group, self.mock_items_group, self.mock_player)
                 self.assertIsInstance(item, WingmanItem, "WingmanItem was not created at game level 3")

if __name__ == '__main__':
    unittest.main() 