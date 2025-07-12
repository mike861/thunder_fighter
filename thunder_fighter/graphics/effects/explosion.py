import pygame

from thunder_fighter.constants import ORANGE, RED, YELLOW


class Explosion(pygame.sprite.Sprite):
    """Explosion effect class"""

    def __init__(self, center):
        super().__init__()
        self.image = pygame.Surface((80, 80))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame > 6:  # 6 frames for smoother explosion effect
                self.kill()
            else:
                self.draw_explosion()

    def draw_explosion(self):
        """Draw explosion effect"""
        # Clear surface
        self.image.fill((0, 0, 0))

        # Draw explosion effect based on current frame
        center = (40, 40)
        intensity = max(0, 5 - self.frame)  # Explosion intensity decreases over time

        # Draw outer explosion circle
        radius = 10 + self.frame * 6
        pygame.draw.circle(self.image, RED, center, radius, 3)

        # Draw inner explosion circle
        if intensity > 2:
            pygame.draw.circle(self.image, ORANGE, center, radius // 2, 2)

        # Draw explosion fragments
        for i in range(8):
            angle = i * 45
            distance = 10 + self.frame * 4
            x = int(center[0] + distance * pygame.math.Vector2(1, 0).rotate(angle).x)
            y = int(center[1] + distance * pygame.math.Vector2(1, 0).rotate(angle).y)
            size = max(1, intensity)
            pygame.draw.circle(self.image, YELLOW, (x, y), size)
