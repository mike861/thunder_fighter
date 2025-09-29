"""
Generate 3D style sample images for player and enemy ships.

Outputs PNGs under docs/3d_samples/ for quick visual comparison.
Safe to run headless (sets SDL_VIDEODRIVER=dummy).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from thunder_fighter.graphics.renderers import create_player_ship, create_enemy_ship
from thunder_fighter.graphics.effects.sprite_depth_styles import apply_depth_style


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_image(surface: pygame.Surface, out_path: Path) -> None:
    pygame.image.save(surface, str(out_path))


def compose_preview(title: str, styled: pygame.Surface) -> pygame.Surface:
    # Add a subtle checkerboard background to appreciate transparency and shadow
    w, h = styled.get_size()
    pad = 16
    tile = 8
    canvas = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)

    # checkerboard
    for y in range(0, h + pad * 2, tile):
        for x in range(0, w + pad * 2, tile):
            c = 230 if (x // tile + y // tile) % 2 == 0 else 200
            pygame.draw.rect(canvas, (c, c, c, 255), (x, y, tile, tile))

    # blit sprite
    canvas.blit(styled, (pad, pad))

    # title
    try:
        pygame.font.init()
        font = pygame.font.Font(None, 20)
        text = font.render(title, True, (20, 20, 20))
        canvas.blit(text, (8, 6))
    except Exception:
        pass

    return canvas


def main() -> int:
    pygame.init()
    # Minimal hidden window for surface conversions
    try:
        pygame.display.set_mode((1, 1))
    except Exception:
        pass

    out_dir = Path("docs/3d_samples")
    ensure_dir(out_dir)

    styles = [
        ("classic_3d", {}),
        ("arcade_rim", {}),
        ("tilt_left", {}),
        ("tilt_right", {}),
    ]

    # Player ship samples
    player = create_player_ship()
    for style, kw in styles:
        styled = apply_depth_style(player, style, **kw)
        img = compose_preview(f"player - {style}", styled)
        save_image(img, out_dir / f"player_{style}.png")

    # Enemy samples at different levels to show base art variation
    enemy_levels = [1, 5, 9]
    for lvl in enemy_levels:
        enemy = create_enemy_ship(lvl)
        for style, kw in styles:
            styled = apply_depth_style(enemy, style, **kw)
            img = compose_preview(f"enemy L{lvl} - {style}", styled)
            save_image(img, out_dir / f"enemy_L{lvl}_{style}.png")

    print(f"Saved samples to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
