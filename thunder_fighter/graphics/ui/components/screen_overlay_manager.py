"""
Screen Overlay Manager Component

Manages special screen overlays including pause screen, victory screen,
game over screen, and level change animations.
"""

import time

import pygame

from thunder_fighter.constants import GREEN, HEIGHT, RED, WHITE, WIDTH, YELLOW
from thunder_fighter.localization import _
from thunder_fighter.utils.logger import logger


class ScreenOverlayManager:
    """Manages all special screen overlays."""

    def __init__(self, screen, fonts):
        """
        Initialize the screen overlay manager.

        Args:
            screen: pygame.Surface - The game screen to draw on
            fonts: dict - Dictionary of fonts with keys 'small', 'medium', 'large'
        """
        self.screen = screen
        self.font_small = fonts.get("small")
        self.font_medium = fonts.get("medium")
        self.font_large = fonts.get("large")

        # Animation timers
        self.level_change_timer = 0.0
        self.level_change_active = False
        self.blink_timer = 0.0
        self.show_blink_text = True

        # Victory screen flag
        self._victory_notifications_added = False

    def update(self):
        """Update animation states."""
        current_time = time.time()

        # Update blink effect timer
        if current_time - self.blink_timer > 0.5:  # Switch every 0.5 seconds
            self.blink_timer = current_time
            self.show_blink_text = not self.show_blink_text

        # Handle level change animation
        if self.level_change_active:
            if current_time - self.level_change_timer > 3.0:  # Animation lasts 3 seconds
                self.level_change_active = False

    def draw_pause_screen(self, is_paused):
        """
        Draw pause screen overlay.

        Args:
            is_paused: Whether the game is paused
        """
        if not is_paused:
            return

        # Create semi-transparent overlay
        pause_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pause_overlay.fill((0, 0, 0, 150))  # Semi-transparent black
        self.screen.blit(pause_overlay, (0, 0))

        # Draw pause text
        pause_text = self.font_large.render(_("GAME_PAUSED"), True, WHITE)
        text_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        self.screen.blit(pause_text, text_rect)

        # Draw tip text
        tip_text = self.font_medium.render(_("RESUME_PROMPT"), True, WHITE)
        tip_rect = tip_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        self.screen.blit(tip_text, tip_rect)

        controls_text = self.font_small.render(_("CONTROLS_INFO"), True, WHITE)
        controls_rect = controls_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        self.screen.blit(controls_text, controls_rect)

    def draw_victory_screen(self, final_score, max_level, game_time):
        """
        Draw victory screen overlay.

        Args:
            final_score: Final score achieved
            max_level: Maximum level reached
            game_time: Total game time in seconds
        """
        # Create semi-transparent overlay
        victory_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        victory_overlay.fill((0, 0, 0, 120))  # Semi-transparent black overlay
        self.screen.blit(victory_overlay, (0, 0))

        # Create a victory panel in the center
        panel_width = 400
        panel_height = 300
        panel_x = (WIDTH - panel_width) // 2
        panel_y = (HEIGHT - panel_height) // 2

        # Draw victory panel background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((20, 40, 80, 200))  # Semi-transparent blue panel

        # Draw panel border
        pygame.draw.rect(panel_surface, GREEN, (0, 0, panel_width, panel_height), 3)

        self.screen.blit(panel_surface, (panel_x, panel_y))

        # Draw victory text
        victory_text = self.font_large.render(_("VICTORY"), True, GREEN)
        text_rect = victory_text.get_rect(center=(WIDTH // 2, panel_y + 60))
        self.screen.blit(victory_text, text_rect)

        # Draw level cleared information
        level_text = self.font_medium.render(_("LEVEL_CLEARED", max_level), True, WHITE)
        level_rect = level_text.get_rect(center=(WIDTH // 2, panel_y + 120))
        self.screen.blit(level_text, level_rect)

        # Draw final score
        score_text = self.font_medium.render(_("FINAL_SCORE", final_score), True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH // 2, panel_y + 160))
        self.screen.blit(score_text, score_rect)

        # Draw survival time
        time_text = self.font_medium.render(_("SURVIVAL_TIME", round(game_time, 1)), True, WHITE)
        time_rect = time_text.get_rect(center=(WIDTH // 2, panel_y + 200))
        self.screen.blit(time_text, time_rect)

        # Draw tip text (blinking)
        if self.show_blink_text:
            exit_text = self.font_small.render(_("EXIT_PROMPT"), True, YELLOW)
            exit_rect = exit_text.get_rect(center=(WIDTH // 2, panel_y + 250))
            self.screen.blit(exit_text, exit_rect)

    def draw_game_over_screen(self, final_score, level_reached, game_time):
        """
        Draw game over screen overlay.

        Args:
            final_score: Final score achieved
            level_reached: Level reached before game over
            game_time: Total game time in seconds
        """
        # Create semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((40, 10, 10, 200))  # Semi-transparent dark red
        self.screen.blit(overlay, (0, 0))

        # Create a game over panel in the center
        panel_width = 500
        panel_height = 400
        panel_x = (WIDTH - panel_width) // 2
        panel_y = (HEIGHT - panel_height) // 2

        # Draw game over panel background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((60, 20, 20, 220))  # Semi-transparent dark red panel

        # Draw panel border
        pygame.draw.rect(panel_surface, RED, (0, 0, panel_width, panel_height), 3)

        self.screen.blit(panel_surface, (panel_x, panel_y))

        # Draw game over text
        gameover_text = self.font_large.render(_("GAME_OVER"), True, RED)
        text_rect = gameover_text.get_rect(center=(WIDTH // 2, panel_y + 50))
        self.screen.blit(gameover_text, text_rect)

        # Draw performance summary title
        summary_text = self.font_medium.render(_("PERFORMANCE_SUMMARY"), True, WHITE)
        summary_rect = summary_text.get_rect(center=(WIDTH // 2, panel_y + 100))
        self.screen.blit(summary_text, summary_rect)

        # Draw statistics
        level_text = self.font_medium.render(_("LEVEL_REACHED", level_reached), True, WHITE)
        level_rect = level_text.get_rect(center=(WIDTH // 2, panel_y + 140))
        self.screen.blit(level_text, level_rect)

        score_text = self.font_medium.render(_("FINAL_SCORE", final_score), True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH // 2, panel_y + 180))
        self.screen.blit(score_text, score_rect)

        time_text = self.font_medium.render(_("SURVIVAL_TIME", round(game_time, 1)), True, WHITE)
        time_rect = time_text.get_rect(center=(WIDTH // 2, panel_y + 220))
        self.screen.blit(time_text, time_rect)

        # Draw control instructions
        restart_text = self.font_small.render(_("RESTART_GAME"), True, GREEN)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, panel_y + 270))
        self.screen.blit(restart_text, restart_rect)

        # Draw exit prompt (blinking)
        if self.show_blink_text:
            exit_text = self.font_small.render(_("EXIT_PROMPT"), True, YELLOW)
            exit_rect = exit_text.get_rect(center=(WIDTH // 2, panel_y + 310))
            self.screen.blit(exit_text, exit_rect)

    def start_level_change_animation(self, level):
        """
        Start the level change animation.

        Args:
            level: The new level number
        """
        self.level_change_active = True
        self.level_change_timer = time.time()
        self.current_level = level
        logger.info(f"Started level change animation for level {level}")

    def draw_level_change_animation(self):
        """Draw the level change animation if active."""
        if not self.level_change_active:
            return

        # Calculate animation duration
        elapsed = time.time() - self.level_change_timer
        if elapsed > 3.0:  # Animation lasts up to 3 seconds
            self.level_change_active = False
            return

        # Create semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        # Adjust transparency based on time
        if elapsed < 0.5:  # Fade in
            alpha = int(150 * elapsed / 0.5)
        elif elapsed > 2.5:  # Fade out
            alpha = int(150 * (3.0 - elapsed) / 0.5)
        else:  # Maintain
            alpha = 150

        overlay.fill((0, 0, 50, alpha))  # Semi-transparent blue
        self.screen.blit(overlay, (0, 0))

        # Draw level change text
        if 0.3 < elapsed < 2.7:  # Display text during this time segment
            level_text = self.font_large.render(_("LEVEL_TEXT", self.current_level), True, WHITE)
            text_rect = level_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(level_text, text_rect)
