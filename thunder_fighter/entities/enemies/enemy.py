import random

import pygame
import pygame.time as ptime

from thunder_fighter.constants import (
    ENEMY_HORIZONTAL_MOVE_MAX,
    ENEMY_HORIZONTAL_MOVE_MIN,
    ENEMY_MIN_SHOOT_DELAY,
    ENEMY_ROTATION_UPDATE,
    ENEMY_SCREEN_BOUNDS,
    ENEMY_SHOOT_LEVEL,
    ENEMY_SPAWN_Y_MAX,
    ENEMY_SPAWN_Y_MIN,
    HEIGHT,
    WIDTH,
)
from thunder_fighter.entities.projectiles.bullets import EnemyBullet
from thunder_fighter.graphics.renderers import create_enemy_ship
from thunder_fighter.utils.logger import logger


class Enemy(pygame.sprite.Sprite):
    """Enemy class"""
    def __init__(self, game_time=0, game_level=1, all_sprites=None, enemy_bullets_group=None):
        pygame.sprite.Sprite.__init__(self)

        # Determine level based on game time and game level
        self.level = self._determine_level(game_time, game_level)

        # Create image based on level
        self.image = create_enemy_ship(self.level)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(ENEMY_SPAWN_Y_MIN, ENEMY_SPAWN_Y_MAX)

        # Add detailed logging here
        logger.debug(f"Enemy spawned - Level: {self.level}, ENEMY_SHOOT_LEVEL: {ENEMY_SHOOT_LEVEL}")

        # Adjust speed based on game time and level
        base_speed_factor = min(3.0, 1.0 + game_time / 60.0)
        level_speed_bonus = self.level * 0.2
        total_speed_factor = base_speed_factor + level_speed_bonus
        self.speedy = random.randrange(1, int(3 + 3 * total_speed_factor))
        self.speedx = random.randrange(ENEMY_HORIZONTAL_MOVE_MIN, ENEMY_HORIZONTAL_MOVE_MAX)

        # Rotation animation properties
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()
        self.original_image = self.image.copy()

        # Shooting capability - ensure enemies only shoot if they're level 2 or higher
        # Since we use 0-based indexing in _determine_level (levels 0-10),
        # and ENEMY_SHOOT_LEVEL=2 means "from level 2", we need to check if level >= 2
        self.can_shoot = self.level >= ENEMY_SHOOT_LEVEL
        logger.debug(f"Enemy ID:{id(self)} Level: {self.level}, Can Shoot: {self.can_shoot}")

        # Sprite groups for bullets
        self.all_sprites = all_sprites
        self.enemy_bullets_group = enemy_bullets_group

        # Shooting properties
        # Initialize shooting properties for all enemies (even non-shooting ones)
        base_delay = 800
        level_reduction = self.level * 50
        self.shoot_delay = max(ENEMY_MIN_SHOOT_DELAY, base_delay - level_reduction)
        if self.level >= 5:
            self.shoot_delay = max(300, self.shoot_delay - 100)
        self.last_shot = pygame.time.get_ticks() - self.shoot_delay + random.randint(0, 1000)

        if self.can_shoot:
            logger.debug(f"Enemy ID:{id(self)} Level:{self.level} Ready to shoot, Delay:{self.shoot_delay}ms")

    def _determine_level(self, game_time, game_level):
        """Determine enemy level based on game time and level

        About level meanings:
        - Enemy levels are integers from 0-10, where 0 is the lowest and 10 is the highest
        - Level 0-1 enemies cannot shoot
        - Level 2 and above enemies can shoot (determined by ENEMY_SHOOT_LEVEL=2 constant)
        - Higher level enemies have more health, speed and attack power
        """
        # Base probabilities (based on game time)
        base_probs = [
            max(0, 0.35 - game_time * 0.05),  # Level 0
            max(0, 0.25 - game_time * 0.03),  # Level 1
            max(0, 0.15),                     # Level 2
            max(0, 0.10 + game_time * 0.01),  # Level 3
            max(0, 0.05 + game_time * 0.015), # Level 4
            max(0, 0.05 + game_time * 0.015), # Level 5
            max(0, 0.02 + game_time * 0.01),  # Level 6
            max(0, 0.02 + game_time * 0.01),  # Level 7
            max(0, 0.01 + game_time * 0.005), # Level 8
            max(0, 0.00 + game_time * 0.003), # Level 9
            max(0, 0.00 + game_time * 0.002)  # Level 10
        ]

        # Game level influence - increase probability of high-level enemies
        # Each game level slightly increases high-level enemy appearance rate
        level_boost = (game_level - 1) * 0.02 # 2% increase per level

        # Transfer probability from low to high levels (simple linear transfer)
        transfer_prob = 0.0
        for i in range(len(base_probs)):
            # Transfer probability from level 0-4 enemies
            if i < 5:
                reduction = base_probs[i] * level_boost * (5 - i) / 5 # Lower levels lose more
                reduction = min(base_probs[i], reduction) # Cannot reduce more than current probability
                base_probs[i] -= reduction
                transfer_prob += reduction
            # Add probability to level 5-10 enemies
            elif i >= 5:
                # Distribute transferred probability proportionally
                boost_share = transfer_prob / max(1, len(base_probs) - 5) # Equal distribution
                base_probs[i] += boost_share
                transfer_prob -= boost_share # Update remaining transfer probability

        # Ensure probabilities are non-negative and make minor adjustments to prevent all zeros
        for i in range(len(base_probs)):
            base_probs[i] = max(0.001, base_probs[i]) # Ensure each level has minimal probability

        # Normalize probabilities to sum to 1
        total = sum(base_probs)
        if total > 0:
            probs = [p / total for p in base_probs]
        else:
            probs = [1/len(base_probs)] * len(base_probs)

        # Choose level based on final probabilities
        chosen_level = random.choices(range(11), weights=probs, k=1)[0]

        # Ensure enemy level doesn't exceed game level + 2
        max_allowed_level = min(10, game_level + 2)
        chosen_level = min(chosen_level, max_allowed_level)

        logger.debug(f"Determined enemy level {chosen_level} (game_time: {game_time:.1f}, game_level: {game_level}, max_allowed: {max_allowed_level})")
        return chosen_level

    def update(self):
        """Update enemy state"""
        self.rect.y += self.speedy
        self.rect.x += self.speedx

        # Reverse horizontal direction if enemy hits the screen edges
        if self.rect.right > WIDTH or self.rect.left < 0:
            self.speedx = -self.speedx

        # Rotation animation (only for fast-moving enemies)
        if abs(self.speedx) > 1:
            now = pygame.time.get_ticks()
            if now - self.last_update > ENEMY_ROTATION_UPDATE:
                self.last_update = now
                self.rot = (self.rot + self.rot_speed) % 360
                self.image = pygame.transform.rotate(self.original_image, self.rot)
                old_center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = old_center

        # If enemy goes off-screen, remove it
        if (self.rect.top > HEIGHT + ENEMY_SCREEN_BOUNDS or
            self.rect.left < -ENEMY_SCREEN_BOUNDS or
            self.rect.right > WIDTH + ENEMY_SCREEN_BOUNDS):
            logger.debug(f"Enemy ID:{id(self)} killed (off-screen).")
            self.kill()

        # Check if enemy can shoot
        time_now = ptime.get_ticks()
        if self.can_shoot and time_now - self.last_shot > self.shoot_delay:
            # Check if enemy is visible on screen
            if self.rect.bottom > 0 and self.rect.top < HEIGHT:
                if self.shoot():
                    self.last_shot = time_now
                    # Log shooting event (changed from print)
                    logger.debug(f"Enemy ID:{id(self)} Level:{self.level} Fired! Delay:{self.shoot_delay}ms")

    def shoot(self):
        """Fires a bullet"""
        try:
            # Ensure sprite groups exist
            if not hasattr(self, 'all_sprites') or not hasattr(self, 'enemy_bullets_group'):
                logger.error(f"Error: Enemy {id(self)} missing required sprite groups for shooting.")
                return False

            # Double-check shooting capability and level requirement
            if not self.can_shoot or self.level < ENEMY_SHOOT_LEVEL:
                logger.warning(f"Enemy ID:{id(self)} attempted to shoot but can_shoot={self.can_shoot}, level={self.level}, required level={ENEMY_SHOOT_LEVEL}")
                return False

            # Create bullet
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom, self.level)

            # Add bullet to game sprite groups
            self.all_sprites.add(bullet)
            self.enemy_bullets_group.add(bullet)

            return True

        except Exception as e:
            # Log shooting error (changed from print)
            logger.error(f"Enemy shooting error: {str(e)}", exc_info=True)
            # traceback.print_exc() # Logger includes traceback with exc_info=True
            return False

    def get_level(self):
        """Get enemy level"""
        return self.level
