import pygame
import math
from thunder_fighter.constants import WIDTH, HEIGHT
from thunder_fighter.graphics.renderers import create_tracking_missile

class TrackingMissile(pygame.sprite.Sprite):
    """
    A missile that tracks a designated enemy.
    """
    def __init__(self, x, y, target):
        super().__init__()
        
        self.image = create_tracking_missile()
        self.original_image = self.image
        self.rect = self.image.get_rect(center=(x, y))

        self.speed = 8
        self.target = target
        self.angle = 0
        self.last_target_pos = self.target.rect.center if self.target else None

    def update(self):
        """
        Update missile position and angle.
        It will track a living target, or continue towards the target's
        last known position if it has been destroyed.
        """
        target_pos = None
        if self.target and self.target.alive():
            # If target is alive, update its last known position
            self.last_target_pos = self.target.rect.center
            target_pos = self.last_target_pos
        elif self.last_target_pos:
            # If target is gone but we have a last known position, use that
            target_pos = self.last_target_pos
        else:
            # No target and no last position, so kill the missile
            self.kill()
            return

        # Vector from missile to target position
        direction_vector = pygame.math.Vector2(target_pos) - pygame.math.Vector2(self.rect.center)
        distance = direction_vector.length()

        # If the missile is very close to its final destination, kill it
        if distance < self.speed:
            self.kill()
            return

        # Normalize the vector and move
        direction_vector.normalize_ip()
        self.rect.center += direction_vector * self.speed

        # Rotate image to face target
        self.angle = math.degrees(math.atan2(-direction_vector.x, -direction_vector.y))
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        # Kill if it goes off-screen (failsafe)
        if self.rect.bottom < 0 or self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.kill() 