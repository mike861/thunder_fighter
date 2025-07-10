"""
Boss Factory

This module provides a factory for creating boss entities with different
configurations and difficulty levels.
"""

from typing import Dict, Any
import pygame
from .entity_factory import ConfigurableEntityFactory
from thunder_fighter.entities.enemies.boss import Boss
from thunder_fighter.utils.logger import logger


class BossFactory(ConfigurableEntityFactory[Boss]):
    """Factory for creating boss entities."""
    
    def __init__(self):
        """Initialize the boss factory."""
        super().__init__(Boss)
        self._setup_default_presets()
        
        logger.info("BossFactory initialized")
    
    def _setup_default_presets(self):
        """Set up default boss configuration presets."""
        self.add_preset("standard", {
            'boss_level': 1,
            'game_level': 2,
            'health_multiplier': 1.0,
            'speed_multiplier': 1.0
        })
        
        self.add_preset("elite", {
            'boss_level': 2,
            'game_level': 5,
            'health_multiplier': 1.5,
            'speed_multiplier': 1.2
        })
    
    def _get_required_fields(self) -> list:
        """Get required fields for boss creation."""
        return ['all_sprites', 'boss_bullets', 'player']
    
    def _create_entity(self, config: Dict[str, Any]) -> Boss:
        """Create a boss entity."""
        boss_level = config.get('boss_level', 1)
        game_level = config.get('game_level', 2)
        all_sprites = config['all_sprites']
        boss_bullets = config['boss_bullets']
        player = config['player']
        
        return Boss(all_sprites, boss_bullets, boss_level, game_level, player)
    
    def _post_creation_setup(self, boss: Boss, config: Dict[str, Any]):
        """Perform post-creation setup on the boss."""
        # Apply multipliers
        health_multiplier = config.get('health_multiplier', 1.0)
        speed_multiplier = config.get('speed_multiplier', 1.0)
        
        if hasattr(boss, 'health'):
            boss.health = int(boss.health * health_multiplier)
        if hasattr(boss, 'max_health'):
            boss.max_health = int(boss.max_health * health_multiplier)
        if hasattr(boss, 'speed'):
            boss.speed = int(boss.speed * speed_multiplier) 