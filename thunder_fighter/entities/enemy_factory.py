"""
Enemy Factory

This module provides a factory for creating enemy entities with different
configurations, difficulty levels, and behavior patterns.
"""

import random
from typing import Dict, Any
import pygame
from .entity_factory import ConfigurableEntityFactory
from thunder_fighter.sprites.enemy import Enemy
from thunder_fighter.utils.logger import logger


class EnemyFactory(ConfigurableEntityFactory[Enemy]):
    """
    Factory for creating enemy entities.
    
    This factory provides centralized enemy creation with support for
    different enemy types, difficulty scaling, and configuration presets.
    """
    
    def __init__(self):
        """Initialize the enemy factory."""
        super().__init__(Enemy)
        self._setup_default_presets()
        
        logger.info("EnemyFactory initialized with default presets")
    
    def _setup_default_presets(self):
        """Set up default enemy configuration presets."""
        # Basic enemy preset
        self.add_preset("basic", {
            'game_time': 0,
            'game_level': 1,
            'spawn_position': None,  # Will be randomized
            'movement_pattern': 'straight',
            'can_shoot': False,
            'health_multiplier': 1.0,
            'speed_multiplier': 1.0
        })
        
        # Shooter enemy preset
        self.add_preset("shooter", {
            'game_time': 2,
            'game_level': 2,
            'spawn_position': None,
            'movement_pattern': 'straight',
            'can_shoot': True,
            'health_multiplier': 1.2,
            'speed_multiplier': 0.8,
            'shoot_frequency': 2.0
        })
        
        # Fast enemy preset
        self.add_preset("fast", {
            'game_time': 1,
            'game_level': 1,
            'spawn_position': None,
            'movement_pattern': 'zigzag',
            'can_shoot': False,
            'health_multiplier': 0.8,
            'speed_multiplier': 1.5
        })
        
        # Tank enemy preset
        self.add_preset("tank", {
            'game_time': 3,
            'game_level': 3,
            'spawn_position': None,
            'movement_pattern': 'straight',
            'can_shoot': True,
            'health_multiplier': 2.0,
            'speed_multiplier': 0.5,
            'shoot_frequency': 1.5
        })
        
        # Elite enemy preset
        self.add_preset("elite", {
            'game_time': 5,
            'game_level': 5,
            'spawn_position': None,
            'movement_pattern': 'weave',
            'can_shoot': True,
            'health_multiplier': 1.8,
            'speed_multiplier': 1.2,
            'shoot_frequency': 2.5
        })
    
    def _get_required_fields(self) -> list:
        """Get required fields for enemy creation."""
        return ['all_sprites', 'enemy_bullets']
    
    def _create_entity(self, config: Dict[str, Any]) -> Enemy:
        """
        Create an enemy entity.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Created Enemy instance
        """
        # Get required parameters
        game_time = config.get('game_time', 0)
        game_level = config.get('game_level', 1)
        all_sprites = config['all_sprites']
        enemy_bullets = config['enemy_bullets']
        
        # Create the enemy
        enemy = Enemy(game_time, game_level, all_sprites, enemy_bullets)
        
        return enemy
    
    def _post_creation_setup(self, enemy: Enemy, config: Dict[str, Any]):
        """
        Perform post-creation setup on the enemy.
        
        Args:
            enemy: The created enemy
            config: Configuration used for creation
        """
        # Apply custom spawn position if specified
        spawn_position = config.get('spawn_position')
        if spawn_position:
            enemy.rect.x, enemy.rect.y = spawn_position
        
        # Apply multipliers
        health_multiplier = config.get('health_multiplier', 1.0)
        speed_multiplier = config.get('speed_multiplier', 1.0)
        
        if hasattr(enemy, 'health'):
            enemy.health = int(enemy.health * health_multiplier)
        if hasattr(enemy, 'max_health'):
            enemy.max_health = int(enemy.max_health * health_multiplier)
        if hasattr(enemy, 'speed'):
            enemy.speed = int(enemy.speed * speed_multiplier)
        
        # Apply shooting configuration - but respect enemy's level-based shooting ability
        # Only override can_shoot if explicitly set to True in preset, don't force False
        can_shoot = config.get('can_shoot')
        if can_shoot is True:
            enemy.can_shoot = True
        # If can_shoot is False or None in preset, keep the enemy's level-based decision
        
        shoot_frequency = config.get('shoot_frequency')
        if shoot_frequency and hasattr(enemy, 'shoot_frequency'):
            enemy.shoot_frequency = shoot_frequency
        
        # Apply movement pattern
        movement_pattern = config.get('movement_pattern')
        if movement_pattern and hasattr(enemy, 'set_movement_pattern'):
            enemy.set_movement_pattern(movement_pattern)
    
    def create_for_level(self, game_level: int, game_time: float, 
                        all_sprites: pygame.sprite.Group, 
                        enemy_bullets: pygame.sprite.Group) -> Enemy:
        """
        Create an enemy appropriate for the given level.
        
        Args:
            game_level: Current game level
            game_time: Current game time
            all_sprites: Sprite group for all sprites
            enemy_bullets: Sprite group for enemy bullets
            
        Returns:
            Created Enemy instance
        """
        # Determine enemy type based on level and time
        enemy_type = self._determine_enemy_type(game_level, game_time)
        
        return self.create_from_preset(
            enemy_type,
            game_level=game_level,
            game_time=game_time,
            all_sprites=all_sprites,
            enemy_bullets=enemy_bullets
        )
    
    def _determine_enemy_type(self, game_level: int, game_time: float) -> str:
        """
        Determine the appropriate enemy type for the given level and time.
        
        Args:
            game_level: Current game level
            game_time: Current game time in minutes
            
        Returns:
            Enemy preset name
        """
        # Early game - mostly basic enemies
        if game_level <= 1:
            return random.choice(["basic", "basic", "fast"])
        
        # Mid game - introduce shooters
        elif game_level <= 3:
            if game_time < 2:
                return random.choice(["basic", "fast", "shooter"])
            else:
                return random.choice(["basic", "shooter", "shooter", "fast"])
        
        # Late game - more variety and difficulty
        elif game_level <= 5:
            return random.choice(["shooter", "fast", "tank", "elite"])
        
        # End game - mostly elite enemies
        else:
            return random.choice(["tank", "elite", "elite", "shooter"])
    
    def create_wave(self, wave_size: int, game_level: int, game_time: float,
                   all_sprites: pygame.sprite.Group, 
                   enemy_bullets: pygame.sprite.Group) -> list:
        """
        Create a wave of enemies.
        
        Args:
            wave_size: Number of enemies in the wave
            game_level: Current game level
            game_time: Current game time
            all_sprites: Sprite group for all sprites
            enemy_bullets: Sprite group for enemy bullets
            
        Returns:
            List of created Enemy instances
        """
        enemies = []
        
        for i in range(wave_size):
            enemy = self.create_for_level(
                game_level, game_time, all_sprites, enemy_bullets
            )
            enemies.append(enemy)
        
        logger.debug(f"Created enemy wave of {wave_size} enemies for level {game_level}")
        return enemies
    
    def create_random_enemy(self, all_sprites: pygame.sprite.Group, 
                           enemy_bullets: pygame.sprite.Group,
                           game_level: int = 1, game_time: float = 0) -> Enemy:
        """
        Create a random enemy from available presets.
        
        Args:
            all_sprites: Sprite group for all sprites
            enemy_bullets: Sprite group for enemy bullets
            game_level: Current game level
            game_time: Current game time
            
        Returns:
            Created Enemy instance
        """
        available_presets = self.list_presets()
        preset_name = random.choice(available_presets)
        
        return self.create_from_preset(
            preset_name,
            game_level=game_level,
            game_time=game_time,
            all_sprites=all_sprites,
            enemy_bullets=enemy_bullets
        )
    
    def create_custom_enemy(self, enemy_config: Dict[str, Any],
                           all_sprites: pygame.sprite.Group,
                           enemy_bullets: pygame.sprite.Group) -> Enemy:
        """
        Create a custom enemy with specific configuration.
        
        Args:
            enemy_config: Custom enemy configuration
            all_sprites: Sprite group for all sprites
            enemy_bullets: Sprite group for enemy bullets
            
        Returns:
            Created Enemy instance
        """
        config = enemy_config.copy()
        config.update({
            'all_sprites': all_sprites,
            'enemy_bullets': enemy_bullets
        })
        
        return self.create(**config)
    
    def get_enemy_stats(self, preset_name: str) -> Dict[str, Any]:
        """
        Get statistics for an enemy preset.
        
        Args:
            preset_name: Name of the preset
            
        Returns:
            Dictionary with enemy statistics
        """
        preset = self.get_preset(preset_name)
        if not preset:
            return {}
        
        return {
            'type': preset_name,
            'can_shoot': preset.get('can_shoot', False),
            'health_multiplier': preset.get('health_multiplier', 1.0),
            'speed_multiplier': preset.get('speed_multiplier', 1.0),
            'movement_pattern': preset.get('movement_pattern', 'straight'),
            'difficulty_level': preset.get('game_level', 1)
        } 