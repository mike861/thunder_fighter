"""
Developer Info Display Component

Displays debug information for developers including FPS, enemy count, and player position.
"""

from thunder_fighter.constants import HEIGHT
from thunder_fighter.utils.config_manager import config_manager


class DevInfoDisplay:
    """Component for displaying developer debug information."""

    def __init__(self, screen, font):
        """
        Initialize the developer info display.

        Args:
            screen: pygame.Surface - The game screen to draw on
            font: pygame.Font - Font for displaying text
        """
        self.screen = screen
        self.font = font
        self.text_color = (200, 200, 200)  # Light gray

        # Position settings
        self.x = 10
        self.y = HEIGHT - 80
        self.line_height = 20

    def draw(self, fps, enemy_count, target_enemy_count, player_pos):
        """
        Draw developer information if dev mode is enabled.

        Args:
            fps: Current frames per second
            enemy_count: Current number of enemies
            target_enemy_count: Target number of enemies
            player_pos: Player position tuple (x, y)
        """
        # Only draw if dev mode is enabled
        if not config_manager.debug.dev_mode:
            return

        x, y = self.x, self.y

        # Format texts
        fps_text = f"FPS: {fps:.2f}"
        enemy_text = f"Enemies: {enemy_count}/{target_enemy_count}"
        player_pos_text = f"Player: ({int(player_pos[0])}, {int(player_pos[1])})"

        # Render texts
        fps_surf = self.font.render(fps_text, True, self.text_color)
        enemy_surf = self.font.render(enemy_text, True, self.text_color)
        player_pos_surf = self.font.render(player_pos_text, True, self.text_color)

        # Draw texts
        self.screen.blit(fps_surf, (x, y))
        self.screen.blit(enemy_surf, (x, y + self.line_height))
        self.screen.blit(player_pos_surf, (x, y + self.line_height * 2))

    def set_position(self, x, y):
        """
        Set the display position.

        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.x = x
        self.y = y

    def set_color(self, color):
        """
        Set the text color.

        Args:
            color: RGB color tuple
        """
        self.text_color = color
