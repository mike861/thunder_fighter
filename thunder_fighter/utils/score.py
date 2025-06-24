import pygame
from thunder_fighter.constants import FONT_NAME, FONT_SIZE_MEDIUM, WHITE

class Score:
    """Game score class"""
    def __init__(self):
        # Use resource manager to load font with caching
        from thunder_fighter.utils.resource_manager import get_resource_manager
        
        resource_manager = get_resource_manager()
        
        try:
            self.font = resource_manager.load_font(FONT_NAME, FONT_SIZE_MEDIUM, system_font=True)
        except Exception:
            self.font = resource_manager.load_font(None, FONT_SIZE_MEDIUM, system_font=False)
        
        self.value = 0
        self.text = None
        self.rect = None
        self.update_display()
    
    def update(self, points):
        """Add points to score"""
        self.value += points
        self.update_display()
    
    def draw(self, screen):
        """Display score"""
        if self.text:
            screen.blit(self.text, self.rect)
    
    def get_value(self):
        """Get current score"""
        return self.value
    
    def update_display(self):
        """Update score display"""
        self.text = self.font.render(f"Score: {self.value}", True, WHITE)
        self.rect = self.text.get_rect()
        self.rect.topleft = (10, 10) 