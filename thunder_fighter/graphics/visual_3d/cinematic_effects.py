"""
High fidelity static 3D effects for ships and enemies.

The cinematic renderer focuses on sculpted lighting, rim illumination,
soft shadows, and material-specific highlights while maintaining
runtime-free generation suitable for pre-rendered assets.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

import pygame

LIGHT_VEC = (-0.45, -0.9)
ViewColor = Tuple[int, int, int]


@dataclass(frozen=True)
class LightingProfile:
    highlight_color: ViewColor
    shadow_color: ViewColor
    rim_color: ViewColor
    rim_alpha: int
    rim_width: int
    glow_color: ViewColor
    glow_alpha: int
    glow_expand: int
    specular_color: ViewColor
    specular_radius: int
    specular_intensity: int


def _normalise(vec: tuple[float, float]) -> tuple[float, float]:
    x, y = vec
    length = math.hypot(x, y) or 1.0
    return (x / length, y / length)


class Cinematic3DEffects:
    """Generate stylised 3D sprites using layered 2D operations."""

    def __init__(self, light_direction: tuple[float, float] = LIGHT_VEC):
        self.light_dir = _normalise(light_direction)
        self.player_profile = LightingProfile(
            highlight_color=(180, 210, 255),
            shadow_color=(20, 35, 60),
            rim_color=(120, 200, 255),
            rim_alpha=100,
            rim_width=3,
            glow_color=(60, 140, 255),
            glow_alpha=110,
            glow_expand=18,
            specular_color=(255, 255, 255),
            specular_radius=12,
            specular_intensity=190,
        )
        self.enemy_profile = LightingProfile(
            highlight_color=(255, 150, 120),
            shadow_color=(35, 5, 25),
            rim_color=(255, 80, 60),
            rim_alpha=110,
            rim_width=4,
            glow_color=(255, 110, 80),
            glow_alpha=130,
            glow_expand=22,
            specular_color=(255, 210, 180),
            specular_radius=10,
            specular_intensity=150,
        )

    def create_player_surface(self, base_surface: pygame.Surface) -> pygame.Surface:
        """Return a player sprite with metallic cinematic lighting."""
        shaded = self._apply_directional_shading(base_surface.copy(), self.player_profile)
        shaded = self._add_specular_node(shaded, self.player_profile, (0.5, 0.28))
        shaded = self._add_rim_light(shaded, base_surface, self.player_profile)
        shaded = self._add_engine_glow(shaded)
        return self._compose_layers(base_surface, shaded, self.player_profile, shadow_offset=(12, 16))

    def create_enemy_surface(self, base_surface: pygame.Surface, level: int = 0) -> pygame.Surface:
        """Return an enemy sprite with organic iridescent lighting."""
        shaded = self._apply_directional_shading(base_surface.copy(), self.enemy_profile)
        shaded = self._add_specular_node(shaded, self.enemy_profile, (0.48, 0.42))
        shaded = self._add_rim_light(shaded, base_surface, self.enemy_profile)
        shaded = self._add_bio_core(shaded, level)
        return self._compose_layers(base_surface, shaded, self.enemy_profile, shadow_offset=(10, 14))

    # ------------------------------------------------------------------
    # Lighting helpers
    # ------------------------------------------------------------------
    def _apply_directional_shading(self, surface: pygame.Surface, profile: LightingProfile) -> pygame.Surface:
        width, height = surface.get_size()
        light_x, light_y = self.light_dir
        highlight_overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        shadow_overlay = pygame.Surface((width, height), pygame.SRCALPHA)

        for y in range(height):
            ny = (y / max(height - 1, 1)) * 2 - 1
            for x in range(width):
                nx = (x / max(width - 1, 1)) * 2 - 1
                dot = nx * light_x + ny * light_y
                value = 0.55 + dot * 0.55  # bias the light for stronger separation
                if value >= 0.55:
                    alpha = min(255, int((value - 0.55) * 280))
                    if alpha > 0:
                        highlight_overlay.set_at((x, y), (*profile.highlight_color, alpha))
                else:
                    alpha = min(220, int((0.55 - value) * 360))
                    if alpha > 0:
                        shadow_overlay.set_at((x, y), (*profile.shadow_color, alpha))

        surface.blit(highlight_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        surface.blit(shadow_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        return surface

    def _add_specular_node(
        self,
        surface: pygame.Surface,
        profile: LightingProfile,
        position_ratio: tuple[float, float],
    ) -> pygame.Surface:
        width, height = surface.get_size()
        cx = int(position_ratio[0] * width)
        cy = int(position_ratio[1] * height)
        radius = max(4, min(profile.specular_radius, width // 2))
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)

        for r in range(radius, 0, -1):
            falloff = r / radius
            alpha = int(profile.specular_intensity * falloff * falloff)
            if alpha <= 0:
                continue
            pygame.draw.circle(
                overlay,
                (*profile.specular_color, alpha),
                (cx, cy),
                r,
            )

        surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return surface

    def _add_rim_light(
        self,
        surface: pygame.Surface,
        base_surface: pygame.Surface,
        profile: LightingProfile,
    ) -> pygame.Surface:
        mask = pygame.mask.from_surface(base_surface, 10)
        outline = mask.outline()
        if len(outline) < 3:
            return surface

        rim_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        alpha = profile.rim_alpha
        for width in range(profile.rim_width, 0, -1):
            pygame.draw.polygon(
                rim_surface,
                (*profile.rim_color, int(alpha)),
                outline,
                width=width,
            )
            alpha = max(0, alpha - 25)

        surface.blit(rim_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return surface

    # ------------------------------------------------------------------
    # Material specific extras
    # ------------------------------------------------------------------
    def _add_engine_glow(self, surface: pygame.Surface) -> pygame.Surface:
        width, height = surface.get_size()
        glow = pygame.Surface((width, height), pygame.SRCALPHA)
        engine_y = height - 6
        colors = [(255, 200, 90, 90), (140, 200, 255, 60)]
        offsets = (-width // 4, width // 4)
        for _idx, dx in enumerate(offsets):
            cx = width // 2 + dx
            for radius, color in zip((8, 4), colors):
                pygame.draw.circle(glow, color, (cx, engine_y), radius)
        surface.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return surface

    def _add_bio_core(self, surface: pygame.Surface, level: int) -> pygame.Surface:
        width, height = surface.get_size()
        core_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        base_alpha = 90 + min(level * 5, 80)
        pygame.draw.circle(
            core_surface,
            (255, 90 + min(level * 4, 60), 60, base_alpha),
            (width // 2, height // 2 + 2),
            max(6, width // 5),
        )
        pygame.draw.circle(
            core_surface,
            (255, 150, 120, base_alpha - 20),
            (width // 2, height // 2 + 2),
            max(10, width // 4),
        )
        surface.blit(core_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return surface

    # ------------------------------------------------------------------
    # Layer composition helpers
    # ------------------------------------------------------------------
    def _compose_layers(
        self,
        base_surface: pygame.Surface,
        shaded_surface: pygame.Surface,
        profile: LightingProfile,
        shadow_offset: tuple[int, int],
    ) -> pygame.Surface:
        width, height = base_surface.get_size()
        padding = profile.glow_expand + 8
        result = pygame.Surface((width + padding * 2, height + padding * 2), pygame.SRCALPHA)

        shadow_surface, shadow_pad = self._create_soft_shadow(base_surface, shadow_offset)
        shadow_pos = (
            padding - shadow_pad + shadow_offset[0],
            padding - shadow_pad + shadow_offset[1],
        )
        result.blit(shadow_surface, shadow_pos)

        glow_surface, glow_pad = self._create_outer_glow(base_surface, profile)
        glow_pos = (
            padding - glow_pad,
            padding - glow_pad,
        )
        result.blit(glow_surface, glow_pos)

        base_pos = (padding, padding)
        result.blit(shaded_surface, base_pos)
        return result

    def _create_soft_shadow(
        self,
        base_surface: pygame.Surface,
        offset: tuple[int, int],
    ) -> tuple[pygame.Surface, int]:
        mask = pygame.mask.from_surface(base_surface, 10)
        width, height = base_surface.get_size()
        padding = 12
        blur_size = (width + padding * 2, height + padding * 2)
        shadow_bitmap = mask.to_surface(setcolor=(0, 0, 0, 255), unsetcolor=(0, 0, 0, 0))
        shadow_bitmap = pygame.transform.smoothscale(shadow_bitmap, blur_size)
        shadow_bitmap.set_alpha(110)
        shadow_surface = pygame.Surface(blur_size, pygame.SRCALPHA)
        shadow_surface.blit(shadow_bitmap, (0, 0))
        return shadow_surface, padding

    def _create_outer_glow(
        self,
        base_surface: pygame.Surface,
        profile: LightingProfile,
    ) -> tuple[pygame.Surface, int]:
        mask = pygame.mask.from_surface(base_surface, 10)
        width, height = base_surface.get_size()
        padding = profile.glow_expand // 2 + 6
        glow_size = (width + padding * 2, height + padding * 2)
        mask_surface = mask.to_surface(
            setcolor=(*profile.glow_color, 0),
            unsetcolor=(0, 0, 0, 0),
        )
        glow_surface = pygame.transform.smoothscale(mask_surface, glow_size)
        glow_surface.set_alpha(profile.glow_alpha)
        return glow_surface, padding


__all__ = ["Cinematic3DEffects"]
