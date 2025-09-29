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
    """Custom hit effect drawing function with pre-calculated particles"""
    # Clear surface
    hit_obj.image.fill((0, 0, 0))

    # Hit effect uses different colors
    center = (40, 40)  # Fixed center for 80x80 surface
    intensity = max(0, 5 - hit_obj.frame)

    # If intensity is 0 or frame is too high, just keep the cleared surface (transparent)
    if intensity <= 0:
        return

    # Draw outer circle - white glow
    radius = 20 - hit_obj.frame * 3
    if radius > 0:
        pygame.draw.circle(hit_obj.image, WHITE, center, radius, 2)

    # Draw inner circle - blue flash
    inner_radius = max(1, 15 - hit_obj.frame * 3)
    if inner_radius > 0:
        pygame.draw.circle(hit_obj.image, (100, 200, 255), center, inner_radius, 2)

    # Draw hit particles using pre-calculated positions
    if not hasattr(hit_obj, '_particles'):
        # Pre-calculate particle positions and sizes once
        hit_obj._particles = []
        num_particles = intensity * 3
        for _ in range(max(15, num_particles)):  # Pre-calc for max particles
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, 20)
            x = int(center[0] + math.cos(angle) * distance)
            y = int(center[1] + math.sin(angle) * distance)
            size = random.randint(1, 3)
            hit_obj._particles.append((x, y, size))

    # Draw only the needed particles for this frame
    particles_to_draw = min(intensity * 3, len(hit_obj._particles))
    for i in range(particles_to_draw):
        x, y, size = hit_obj._particles[i]
        pygame.draw.circle(hit_obj.image, (150, 230, 255), (x, y), size)
