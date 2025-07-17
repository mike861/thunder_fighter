"""
Explosion Effects

Handles explosion and hit effect creation and rendering.
"""

import math
import random

import pygame

from thunder_fighter.constants import WHITE
from thunder_fighter.graphics.effects.explosion import Explosion


def create_explosion(center, size_str="md"):
    """Creates an explosion sprite at the given center position."""
    # Size parameter is no longer used since Explosion class has fixed size
    return Explosion(center)


def create_hit_effect(x, y, size=20):
    """Create hit effect"""
    hit = Explosion((x, y))
    # Modify explosion effect color and appearance for hit effect
    hit._custom_draw = True
    hit._draw_function = lambda: _draw_hit_effect(hit)
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
