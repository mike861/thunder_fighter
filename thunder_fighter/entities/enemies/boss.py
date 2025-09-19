import random
from typing import Optional

import pygame
import pygame.time as ptime

from thunder_fighter.constants import (
    BOSS_COMBAT,
    BOSS_CONFIG,
    WIDTH,
)
from thunder_fighter.graphics.renderers import create_boss_ship, draw_health_bar
from thunder_fighter.utils.logger import logger


class Boss(pygame.sprite.Sprite):
    """Boss class representing the main enemy with multiple attack patterns and health bar display"""

    def __init__(
        self,
        all_sprites: pygame.sprite.Group,
        boss_bullets_group: pygame.sprite.Group,
        level: Optional[int] = None,
        game_level: int = 1,
        player: Optional[object] = None,
    ) -> None:
        super().__init__()

        # Determine Boss level - if not specified, generate randomly based on game progress
        if level is None:
            # Random level assignment based on game progression
            self.level = min(max(1, game_level // 3 + random.randint(1, 2)), 10)
        else:
            self.level = max(1, min(level, 10))

        self.game_level = game_level
        self.player = player  # Store player reference for tracking

        # Store original image - used to restore during flash effects
        self.image = create_boss_ship(self.level)
        self.original_image = self.image.copy()

        # Adjust attributes based on level
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.y = 20

        # Calculate speed based on level (faster at higher levels)
        self.speedx = 1 + (self.level - 1) * 0.5

        # Create collision mask - used for more precise collision detection
        self.mask = pygame.mask.from_surface(self.image)

        # Adjust health based on level
        base_health = 100
        self.max_health = base_health + (self.level - 1) * 50
        self.health = self.max_health

        # Adjust shooting based on level
        self.shoot_delay = float(
            max(300, int(BOSS_CONFIG["SHOOT_DELAY"]) - (self.level - 1) * 150)
        )  # Higher levels shoot faster

        # Set initial attack mode
        self.shoot_pattern = "normal"

        self.last_shot = ptime.get_ticks()
        self.direction = 1  # Movement direction
        self.move_counter = 0
        self.damage_flash = 0

        # Pre-create flash images
        self.flash_images = self._create_flash_images()

        # Define base movement speed and range
        self.base_speedx = 2
        self.move_margin = BOSS_COMBAT["MOVE_MARGIN"]  # Minimum margin from screen edge

        # Sprite groups
        self.all_sprites = all_sprites
        self.boss_bullets_group = boss_bullets_group

        # Boss initialization info should be displayed in game UI, not just logs
        logger.debug(f"Boss level {self.level} initialized with {self.health} health")

    def _create_flash_images(self):
        """Pre-create flash effect image sequence"""
        flash_images = []

        # Create copy of original image
        base_image = self.original_image.copy()
        flash_images.append(base_image)  # First frame is original image

        # Create multiple flash effect images
        # Method 1: Strong red overlay
        red_image = self.original_image.copy()
        red_overlay = pygame.Surface(red_image.get_size())
        red_overlay.fill((255, 80, 80))  # Very bright red
        red_image.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        flash_images.append(red_image)

        # Method 2: Pure white highlight (most obvious flash effect)
        white_image = self.original_image.copy()
        white_overlay = pygame.Surface(white_image.get_size())
        white_overlay.fill((180, 180, 180))  # Very bright white overlay
        white_image.blit(white_overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        flash_images.append(white_image)

        # Method 3: Yellow warning effect (additional flash variation)
        yellow_image = self.original_image.copy()
        yellow_overlay = pygame.Surface(yellow_image.get_size())
        yellow_overlay.fill((200, 200, 0))  # Bright yellow
        yellow_image.blit(yellow_overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        flash_images.append(yellow_image)

        return flash_images

    def damage(self, amount):
        """Handle Boss damage taken

        Args:
            amount: Damage value

        Returns:
            bool: Returns True if Boss is destroyed, otherwise False
        """
        self.health -= amount
        self.damage_flash = int(BOSS_COMBAT["DAMAGE_FLASH_FRAMES"])  # Increase flash frames for more obvious effect

        # Determine attack mode transitions based on Boss level and health percentage
        health_percentage = self.health / self.max_health

        # Level 2+ Bosses can enter aggressive mode
        if (
            health_percentage <= BOSS_COMBAT["AGGRESSIVE_THRESHOLD"]
            and self.shoot_pattern == "normal"
            and self.level >= 2
        ):
            self.shoot_pattern = "aggressive"
            # When health decreases, reduce shooting delay to increase attack frequency
            self.shoot_delay = max(
                BOSS_COMBAT["MIN_AGGRESSIVE_DELAY"], self.shoot_delay * BOSS_COMBAT["AGGRESSIVE_DELAY_MULTIPLIER"]
            )
            # Boss entering aggressive mode info should be displayed in game UI
            logger.debug(f"Level {self.level} Boss entered aggressive mode! Shoot delay: {self.shoot_delay}")

        # Level 3+ Bosses can enter final mode
        if (
            health_percentage <= BOSS_COMBAT["FINAL_THRESHOLD"]
            and self.shoot_pattern == "aggressive"
            and self.level >= 3
        ):
            self.shoot_pattern = "final"
            # Reduce shooting delay again
            self.shoot_delay = max(
                BOSS_COMBAT["MIN_FINAL_DELAY"], self.shoot_delay * BOSS_COMBAT["FINAL_DELAY_MULTIPLIER"]
            )
            # Boss entering final mode info should be displayed in game UI
            logger.debug(f"Level {self.level} Boss entered final mode! Shoot delay: {self.shoot_delay}")

        # Check if destroyed
        if self.health <= 0:
            self.kill()
            return True

        return False

    def update(self):
        """Update Boss state"""
        # Boss entrance animation
        if self.rect.top < BOSS_COMBAT["ENTRANCE_TARGET_Y"]:
            self.rect.y += BOSS_COMBAT["ENTRANCE_SPEED"]
        else:
            # Left-right movement
            self.move_counter += 1
            if self.move_counter >= BOSS_COMBAT["DIRECTION_CHANGE_INTERVAL"]:  # Change direction periodically
                self.direction *= -1
                self.move_counter = 0

            # Calculate dynamic movement boundaries based on game_level
            # Higher game_level allows moving closer to the edges
            # Reduce margin based on game level, but keep at least a small margin
            current_margin = max(5, self.move_margin + 50 - self.game_level * 5)

            left_boundary = current_margin
            right_boundary = WIDTH - self.rect.width - current_margin

            # Adjust speed slightly based on game level
            current_speedx = self.base_speedx + (self.game_level - 1) * 0.1

            self.rect.x += current_speedx * self.direction

            # Prevent Boss from flying out of dynamic boundaries
            if self.rect.left < left_boundary:
                self.rect.left = left_boundary
                self.direction = 1  # Force move right
                self.move_counter = 0  # Reset move counter to prevent getting stuck
            if self.rect.right > right_boundary:
                self.rect.right = right_boundary
                self.direction = -1  # Force move left
                self.move_counter = 0  # Reset move counter

        # Boss shooting
        now = ptime.get_ticks()
        if now - self.last_shot > self.shoot_delay and self.rect.top >= 0:
            self.last_shot = now
            self.shoot()

        # Damage flash effect
        if self.damage_flash > 0:
            self.damage_flash -= 1

            # Use stronger and more varied flash effects
            if self.damage_flash > 0:
                # Select different effects based on flash frame count to create more dynamic flashing
                flash_cycle = self.damage_flash % 6
                if flash_cycle == 0:
                    self.image = self.flash_images[2]  # White highlight version (most obvious)
                elif flash_cycle == 1:
                    self.image = self.flash_images[3]  # Yellow warning version
                elif flash_cycle == 2:
                    self.image = self.flash_images[2]  # White highlight again
                elif flash_cycle == 3:
                    self.image = self.flash_images[1]  # Red version
                elif flash_cycle == 4:
                    self.image = self.flash_images[0]  # Original version
                else:  # flash_cycle == 5
                    self.image = self.flash_images[1]  # Red version
            else:
                # When flashing ends, ensure original image is restored
                self.image = self.original_image.copy()  # Use copy to avoid reference issues

    def shoot(self):
        """Fire bullets"""
        # Due to circular import, need to import BossBullet externally
        from thunder_fighter.entities.projectiles.bullets import BossBullet

        # Determine bullet count and pattern based on level and attack mode
        if self.shoot_pattern == "normal":
            if self.level == 1:
                # Level 1 Boss: 3 bullets, straight fire
                offsets = [-30, 0, 30]
            elif self.level == 2:
                # Level 2 Boss: 4 bullets, fan distribution
                offsets = [-45, -15, 15, 45]
            else:
                # Level 3 Boss: 5 bullets, denser fan distribution
                offsets = [-60, -30, 0, 30, 60]
        elif self.shoot_pattern == "aggressive":
            # In aggressive mode, increase bullet count and distribution range
            if self.level == 1:
                # Level 1 Boss: 4 bullets, wider fan
                offsets = [-45, -15, 15, 45]
            elif self.level == 2:
                # Level 2 Boss: 5 bullets, wider fan
                offsets = [-60, -30, 0, 30, 60]
            else:
                # Level 3 Boss: 6 bullets, denser fan distribution
                offsets = [-75, -45, -15, 15, 45, 75]
        else:  # "final" mode
            # In final mode, maximum range and bullet count
            if self.level == 1:
                # Level 1 Boss: 5 bullets, wide fan
                offsets = [-60, -30, 0, 30, 60]
            elif self.level == 2:
                # Level 2 Boss: 6 bullets, wide fan
                offsets = [-75, -45, -15, 15, 45, 75]
            else:
                # Level 3 Boss: 7 bullets, almost full-screen fan
                offsets = [-90, -60, -30, 0, 30, 60, 90]

        # Get player position (for Final mode tracking)
        target_pos = None
        if self.shoot_pattern == "final" and self.player and hasattr(self.player, "rect"):
            target_pos = (self.player.rect.centerx, self.player.rect.centery)

        # Fire bullets
        for offset in offsets:
            boss_bullet = BossBullet(self.rect.centerx + offset, self.rect.bottom, self.shoot_pattern, target_pos)
            self.all_sprites.add(boss_bullet)
            self.boss_bullets_group.add(boss_bullet)

    def draw_health_bar(self, surface):
        """Draw Boss health bar"""
        # Calculate health bar size and position
        bar_width = max(self.rect.width + 20, 120)  # Health bar slightly wider than boss, but at least 120 pixels
        bar_height = 12  # Increase health bar height
        bar_x = self.rect.centerx - bar_width // 2  # Center health bar with boss
        bar_y = self.rect.y - 25  # Health bar 25 pixels above boss top

        # Prevent health bar from going off top of screen
        if bar_y < 5:
            bar_y = 5

        # Prevent health bar from going off left/right edges of screen
        if bar_x < 5:
            bar_x = 5
        elif bar_x + bar_width > WIDTH - 5:
            bar_x = WIDTH - bar_width - 5

        # Draw health bar body
        draw_health_bar(surface, bar_x, bar_y, bar_width, bar_height, self.health, self.max_health)

        # Add health bar border effects based on attack mode
        import pygame

        from thunder_fighter.constants import ORANGE, RED, WHITE, YELLOW

        if self.shoot_pattern == "aggressive":
            # Aggressive mode: yellow border
            pygame.draw.rect(surface, YELLOW, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), 2)
        elif self.shoot_pattern == "final":
            # Final mode: flashing red border
            border_color = RED if (pygame.time.get_ticks() // 200) % 2 else ORANGE
            pygame.draw.rect(surface, border_color, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), 3)

        # Draw boss level indicator and mode
        from thunder_fighter.localization import _

        # Get localized boss level text based on mode
        if self.shoot_pattern == "aggressive":
            level_text = _("BOSS_LEVEL_DANGER", self.level)
        elif self.shoot_pattern == "final":
            level_text = _("BOSS_LEVEL_EXTREME", self.level)
        else:
            level_text = _("BOSS_LEVEL_NORMAL", self.level)

        # Use resource manager for better Chinese font support
        from thunder_fighter.utils.resource_manager import get_resource_manager

        resource_manager = get_resource_manager()
        font = resource_manager.load_font(None, 20, system_font=True)

        # Change text color based on mode
        text_color = WHITE
        if self.shoot_pattern == "aggressive":
            text_color = YELLOW
        elif self.shoot_pattern == "final":
            text_color = RED

        level_surface = font.render(level_text, True, text_color)
        level_rect = level_surface.get_rect()
        level_rect.centerx = bar_x + bar_width // 2
        level_rect.bottom = bar_y - 2  # Display above health bar

        # If level text goes off top of screen, display below health bar
        if level_rect.top < 0:
            level_rect.top = bar_y + bar_height + 2

        surface.blit(level_surface, level_rect)

        # Draw health value
        health_text = f"{self.health}/{self.max_health}"
        health_surface = font.render(health_text, True, WHITE)
        health_rect = health_surface.get_rect()
        health_rect.center = (bar_x + bar_width // 2, bar_y + bar_height // 2)
        surface.blit(health_surface, health_rect)
