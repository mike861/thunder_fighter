import math
import random
from typing import Optional, Tuple, Callable, Any

import pygame

from thunder_fighter.constants import (
    BOSS_BULLET_CONFIG,
    HEIGHT,
    WIDTH,
)
from thunder_fighter.graphics.renderers import create_bullet
from thunder_fighter.utils.logger import logger
from thunder_fighter.entities.projectiles.logic import BulletLogic


class Bullet(pygame.sprite.Sprite):
    """Player bullet class with logic/graphics separation"""

    def __init__(self, x, y, speed=10, angle=0, renderer: Optional[Callable[[], pygame.Surface]] = None):
        """Initialize bullet with optional renderer injection.
        
        Args:
            x: Initial X position
            y: Initial Y position  
            speed: Movement speed
            angle: Movement angle in degrees
            renderer: Optional graphics renderer function (for testing/injection)
        """
        pygame.sprite.Sprite.__init__(self)
        
        # Initialize pure business logic
        self.logic = BulletLogic(x, y, speed, angle)
        
        # Initialize graphics (with optional injection for testing)
        self._setup_graphics(x, y, angle, renderer)
    
    def _setup_graphics(self, x: float, y: float, angle: float, 
                       renderer: Optional[Callable[[], pygame.Surface]] = None) -> None:
        """Setup graphics components with optional renderer injection."""
        # Use injected renderer or default
        graphics_renderer = renderer or create_bullet
        self.image = graphics_renderer()
        self.rect = self.image.get_rect()
        self.rect.centerx = int(x)
        self.rect.bottom = int(y)

        # Rotate image when angle is not 0
        if angle != 0:
            self.image = pygame.transform.rotate(self.image, -angle)
            self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        """Update bullet position using logic layer"""
        # Calculate new position using pure logic
        new_x, new_y = self.logic.update_position()
        
        # Update graphics position
        self.rect.centerx = int(new_x)
        self.rect.centery = int(new_y)

        # Check boundaries using logic layer
        if self.logic.is_out_of_bounds(WIDTH, HEIGHT):
            self.kill()


class BossBullet(pygame.sprite.Sprite):
    """Boss bullet class that supports bullet variations for different attack modes.

    Creates bullets with different appearance, speed, damage and movement patterns
    based on Boss attack mode (normal/aggressive/final). Final mode bullets support
    initial direction tracking.

    Attributes:
        shoot_pattern (str): Attack mode - "normal", "aggressive", or "final"
        damage (int): Bullet damage value
        speedx (float): Horizontal movement speed
        speedy (float): Vertical movement speed
        image (pygame.Surface): Bullet appearance image
        rect (pygame.Rect): Bullet collision rectangle
    """

    def __init__(
        self, x: int, y: int, shoot_pattern: str = "normal", target_pos: Optional[Tuple[int, int]] = None
    ) -> None:
        """Initialize Boss bullet.

        Args:
            x: Initial bullet X coordinate
            y: Initial bullet Y coordinate
            shoot_pattern: Attack mode, valid values: "normal", "aggressive", "final"
            target_pos: Target position (x, y), only used in final mode for tracking direction calculation

        Raises:
            ValueError: When attack mode is not within valid range

        Note:
            Final mode tracking only affects direction calculation at firing moment,
            afterwards bullet flies in straight line
        """
        super().__init__()

        try:
            # Validate attack mode
            valid_patterns = ["normal", "aggressive", "final"]
            if shoot_pattern not in valid_patterns:
                logger.warning(f"Invalid shoot_pattern '{shoot_pattern}', defaulting to 'normal'")
                shoot_pattern = "normal"

            self.shoot_pattern: str = shoot_pattern

            # Create bullets with different appearance based on attack mode
            self.image: pygame.Surface = self._create_boss_bullet()
            self.rect: pygame.Rect = self.image.get_rect()
            self.rect.centerx = x
            self.rect.top = y

            # Set different speed and damage based on attack mode
            self._setup_bullet_properties()

            # Final mode tracking logic (only affects firing direction)
            if shoot_pattern == "final" and target_pos is not None:
                self._setup_tracking_movement(x, y, target_pos)
            else:
                # Normal straight movement
                self.speedx: float = 0.0
                self.speedy: float = float(self.base_speed)

            logger.debug(
                f"BossBullet created: pattern={shoot_pattern}, "
                f"damage={self.damage}, speed=({self.speedx:.1f}, {self.speedy:.1f})"
            )

        except Exception as e:
            logger.error(f"Error creating BossBullet: {e}", exc_info=True)
            # Fall back to default settings
            self._setup_fallback_bullet()

    def _setup_bullet_properties(self) -> None:
        """Set bullet properties based on attack mode."""
        if self.shoot_pattern == "normal":
            self.base_speed: int = int(BOSS_BULLET_CONFIG["NORMAL_SPEED"])
            self.damage: int = int(BOSS_BULLET_CONFIG["NORMAL_DAMAGE"])
        elif self.shoot_pattern == "aggressive":
            self.base_speed = int(BOSS_BULLET_CONFIG["AGGRESSIVE_SPEED"])
            self.damage = int(BOSS_BULLET_CONFIG["AGGRESSIVE_DAMAGE"])
        else:  # final mode
            self.base_speed = int(BOSS_BULLET_CONFIG["FINAL_SPEED"])
            self.damage = int(BOSS_BULLET_CONFIG["FINAL_DAMAGE"])

    def _setup_tracking_movement(self, x: int, y: int, target_pos: Tuple[int, int]) -> None:
        """Set Final mode tracking movement.

        Args:
            x: Bullet start X coordinate
            y: Bullet start Y coordinate
            target_pos: Target position (x, y)
        """
        try:
            # Calculate direction vector towards player
            dx: float = float(target_pos[0] - x)
            dy: float = float(target_pos[1] - y)
            distance: float = math.sqrt(dx * dx + dy * dy)

            if distance > 0:
                # Normalize direction vector and apply speed
                self.speedx = (
                    (dx / distance) * self.base_speed * float(BOSS_BULLET_CONFIG["TRACKING_HORIZONTAL_FACTOR"])
                )
                self.speedy = max(
                    float(BOSS_BULLET_CONFIG["MINIMUM_VERTICAL_SPEED"]), (dy / distance) * self.base_speed
                )
            else:
                self.speedx = 0.0
                self.speedy = float(self.base_speed)
        except (TypeError, ValueError) as e:
            logger.warning(f"Error calculating tracking movement: {e}, using default movement")
            self.speedx = 0.0
            self.speedy = float(self.base_speed)

    def _setup_fallback_bullet(self) -> None:
        """Set fallback bullet properties (used in error cases)."""
        self.shoot_pattern = "normal"
        self.base_speed = int(BOSS_BULLET_CONFIG["NORMAL_SPEED"])
        self.damage = int(BOSS_BULLET_CONFIG["NORMAL_DAMAGE"])
        self.speedx = 0.0
        self.speedy = float(self.base_speed)
        try:
            self.image = self._create_boss_bullet()
            self.rect = self.image.get_rect()
        except Exception:
            # Final fallback option
            self.image = pygame.Surface((int(BOSS_BULLET_CONFIG["BASE_WIDTH"]), int(BOSS_BULLET_CONFIG["BASE_HEIGHT"])))
            self.image.fill((255, 0, 255))  # Purple as error indicator
            self.rect = self.image.get_rect()

    def _create_boss_bullet(self) -> pygame.Surface:
        """Create bullets with different appearance based on attack mode.

        Returns:
            Created bullet surface image

        Raises:
            Exception: When image creation fails
        """
        try:
            if self.shoot_pattern == "normal":
                # Normal mode: purple bullet
                return self._create_bullet_sprite(
                    tuple(BOSS_BULLET_CONFIG["NORMAL_COLOR_PRIMARY"]),
                    tuple(BOSS_BULLET_CONFIG["NORMAL_COLOR_SECONDARY"]),
                )
            elif self.shoot_pattern == "aggressive":
                # Aggressive mode: red bullet, slightly larger
                return self._create_bullet_sprite(
                    tuple(BOSS_BULLET_CONFIG["AGGRESSIVE_COLOR_PRIMARY"]),
                    tuple(BOSS_BULLET_CONFIG["AGGRESSIVE_COLOR_SECONDARY"]),
                    size_multiplier=float(BOSS_BULLET_CONFIG["AGGRESSIVE_SIZE_MULTIPLIER"]),
                )
            else:  # final mode
                # Final mode: blue-white tracking bullet with effects
                return self._create_bullet_sprite(
                    tuple(BOSS_BULLET_CONFIG["FINAL_COLOR_PRIMARY"]),
                    tuple(BOSS_BULLET_CONFIG["FINAL_COLOR_SECONDARY"]),
                    size_multiplier=float(BOSS_BULLET_CONFIG["FINAL_SIZE_MULTIPLIER"]),
                    glow=True,
                )
        except Exception as e:
            logger.error(f"Error creating boss bullet sprite: {e}", exc_info=True)
            # Fall back to simple purple rectangle
            surface = pygame.Surface((int(BOSS_BULLET_CONFIG["BASE_WIDTH"]), int(BOSS_BULLET_CONFIG["BASE_HEIGHT"])))
            surface.fill(tuple(BOSS_BULLET_CONFIG["NORMAL_COLOR_PRIMARY"]))
            return surface

    def _create_bullet_sprite(
        self,
        primary_color: Tuple[int, int, int],
        secondary_color: Tuple[int, int, int],
        size_multiplier: float = 1.0,
        glow: bool = False,
    ) -> pygame.Surface:
        """Create bullet sprite image.

        Args:
            primary_color: Primary color RGB tuple
            secondary_color: Secondary color RGB tuple
            size_multiplier: Size multiplier
            glow: Whether to add glow effect

        Returns:
            Created bullet surface image

        Raises:
            ValueError: When color values are invalid
            Exception: When image creation fails
        """
        try:
            base_width: int = int(int(BOSS_BULLET_CONFIG["BASE_WIDTH"]) * size_multiplier)
            base_height: int = int(int(BOSS_BULLET_CONFIG["BASE_HEIGHT"]) * size_multiplier)

            bullet_surface = pygame.Surface((base_width, base_height), pygame.SRCALPHA)

            # Draw bullet body
            main_body_height = base_height - 5
            pygame.draw.rect(bullet_surface, primary_color, (0, 0, base_width, main_body_height))
            pygame.draw.rect(bullet_surface, secondary_color, (0, main_body_height, base_width, 5))

            # Add light effect edges
            center_x = base_width // 2
            pygame.draw.line(bullet_surface, (255, 255, 255), (center_x, 0), (center_x, main_body_height), 2)

            # Add glow effect for Final mode
            if glow:
                return self._add_glow_effect(bullet_surface, primary_color, base_width, base_height)

            return bullet_surface

        except (ValueError, TypeError) as e:
            logger.error(f"Error creating bullet sprite: {e}", exc_info=True)
            # Fall back to basic rectangle
            surface = pygame.Surface((int(BOSS_BULLET_CONFIG["BASE_WIDTH"]), int(BOSS_BULLET_CONFIG["BASE_HEIGHT"])))
            surface.fill(primary_color)
            return surface

    def _add_glow_effect(
        self, bullet_surface: pygame.Surface, primary_color: Tuple[int, int, int], base_width: int, base_height: int
    ) -> pygame.Surface:
        """Add glow effect to bullet.

        Args:
            bullet_surface: Original bullet surface
            primary_color: Glow color
            base_width: Bullet width
            base_height: Bullet height

        Returns:
            Surface with glow effect
        """
        try:
            glow_size = int(BOSS_BULLET_CONFIG["GLOW_EFFECT_SIZE"])
            glow_surface = pygame.Surface((base_width + glow_size, base_height + glow_size), pygame.SRCALPHA)

            # Create glow circle
            for i in range(int(BOSS_BULLET_CONFIG["GLOW_LAYERS"])):
                alpha = 60 - i * 20
                glow_color = (*primary_color, alpha)
                offset = 2 - i
                size_add = i * 2
                pygame.draw.ellipse(
                    glow_surface, glow_color, (offset, offset, base_width + 4 + size_add, base_height + 4 + size_add)
                )

            # Draw main bullet on glow surface
            glow_surface.blit(bullet_surface, (4, 4))
            return glow_surface

        except Exception as e:
            logger.warning(f"Failed to add glow effect: {e}, returning original surface")
            return bullet_surface

    def update(self) -> None:
        """Update bullet position and check boundaries.

        Bullet moves at set speed, automatically destroys if exceeding screen boundaries.
        """
        try:
            self.rect.y += int(self.speedy)
            self.rect.x += int(self.speedx)

            # Remove bullet if it goes off bottom or left/right edges of screen
            if self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
                self.kill()
                logger.debug(f"BossBullet destroyed: out of bounds at ({self.rect.x}, {self.rect.y})")

        except Exception as e:
            logger.error(f"Error updating BossBullet: {e}", exc_info=True)
            self.kill()  # Destroy bullet when error occurs

    def get_damage(self) -> int:
        """Get bullet damage value.

        Returns:
            Damage value caused by bullet
        """
        return getattr(self, "damage", int(BOSS_BULLET_CONFIG["NORMAL_DAMAGE"]))


class EnemyBullet(pygame.sprite.Sprite):
    """Enemy bullet class with level-based variations"""

    def __init__(self, x, y, enemy_level=0):
        pygame.sprite.Sprite.__init__(self)
        # Create bullets with different appearances based on enemy level
        self.enemy_level = enemy_level
        self.image = self._create_enemy_bullet()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        # Move bullet spawn position slightly down to ensure it's not blocked by enemy aircraft
        self.rect.top = y + 5

        # Bullet speed correlates with enemy level, adjusted to more reasonable values
        base_speed = 5  # Reduced base speed
        level_bonus = min(3, enemy_level * 0.5)  # Reduced level bonus
        self.speedy = base_speed + level_bonus

        # High-level enemy bullets may have horizontal speed
        if enemy_level >= 5:
            # Level 5+ has 25% chance for horizontal movement (reduced probability)
            if random.random() < 0.25:
                self.speedx = random.choice([-2, -1, 1, 2])  # Reduced horizontal speed
                # Level 8+ may have additional curve movement
                if enemy_level >= 8:
                    self.curve = True
                    self.angle = 0
                    self.curve_amplitude = random.uniform(0.5, 1.5)  # Reduced curve amplitude
                else:
                    self.curve = False
            else:
                self.speedx = 0
                self.curve = False
        else:
            self.speedx = 0
            self.curve = False

        # Log bullet creation
        logger.debug(
            f"EnemyBullet created: Pos=({x}, {self.rect.top}), SpeedY={self.speedy:.2f}, SpeedX={getattr(self, 'speedx', 0)}, Level={enemy_level}"
        )

    def _create_enemy_bullet(self):
        """Create bullet appearance based on enemy level"""
        # Reduce bullet size, decrease level-based scaling
        bullet_size = 4 + min(3, self.enemy_level // 2)  # Reduced base size and level growth coefficient

        # Create bullet surface with reduced overall size
        bullet_surface = pygame.Surface((bullet_size * 1.5, bullet_size * 2), pygame.SRCALPHA)

        # Color changes based on enemy level
        if self.enemy_level < 3:
            # Low-level enemy bullets: red
            bullet_color = (255, 50, 50)  # Brighter red
            glow_color = (255, 100, 100, 120)  # Reduced glow opacity
        elif self.enemy_level < 6:
            # Mid-level enemy bullets: orange
            bullet_color = (255, 160, 0)  # Brighter orange
            glow_color = (255, 220, 0, 120)  # Reduced glow opacity
        elif self.enemy_level < 9:
            # High-level enemy bullets: blue
            bullet_color = (50, 170, 255)  # Brighter blue
            glow_color = (100, 200, 255, 120)  # Reduced glow opacity
        else:
            # Ultra high-level enemy bullets: purple
            bullet_color = (200, 50, 250)  # Brighter purple
            glow_color = (220, 100, 250, 120)  # Reduced glow opacity

        # Draw bullet core with reduced size
        pygame.draw.rect(bullet_surface, bullet_color, (bullet_size / 2, 0, bullet_size / 1.5, bullet_size * 1.5))

        # Draw bullet tail with reduced size
        pygame.draw.rect(
            bullet_surface, (200, 200, 200), (bullet_size / 2, bullet_size * 1.5, bullet_size / 1.5, bullet_size / 2)
        )

        # Add white border to increase visibility
        pygame.draw.rect(bullet_surface, (255, 255, 255), (bullet_size / 2, 0, bullet_size / 1.5, bullet_size * 1.5), 1)

        # Reduce glow effect
        # Create smaller glow circle
        glow_size = bullet_size * 3  # Previously * 5, reduced glow range
        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surface, glow_color, (glow_size / 2, glow_size / 2), bullet_size * 1
        )  # Previously * 1.5

        # Draw glow effect on bullet surface, adjust offset for new size
        bullet_surface.blit(
            glow_surface, (-glow_size / 2 + bullet_size / 2, -bullet_size / 2), special_flags=pygame.BLEND_ALPHA_SDL2
        )

        return bullet_surface

    def update(self):
        """Update bullet position"""
        try:
            # Vertical movement
            self.rect.y += self.speedy

            # Horizontal movement
            if hasattr(self, "speedx") and self.speedx != 0:
                self.rect.x += self.speedx

                # Curve movement (only for high-level enemy bullets)
                if hasattr(self, "curve") and self.curve:
                    if not hasattr(self, "angle"):
                        self.angle = 0
                    self.angle = (self.angle + 5) % 360
                    curve_offset = int(self.curve_amplitude * pygame.math.Vector2(1, 0).rotate(self.angle).x)
                    self.rect.x += curve_offset

            # Remove bullet if it goes off screen
            if self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
                logger.debug(f"EnemyBullet {id(self)} killed (off-screen).")
                self.kill()
        except Exception as e:
            # Log update error
            logger.error(f"EnemyBullet update error: {str(e)}", exc_info=True)
            self.kill()  # Remove bullet on error
