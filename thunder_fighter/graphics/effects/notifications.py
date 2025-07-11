"""
Notification System

Handles all types of notifications including regular, warning, and achievement notifications.
"""

import pygame
from thunder_fighter.constants import WIDTH, HEIGHT, WHITE, YELLOW, RED, GREEN


class Notification:
    """Class for displaying temporary notification messages"""
    def __init__(self, text, duration=2000, color=WHITE, size=24, position='center'):
        try:
            # Use resource manager for better Chinese font support
            from thunder_fighter.utils.resource_manager import get_resource_manager
            resource_manager = get_resource_manager()
            self.font = resource_manager.load_font(None, size, system_font=True)
        except (pygame.error, AttributeError):
            # If pygame font is not initialized or available (test environment)
            # Create a dummy font interface
            class DummyFont:
                def render(self, text, antialias=True, color=(255, 255, 255)):
                    # Create a dummy surface with the essential methods
                    if hasattr(pygame, 'Surface'):
                        surf = pygame.Surface((len(text) * 10, size))
                        rect = surf.get_rect()
                        return surf
                    else:
                        # Pure mock for extreme cases
                        mock_surf = type('MockSurface', (), {
                            'get_rect': lambda: type('MockRect', (), {
                                'center': (0, 0),
                                'centerx': 0,
                                'centery': 0
                            })()
                        })()
                        return mock_surf
            self.font = DummyFont()
            
        self.text = text
        self.color = color
        self.creation_time = pygame.time.get_ticks() if hasattr(pygame, 'time') else 0
        self.duration = duration  # Duration in milliseconds
        self.alpha = 255  # Fully opaque
        self.position = position
        
        # Create the text surface
        try:
            self.surface = self.font.render(text, True, color)
            self.rect = self.surface.get_rect()
        except (pygame.error, AttributeError):
            # Create dummy surface and rect for test environments
            if hasattr(pygame, 'Surface'):
                self.surface = pygame.Surface((len(text) * 10, size))
            else:
                self.surface = type('MockSurface', (), {})()
            self.rect = type('MockRect', (), {
                'center': (WIDTH // 2, HEIGHT // 2),
                'centerx': WIDTH // 2,
                'centery': HEIGHT // 2
            })()
        
        # Set position based on position parameter
        if position == 'center':
            self.rect.center = (WIDTH // 2, HEIGHT // 2)
        elif position == 'top':
            self.rect.center = (WIDTH // 2, 100)
        elif position == 'bottom':
            self.rect.center = (WIDTH // 2, HEIGHT - 100)
            
        # Add vertical offset for stacking multiple messages
        self.y_offset = 0
    
    def update(self):
        """Update notification state, check if it should disappear"""
        if hasattr(pygame, 'time'):
            current_time = pygame.time.get_ticks()
        else:
            # For test environments without pygame.time
            return True  # Just keep notifications alive in tests
            
        time_passed = current_time - self.creation_time
        
        # If duration exceeded, return False to indicate notification should be removed
        if time_passed > self.duration:
            return False
        
        # Fade out in the last 500 milliseconds
        if time_passed > self.duration - 500:
            # Calculate alpha value for fade effect
            self.alpha = max(0, int(255 * (self.duration - time_passed) / 500))
        
        return True
    
    def set_y_position(self, y):
        """Set the Y coordinate of the notification, keeping X coordinate unchanged"""
        old_center_x = self.rect.centerx
        self.rect.centery = y
        self.rect.centerx = old_center_x
    
    def draw(self, surface):
        """Draw notification on screen"""
        try:
            # Create a temporary surface with alpha channel
            temp_surface = pygame.Surface(self.surface.get_size(), pygame.SRCALPHA)
            temp_surface.fill((0, 0, 0, 0))  # Completely transparent fill
            temp_surface.blit(self.surface, (0, 0))
            
            # Apply alpha value
            temp_surface.set_alpha(self.alpha)
            
            # Draw to screen
            surface.blit(temp_surface, self.rect)
        except (pygame.error, AttributeError):
            # In test environment, just pass
            pass


class WarningNotification(Notification):
    """Special warning notification with flashing effect and longer duration"""
    def __init__(self, text, duration=3000, color=YELLOW, size=28, position='top'):
        super().__init__(text, duration, color, size, position)
        self.flash_speed = 200  # Flash speed (milliseconds)
        self.flash_colors = [YELLOW, RED]  # Flash colors
        self.current_color_index = 0
        self.last_flash = self.creation_time
    
    def update(self):
        """Update warning notification state, add flashing effect"""
        current_time = pygame.time.get_ticks()
        
        # Handle flashing effect
        if current_time - self.last_flash > self.flash_speed:
            self.last_flash = current_time
            self.current_color_index = (self.current_color_index + 1) % len(self.flash_colors)
            self.surface = self.font.render(self.text, True, self.flash_colors[self.current_color_index])
        
        # Call parent update to handle fade and time check
        return super().update()


class AchievementNotification(Notification):
    """Achievement or positive event notification with green color and special effects"""
    def __init__(self, text, duration=2500, color=GREEN, size=24, position='bottom'):
        super().__init__(text, duration, color, size, position)
        # Add any special effects or custom logic 