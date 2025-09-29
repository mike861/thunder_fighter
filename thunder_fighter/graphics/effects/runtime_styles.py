"""
Runtime-friendly sprite styling for 2.5D effects (arcade_rim).

Designed to be fast (no blurs), and used together with a small LRU cache.
"""

from __future__ import annotations

import pygame


def apply_arcade_rim_fast(
    surface: pygame.Surface,
    *,
    shadow_offset: tuple[int, int] = (6, 6),
    shadow_alpha: int = 140,
    rim_alpha: int = 60,
    rim_radius: int = 2,
) -> pygame.Surface:
    """Apply a fast arcade rim + drop shadow style.

    - Shadow: single offset, no blur
    - Rim: silhouette expansion with 1–2px offsets, colorized white with alpha
    """
    base = surface
    w, h = base.get_size()
    ox, oy = shadow_offset
    canvas_w = w + max(0, ox)
    canvas_h = h + max(0, oy)

    canvas = pygame.Surface((canvas_w, canvas_h), pygame.SRCALPHA)

    # Shadow from silhouette
    shadow = base.copy()
    shadow.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    shadow.set_alpha(max(0, min(255, shadow_alpha)))
    canvas.blit(shadow, (max(0, ox), max(0, oy)))

    # Draw original on top
    canvas.blit(base, (0, 0))

    # Rim light (white glow around edges)
    rim = pygame.Surface((w, h), pygame.SRCALPHA)
    opaque = base.copy()
    opaque.set_alpha(255)

    rim_radius = max(1, rim_radius)
    for d in range(1, rim_radius + 1):
        for dx in (-d, 0, d):
            for dy in (-d, 0, d):
                if dx == 0 and dy == 0:
                    continue
                rim.blit(opaque, (dx, dy))

    # Colorize rim
    tint = pygame.Surface((w, h), pygame.SRCALPHA)
    tint.fill((255, 255, 255, max(0, min(255, rim_alpha))))
    rim.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    canvas.blit(rim, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return canvas
