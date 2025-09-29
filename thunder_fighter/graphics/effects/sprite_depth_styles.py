"""
Sprite depth styling utilities to enhance 2.5D look for ships.

These functions are offline-friendly (for asset preview/export) and avoid
adding runtime cost in the main loop. They add cues like drop shadows,
specular highlights, rim light and slight tilt to improve perceived depth.
"""

from __future__ import annotations

from typing import Tuple, Literal, Optional

import pygame


Color = Tuple[int, int, int]
RGBA = Tuple[int, int, int, int]
StyleName = Literal["classic_3d", "arcade_rim", "tilt_left", "tilt_right"]


def _make_canvas(size: Tuple[int, int], alpha: bool = True) -> pygame.Surface:
    flags = pygame.SRCALPHA if alpha else 0
    return pygame.Surface(size, flags)


def _with_padding(surface: pygame.Surface, pad: int) -> pygame.Surface:
    w, h = surface.get_size()
    canvas = _make_canvas((w + pad * 2, h + pad * 2))
    canvas.blit(surface, (pad, pad))
    return canvas


def _drop_shadow(
    surface: pygame.Surface,
    offset: Tuple[int, int] = (6, 6),
    alpha: int = 110,
    blur_radius: int = 2,
) -> pygame.Surface:
    """Return a new surface with dropped shadow behind the original surface."""
    ox, oy = offset
    w, h = surface.get_size()
    canvas = _make_canvas((w + abs(ox), h + abs(oy)))

    # Create shadow from silhouette
    shadow = surface.copy()
    shadow.fill((0, 0, 0, 0))
    # Use original alpha as mask; draw a solid black copy
    mask = surface.copy()
    mask.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    mask.set_alpha(alpha)

    # Place shadow with offset
    sx = max(0, ox)
    sy = max(0, oy)
    canvas.blit(mask, (sx, sy))

    # Simple blur: scale down then up a few times (only used offline)
    if blur_radius > 0:
        try:
            small = pygame.transform.smoothscale(canvas, (max(1, (w + abs(ox)) // 2), max(1, (h + abs(oy)) // 2)))
            canvas = pygame.transform.smoothscale(small, (w + abs(ox), h + abs(oy)))
        except Exception:
            pass

    # Draw original on top (aligned at 0,0 relative to shadow canvas origin)
    canvas.blit(surface, (0, 0))
    return canvas


def _linear_vertical_gradient(size: Tuple[int, int], top_rgba: RGBA, bottom_rgba: RGBA) -> pygame.Surface:
    w, h = size
    grad = _make_canvas((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top_rgba[0] * (1 - t) + bottom_rgba[0] * t)
        g = int(top_rgba[1] * (1 - t) + bottom_rgba[1] * t)
        b = int(top_rgba[2] * (1 - t) + bottom_rgba[2] * t)
        a = int(top_rgba[3] * (1 - t) + bottom_rgba[3] * t)
        pygame.draw.line(grad, (r, g, b, a), (0, y), (w, y))
    return grad


def _specular_highlight(size: Tuple[int, int], pos: Tuple[int, int], radius: int, color: RGBA) -> pygame.Surface:
    w, h = size
    surf = _make_canvas((w, h))
    cx, cy = pos
    # soft circle by multiple rings
    for r in range(radius, 0, -2):
        alpha = int(color[3] * (r / radius) ** 2)
        pygame.draw.circle(surf, (color[0], color[1], color[2], alpha), (cx, cy), r)
    return surf


def _rim_light(surface: pygame.Surface, color: RGBA = (255, 255, 255, 60)) -> pygame.Surface:
    w, h = surface.get_size()
    rim = _make_canvas((w, h))
    # Draw an outer glow around opaque areas by expanding silhouette
    base = surface.copy()
    base.set_alpha(255)
    for d in (1, 2):
        for dx in (-d, 0, d):
            for dy in (-d, 0, d):
                if dx == 0 and dy == 0:
                    continue
                rim.blit(base, (dx, dy))
    # Colorize
    color_layer = _make_canvas((w, h))
    color_layer.fill(color)
    rim.blit(color_layer, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return rim


def apply_depth_style(
    image: pygame.Surface,
    style: StyleName,
    *,
    tilt_degrees: Optional[int] = None,
) -> pygame.Surface:
    """Apply a pre-defined depth style to the given ship image.

    Styles:
      - classic_3d: slight left tilt, soft drop shadow, top-left highlight, bottom shade
      - arcade_rim: no tilt, strong rim light, compact shadow
      - tilt_left / tilt_right: pronounced tilt, highlight on leading edge
    """
    base = image.convert_alpha()

    # Optional tilt
    if style in ("tilt_left", "classic_3d"):
        angle = tilt_degrees if tilt_degrees is not None else -12
        base = pygame.transform.rotate(base, angle)
    elif style == "tilt_right":
        angle = tilt_degrees if tilt_degrees is not None else 12
        base = pygame.transform.rotate(base, angle)

    # Start with drop shadow
    if style == "arcade_rim":
        composed = _drop_shadow(base, offset=(4, 4), alpha=140, blur_radius=1)
    else:
        composed = _drop_shadow(base, offset=(8, 8), alpha=120, blur_radius=2)

    w, h = composed.get_size()

    # Overlays: gradient shading and specular
    if style in ("classic_3d", "tilt_left", "tilt_right"):
        # Top highlight to bottom shade
        grad = _linear_vertical_gradient((w, h), (255, 255, 255, 35), (0, 0, 0, 70))
        composed.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # Specular spot near nose (assuming ship points up in original, adjust after rotate)
        spec = _specular_highlight((w, h), (int(w * 0.55), int(h * 0.25)), max(6, min(w, h) // 8), (255, 255, 255, 90))
        composed.blit(spec, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    if style == "arcade_rim":
        rim = _rim_light(base)
        # Center rim over composed; base is unpadded relative to composed top-left
        composed.blit(rim, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    return composed

