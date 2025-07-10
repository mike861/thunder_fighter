import pygame
import random
from thunder_fighter.graphics.effects.explosion import Explosion
import math
from thunder_fighter.constants import WIDTH, HEIGHT, WHITE, YELLOW, RED, GREEN

def create_explosion(center, size_str='md'):
    """Creates an explosion sprite at the given center position."""
    # Size parameter is no longer used since Explosion class has fixed size
    return Explosion(center)

def create_hit_effect(x, y, size=20):
    """Create hit effect"""
    hit = Explosion((x, y))
    # Modify explosion effect color and appearance for hit effect
    hit.draw_explosion = lambda: _draw_hit_effect(hit)
    hit.frame_rate = 40  # Hit effect is slightly faster
    _draw_hit_effect(hit)  # Draw first frame immediately
    return hit

def _draw_hit_effect(hit_obj):
    """Custom hit effect drawing function"""
    # Clear surface
    hit_obj.image.fill((0, 0, 0))
    
    # Hit effect uses different colors
    center = (40, 40)  # Fixed center for 80x80 surface
    intensity = max(0, 5 - hit_obj.frame)
    
    # Draw outer circle - white glow
    radius = 20 - hit_obj.frame * 3
    if radius > 0:
        pygame.draw.circle(hit_obj.image, WHITE, center, radius, 2)
    
    # Draw inner circle - blue flash
    inner_radius = max(1, 15 - hit_obj.frame * 3)
    if inner_radius > 0:
        pygame.draw.circle(hit_obj.image, (100, 200, 255), center, inner_radius, 2)
    
    # Draw hit particles - blue
    for _ in range(intensity * 3):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, 20)
        x = int(center[0] + math.cos(angle) * distance)
        y = int(center[1] + math.sin(angle) * distance)
        size = random.randint(1, 3)
        pygame.draw.circle(hit_obj.image, (150, 230, 255), (x, y), size)

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

class FlashEffect:
    """Flash effect that modifies entity's color directly"""
    def __init__(self, entity, color=WHITE, duration=200, flash_speed=50):
        self.entity = entity  # The sprite to flash
        self.color = color
        self.duration = duration
        self.creation_time = pygame.time.get_ticks()
        self.flash_speed = flash_speed  # Flash frequency in milliseconds
        self.last_flash = self.creation_time
        self.is_flashing = True
        self.active = True
        
        # Store original image to restore later
        if hasattr(entity, 'image'):
            self.original_image = entity.image.copy()
        else:
            self.original_image = None
            
    def update(self):
        """Update flash effect on the entity"""
        if not self.active or not self.entity.alive():
            self.stop()
            return False
            
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.creation_time
        
        # Check if effect should end
        if elapsed > self.duration:
            self.stop()
            return False
            
        # Toggle flash
        if current_time - self.last_flash > self.flash_speed:
            self.is_flashing = not self.is_flashing
            self.last_flash = current_time
            
            if self.is_flashing and self.original_image:
                # Apply color overlay
                flash_image = self.original_image.copy()
                flash_image.fill(self.color, special_flags=pygame.BLEND_ADD)
                self.entity.image = flash_image
            elif self.original_image:
                # Restore original
                self.entity.image = self.original_image.copy()
                
        return True
        
    def stop(self):
        """Stop the flash effect and restore original image"""
        self.active = False
        if self.original_image and hasattr(self.entity, 'image'):
            self.entity.image = self.original_image.copy()


class FlashEffectManager:
    """Manages flash effects for entities"""
    def __init__(self):
        self.effects = []
        
    def add_flash(self, entity, color=WHITE, duration=200):
        """Add a flash effect to an entity"""
        # Remove any existing flash effect for this entity
        self.effects = [e for e in self.effects if e.entity != entity]
        
        # Create new flash effect
        effect = FlashEffect(entity, color, duration)
        self.effects.append(effect)
        
    def update(self):
        """Update all flash effects"""
        # Update effects and remove inactive ones
        self.effects = [effect for effect in self.effects if effect.update()]
        
    def clear(self):
        """Clear all flash effects"""
        for effect in self.effects:
            effect.stop()
        self.effects.clear()


# Global flash effect manager
flash_manager = FlashEffectManager()


def create_flash_effect(entity, color=WHITE, duration=200):
    """Create a flash effect on an entity"""
    flash_manager.add_flash(entity, color, duration) 