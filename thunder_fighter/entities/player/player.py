import math

import pygame
import pygame.time as ptime

from thunder_fighter.constants import (
    BULLET_CONFIG,
    HEIGHT,
    PLAYER_CONFIG,
    WHITE,
    WIDTH,
)
from thunder_fighter.entities.base_3d import Entity3D
from thunder_fighter.entities.player.wingman import Wingman
from thunder_fighter.events.game_events import GameEvent
from thunder_fighter.graphics.effects import create_explosion, create_flash_effect
from thunder_fighter.graphics.renderers import create_player_ship
from thunder_fighter.utils.logger import logger


class Player(Entity3D):
    """Player class with 3D perspective support"""

    def __init__(
        self, game, all_sprites, bullets_group, missiles_group, enemies_group, sound_manager=None, event_system=None
    ):
        # Initialize 3D entity with player position (z=0 for closest to camera)
        super().__init__(
            x=float(WIDTH // 2),
            y=float(HEIGHT - 10),
            width=60,  # Match player ship size
            height=50,
            z=0.0  # Player stays at front depth
        )

        self.game = game
        self.sound_manager = sound_manager  # Store sound manager instance
        self.event_system = event_system  # For event-driven shooting

        # Use custom graphics instead of rectangle
        self.image = create_player_ship()
        self.rect = self.image.get_rect()

        # Set initial rect position based on 3D coordinates
        screen_pos = self.get_screen_position()
        self.rect.centerx = int(screen_pos[0])
        self.rect.bottom = int(screen_pos[1])
        self.speed = int(PLAYER_CONFIG["SPEED"])  # Use self.speed for current player speed
        self.max_speed = int(PLAYER_CONFIG["MAX_SPEED"])
        # velocity_x and velocity_y are inherited from GameObject
        self.health = int(PLAYER_CONFIG["HEALTH"])
        self.shoot_delay = int(PLAYER_CONFIG["SHOOT_DELAY"])
        self.last_shot = ptime.get_ticks()
        # Add thruster animation effect
        self.thrust = 0

        # Bullet attributes
        self.bullet_speed = int(BULLET_CONFIG["SPEED_DEFAULT"])
        self.max_bullet_speed = int(BULLET_CONFIG["SPEED_MAX"])
        self.bullet_paths = int(BULLET_CONFIG["PATHS_DEFAULT"])
        self.max_bullet_paths = int(BULLET_CONFIG["PATHS_MAX"])

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

        # Enable subtle 3D breathing/floating effect
        self.enable_depth_oscillation(amplitude=2.0, frequency=1.5)

    def update(self, dt: float = 1/60):
        """Update player state with 3D perspective support"""
        # Reset movement velocity
        self.velocity_x = 0
        self.velocity_y = 0

        # Get key states
        keystate = pygame.key.get_pressed()
        # Convert speed from pixels/frame to pixels/second (multiply by 60 FPS)
        speed_per_second = self.speed * 60
        if keystate[pygame.K_LEFT] or keystate[pygame.K_a]:
            self.velocity_x = -speed_per_second
        if keystate[pygame.K_RIGHT] or keystate[pygame.K_d]:
            self.velocity_x = speed_per_second
        if keystate[pygame.K_UP] or keystate[pygame.K_w]:
            self.velocity_y = -speed_per_second
        if keystate[pygame.K_DOWN] or keystate[pygame.K_s]:
            self.velocity_y = speed_per_second

        # Shooting
        if keystate[pygame.K_SPACE]:
            self.shoot()

        # Fire missiles
        self.shoot_missiles()

        # Apply movement using 3D base class (handles depth and perspective)
        super().update(dt)

        # Slight floating animation for the aircraft
        self.angle = (self.angle + 1) % 360
        floating_offset = math.sin(math.radians(self.angle)) * 0.5  # Small up and down float
        self.y += floating_offset

        # Update rect position using 3D screen coordinates
        screen_pos = self.get_screen_position()
        visual_size = self.get_visual_size()

        self.rect.centerx = int(screen_pos[0])
        self.rect.centery = int(screen_pos[1])
        self.rect.width = visual_size[0]
        self.rect.height = visual_size[1]

        # Keep player within bounds (in world coordinates)
        if self.x < 30:  # Account for half-width
            self.x = 30
        if self.x > WIDTH - 30:
            self.x = WIDTH - 30
        if self.y < 25:  # Account for half-height
            self.y = 25
        if self.y > HEIGHT - 25:
            self.y = HEIGHT - 25

        # Update rect after boundary check
        screen_pos = self.get_screen_position()
        self.rect.centerx = int(screen_pos[0])
        self.rect.centery = int(screen_pos[1])

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
        """Fire bullets using event-driven architecture"""
        now = ptime.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now

            # Play shooting sound effect
            # self.sound_manager.play_sound('player_shoot')  # Commented out - sound file doesn't exist

            # Calculate shooting parameters using pure logic
            shooting_data = self._calculate_shooting_parameters()

            # If no event system available, fall back to legacy behavior
            if self.event_system is None:
                logger.warning("No event system available, falling back to legacy shooting behavior")
                self._legacy_shoot_fallback(shooting_data)
            else:
                # Emit event with shooting parameters
                self.event_system.dispatch_event(
                    GameEvent.create_player_shoot(shooting_data=shooting_data, source="player")
                )

    def _calculate_shooting_parameters(self) -> list[dict]:
        """
        Pure logic: Calculate shooting parameters based on bullet_paths.
        Returns list of bullet creation parameters.
        """
        bullets_data = []

        if self.bullet_paths == 1:
            # Single straight shot
            bullets_data.append(
                {
                    "x": self.rect.centerx,
                    "y": self.rect.top,
                    "speed": self.bullet_speed,
                    "angle": int(BULLET_CONFIG["ANGLE_STRAIGHT"]),
                    "owner": "player",
                }
            )
        elif self.bullet_paths == 2:
            # Double parallel shots
            bullets_data.extend(
                [
                    {
                        "x": self.rect.left + 5,
                        "y": self.rect.top,
                        "speed": self.bullet_speed,
                        "angle": int(BULLET_CONFIG["ANGLE_STRAIGHT"]),
                        "owner": "player",
                    },
                    {
                        "x": self.rect.right - 5,
                        "y": self.rect.top,
                        "speed": self.bullet_speed,
                        "angle": int(BULLET_CONFIG["ANGLE_STRAIGHT"]),
                        "owner": "player",
                    },
                ]
            )
        elif self.bullet_paths == 3:
            # Three shots: one straight, two angled
            bullets_data.extend(
                [
                    {  # Center straight
                        "x": self.rect.centerx,
                        "y": self.rect.top,
                        "speed": self.bullet_speed,
                        "angle": int(BULLET_CONFIG["ANGLE_STRAIGHT"]),
                        "owner": "player",
                    },
                    {  # Left angled
                        "x": self.rect.left + 5,
                        "y": self.rect.top,
                        "speed": self.bullet_speed,
                        "angle": -int(BULLET_CONFIG["ANGLE_SPREAD_SMALL"]),
                        "owner": "player",
                    },
                    {  # Right angled
                        "x": self.rect.right - 5,
                        "y": self.rect.top,
                        "speed": self.bullet_speed,
                        "angle": int(BULLET_CONFIG["ANGLE_SPREAD_SMALL"]),
                        "owner": "player",
                    },
                ]
            )
        elif self.bullet_paths >= 4:
            # Four or more shots (max limit is 4): two straight, two angled
            bullets_data.extend(
                [
                    {  # Left center straight
                        "x": self.rect.centerx - 8,
                        "y": self.rect.top,
                        "speed": self.bullet_speed,
                        "angle": int(BULLET_CONFIG["ANGLE_STRAIGHT"]),
                        "owner": "player",
                    },
                    {  # Right center straight
                        "x": self.rect.centerx + 8,
                        "y": self.rect.top,
                        "speed": self.bullet_speed,
                        "angle": int(BULLET_CONFIG["ANGLE_STRAIGHT"]),
                        "owner": "player",
                    },
                    {  # Left angled
                        "x": self.rect.left + 5,
                        "y": self.rect.top,
                        "speed": self.bullet_speed,
                        "angle": -int(BULLET_CONFIG["ANGLE_SPREAD_LARGE"]),
                        "owner": "player",
                    },
                    {  # Right angled
                        "x": self.rect.right - 5,
                        "y": self.rect.top,
                        "speed": self.bullet_speed,
                        "angle": int(BULLET_CONFIG["ANGLE_SPREAD_LARGE"]),
                        "owner": "player",
                    },
                ]
            )

        return bullets_data

    def _legacy_shoot_fallback(self, shooting_data: list[dict]):
        """
        Legacy fallback when no event system is available.
        This maintains backward compatibility.
        """
        # Import here to avoid circular imports and maintain clean architecture
        from thunder_fighter.entities.projectiles.bullets import Bullet

        bullets = []
        for bullet_data in shooting_data:
            bullet = Bullet(bullet_data["x"], bullet_data["y"], bullet_data["speed"], bullet_data["angle"])
            bullets.append(bullet)

        # Add to sprite groups
        if bullets:
            self.all_sprites.add(*bullets)
            self.bullets_group.add(*bullets)

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

    def launch_missile(self):
        """Launch missile - alias for shoot_missiles for compatibility."""
        self.shoot_missiles()

    def add_wingman(self):
        """Add a wingman"""
        if len(self.wingmen_list) >= int(PLAYER_CONFIG["MAX_WINGMEN"]):
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
        self.flash_timer = int(PLAYER_CONFIG["FLASH_FRAMES"])

        # Create flash effect instead of hit effect
        create_flash_effect(self, WHITE)

        # Play hit sound effect
        if self.sound_manager:
            self.sound_manager.play_sound("player_hit")

        return self.health <= 0  # Return whether dead

    def heal(self, amount=None):
        """Player heals"""
        if amount is None:
            amount = int(PLAYER_CONFIG["HEAL_AMOUNT"])
        self.health = min(int(PLAYER_CONFIG["HEALTH"]), self.health + amount)

    def increase_bullet_speed(self, amount=None):
        """Increase bullet speed"""
        if amount is None:
            amount = int(BULLET_CONFIG["SPEED_UPGRADE_AMOUNT"])
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
        if self.speed >= int(PLAYER_CONFIG["MAX_SPEED"]):
            return False

        self.speed += int(PLAYER_CONFIG["SPEED_UPGRADE_AMOUNT"])
        # Player speed increase should be shown in game UI, not just logged
        logger.info(f"Player speed increased to: {self.speed}")
        return True

    def increase_player_speed(self, amount=None):
        """
        Increase player movement speed - matches method name called in collisions.py

        Args:
            amount: Speed increase amount

        Returns:
            float: Current player speed
        """
        if amount is None:
            amount = int(PLAYER_CONFIG["SPEED_UPGRADE_AMOUNT"])
        # Check if already at max speed
        if self.speed >= int(PLAYER_CONFIG["MAX_SPEED"]):
            return self.speed

        # Increase speed but not exceed max
        self.speed = min(self.max_speed, self.speed + amount)
        logger.info(f"Player speed increased to: {self.speed}")
        return self.speed
