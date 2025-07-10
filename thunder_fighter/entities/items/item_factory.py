"""
Item Factory

This module provides a factory for creating item entities with different
types and configurations.
"""

import random
from typing import Dict, Any
import pygame
from ..entity_factory import ConfigurableEntityFactory
from thunder_fighter.entities.items.items import HealthItem, BulletSpeedItem, BulletPathItem, PlayerSpeedItem, WingmanItem
from thunder_fighter.utils.logger import logger


class ItemFactory(ConfigurableEntityFactory):
    """Factory for creating item entities."""
    
    def __init__(self):
        """Initialize the item factory."""
        super().__init__(HealthItem)  # Default type, will be overridden
        self._item_types = {
            'health': HealthItem,
            'bullet_speed': BulletSpeedItem,
            'bullet_path': BulletPathItem,
            'player_speed': PlayerSpeedItem,
            'wingman': WingmanItem
        }
        self._setup_default_presets()
        
        logger.info("ItemFactory initialized")
    
    def _setup_default_presets(self):
        """Set up default item configuration presets."""
        for item_type in self._item_types.keys():
            self.add_preset(item_type, {
                'item_type': item_type,
                'spawn_position': None
            })
    
    def _get_required_fields(self) -> list:
        """Get required fields for item creation."""
        return ['all_sprites', 'items', 'player']
    
    def _create_entity(self, config: Dict[str, Any]):
        """Create an item entity."""
        item_type = config.get('item_type', 'health')
        all_sprites = config['all_sprites']
        items = config['items']
        player = config['player']
        
        item_class = self._item_types.get(item_type, HealthItem)
        # Create item instance without parameters
        item = item_class()
        
        # Add to sprite groups
        all_sprites.add(item)
        items.add(item)
        
        return item
    
    def create_random_item(self, all_sprites: pygame.sprite.Group,
                          items: pygame.sprite.Group, player):
        """Create a random item."""
        item_type = random.choice(list(self._item_types.keys()))
        return self.create_from_preset(
            item_type,
            all_sprites=all_sprites,
            items=items,
            player=player
        ) 