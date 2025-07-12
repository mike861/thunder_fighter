import math

import pygame
import pygame.time as ptime

from thunder_fighter.constants import (
    BULLET_ANGLE_SPREAD_LARGE,
    BULLET_ANGLE_SPREAD_SMALL,
    BULLET_ANGLE_STRAIGHT,
    BULLET_PATHS_DEFAULT,
    BULLET_PATHS_MAX,
    BULLET_SPEED_DEFAULT,
    BULLET_SPEED_MAX,
    BULLET_SPEED_UPGRADE_AMOUNT,
    HEIGHT,
    PLAYER_FLASH_FRAMES,
    PLAYER_HEAL_AMOUNT,
    PLAYER_HEALTH,
    PLAYER_MAX_SPEED,
    PLAYER_MAX_WINGMEN,
    PLAYER_SHOOT_DELAY,
    PLAYER_SPEED,
    PLAYER_SPEED_UPGRADE_AMOUNT,
    WHITE,
    WIDTH,
)
from thunder_fighter.entities.player.wingman import Wingman
from thunder_fighter.entities.projectiles.bullets import Bullet
from thunder_fighter.graphics.effects import create_explosion, create_flash_effect
from thunder_fighter.graphics.renderers import create_player_ship
from thunder_fighter.utils.logger import logger


class Player(pygame.sprite.Sprite):
    """Player class"""

    def __init__(self, game, all_sprites, bullets_group, missiles_group, enemies_group, sound_manager=None):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.sound_manager = sound_manager  # Store sound manager instance

        # Use custom graphics instead of rectangle
        self.image = create_player_ship()
        self.rect = self.image.get_rect()

        # Position (float for precision)
        self.x = float(WIDTH // 2)
        self.y = float(HEIGHT - 10)
        self.rect.centerx = int(self.x)
        self.rect.bottom = int(self.y)
        self.speed = PLAYER_SPEED  # Use self.speed for current player speed
        self.max_speed = PLAYER_MAX_SPEED
        self.speedx = 0
        self.speedy = 0
        self.health = PLAYER_HEALTH
        self.shoot_delay = PLAYER_SHOOT_DELAY
        self.last_shot = ptime.get_ticks()
        # Add thruster animation effect
        self.thrust = 0

        # Bullet attributes
        self.bullet_speed = BULLET_SPEED_DEFAULT
        self.max_bullet_speed = BULLET_SPEED_MAX
        self.bullet_paths = BULLET_PATHS_DEFAULT
        self.max_bullet_paths = BULLET_PATHS_MAX

        # Sprite groups
        self.all_sprites = all_sprites
        self.bullets_group = bullets_group

        # Visual effects
        self.flash_timer = 0
        self.flash_duration = 0
        self.original_image = self.image.copy()

        # Animation effects
        self.angle = 0  # For rotation animation

        # Wingmen
        self.wingmen = pygame.sprite.Group()
        self.wingmen_list = []
        self.missiles_group = missiles_group
        self.enemies_group = enemies_group
        self.last_missile_shot = ptime.get_ticks()
        self.missile_shoot_delay = 2000  # 2 seconds

    def update(self):
        """Update player state"""
        # Reset movement speed
        self.speedx = 0
        self.speedy = 0

        # Get key states
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT] or keystate[pygame.K_a]:
            self.speedx = -self.speed  # Use current speed
        if keystate[pygame.K_RIGHT] or keystate[pygame.K_d]:
            self.speedx = self.speed  # Use current speed
        if keystate[pygame.K_UP] or keystate[pygame.K_w]:
            self.speedy = -self.speed  # Use current speed
        if keystate[pygame.K_DOWN] or keystate[pygame.K_s]:
            self.speedy = self.speed  # Use current speed

        # Shooting
        if keystate[pygame.K_SPACE]:
            self.shoot()

        # Fire missiles
        self.shoot_missiles()

        # Move player
        self.x += self.speedx
        self.y += self.speedy

        # Slight floating animation for the aircraft
        self.angle = (self.angle + 1) % 360
        dy = math.sin(math.radians(self.angle)) * 0.5  # Small up and down float
        self.y += dy

        # Update final rect position
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

        # Keep player within bounds
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.x = self.rect.centerx
        if self.rect.left < 0:
            self.rect.left = 0
            self.x = self.rect.centerx
        if self.rect.top < 0:
            self.rect.top = 0
            self.y = self.rect.centery
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.y = self.rect.centery

        # Update thruster animation
        self.thrust = (self.thrust + 1) % 10

        # Flash effect
        current_time = ptime.get_ticks()
        if self.flash_timer > 0:
            # Toggle visibility every 100 milliseconds
            if (current_time // 100) % 2 == 0:
                self.image = self.original_image.copy()
            else:
                self.image = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)

            # Decrease timer
            self.flash_timer -= 1
        else:
            # Ensure original image is restored after flashing ends
            if self.image != self.original_image:
                self.image = self.original_image.copy()

        # Update wingmen positions
        self.wingmen.update()

    def shoot(self):
        """Fire bullets"""
        now = ptime.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now

            # Play shooting sound effect
            # self.sound_manager.play_sound('player_shoot')  # Commented out - sound file doesn't exist

            # Create different numbers and angles of bullets based on bullet paths
            if self.bullet_paths == 1:
                # Single straight shot
                bullet = Bullet(self.rect.centerx, self.rect.top, self.bullet_speed, BULLET_ANGLE_STRAIGHT)
                self.all_sprites.add(bullet)
                self.bullets_group.add(bullet)
            elif self.bullet_paths == 2:
                # Double parallel shots
                bullet1 = Bullet(self.rect.left + 5, self.rect.top, self.bullet_speed, BULLET_ANGLE_STRAIGHT)
                bullet2 = Bullet(self.rect.right - 5, self.rect.top, self.bullet_speed, BULLET_ANGLE_STRAIGHT)
                self.all_sprites.add(bullet1, bullet2)
                self.bullets_group.add(bullet1, bullet2)
            elif self.bullet_paths == 3:
                # Three shots: one straight, two angled
                bullet1 = Bullet(
                    self.rect.centerx, self.rect.top, self.bullet_speed, BULLET_ANGLE_STRAIGHT
                )  # Center straight
                bullet2 = Bullet(
                    self.rect.left + 5, self.rect.top, self.bullet_speed, -BULLET_ANGLE_SPREAD_SMALL
                )  # Left angled
                bullet3 = Bullet(
                    self.rect.right - 5, self.rect.top, self.bullet_speed, BULLET_ANGLE_SPREAD_SMALL
                )  # Right angled
                self.all_sprites.add(bullet1, bullet2, bullet3)
                self.bullets_group.add(bullet1, bullet2, bullet3)
            elif self.bullet_paths >= 4:
                # Four or more shots (max limit is 4): two straight, two angled
                bullet1 = Bullet(
                    self.rect.centerx - 8, self.rect.top, self.bullet_speed, BULLET_ANGLE_STRAIGHT
                )  # Left center straight
                bullet2 = Bullet(
                    self.rect.centerx + 8, self.rect.top, self.bullet_speed, BULLET_ANGLE_STRAIGHT
                )  # Right center straight
                bullet3 = Bullet(
                    self.rect.left + 5, self.rect.top, self.bullet_speed, -BULLET_ANGLE_SPREAD_LARGE
                )  # Left angled
                bullet4 = Bullet(
                    self.rect.right - 5, self.rect.top, self.bullet_speed, BULLET_ANGLE_SPREAD_LARGE
                )  # Right angled
                self.all_sprites.add(bullet1, bullet2, bullet3, bullet4)
                self.bullets_group.add(bullet1, bullet2, bullet3, bullet4)

    def shoot_missiles(self):
        """Fires missiles from wingmen with intelligent targeting."""
        now = ptime.get_ticks()
        if not self.wingmen_list or now - self.last_missile_shot < self.missile_shoot_delay:
            return

        self.last_missile_shot = now

        # Access the game object to check for a boss
        game = self.game
        if not game:
            return

        targets = []
        # Prioritize the boss if it's active
        if game.boss and game.boss.alive():
            targets = [game.boss] * len(self.wingmen_list)
        else:
            # If no boss, assign unique enemies to each wingman
            if not self.enemies_group:
                return

            # Sort enemies by distance to the player
            sorted_enemies = sorted(
                self.enemies_group.sprites(),
                key=lambda e: pygame.math.Vector2(self.rect.center).distance_to(e.rect.center),
            )

            # Assign the closest enemies to the wingmen
            targets = sorted_enemies[: len(self.wingmen_list)]

        # Fire missiles
        for i, wingman in enumerate(self.wingmen_list):
            if i < len(targets):
                target = targets[i]
                wingman.shoot(self.all_sprites, self.missiles_group, target)

    def add_wingman(self):
        """Add a wingman"""
        if len(self.wingmen_list) >= PLAYER_MAX_WINGMEN:
            return False  # Maximum number reached

        # Determine position for new wingman
        if not self.wingmen_list:
            side = "left"
        else:
            # If there's already one, check which side it's on
            existing_side = self.wingmen_list[0].side
            side = "right" if existing_side == "left" else "left"

        wingman = Wingman(self, side)
        self.all_sprites.add(wingman)
        self.wingmen.add(wingman)
        self.wingmen_list.append(wingman)
        return True

    def take_damage(self, damage=10):
        """Player takes damage, consume wingman first"""
        if self.wingmen_list:
            # Consume one wingman
            wingman_to_remove = self.wingmen_list.pop()
            wingman_to_remove.kill()

            # Create explosion effect
            explosion = create_explosion(wingman_to_remove.rect.center, "sm")
            self.all_sprites.add(explosion)

            # Play sound effect
            if self.sound_manager:
                self.sound_manager.play_sound("enemy_explosion")
            return False  # Player not dead

        self.health -= damage

        # Damage flash effect
        self.flash_timer = PLAYER_FLASH_FRAMES

        # Create flash effect instead of hit effect
        create_flash_effect(self, WHITE)

        # Play hit sound effect
        if self.sound_manager:
            self.sound_manager.play_sound("player_hit")

        return self.health <= 0  # Return whether dead

    def heal(self, amount=PLAYER_HEAL_AMOUNT):
        """Player heals"""
        self.health = min(PLAYER_HEALTH, self.health + amount)

    def increase_bullet_speed(self, amount=BULLET_SPEED_UPGRADE_AMOUNT):
        """Increase bullet speed"""
        self.bullet_speed = min(self.max_bullet_speed, self.bullet_speed + amount)
        return self.bullet_speed

    def increase_bullet_paths(self):
        """Increase bullet paths"""
        if self.bullet_paths < self.max_bullet_paths:
            self.bullet_paths += 1
        return self.bullet_paths

    def increase_speed(self):
        """
        Increase player movement speed

        Returns:
            bool: Whether speed was successfully increased
        """
        # Check if already at max speed
        if self.speed >= PLAYER_MAX_SPEED:
            return False

        self.speed += PLAYER_SPEED_UPGRADE_AMOUNT
        # Player speed increase should be shown in game UI, not just logged
        logger.info(f"Player speed increased to: {self.speed}")
        return True

    def increase_player_speed(self, amount=PLAYER_SPEED_UPGRADE_AMOUNT):
        """
        Increase player movement speed - matches method name called in collisions.py

        Args:
            amount: Speed increase amount

        Returns:
            float: Current player speed
        """
        # Check if already at max speed
        if self.speed >= PLAYER_MAX_SPEED:
            return self.speed

        # Increase speed but not exceed max
        self.speed = min(self.max_speed, self.speed + amount)
        logger.info(f"Player speed increased to: {self.speed}")
        return self.speed
