import math
import random

import pygame
import pygame.time as ptime

from thunder_fighter.constants import (
    ENEMY_CONFIG,
    HEIGHT,
    WIDTH,
)
from thunder_fighter.entities.projectiles.bullets import EnemyBullet
from thunder_fighter.entities.base_3d import Entity3D
from thunder_fighter.config.pseudo_3d_config import (
    SPAWN_DEPTH_CONFIG,
    MOVEMENT_3D_CONFIG,
)
from thunder_fighter.graphics.renderers import create_enemy_ship
from thunder_fighter.utils.logger import logger


class Enemy(Entity3D):
    """Enemy class"""

    def __init__(self, game_time=0, game_level=1, all_sprites=None, enemy_bullets_group=None, spawn_depth=None):
        # Determine level based on game time and game level
        self.level = self._determine_level(game_time, game_level)

        # Calculate spawn depth if not provided
        if spawn_depth is None:
            base_depth = SPAWN_DEPTH_CONFIG["enemy_min_depth"] + (game_level * 30)
            depth_variation = SPAWN_DEPTH_CONFIG["enemy_depth_variation"]
            spawn_depth = base_depth + random.uniform(-depth_variation//2, depth_variation//2)
            spawn_depth = max(SPAWN_DEPTH_CONFIG["enemy_min_depth"],
                            min(SPAWN_DEPTH_CONFIG["enemy_max_depth"], spawn_depth))

        # First, initialize parent classes with placeholder dimensions
        # We need to call super().__init__() before setting the image because
        # GameObject.__init__() sets self.image = None and overwrites our image
        super().__init__(
            x=random.randrange(WIDTH - 45),  # Use default size for now
            y=random.randrange(int(ENEMY_CONFIG["SPAWN_Y_MIN"]), int(ENEMY_CONFIG["SPAWN_Y_MAX"])),
            width=45, height=45,  # Default size
            z=spawn_depth
        )

        # NOW create the image after parent initialization
        try:
            self.image = create_enemy_ship(self.level)
        except Exception as e:
            logger.error(f"Exception in create_enemy_ship for level {self.level}: {e}")
            self.image = None

        # Handle case where image creation fails
        if self.image is None:
            logger.error(f"Failed to create enemy image for level {self.level}, creating fallback")
            try:
                # Create a simple fallback surface
                self.image = pygame.Surface((45, 45))
                self.image.set_colorkey((0, 0, 0))
                pygame.draw.rect(self.image, (255, 0, 0), (10, 10, 25, 25))  # Red square as fallback
                pygame.draw.rect(self.image, (255, 255, 255), (10, 10, 25, 25), 2)  # White border
            except Exception as e:
                logger.error(f"Failed to create fallback image: {e}")
                # Last resort - create minimal surface
                self.image = pygame.Surface((30, 30))

        # Update dimensions based on actual image
        image_rect = self.image.get_rect()
        self.width = image_rect.width
        self.height = image_rect.height

        # Recalculate spawn position with correct dimensions
        spawn_x = random.randrange(WIDTH - image_rect.width)
        spawn_y = random.randrange(int(ENEMY_CONFIG["SPAWN_Y_MIN"]), int(ENEMY_CONFIG["SPAWN_Y_MAX"]))

        # Update position
        self.x = spawn_x
        self.y = spawn_y

        # Set up rect for collision detection
        self.rect = self.image.get_rect()
        self.rect.x = spawn_x
        self.rect.y = spawn_y

        # Set up 3D movement
        z_velocity_min = MOVEMENT_3D_CONFIG["enemy_z_velocity_min"]
        z_velocity_max = MOVEMENT_3D_CONFIG["enemy_z_velocity_max"]
        self.set_z_velocity(random.uniform(z_velocity_min, z_velocity_max))

        # Enable depth oscillation for visual interest
        if MOVEMENT_3D_CONFIG["depth_oscillation_enabled"]:
            amplitude = random.uniform(
                MOVEMENT_3D_CONFIG["oscillation_amplitude_min"],
                MOVEMENT_3D_CONFIG["oscillation_amplitude_max"]
            )
            frequency = MOVEMENT_3D_CONFIG["oscillation_frequency"]
            self.enable_depth_oscillation(amplitude, frequency)

        # Add detailed logging here
        logger.debug(f"Enemy spawned - Level: {self.level}, Depth: {spawn_depth:.1f}, ENEMY_SHOOT_LEVEL: {int(ENEMY_CONFIG['SHOOT_LEVEL'])}")

        # Adjust speed based on game time and level
        base_speed_factor = min(3.0, 1.0 + game_time / 60.0)
        level_speed_bonus = self.level * 0.2
        total_speed_factor = base_speed_factor + level_speed_bonus
        self.speedy = random.randrange(1, int(3 + 3 * total_speed_factor))
        self.speedx = random.randrange(
            int(ENEMY_CONFIG["HORIZONTAL_MOVE_MIN"]), int(ENEMY_CONFIG["HORIZONTAL_MOVE_MAX"])
        )

        # Set velocities for Entity3D system
        self.velocity_y = self.speedy
        self.velocity_x = self.speedx

        # Rotation animation properties
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()
        self.original_image = self.image.copy()

        # Shooting capability - ensure enemies only shoot if they're level 2 or higher
        # Since we use 0-based indexing in _determine_level (levels 0-10),
        # and ENEMY_SHOOT_LEVEL=2 means "from level 2", we need to check if level >= 2
        self.can_shoot = self.level >= int(ENEMY_CONFIG["SHOOT_LEVEL"])
        logger.debug(f"Enemy ID:{id(self)} Level: {self.level}, Can Shoot: {self.can_shoot}")

        # Sprite groups for bullets
        self.all_sprites = all_sprites
        self.enemy_bullets_group = enemy_bullets_group

        # Shooting properties
        # Initialize shooting properties for all enemies (even non-shooting ones)
        base_delay = 800
        level_reduction = self.level * 50
        self.shoot_delay = max(int(ENEMY_CONFIG["MIN_SHOOT_DELAY"]), base_delay - level_reduction)
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
        - Level 2 and above enemies can shoot (determined by ENEMY_CONFIG["SHOOT_LEVEL"]=2 constant)
        - Higher level enemies have more health, speed and attack power
        """
        # Base probabilities (based on game time)
        base_probs = [
            max(0, 0.35 - game_time * 0.05),  # Level 0
            max(0, 0.25 - game_time * 0.03),  # Level 1
            max(0, 0.15),  # Level 2
            max(0, 0.10 + game_time * 0.01),  # Level 3
            max(0, 0.05 + game_time * 0.015),  # Level 4
            max(0, 0.05 + game_time * 0.015),  # Level 5
            max(0, 0.02 + game_time * 0.01),  # Level 6
            max(0, 0.02 + game_time * 0.01),  # Level 7
            max(0, 0.01 + game_time * 0.005),  # Level 8
            max(0, 0.00 + game_time * 0.003),  # Level 9
            max(0, 0.00 + game_time * 0.002),  # Level 10
        ]

        # Game level influence - increase probability of high-level enemies
        # Each game level slightly increases high-level enemy appearance rate
        level_boost = (game_level - 1) * 0.02  # 2% increase per level

        # Transfer probability from low to high levels (simple linear transfer)
        transfer_prob = 0.0
        for i in range(len(base_probs)):
            # Transfer probability from level 0-4 enemies
            if i < 5:
                reduction = base_probs[i] * level_boost * (5 - i) / 5  # Lower levels lose more
                reduction = min(base_probs[i], reduction)  # Cannot reduce more than current probability
                base_probs[i] -= reduction
                transfer_prob += reduction
            # Add probability to level 5-10 enemies
            elif i >= 5:
                # Distribute transferred probability proportionally
                boost_share = transfer_prob / max(1, len(base_probs) - 5)  # Equal distribution
                base_probs[i] += boost_share
                transfer_prob -= boost_share  # Update remaining transfer probability

        # Ensure probabilities are non-negative and make minor adjustments to prevent all zeros
        for i in range(len(base_probs)):
            base_probs[i] = max(0.001, base_probs[i])  # Ensure each level has minimal probability

        # Normalize probabilities to sum to 1
        total = sum(base_probs)
        if total > 0:
            probs = [p / total for p in base_probs]
        else:
            probs = [1 / len(base_probs)] * len(base_probs)

        # Choose level based on final probabilities
        chosen_level = random.choices(range(11), weights=probs, k=1)[0]

        # Ensure enemy level doesn't exceed game level + 2
        max_allowed_level = min(10, game_level + 2)
        chosen_level = min(chosen_level, max_allowed_level)

        logger.debug(
            f"Determined enemy level {chosen_level} (game_time: {game_time:.1f}, game_level: {game_level}, max_allowed: {max_allowed_level})"
        )
        return chosen_level

    def update(self, dt: float = 1.0/60.0):
        """Update enemy state with 3D movement"""
        # Capture state before update for analysis
        old_logical_pos = (self.x, self.y)
        old_screen_pos = self.get_screen_position()
        old_scale = self.get_depth_scale()
        old_visual_size = self.get_visual_size()
        old_rect_pos = (self.rect.x, self.rect.y)

        # Update velocities BEFORE calling super().update() to avoid 1-frame delay
        # Convert from pixels/frame to pixels/second for Entity3D system
        self.velocity_x = self.speedx * 60.0  # Convert to pixels/second
        self.velocity_y = self.speedy * 60.0  # Convert to pixels/second

        # Call parent 3D update which handles depth movement and position
        super().update(dt)

        # Debug analysis every 5 seconds (300 frames at 60 FPS)
        if not hasattr(self, '_detailed_debug_counter'):
            self._detailed_debug_counter = 0
        self._detailed_debug_counter += 1

        if self._detailed_debug_counter % 300 == 0:  # Every 5 seconds
            new_logical_pos = (self.x, self.y)
            new_screen_pos = self.get_screen_position()
            new_scale = self.get_depth_scale()
            new_visual_size = self.get_visual_size()
            new_rect_pos = (self.rect.x, self.rect.y)

            logical_movement = (new_logical_pos[0] - old_logical_pos[0], new_logical_pos[1] - old_logical_pos[1])
            screen_movement = (new_screen_pos[0] - old_screen_pos[0], new_screen_pos[1] - old_screen_pos[1])
            rect_movement = (new_rect_pos[0] - old_rect_pos[0], new_rect_pos[1] - old_rect_pos[1])

            logger.info(f"[DETAILED] Enemy {id(self)} Analysis:")
            logger.info(f"  Logical: ({old_logical_pos[0]:.1f},{old_logical_pos[1]:.1f}) → ({new_logical_pos[0]:.1f},{new_logical_pos[1]:.1f}) Δ({logical_movement[0]:+.1f},{logical_movement[1]:+.1f})")
            logger.info(f"  Screen:  ({old_screen_pos[0]:.1f},{old_screen_pos[1]:.1f}) → ({new_screen_pos[0]:.1f},{new_screen_pos[1]:.1f}) Δ({screen_movement[0]:+.1f},{screen_movement[1]:+.1f})")
            logger.info(f"  Rect:    ({old_rect_pos[0]},{old_rect_pos[1]}) → ({new_rect_pos[0]},{new_rect_pos[1]}) Δ({rect_movement[0]:+},{rect_movement[1]:+})")
            logger.info(f"  Scale:   {old_scale:.3f} → {new_scale:.3f}, Size: {old_visual_size} → {new_visual_size}")
            logger.info(f"  Depth:   {self.z:.1f}, Velocity: ({self.velocity_x},{self.velocity_y})")

            # Determine visual movement direction
            if screen_movement[1] > 0:
                visual_direction = "DOWN"
            elif screen_movement[1] < 0:
                visual_direction = "UP"
            else:
                visual_direction = "STATIC"

            logger.info(f"  VISUAL MOVEMENT: {visual_direction} (screen Y change: {screen_movement[1]:+.1f})")

        # Reverse horizontal direction if enemy hits the screen edges
        # Note: Use logical position for boundary checking, not visual position
        if self.x + self.width > WIDTH or self.x < 0:
            self.speedx = -self.speedx
            self.velocity_x = self.speedx

        # Rotation animation (only for fast-moving enemies)
        if abs(self.speedx) > 1:
            now = pygame.time.get_ticks()
            if now - self.last_update > int(ENEMY_CONFIG["ROTATION_UPDATE"]):
                self.last_update = now
                self.rot = (self.rot + self.rot_speed) % 360

                # Quantize rotation angle to improve cache performance
                # Only use angles in 15-degree increments for better caching
                quantized_angle = round(self.rot / 15) * 15

                # Create rotated image from original with quantized angle
                rotated_image = pygame.transform.rotate(self.original_image, quantized_angle)
                self.image = rotated_image

        # Check for off-screen removal (use logical position)
        if (
            self.y > HEIGHT + int(ENEMY_CONFIG["SCREEN_BOUNDS"])
            or self.x < -int(ENEMY_CONFIG["SCREEN_BOUNDS"])
            or self.x > WIDTH + int(ENEMY_CONFIG["SCREEN_BOUNDS"])
            or self.z <= 50  # Remove if too close (3D specific)
        ):
            logger.debug(f"Enemy ID:{id(self)} killed (off-screen or too close, z={self.z:.1f}).")
            self.kill()

        # Check if enemy can shoot
        time_now = ptime.get_ticks()
        if self.can_shoot and time_now - self.last_shot > self.shoot_delay:
            # Check if enemy is visible on screen (use visual position)
            screen_pos = self.get_screen_position()
            visual_size = self.get_visual_size()
            if (screen_pos[1] + visual_size[1] > 0 and
                screen_pos[1] < HEIGHT and
                self.should_render()):  # Only shoot if visually significant
                if self.shoot():
                    self.last_shot = time_now
                    # Log shooting event (changed from print)
                    logger.debug(f"Enemy ID:{id(self)} Level:{self.level} Depth:{self.z:.0f} Fired! Delay:{self.shoot_delay}ms")

    def shoot(self):
        """Fires a bullet"""
        try:
            # Ensure sprite groups exist
            if not hasattr(self, "all_sprites") or not hasattr(self, "enemy_bullets_group"):
                logger.error(f"Error: Enemy {id(self)} missing required sprite groups for shooting.")
                return False

            # Double-check shooting capability and level requirement
            if not self.can_shoot or self.level < int(ENEMY_CONFIG["SHOOT_LEVEL"]):
                logger.warning(
                    f"Enemy ID:{id(self)} attempted to shoot but can_shoot={self.can_shoot}, level={self.level}, required level={int(ENEMY_CONFIG['SHOOT_LEVEL'])}"
                )
                return False

            # Create bullet at enemy's visual position
            # TODO: Upgrade EnemyBullet to 3D support in Phase 2
            screen_pos = self.get_screen_position()
            bullet = EnemyBullet(
                screen_pos[0], screen_pos[1] + self.get_visual_size()[1] // 2,
                self.level
            )

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

    def render(self, screen: pygame.Surface):
        """
        Standard 2D render method for compatibility.

        This provides backward compatibility with 2D rendering while the 3D
        system uses render_3d() method from Entity3D base class.
        """
        if self.image and self.rect:
            screen.blit(self.image, self.rect)
