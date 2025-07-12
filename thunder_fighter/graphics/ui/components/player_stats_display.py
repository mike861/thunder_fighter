"""
Player Stats Display Component

Displays player statistics including health, bullet speed, movement speed, and wingmen count.
"""

from thunder_fighter.constants import WHITE
from thunder_fighter.localization import _
from thunder_fighter.utils.config_manager import config_manager

from .health_bar import HealthBarComponent


class PlayerStatsDisplay:
    """Component for displaying player statistics."""

    def __init__(self, screen, font=None):
        """
        Initialize the player stats display.
        
        Args:
            screen: pygame.Surface - The game screen to draw on
            font: pygame.Font - Font for displaying text (optional, will use resource manager if None)
        """
        self.screen = screen

        # Use resource manager for font if not provided
        if font is None:
            from thunder_fighter.utils.resource_manager import get_resource_manager
            resource_manager = get_resource_manager()
            # Use original font size with Chinese character support
            self.font = resource_manager.load_font(None, 24, system_font=True)
        else:
            self.font = font

        self.text_color = WHITE

        # Create health bar component
        self.health_bar = HealthBarComponent(screen, self.font)

        # Position settings
        self.x = 10
        self.y = 10
        self.line_height = 20

        # Player info cache
        self.player_info = {
            'health': 100,
            'max_health': 100,
            'bullet_paths': 1,
            'bullet_speed': 7,
            'speed': 5,
            'wingmen': 0
        }

    def update_info(self, health=None, max_health=None, bullet_paths=None,
                    bullet_speed=None, speed=None, wingmen=None):
        """
        Update player information.
        
        Args:
            health: Current health
            max_health: Maximum health
            bullet_paths: Number of bullet paths
            bullet_speed: Bullet speed
            speed: Movement speed
            wingmen: Number of wingmen
        """
        if health is not None:
            self.player_info['health'] = health
        if max_health is not None:
            self.player_info['max_health'] = max_health
        if bullet_paths is not None:
            self.player_info['bullet_paths'] = bullet_paths
        if bullet_speed is not None:
            self.player_info['bullet_speed'] = bullet_speed
        if speed is not None:
            self.player_info['speed'] = speed
        if wingmen is not None:
            self.player_info['wingmen'] = wingmen

    def draw(self):
        """Draw player statistics."""
        x, y = self.x, self.y

        # Draw health bar
        self.health_bar.draw(
            x, y, 150, 20,
            self.player_info['health'],
            self.player_info['max_health']
        )

        y += 25

        # Always display bullet speed
        bullet_speed_text = _("PLAYER_BULLET_SPEED_INFO", self.player_info['bullet_speed'])
        bullet_speed_surf = self.font.render(bullet_speed_text, True, self.text_color)
        self.screen.blit(bullet_speed_surf, (x, y))

        y += self.line_height

        # Always display movement speed
        speed_text = _("PLAYER_SPEED_INFO", self.player_info['speed'])
        speed_surf = self.font.render(speed_text, True, self.text_color)
        self.screen.blit(speed_surf, (x, y))

        # Display extra info only in dev mode
        if config_manager.debug.dev_mode:
            y += self.line_height

            # Draw bullet path info
            bullet_path_text = _("PLAYER_BULLET_PATHS_INFO", self.player_info['bullet_paths'])
            bullet_path_surf = self.font.render(bullet_path_text, True, self.text_color)
            self.screen.blit(bullet_path_surf, (x, y))

            y += self.line_height

            # Draw wingmen information
            wingmen_text = _("PLAYER_WINGMEN_INFO", self.player_info['wingmen'])
            wingmen_surf = self.font.render(wingmen_text, True, self.text_color)
            self.screen.blit(wingmen_surf, (x, y))

    def set_position(self, x, y):
        """
        Set the display position.
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.x = x
        self.y = y

    def reset(self):
        """Reset player stats to initial values."""
        self.player_info = {
            'health': 100,
            'max_health': 100,
            'bullet_paths': 1,
            'bullet_speed': 7,
            'speed': 5,
            'wingmen': 0
        }
