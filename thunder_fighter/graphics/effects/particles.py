"""
Particle Effects System

Manages various particle effects: explosions, trails, flashes, etc.
"""

import math
import random
from typing import List, Tuple

import pygame


class Particle:
    """Single Particle Class"""

    def __init__(self, x: float, y: float, velocity: Tuple[float, float],
                 color: Tuple[int, int, int], lifetime: float, size: int = 2):
        self.x = x
        self.y = y
        self.velocity_x, self.velocity_y = velocity
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.active = True

    def update(self, dt: float):
        """Updates particle state."""
        if not self.active:
            return

        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.lifetime -= dt

        if self.lifetime <= 0:
            self.active = False

    def render(self, screen: pygame.Surface):
        """Renders the particle."""
        if not self.active:
            return

        # Calculate transparency (based on remaining lifetime)
        alpha_ratio = self.lifetime / self.max_lifetime
        alpha = int(255 * alpha_ratio)

        # Create a surface with transparency
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        color_with_alpha = (*self.color, alpha)
        pygame.draw.circle(surf, color_with_alpha, (self.size, self.size), self.size)

        screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))


class ParticleSystem:
    """Particle System Manager"""

    def __init__(self):
        self.particles: List[Particle] = []

    def create_explosion(self, x: float, y: float, particle_count: int = 20):
        """Creates an explosion effect."""
        colors = [(255, 255, 0), (255, 128, 0), (255, 0, 0)]  # Yellow, Orange, Red

        for _ in range(particle_count):
            # Random direction and speed
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)

            color = random.choice(colors)
            lifetime = random.uniform(0.5, 1.5)
            size = random.randint(2, 4)

            particle = Particle(x, y, velocity, color, lifetime, size)
            self.particles.append(particle)

    def create_trail(self, x: float, y: float, direction: Tuple[float, float],
                     particle_count: int = 5):
        """Creates a trail effect."""
        colors = [(255, 255, 255), (200, 200, 255), (150, 150, 255)]  # White to Blue

        for i in range(particle_count):
            # Create particles in the opposite direction
            speed = random.uniform(20, 50)
            spread = 0.3  # Spread angle

            # Add random spread
            dir_x = direction[0] + random.uniform(-spread, spread)
            dir_y = direction[1] + random.uniform(-spread, spread)

            velocity = (-dir_x * speed, -dir_y * speed)

            color = random.choice(colors)
            lifetime = random.uniform(0.2, 0.8)
            size = random.randint(1, 2)

            particle = Particle(x, y, velocity, color, lifetime, size)
            self.particles.append(particle)

    def create_sparks(self, x: float, y: float, particle_count: int = 10):
        """Creates a sparks effect."""
        colors = [(255, 255, 100), (255, 200, 50), (255, 150, 0)]  # Yellow to Orange

        for _ in range(particle_count):
            # Upward sparks
            angle = random.uniform(-math.pi/3, -2*math.pi/3)  # 60-degree range upwards
            speed = random.uniform(80, 120)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)

            color = random.choice(colors)
            lifetime = random.uniform(0.3, 1.0)
            size = random.randint(1, 3)

            particle = Particle(x, y, velocity, color, lifetime, size)
            self.particles.append(particle)

    def create_hit_effect(self, x: float, y: float, color: Tuple[int, int, int] = (255, 255, 255)):
        """Creates a hit effect."""
        particle_count = 8

        for _ in range(particle_count):
            # Radial spread
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 80)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)

            lifetime = random.uniform(0.2, 0.6)
            size = random.randint(1, 2)

            particle = Particle(x, y, velocity, color, lifetime, size)
            self.particles.append(particle)

    def update(self, dt: float):
        """Updates all particles."""
        for particle in self.particles[:]:  # Use slice copy for safe deletion
            particle.update(dt)
            if not particle.active:
                self.particles.remove(particle)

    def render(self, screen: pygame.Surface):
        """Renders all particles."""
        for particle in self.particles:
            particle.render(screen)

    def clear(self):
        """Clears all particles."""
        self.particles.clear()

    def get_particle_count(self) -> int:
        """Gets the current particle count."""
        return len(self.particles)


# Global particle system instance
_global_particle_system = None


def get_particle_system() -> ParticleSystem:
    """Gets the global particle system instance."""
    global _global_particle_system
    if _global_particle_system is None:
        _global_particle_system = ParticleSystem()
    return _global_particle_system


def create_particle_explosion(x: float, y: float, particle_count: int = 20):
    """Convenience function: Creates an explosion particle effect."""
    get_particle_system().create_explosion(x, y, particle_count)


def create_particle_trail(x: float, y: float, direction: Tuple[float, float],
                         particle_count: int = 5):
    """Convenience function: Creates a trail particle effect."""
    get_particle_system().create_trail(x, y, direction, particle_count)


def create_particle_sparks(x: float, y: float, particle_count: int = 10):
    """Convenience function: Creates a sparks particle effect."""
    get_particle_system().create_sparks(x, y, particle_count)


def create_particle_hit_effect(x: float, y: float, color: Tuple[int, int, int] = (255, 255, 255)):
    """Convenience function: Creates a hit particle effect."""
    get_particle_system().create_hit_effect(x, y, color)


def update_particles(dt: float):
    """Convenience function: Updates the particle system."""
    get_particle_system().update(dt)


def render_particles(screen: pygame.Surface):
    """Convenience function: Renders the particle system."""
    get_particle_system().render(screen)


def clear_particles():
    """Convenience function: Clears all particles."""
    get_particle_system().clear()
