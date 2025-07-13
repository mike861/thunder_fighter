"""
Health Bar Component

Responsible for rendering health bars with various styles and colors.
"""

import pygame

from thunder_fighter.constants import GREEN, RED, WHITE, YELLOW
from thunder_fighter.utils.logger import logger


class HealthBarComponent:
    """Component for drawing health bars."""

    def __init__(self, screen, font):
        """
        Initialize the health bar component.

        Args:
            screen: pygame.Surface - The game screen to draw on
            font: pygame.Font - Font for displaying text
        """
        self.screen = screen
        self.font = font

    def draw(
        self,
        x,
        y,
        width,
        height,
        current,
        maximum,
        border_color=WHITE,
        fill_color=GREEN,
        background_color=(60, 60, 60),
        show_text=True,
        text_format="{current}/{maximum}",
    ):
        """
        Draw a health bar.

        Args:
            x, y: Position coordinates
            width, height: Dimensions of the health bar
            current: Current value
            maximum: Maximum value
            border_color: Color of the border
            fill_color: Default fill color (may change based on percentage)
            background_color: Background color
            show_text: Whether to show text on the bar
            text_format: Format string for the text
        """
        # Draw background
        pygame.draw.rect(self.screen, background_color, (x, y, width, height))

        # Calculate fill width
        fill_width = max(0, int(width * current / maximum)) if maximum > 0 else 0

        # Draw fill part
        if current > 0 and maximum > 0:
            # Change color based on health percentage
            percentage = current / maximum
            if percentage < 0.3:
                color = RED  # Red when health is low
            elif percentage < 0.6:
                color = YELLOW  # Yellow when health is medium
            else:
                color = fill_color  # Default color when health is high

            pygame.draw.rect(self.screen, color, (x, y, fill_width, height))

        # Draw border
        pygame.draw.rect(self.screen, border_color, (x, y, width, height), 2)

        # Display text if requested
        if show_text:
            text = text_format.format(current=current, maximum=maximum)
            value_text = self.font.render(text, True, WHITE)
            text_rect = value_text.get_rect(center=(x + width // 2, y + height // 2))
            self.screen.blit(value_text, text_rect)

        logger.debug(f"Drew health bar at ({x}, {y}) - {current}/{maximum}")

    def draw_simple(self, x, y, width, height, percentage, color=GREEN):
        """
        Draw a simple health bar without text.

        Args:
            x, y: Position coordinates
            width, height: Dimensions
            percentage: Fill percentage (0.0 to 1.0)
            color: Fill color
        """
        # Draw background
        pygame.draw.rect(self.screen, (60, 60, 60), (x, y, width, height))

        # Draw fill
        fill_width = int(width * max(0, min(1, percentage)))
        if fill_width > 0:
            pygame.draw.rect(self.screen, color, (x, y, fill_width, height))

        # Draw border
        pygame.draw.rect(self.screen, WHITE, (x, y, width, height), 2)
