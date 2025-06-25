"""
Game Info Display Component

Displays game information such as score, level, and elapsed time.
"""

import pygame
from thunder_fighter.constants import WIDTH, WHITE
from thunder_fighter.localization import _
from thunder_fighter.utils.logger import logger


class GameInfoDisplay:
    """Component for displaying game information."""
    
    def __init__(self, screen, font=None):
        """
        Initialize the game info display.
        
        Args:
            screen: pygame.Surface - The game screen to draw on
            font: pygame.Font - Font for displaying text (optional, will use resource manager if None)
        """
        self.screen = screen
        
        # Use resource manager for font if not provided
        if font is None:
            from thunder_fighter.utils.resource_manager import get_resource_manager
            resource_manager = get_resource_manager()
            self.font = resource_manager.load_font(None, 24, system_font=False)
        else:
            self.font = font
            
        self.text_color = WHITE
        
        # Position settings
        self.x = WIDTH - 200
        self.y = 10
        self.line_height = 25
        
    def draw(self, score, level, game_time):
        """
        Draw game information.
        
        Args:
            score: Current score
            level: Current game level
            game_time: Elapsed game time in seconds
        """
        # Format texts
        score_text = _("SCORE", score)
        level_text = _("LEVEL", level)
        time_text = _("TIME", game_time)
        
        # Render texts
        score_surf = self.font.render(score_text, True, self.text_color)
        level_surf = self.font.render(level_text, True, self.text_color)
        time_surf = self.font.render(time_text, True, self.text_color)
        
        # Draw texts
        self.screen.blit(score_surf, (self.x, self.y))
        self.screen.blit(level_surf, (self.x, self.y + self.line_height))
        self.screen.blit(time_surf, (self.x, self.y + self.line_height * 2))
        
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