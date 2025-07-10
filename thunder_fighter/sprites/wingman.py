import pygame
from thunder_fighter.entities.projectiles.missile import TrackingMissile
from thunder_fighter.graphics.renderers import create_wingman
from thunder_fighter.constants import WINGMAN_FORMATION_SPACING

class Wingman(pygame.sprite.Sprite):
    """
    A wingman aircraft that follows the player, fires missiles,
    and acts as a shield.
    """
    def __init__(self, player, side):
        """
        Initialize the Wingman.
        - player: The player sprite this wingman is attached to.
        - side: 'left' or 'right' to determine position.
        """
        super().__init__()
        self.player = player
        self.side = side
        
        self.image = create_wingman()
        
        self.rect = self.image.get_rect()
        self.update() # Set initial position

    def update(self):
        """Update the wingman's position to follow the player."""
        if self.side == 'left':
            self.rect.centerx = self.player.rect.centerx - WINGMAN_FORMATION_SPACING
        else: # 'right'
            self.rect.centerx = self.player.rect.centerx + WINGMAN_FORMATION_SPACING
        self.rect.centery = self.player.rect.centery + 10

    def shoot(self, all_sprites, missiles_group, target):
        """Fire a tracking missile at a specific target."""
        if not target:
            return
        missile = TrackingMissile(self.rect.centerx, self.rect.top, target)
        all_sprites.add(missile)
        missiles_group.add(missile)
