import math
import pygame

from thunder_fighter.constants import ORANGE, RED, YELLOW


class Explosion(pygame.sprite.Sprite):
    """Explosion effect class with pre-calculated frames for performance"""

    # Class-level cache for pre-calculated explosion frames
    _explosion_frames_cache = None

    def __init__(self, center):
        super().__init__()
        self.rect = pygame.Rect(0, 0, 80, 80)
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        self._custom_draw = False
        self._draw_function = None

        # Set explosion z-depth to foreground to minimize sorting impact
        self.z = -10  # Negative z for foreground rendering

        # Initialize explosion frames if not cached
        if Explosion._explosion_frames_cache is None:
            Explosion._explosion_frames_cache = self._create_explosion_frames()

        # Set initial frame
        self.image = Explosion._explosion_frames_cache[0]

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1

            if self._custom_draw and self._draw_function:
                # For custom drawing, check if effect should end
                self._draw_function()
                # Check if custom effect should end (intensity <= 0)
                intensity = max(0, 5 - self.frame)
                if intensity <= 0:
                    # Set transparent image before killing to avoid visual artifacts
                    self.image = pygame.Surface((80, 80))
                    self.image.set_colorkey((0, 0, 0))
                    self.image.fill((0, 0, 0))
                    self.kill()
            else:
                # Standard explosion frames
                if self.frame >= len(Explosion._explosion_frames_cache):
                    # Set transparent image before killing to avoid visual artifacts
                    self.image = pygame.Surface((80, 80))
                    self.image.set_colorkey((0, 0, 0))
                    self.image.fill((0, 0, 0))
                    self.kill()
                else:
                    # Use pre-calculated frame
                    self.image = Explosion._explosion_frames_cache[self.frame]

    def _create_explosion_frames(self):
        """Create and cache all explosion frames for performance"""
        frames = []
        center = (40, 40)

        # Pre-calculate angles for fragments to avoid repeated math
        fragment_angles = [i * 45 for i in range(8)]

        for frame_num in range(7):  # 7 frames (0-6)
            # Create frame surface
            frame_surface = pygame.Surface((80, 80))
            frame_surface.set_colorkey((0, 0, 0))

            intensity = max(0, 5 - frame_num)

            # Draw outer explosion circle
            radius = 10 + frame_num * 6
            pygame.draw.circle(frame_surface, RED, center, radius, 3)

            # Draw inner explosion circle
            if intensity > 2:
                pygame.draw.circle(frame_surface, ORANGE, center, radius // 2, 2)

            # Draw explosion fragments using optimized math
            distance = 10 + frame_num * 4
            size = max(1, intensity)

            for angle in fragment_angles:
                # Use direct trigonometry instead of Vector2
                angle_rad = math.radians(angle)
                x = int(center[0] + distance * math.cos(angle_rad))
                y = int(center[1] + distance * math.sin(angle_rad))
                pygame.draw.circle(frame_surface, YELLOW, (x, y), size)

            frames.append(frame_surface)

        return frames
