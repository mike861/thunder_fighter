"""
Collision Detection System

Manages all collision detection logic between game entities in a unified way.
Refactored from utils/collisions.py to add system-level management.
"""

import random
from typing import Any, Dict

import pygame

from thunder_fighter.constants import BULLET_DAMAGE_TO_BOSS, RED, WHITE
from thunder_fighter.utils.logger import logger

SCORE_THRESHOLD = 200  # Every 200 points might spawn an item


class CollisionSystem:
    """Collision Detection System Class"""

    def __init__(self):
        self.collision_handlers = {}
        self._setup_collision_handlers()

    def _setup_collision_handlers(self):
        """Sets up the collision handler mapping."""
        self.collision_handlers = {
            'missile_enemy': self.check_missile_enemy_collisions,
            'bullet_enemy': self.check_bullet_enemy_collisions,
            'bullet_boss': self.check_bullet_boss_collisions,
            'enemy_player': self.check_enemy_player_collisions,
            'boss_bullet_player': self.check_boss_bullet_player_collisions,
            'enemy_bullet_player': self.check_enemy_bullet_player_collisions,
            'items_player': self.check_items_player_collisions,
        }

    def check_all_collisions(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Checks all collisions."""
        results = {}

        # Check various collision types
        for collision_type, handler in self.collision_handlers.items():
            try:
                if collision_type == 'missile_enemy':
                    results[collision_type] = handler(
                        game_state.get('missiles'),
                        game_state.get('enemies'),
                        game_state.get('all_sprites'),
                        game_state.get('score')
                    )
                elif collision_type == 'bullet_enemy':
                    results[collision_type] = handler(
                        game_state.get('enemies'),
                        game_state.get('bullets'),
                        game_state.get('all_sprites'),
                        game_state.get('score'),
                        game_state.get('last_score_checkpoint', 0),
                        game_state.get('score_threshold', SCORE_THRESHOLD),
                        game_state.get('items_group'),
                        game_state.get('player')
                    )
                # Handling for other collision types...
            except Exception as e:
                logger.error(f"Error in collision check {collision_type}: {e}")
                results[collision_type] = None

        return results

    def check_missile_enemy_collisions(self, missiles, enemies, all_sprites, score):
        """Checks missile-enemy collisions and creates appropriate effects."""
        hits = pygame.sprite.groupcollide(missiles, enemies, True, False)

        for missile, hit_enemies in hits.items():
            for enemy in hit_enemies:
                if hasattr(enemy, 'damage'):
                    # It's a boss, apply damage.
                    if enemy.damage(50): # damage() returns True if boss is defeated
                        from thunder_fighter.graphics.effects import create_explosion
                        explosion = create_explosion(enemy.rect.center, 'lg')
                        all_sprites.add(explosion)
                        score.update(500) # Bonus for boss kill with missile
                    else:
                        # Hit but not destroyed - still use explosion for missile
                        from thunder_fighter.graphics.effects import create_explosion
                        explosion = create_explosion(missile.rect.center, 'md')
                        all_sprites.add(explosion)
                else:
                    # It's a regular enemy, kill it.
                    enemy.kill()
                    from thunder_fighter.graphics.effects import create_explosion
                    explosion = create_explosion(enemy.rect.center, 'md')
                    all_sprites.add(explosion)
                    score.update(25) # More points for missile kill

    def check_bullet_enemy_collisions(self, enemies, bullets, all_sprites, score,
                                      last_score_checkpoint, score_threshold, items_group, player):
        """Check collisions between bullets and enemies"""
        try:
            # Return detailed results
            result = {
                'enemy_hit': False,  # Whether enemy was hit
                'score_checkpoint': last_score_checkpoint, # Current score checkpoint
                'enemy_count': 0,  # Number of enemies hit
                'generated_item': False  # Whether item was generated
            }

            hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
            result['enemy_count'] = len(hits)
            result['enemy_hit'] = bool(hits)  # Set to True if there were hits

            for hit in hits:
                # Add score based on enemy level
                enemy_level = getattr(hit, 'level', 0)
                score_value = 10 + enemy_level * 2
                score.update(score_value)

                # Create explosion effect
                from thunder_fighter.graphics.effects.explosion import Explosion
                explosion = Explosion(hit.rect.center)
                all_sprites.add(explosion)

                # Check if we need to generate item based on score checkpoints
                current_score_checkpoint = score.value // score_threshold
                if current_score_checkpoint > last_score_checkpoint:
                    from thunder_fighter.entities.items.items import create_random_item
                    # Hack: Get game_level from a sprite's group's game reference if available
                    # This is not ideal, but avoids a large refactor to pass 'game' down.
                    game_level = 1
                    game_time = 0 # Placeholder for game_time
                    if all_sprites.sprites():
                        game_instance = getattr(all_sprites.sprites()[0], 'game', None)
                        if game_instance:
                            game_level = getattr(game_instance, 'game_level', 1)
                            game_time = getattr(game_instance, 'game_time', 0)

                    create_random_item(game_time, game_level, all_sprites, items_group, player)

                    last_score_checkpoint = current_score_checkpoint
                    result['generated_item'] = True
                    logger.debug(f"Score milestone reached: {score.value}. Item spawned.")

            result['score_checkpoint'] = last_score_checkpoint
            return result
        except Exception as e:
            logger.error(f"Error in bullet-enemy collision check: {e}", exc_info=True)
            return {'enemy_hit': False, 'score_checkpoint': last_score_checkpoint, 'enemy_count': 0, 'generated_item': False}

    def check_bullet_boss_collisions(self, boss, bullets, all_sprites):
        """Check collisions between player bullets and boss"""
        if boss is None:
            return {'boss_hit': False, 'boss_defeated': False, 'damage': 0}

        result = {
            'boss_hit': False,
            'boss_defeated': False,
            'damage': 0
        }

        try:
            # Add debug logging
            logger.debug(f"Checking bullet-boss collisions. Boss rect: {boss.rect}, Health: {boss.health}")
            logger.debug(f"Bullets in group: {len(bullets)}")

            # For pygame.sprite.spritecollide, the first parameter needs to be a single sprite
            # Ensure boss is a sprite instance rather than a group
            if hasattr(boss, 'rect') and hasattr(boss, 'health'):
                # Use collision masks for more precise collision detection - masks improve collision detection accuracy
                boss_hits = pygame.sprite.spritecollide(
                    boss, bullets, True,
                    pygame.sprite.collide_mask
                )

                # Record collision results
                hits_count = len(boss_hits)
                if hits_count > 0:
                    logger.debug(f"Boss hit by {hits_count} bullets")

                result['boss_hit'] = bool(boss_hits)
                result['damage'] = len(boss_hits) * BULLET_DAMAGE_TO_BOSS  # Damage per bullet from constants

                for _hit in boss_hits:
                    # Use boss's damage method to handle damage
                    boss_defeated = boss.damage(BULLET_DAMAGE_TO_BOSS)

                    # Check if Boss is defeated
                    if boss_defeated:
                        # Create big explosion when boss is defeated
                        from thunder_fighter.graphics.effects.explosion import Explosion
                        for _ in range(10):
                            pos_x = random.randint(boss.rect.left, boss.rect.right)
                            pos_y = random.randint(boss.rect.top, boss.rect.bottom)
                            explosion = Explosion((pos_x, pos_y))
                            all_sprites.add(explosion)

                        result['boss_defeated'] = True
                        logger.info("Boss defeated!")
            else:
                logger.error("Invalid boss instance: missing rect or health attribute")

            return result
        except Exception as e:
            logger.error(f"Error in bullet-boss collision check: {e}", exc_info=True)
            return {'boss_hit': False, 'boss_defeated': False, 'damage': 0}

    def check_enemy_player_collisions(self, player, enemies, all_sprites):
        """Check collisions between enemies and player"""
        result = {
            'was_hit': False,
            'game_over': False,
            'damage': 0
        }

        try:
            hits = pygame.sprite.spritecollide(player, enemies, True)
            result['was_hit'] = bool(hits)

            for hit in hits:
                # Increase damage based on enemy level
                enemy_level = getattr(hit, 'level', 0)  # Get enemy level, default to 0
                damage = 15 + enemy_level * 1  # Base damage 15, extra 1 per level
                player.health -= damage
                result['damage'] += damage

                # Create explosion
                from thunder_fighter.graphics.effects.explosion import Explosion
                explosion = Explosion(hit.rect.center)
                all_sprites.add(explosion)

                # If player health is 0, game over
                if player.health <= 0:
                    result['game_over'] = True

            return result
        except Exception as e:
            logger.error(f"Error in enemy-player collision check: {e}", exc_info=True)
            return {'was_hit': False, 'game_over': False, 'damage': 0}

    def check_boss_bullet_player_collisions(self, player, boss_bullets, all_sprites):
        """Check collisions between boss bullets and player"""
        result = {
            'was_hit': False,
            'game_over': False,
            'damage': 0
        }

        try:
            hits = pygame.sprite.spritecollide(player, boss_bullets, True)
            result['was_hit'] = bool(hits)

            total_damage = 0
            for hit in hits:
                # Use bullet's dynamic damage value
                damage = hit.get_damage() if hasattr(hit, 'get_damage') else 15
                total_damage += damage
                player.health -= damage
                # Create flash effect for boss bullet hit
                from thunder_fighter.graphics.effects import create_flash_effect
                create_flash_effect(player, RED)

                # If player health is 0, game over
                if player.health <= 0:
                    result['game_over'] = True

            result['damage'] = total_damage

            return result
        except Exception as e:
            logger.error(f"Error in boss_bullet-player collision check: {e}", exc_info=True)
            return {'was_hit': False, 'game_over': False, 'damage': 0}

    def check_enemy_bullet_player_collisions(self, player, enemy_bullets, all_sprites):
        """Check collisions between enemy bullets and player"""
        result = {
            'was_hit': False,
            'game_over': False,
            'damage': 0
        }

        try:
            hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
            result['was_hit'] = bool(hits)

            for hit in hits:
                # Calculate damage based on enemy bullet level
                enemy_level = getattr(hit, 'enemy_level', 0)  # Get bullet level, default to 0
                damage = 5 + enemy_level * 1  # Base damage 5, extra 1 per level

                # Use take_damage to handle damage and effects
                if player.take_damage(damage):
                    result['game_over'] = True

                result['damage'] += damage

                # Create small flash effect for bullet hit
                from thunder_fighter.graphics.effects import create_flash_effect
                create_flash_effect(player, WHITE)

            return result
        except Exception as e:
            logger.error(f"Error in enemy_bullet-player collision check: {e}", exc_info=True)
            return {'was_hit': False, 'game_over': False, 'damage': 0}

    def check_items_player_collisions(self, items, player, ui_manager, sound_manager=None):
        """Check collisions between items and player

        Args:
            items: Items sprite group
            player: Player object
            ui_manager: UI manager for notifications
            sound_manager: Sound manager instance for playing sounds
        """

        hits = pygame.sprite.spritecollide(player, items, True)
        for hit in hits:
            item_type = getattr(hit, 'type', 'unknown')

            # Perform different actions based on item type
            if item_type == 'health':
                player.heal()
            elif item_type == 'bullet_speed':
                player.increase_bullet_speed()
            elif item_type == 'bullet_path':
                player.increase_bullet_paths()
            elif item_type == 'player_speed':
                player.increase_player_speed()
            elif item_type == 'wingman':
                player.add_wingman()

            # Show notification
            if ui_manager:
                ui_manager.show_item_collected(item_type)

            # Play sound effect
            if sound_manager:
                sound_manager.play_sound('item_pickup')


# Global collision system instance
_global_collision_system = None


def get_collision_system() -> CollisionSystem:
    """Gets the global collision system instance."""
    global _global_collision_system
    if _global_collision_system is None:
        _global_collision_system = CollisionSystem()
    return _global_collision_system


# Compatibility functions - maintain original API
def check_missile_enemy_collisions(missiles, enemies, all_sprites, score):
    """Checks missile-enemy collisions and creates appropriate effects."""
    return get_collision_system().check_missile_enemy_collisions(missiles, enemies, all_sprites, score)


def check_bullet_enemy_collisions(enemies, bullets, all_sprites, score,
                                  last_score_checkpoint, score_threshold, items_group, player):
    """Check collisions between bullets and enemies"""
    return get_collision_system().check_bullet_enemy_collisions(
        enemies, bullets, all_sprites, score,
        last_score_checkpoint, score_threshold, items_group, player)


def check_bullet_boss_collisions(boss, bullets, all_sprites):
    """Check collisions between player bullets and boss"""
    return get_collision_system().check_bullet_boss_collisions(boss, bullets, all_sprites)


def check_enemy_player_collisions(player, enemies, all_sprites):
    """Check collisions between enemies and player"""
    return get_collision_system().check_enemy_player_collisions(player, enemies, all_sprites)


def check_boss_bullet_player_collisions(player, boss_bullets, all_sprites):
    """Check collisions between boss bullets and player"""
    return get_collision_system().check_boss_bullet_player_collisions(player, boss_bullets, all_sprites)


def check_enemy_bullet_player_collisions(player, enemy_bullets, all_sprites):
    """Check collisions between enemy bullets and player"""
    return get_collision_system().check_enemy_bullet_player_collisions(player, enemy_bullets, all_sprites)


def check_items_player_collisions(items, player, ui_manager, sound_manager=None):
    """Check collisions between items and player"""
    return get_collision_system().check_items_player_collisions(items, player, ui_manager, sound_manager)
