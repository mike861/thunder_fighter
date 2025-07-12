"""
Boss Status Display Component

Displays boss health bar and status information.
"""

from thunder_fighter.constants import RED, WHITE, WIDTH
from thunder_fighter.localization import _

from .health_bar import HealthBarComponent


class BossStatusDisplay:
    """Component for displaying boss status."""

    def __init__(self, screen, font):
        """
        Initialize the boss status display.

        Args:
            screen: pygame.Surface - The game screen to draw on
            font: pygame.Font - Font for displaying text
        """
        self.screen = screen
        self.font = font
        self.text_color = WHITE

        # Create health bar component
        self.health_bar = HealthBarComponent(screen, font)

        # Health bar settings
        self.bar_length = 200
        self.bar_height = 20
        self.bar_bg_color = (50, 50, 50)
        self.boss_hp_color = RED

        # Boss info
        self.boss_info = {
            'active': False,
            'health': 0,
            'max_health': 0,
            'level': 0,
            'mode': 'normal'
        }

    def update_info(self, active, health=None, max_health=None, level=None, mode=None):
        """
        Update boss information.

        Args:
            active: Whether boss is active
            health: Current health
            max_health: Maximum health
            level: Boss level
            mode: Boss mode (normal, aggressive, final)
        """
        self.boss_info['active'] = active

        if not active:
            return

        if health is not None:
            self.boss_info['health'] = health
        if max_health is not None:
            self.boss_info['max_health'] = max_health
        if level is not None:
            self.boss_info['level'] = level
        if mode is not None:
            self.boss_info['mode'] = mode

    def draw(self):
        """Draw boss status if active."""
        if not self.boss_info['active']:
            return

        # Position the boss bar at the top center
        bar_x = (WIDTH - self.bar_length) // 2
        bar_y = 10

        # Draw health bar using the component
        self.health_bar.draw(
            bar_x, bar_y, self.bar_length, self.bar_height,
            self.boss_info['health'], self.boss_info['max_health'],
            border_color=WHITE,
            fill_color=self.boss_hp_color,
            background_color=self.bar_bg_color,
            show_text=False  # We'll draw custom text
        )

        # Draw boss health text
        boss_health_text = _("BOSS_HEALTH", self.boss_info['health'], self.boss_info['max_health'])
        text_surface = self.font.render(boss_health_text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, bar_y + self.bar_height // 2))
        self.screen.blit(text_surface, text_rect)

        # Draw boss mode indicator if not normal
        if self.boss_info['mode'] != 'normal':
            mode_y = bar_y + self.bar_height + 5
            mode_text = f"[{self.boss_info['mode'].upper()}]"
            mode_color = RED if self.boss_info['mode'] == 'final' else (255, 165, 0)  # Orange for aggressive
            mode_surface = self.font.render(mode_text, True, mode_color)
            mode_rect = mode_surface.get_rect(center=(WIDTH // 2, mode_y))
            self.screen.blit(mode_surface, mode_rect)

    def is_active(self):
        """Check if boss is currently active."""
        return self.boss_info['active']

    def reset(self):
        """Reset boss status to initial values."""
        self.boss_info = {
            'active': False,
            'health': 0,
            'max_health': 0,
            'level': 0,
            'mode': 'normal'
        }
