import random

import pygame

from thunder_fighter.constants import HEIGHT, WIDTH


class Star:
    """Background star class"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.5, 2)
        self.size = random.randint(1, 3)
        self.brightness = random.randint(100, 255)

    def update(self):
        """Update star position"""
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, screen):
        """Draw star"""
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)

def create_stars(count):
    """Create specified number of stars"""
    return [Star() for _ in range(count)]
