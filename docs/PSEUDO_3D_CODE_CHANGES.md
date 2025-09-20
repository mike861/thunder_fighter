# Thunder Fighter Pseudo-3D Code Changes Specification

## Overview

This document provides specific code modifications, new file structures, and class changes needed to implement the pseudo-3D depth scaling system in Thunder Fighter.

## File Structure Changes

### New Files to Create

```
thunder_fighter/
├── entities/
│   └── base_3d.py                    # 3D-aware base classes
├── graphics/
│   ├── depth_renderer.py             # Depth-sorted rendering
│   ├── image_cache.py                # Scaling cache system
│   └── effects/
│       └── depth_effects.py          # Fog and depth visual effects
├── systems/
│   └── depth_manager.py              # Depth calculation utilities
└── config/
    └── pseudo_3d_config.py           # 3D configuration constants
```

### Files to Modify

```
thunder_fighter/
├── entities/
│   ├── base.py                       # Add 3D compatibility layer
│   ├── enemies/
│   │   ├── enemy.py                  # Inherit from Entity3D
│   │   └── enemy_factory.py          # Add depth spawn parameters
│   ├── projectiles/
│   │   ├── bullets.py                # Add depth movement
│   │   └── projectile_factory.py     # Add depth creation options
│   └── player/
│       └── player.py                 # Add depth interaction
├── graphics/
│   ├── background.py                 # Add depth layers
│   └── effects/
│       └── explosion.py              # Add depth-aware explosions
├── systems/
│   ├── collision.py                  # Add depth collision logic
│   ├── spawning.py                   # Add depth spawn logic
│   └── physics.py                    # Add depth movement
└── game.py                           # Integrate depth rendering
```

## Detailed Code Changes

### 1. New Base 3D Classes

**File**: `thunder_fighter/entities/base_3d.py`

```python
"""
3D-aware base entity classes for pseudo-3D rendering.
"""

from typing import Tuple, Optional
import pygame
import math

from thunder_fighter.entities.base import GameObject
from thunder_fighter.constants import WIDTH, HEIGHT


class GameObject3D(GameObject):
    """Base 3D-aware game object with depth support."""

    def __init__(self, x: float, y: float, width: int, height: int, z: float = 0.0):
        super().__init__(x, y, width, height)
        self.z = z  # Depth: 0=nearest, 1000=farthest
        self.perspective_enabled = True

        # Performance caching
        self._cache_scale = None
        self._cache_screen_pos = None
        self._cache_z = None
        self._cache_dirty = True

        # Depth constants (configurable)
        self.depth_factor = 0.002
        self.vanish_point = (WIDTH // 2, HEIGHT // 4)
        self.perspective_x_factor = 0.2
        self.perspective_y_factor = 0.15

    def get_depth_scale(self) -> float:
        """Calculate perspective scaling factor."""
        if self._cache_scale is None or self._cache_dirty:
            self._cache_scale = 1.0 / (1.0 + self.z * self.depth_factor)
        return self._cache_scale

    def get_screen_position(self) -> Tuple[float, float]:
        """Calculate perspective-adjusted screen position."""
        if self._cache_screen_pos is None or self._cache_dirty:
            if not self.perspective_enabled:
                self._cache_screen_pos = (self.x, self.y)
            else:
                depth_factor = self.z / 1000.0
                screen_x = self.x + (self.vanish_point[0] - self.x) * depth_factor * self.perspective_x_factor
                screen_y = self.y + (self.vanish_point[1] - self.y) * depth_factor * self.perspective_y_factor
                self._cache_screen_pos = (screen_x, screen_y)
        return self._cache_screen_pos

    def get_visual_size(self) -> Tuple[int, int]:
        """Get scaled size for rendering."""
        scale = self.get_depth_scale()
        return (max(1, int(self.width * scale)), max(1, int(self.height * scale)))

    def set_depth(self, z: float):
        """Update depth and invalidate cache."""
        if abs(self.z - z) > 0.1:  # Only update if significant change
            self.z = z
            self._invalidate_cache()

    def _invalidate_cache(self):
        """Mark cache as dirty."""
        self._cache_dirty = True
        self._cache_scale = None
        self._cache_screen_pos = None

    def should_render(self) -> bool:
        """Determine if entity should be rendered based on size/distance."""
        scale = self.get_depth_scale()
        visual_size = self.get_visual_size()
        return scale >= 0.05 and visual_size[0] >= 2 and visual_size[1] >= 2


class Entity3D(GameObject3D):
    """3D-aware entity with perspective rendering."""

    def __init__(self, x: float, y: float, width: int, height: int, z: float = 0.0):
        super().__init__(x, y, width, height, z)
        self.z_velocity = 0.0  # Depth movement speed

    def update(self, dt: float):
        """Update with depth movement."""
        # Standard position update
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

        # Depth movement
        if self.z_velocity != 0:
            self.set_depth(self.z + self.z_velocity * dt)

        # Update rect for collision detection (use screen position)
        screen_pos = self.get_screen_position()
        self.rect.x = int(screen_pos[0])
        self.rect.y = int(screen_pos[1])

    def render_3d(self, screen: pygame.Surface):
        """Render entity with 3D perspective effects."""
        if not self.should_render() or not self.image:
            return

        try:
            # Get cached values
            scale = self.get_depth_scale()
            screen_pos = self.get_screen_position()
            visual_size = self.get_visual_size()

            # Get scaled image from cache
            from thunder_fighter.graphics.image_cache import get_scaling_cache
            cache = get_scaling_cache()
            scaled_image = cache.get_scaled_image(self.image, scale)

            if scaled_image:
                # Apply depth effects
                final_image = self._apply_depth_effects(scaled_image, scale)

                # Calculate centered render position
                render_x = screen_pos[0] - visual_size[0] // 2
                render_y = screen_pos[1] - visual_size[1] // 2

                screen.blit(final_image, (render_x, render_y))

        except Exception as e:
            # Fallback to standard rendering
            if hasattr(self, 'render'):
                self.render(screen)

    def _apply_depth_effects(self, image: pygame.Surface, scale: float) -> pygame.Surface:
        """Apply fog and depth-based visual effects."""
        if scale >= 0.8:
            return image  # Near objects unchanged

        # Apply fog effect for distant objects
        fog_intensity = int((1.0 - scale) * 80)
        if fog_intensity > 10:
            fog_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
            fog_surface.fill((20, 30, 50, fog_intensity))

            result = image.copy()
            result.blit(fog_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
            return result

        return image

    def set_z_velocity(self, z_velocity: float):
        """Set depth movement speed."""
        self.z_velocity = z_velocity
```

### 2. Depth Rendering System

**File**: `thunder_fighter/graphics/depth_renderer.py`

```python
"""
Depth-aware rendering system for pseudo-3D effects.
"""

import pygame
from typing import List, Any
from thunder_fighter.utils.logger import logger


class DepthSortedGroup(pygame.sprite.Group):
    """Sprite group that renders entities in depth order."""

    def __init__(self):
        super().__init__()
        self._sorted_sprites = []
        self._sort_dirty = True
        self._render_stats = {
            "rendered": 0,
            "skipped": 0,
            "total": 0
        }

    def add(self, *sprites):
        """Add sprites and mark for re-sorting."""
        super().add(*sprites)
        self._sort_dirty = True

    def remove(self, *sprites):
        """Remove sprites and mark for re-sorting."""
        super().remove(*sprites)
        self._sort_dirty = True

    def _sort_by_depth(self):
        """Sort sprites by depth (farthest first for proper layering)."""
        if self._sort_dirty:
            all_sprites = self.sprites()
            self._sorted_sprites = sorted(
                all_sprites,
                key=lambda sprite: getattr(sprite, 'z', 0),
                reverse=True  # Render far to near
            )
            self._sort_dirty = False

    def render_with_depth(self, screen: pygame.Surface):
        """Render all sprites with depth-aware transformations."""
        self._sort_by_depth()

        rendered = 0
        skipped = 0

        for sprite in self._sorted_sprites:
            if hasattr(sprite, 'render_3d') and hasattr(sprite, 'should_render'):
                if sprite.should_render():
                    sprite.render_3d(screen)
                    rendered += 1
                else:
                    skipped += 1
            elif hasattr(sprite, 'image') and hasattr(sprite, 'rect'):
                # Fallback for 2D sprites
                screen.blit(sprite.image, sprite.rect)
                rendered += 1
            else:
                skipped += 1

        # Update stats
        self._render_stats = {
            "rendered": rendered,
            "skipped": skipped,
            "total": len(self._sorted_sprites)
        }

    def get_render_stats(self) -> dict:
        """Get rendering performance statistics."""
        return self._render_stats.copy()

    def update(self, *args):
        """Override update to handle depth-based LOD."""
        for sprite in self.sprites():
            if hasattr(sprite, 'update'):
                # Apply LOD-based update frequency
                update_freq = self._get_update_frequency(sprite)
                if update_freq >= 1.0 or getattr(sprite, '_lod_counter', 0) % int(1.0 / update_freq) == 0:
                    sprite.update(*args)

                # Increment LOD counter
                sprite._lod_counter = getattr(sprite, '_lod_counter', 0) + 1

    def _get_update_frequency(self, sprite) -> float:
        """Get update frequency based on sprite depth."""
        if hasattr(sprite, 'get_depth_scale'):
            scale = sprite.get_depth_scale()
            if scale >= 0.8:
                return 1.0  # Full frequency
            elif scale >= 0.4:
                return 0.5  # Half frequency
            else:
                return 0.25  # Quarter frequency
        return 1.0  # Default full frequency


class DepthRenderer:
    """Main depth rendering coordinator."""

    def __init__(self):
        self.enabled = True
        self.debug_mode = False
        self.performance_mode = "auto"  # "high", "medium", "low", "auto"

    def render_scene(self, screen: pygame.Surface, sprite_groups: List[DepthSortedGroup]):
        """Render entire scene with depth sorting."""
        if not self.enabled:
            # Fallback to standard rendering
            for group in sprite_groups:
                group.draw(screen)
            return

        # Collect all sprites from all groups
        all_sprites = []
        for group in sprite_groups:
            all_sprites.extend(group.sprites())

        # Sort by depth globally
        all_sprites.sort(key=lambda sprite: getattr(sprite, 'z', 0), reverse=True)

        # Render in depth order
        for sprite in all_sprites:
            if hasattr(sprite, 'render_3d') and hasattr(sprite, 'should_render'):
                if sprite.should_render():
                    sprite.render_3d(screen)
            elif hasattr(sprite, 'image') and hasattr(sprite, 'rect'):
                screen.blit(sprite.image, sprite.rect)

        # Debug rendering
        if self.debug_mode:
            self._render_debug_info(screen, all_sprites)

    def _render_debug_info(self, screen: pygame.Surface, sprites: List[Any]):
        """Render debug information about depth."""
        font = pygame.font.Font(None, 24)

        for sprite in sprites[:10]:  # Show top 10 for performance
            if hasattr(sprite, 'z') and hasattr(sprite, 'rect'):
                depth_text = font.render(f"Z:{sprite.z:.0f}", True, (255, 255, 0))
                screen.blit(depth_text, (sprite.rect.x, sprite.rect.y - 20))

    def set_performance_mode(self, mode: str):
        """Set performance mode for depth rendering."""
        self.performance_mode = mode
        logger.info(f"Depth renderer performance mode set to: {mode}")

    def toggle_debug(self):
        """Toggle debug visualization."""
        self.debug_mode = not self.debug_mode
        logger.info(f"Depth renderer debug mode: {self.debug_mode}")
```

### 3. Image Scaling Cache

**File**: `thunder_fighter/graphics/image_cache.py`

```python
"""
LRU cache system for scaled images to optimize 3D rendering performance.
"""

import pygame
from typing import Dict, Tuple, Optional
from collections import OrderedDict
from thunder_fighter.utils.logger import logger


class ScalingCache:
    """LRU cache for scaled images with performance optimization."""

    def __init__(self, max_size: int = 200, scale_precision: int = 2):
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size
        self.scale_precision = scale_precision

        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def get_scaled_image(self, original: pygame.Surface, scale: float) -> Optional[pygame.Surface]:
        """Get cached scaled image or create new one."""
        if scale <= 0.01:
            return None  # Too small to render

        # Quantize scale to reduce cache fragmentation
        quantized_scale = round(scale, self.scale_precision)
        if quantized_scale <= 0.01:
            return None

        # Create cache key
        cache_key = (id(original), quantized_scale)

        # Check cache
        if cache_key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(cache_key)
            self.hits += 1
            return self.cache[cache_key]

        # Cache miss - create new scaled image
        self.misses += 1
        scaled_image = self._create_scaled_image(original, quantized_scale)

        if scaled_image:
            self._add_to_cache(cache_key, scaled_image)

        return scaled_image

    def _create_scaled_image(self, original: pygame.Surface, scale: float) -> Optional[pygame.Surface]:
        """Create a new scaled image."""
        try:
            original_width = original.get_width()
            original_height = original.get_height()

            new_width = max(1, int(original_width * scale))
            new_height = max(1, int(original_height * scale))

            # Use smooth scaling for better quality
            if scale < 0.5:
                # For significant downscaling, use smoother algorithm
                return pygame.transform.smoothscale(original, (new_width, new_height))
            else:
                # For minor scaling, use faster algorithm
                return pygame.transform.scale(original, (new_width, new_height))

        except Exception as e:
            logger.error(f"Error creating scaled image: {e}")
            return None

    def _add_to_cache(self, cache_key: Tuple, image: pygame.Surface):
        """Add image to cache with LRU management."""
        # Remove oldest entries if cache is full
        while len(self.cache) >= self.max_size:
            oldest_key, oldest_image = self.cache.popitem(last=False)
            self.evictions += 1

        # Add new entry
        self.cache[cache_key] = image

    def clear(self):
        """Clear the entire cache."""
        self.cache.clear()
        logger.info("Image scaling cache cleared")

    def get_stats(self) -> Dict[str, int]:
        """Get cache performance statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": hit_rate
        }

    def optimize(self):
        """Optimize cache by removing rarely used entries."""
        if len(self.cache) > self.max_size * 0.8:
            # Remove oldest 25% of entries
            remove_count = len(self.cache) // 4
            for _ in range(remove_count):
                if self.cache:
                    self.cache.popitem(last=False)
                    self.evictions += 1


# Global cache instance
_global_scaling_cache: Optional[ScalingCache] = None


def get_scaling_cache() -> ScalingCache:
    """Get the global scaling cache instance."""
    global _global_scaling_cache
    if _global_scaling_cache is None:
        _global_scaling_cache = ScalingCache()
    return _global_scaling_cache


def clear_scaling_cache():
    """Clear the global scaling cache."""
    global _global_scaling_cache
    if _global_scaling_cache:
        _global_scaling_cache.clear()
```

### 4. Configuration Constants

**File**: `thunder_fighter/config/pseudo_3d_config.py`

```python
"""
Configuration constants for pseudo-3D rendering system.
"""

# Core 3D rendering settings
PSEUDO_3D_CONFIG = {
    "enabled": True,
    "depth_intensity": 1.0,          # 0.5-2.0 range for effect strength
    "fog_enabled": True,             # Enable distance fog effects
    "perspective_strength": 1.0,     # 0.5-2.0 range for perspective distortion
    "performance_mode": "auto",      # "high", "medium", "low", "auto"
}

# Depth calculation parameters
DEPTH_SETTINGS = {
    "depth_factor": 0.002,           # Perspective scaling factor
    "vanish_point_x": 0.5,           # Vanishing point X (0.0-1.0 screen ratio)
    "vanish_point_y": 0.25,          # Vanishing point Y (0.0-1.0 screen ratio)
    "perspective_x_factor": 0.2,     # Horizontal perspective strength
    "perspective_y_factor": 0.15,    # Vertical perspective strength
    "min_render_scale": 0.05,        # Minimum scale before culling
    "min_render_size": 2,            # Minimum pixel size before culling
}

# Spawning depth ranges
SPAWN_DEPTH_CONFIG = {
    "enemy_min_depth": 500,          # Minimum enemy spawn depth
    "enemy_max_depth": 800,          # Maximum enemy spawn depth
    "enemy_depth_variation": 200,    # Random depth variation
    "boss_spawn_depth": 600,         # Boss spawn depth
    "item_spawn_depth": 400,         # Item spawn depth
    "bullet_start_depth": 100,       # Player bullet starting depth
}

# Performance settings
PERFORMANCE_CONFIG = {
    "image_cache_size": 200,         # Max cached scaled images
    "scale_precision": 2,            # Decimal places for scale quantization
    "lod_thresholds": {              # Level of detail thresholds
        "high": 0.8,                 # Above this: full quality
        "medium": 0.4,               # Above this: medium quality
        "low": 0.2,                  # Above this: low quality
    },
    "update_frequencies": {          # Update frequency multipliers
        "high": 1.0,                 # Full update rate
        "medium": 0.5,               # Half update rate
        "low": 0.25,                 # Quarter update rate
    },
}

# Visual effects settings
VISUAL_EFFECTS_CONFIG = {
    "fog_color": (20, 30, 50),       # RGB color for distance fog
    "fog_intensity_max": 80,         # Maximum fog alpha value
    "fog_start_distance": 0.8,       # Scale value where fog starts
    "depth_color_shift": True,       # Enable color shifting by depth
    "particle_depth_scaling": True,  # Scale particle effects by depth
}

# Debug settings
DEBUG_3D_CONFIG = {
    "show_depth_values": False,      # Display depth numbers on entities
    "render_depth_zones": False,     # Show depth zone boundaries
    "collision_depth_visualization": False,  # Visualize collision depths
    "performance_overlay": False,    # Show performance metrics
    "cache_statistics": False,       # Display cache hit rates
}

# Gameplay balance settings
GAMEPLAY_3D_CONFIG = {
    "depth_hit_probability": True,   # Reduce hit chance for distant targets
    "depth_score_bonus": True,       # Bonus points for distant hits
    "depth_difficulty_scaling": True, # Scale difficulty with depth
    "auto_aim_assistance": False,    # Provide aim assistance for distant targets
    "collision_depth_tolerance": 100, # Max depth difference for collisions
}
```

## Key Modifications to Existing Files

### Entity Base Classes

**File**: `thunder_fighter/entities/base.py` (Add compatibility layer)

```python
# Add at the end of the file

def upgrade_to_3d(entity: Entity, z: float = 0.0) -> 'Entity3D':
    """
    Upgrade a 2D entity to 3D capabilities.
    This provides backward compatibility during transition.
    """
    from thunder_fighter.entities.base_3d import Entity3D

    # Create new 3D entity with same properties
    entity_3d = Entity3D(entity.x, entity.y, entity.width, entity.height, z)

    # Copy relevant attributes
    entity_3d.velocity_x = entity.velocity_x
    entity_3d.velocity_y = entity.velocity_y
    entity_3d.health = entity.health
    entity_3d.max_health = entity.max_health
    entity_3d.active = entity.active
    entity_3d.image = entity.image
    entity_3d.rect = entity.rect.copy()

    return entity_3d
```

### Enemy Class Modifications

**File**: `thunder_fighter/entities/enemies/enemy.py` (Add to imports and modify class)

```python
# Add import
from thunder_fighter.entities.base_3d import Entity3D
from thunder_fighter.config.pseudo_3d_config import SPAWN_DEPTH_CONFIG
import math

# Modify class declaration
class Enemy(Entity3D):  # Changed from pygame.sprite.Sprite
    """3D-aware enemy with depth-based movement."""

    def __init__(self, game_time=0, game_level=1, all_sprites=None,
                 enemy_bullets_group=None, spawn_depth=None):

        # Calculate spawn depth
        if spawn_depth is None:
            base_depth = SPAWN_DEPTH_CONFIG["enemy_min_depth"] + (game_level * 30)
            depth_variation = SPAWN_DEPTH_CONFIG["enemy_depth_variation"]
            spawn_depth = base_depth + random.uniform(-depth_variation//2, depth_variation//2)
            spawn_depth = max(SPAWN_DEPTH_CONFIG["enemy_min_depth"],
                            min(SPAWN_DEPTH_CONFIG["enemy_max_depth"], spawn_depth))

        # Initialize with depth
        super().__init__(
            x=random.randrange(WIDTH - 32),
            y=random.randrange(-100, -50),
            width=32, height=32,
            z=spawn_depth
        )

        # Set depth movement (toward player)
        self.set_z_velocity(-random.uniform(30, 80))

        # Add depth oscillation for visual interest
        self.depth_oscillation_phase = random.uniform(0, math.pi * 2)
        self.depth_oscillation_amplitude = random.uniform(5, 20)

        # Rest of existing initialization...

    def update(self, dt: float):
        """Update with 3D depth movement."""
        # Call parent 3D update
        super().update(dt)

        # Add depth oscillation
        self.depth_oscillation_phase += dt * 2.0
        depth_offset = math.sin(self.depth_oscillation_phase) * self.depth_oscillation_amplitude
        current_depth = self.z + depth_offset

        # Remove if too close or off-screen
        if current_depth <= 50 or self.rect.y > HEIGHT + 100:
            self.kill()
```

### Game Loop Integration

**File**: `thunder_fighter/game.py` (Modify rendering loop)

```python
# Add imports
from thunder_fighter.graphics.depth_renderer import DepthSortedGroup, DepthRenderer
from thunder_fighter.config.pseudo_3d_config import PSEUDO_3D_CONFIG

class RefactoredGame:
    def __init__(self):
        # Existing initialization...

        # Initialize 3D rendering system
        self.depth_renderer = DepthRenderer()
        self.use_3d_rendering = PSEUDO_3D_CONFIG["enabled"]

        # Convert sprite groups to depth-aware groups
        if self.use_3d_rendering:
            self.all_sprites = DepthSortedGroup()
            self.enemies = DepthSortedGroup()
            self.bullets = DepthSortedGroup()
            self.boss_bullets = DepthSortedGroup()
            self.missiles = DepthSortedGroup()
            self.bosses = DepthSortedGroup()
            self.items = DepthSortedGroup()
        else:
            # Keep existing sprite groups for 2D mode
            pass

    def render(self):
        """Enhanced rendering with 3D depth support."""
        # Clear screen
        self.screen.fill((0, 0, 0))

        # Render background (with depth layers if enabled)
        if hasattr(self.background, 'render_with_depth') and self.use_3d_rendering:
            self.background.render_with_depth(self.screen)
        else:
            self.background.render(self.screen)

        # Render entities with depth sorting
        if self.use_3d_rendering:
            sprite_groups = [self.all_sprites]  # Or multiple groups
            self.depth_renderer.render_scene(self.screen, sprite_groups)
        else:
            # Fallback to standard rendering
            self.all_sprites.draw(self.screen)

        # Render UI elements (always on top)
        if self.ui_manager:
            self.ui_manager.render(self.screen)

        # Update display
        pygame.display.flip()
```

## Implementation Priority

### Phase 1 (Core Infrastructure)
1. Create `base_3d.py` with core 3D classes
2. Create `image_cache.py` with scaling cache
3. Create `depth_renderer.py` with rendering system
4. Create `pseudo_3d_config.py` with all configurations

### Phase 2 (Entity Integration)
1. Modify `enemy.py` to inherit from Entity3D
2. Update `enemy_factory.py` with depth spawn parameters
3. Modify `game.py` to use DepthSortedGroup
4. Add depth movement to projectiles

### Phase 3 (Systems Integration)
1. Update collision system with depth awareness
2. Enhance spawning system with depth logic
3. Add depth effects to background system
4. Implement performance optimizations

### Phase 4 (Polish & Balance)
1. Add visual effects (fog, depth blur)
2. Implement LOD system
3. Add configuration options
4. Balance gameplay difficulty

This structured approach ensures each component is properly implemented and tested before moving to the next phase.