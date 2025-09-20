# Thunder Fighter Pseudo-3D Implementation Design

## Executive Summary

This document provides a detailed implementation design for transforming Thunder Fighter from a 2D space shooter into a pseudo-3D visual experience using the **Depth Scaling System** approach. The design leverages the existing event-driven architecture, factory patterns, and sprite-based entity system while introducing depth-aware rendering and physics.

## Current Architecture Analysis

### Existing Entity Hierarchy
The game currently uses a well-structured entity system:
```
GameObject (abstract base)
├── Entity (concrete implementation)
├── MovableEntity (adds movement)
└── LivingEntity (adds health/damage)
```

### Current Rendering Pipeline
- **Entity Rendering**: Each entity handles its own `render()` method via `entity.render(screen)`
- **Sprite Groups**: Entities managed through `pygame.sprite.Group` for batch operations
- **Layer Management**: Basic z-ordering through sprite group internal ordering
- **Resource Management**: Centralized asset loading via `ResourceManager`

### Current Physics System
- **Movement**: Position updates via `velocity_x` and `velocity_y`
- **Boundaries**: Screen boundary detection and entity cleanup
- **Collision**: Unified collision detection via `CollisionSystem`
- **Update Loop**: Delta-time based updates (`update(dt: float)`)

## Pseudo-3D Implementation Strategy

### Phase 1: Core 3D Foundation (2-3 days)

#### 1.1 Enhanced Base Entity Classes

**New File**: `thunder_fighter/entities/base_3d.py`

```python
class GameObject3D(GameObject):
    """3D-aware base game object with depth support"""

    def __init__(self, x: float, y: float, width: int, height: int, z: float = 0.0):
        super().__init__(x, y, width, height)
        self.z = z  # Depth: 0=nearest, 1000=farthest
        self.base_scale = 1.0
        self.perspective_enabled = True

        # Caching for performance
        self._cached_scale = None
        self._cached_screen_pos = None
        self._cached_z = None
        self._cache_dirty = True

    def get_depth_scale(self) -> float:
        """Calculate perspective scaling based on depth"""
        if self._cached_scale is None or self._cache_dirty:
            # Linear perspective formula: scale = 1.0 / (1.0 + z * depth_factor)
            depth_factor = 0.002  # Tunable parameter
            self._cached_scale = 1.0 / (1.0 + self.z * depth_factor)
            self._cache_dirty = False
        return self._cached_scale

    def get_screen_position(self) -> Tuple[float, float]:
        """Calculate perspective-adjusted screen position"""
        if self._cached_screen_pos is None or self._cache_dirty:
            if not self.perspective_enabled:
                self._cached_screen_pos = (self.x, self.y)
            else:
                # Vanishing point configuration
                vanish_point = (WIDTH // 2, HEIGHT // 4)
                depth_factor = self.z / 1000.0

                # Apply perspective transformation
                screen_x = self.x + (vanish_point[0] - self.x) * depth_factor * 0.2
                screen_y = self.y + (vanish_point[1] - self.y) * depth_factor * 0.15
                self._cached_screen_pos = (screen_x, screen_y)

        return self._cached_screen_pos

    def set_depth(self, z: float):
        """Update depth and invalidate cache"""
        if self.z != z:
            self.z = z
            self._cache_dirty = True

    def get_visual_size(self) -> Tuple[int, int]:
        """Get scaled size for rendering"""
        scale = self.get_depth_scale()
        return (int(self.width * scale), int(self.height * scale))
```

#### 1.2 Depth-Aware Rendering System

**New File**: `thunder_fighter/graphics/depth_renderer.py`

```python
class DepthSortedGroup(pygame.sprite.Group):
    """Sprite group that renders entities by depth order"""

    def __init__(self):
        super().__init__()
        self._sorted_sprites = []
        self._sort_dirty = True

    def add(self, *sprites):
        """Add sprites and mark for re-sorting"""
        super().add(*sprites)
        self._sort_dirty = True

    def remove(self, *sprites):
        """Remove sprites and mark for re-sorting"""
        super().remove(*sprites)
        self._sort_dirty = True

    def _sort_by_depth(self):
        """Sort sprites by depth (farthest first)"""
        if self._sort_dirty:
            self._sorted_sprites = sorted(
                self.sprites(),
                key=lambda sprite: getattr(sprite, 'z', 0),
                reverse=True  # Far to near rendering
            )
            self._sort_dirty = False

    def render_with_depth(self, screen: pygame.Surface):
        """Render all sprites with depth-aware transformations"""
        self._sort_by_depth()

        for sprite in self._sorted_sprites:
            if hasattr(sprite, 'render_3d'):
                sprite.render_3d(screen)
            elif hasattr(sprite, 'image') and hasattr(sprite, 'rect'):
                # Fallback for 2D sprites
                screen.blit(sprite.image, sprite.rect)
```

#### 1.3 Enhanced Entity Implementations

**Modify**: `thunder_fighter/entities/base.py`

```python
class Entity3D(GameObject3D):
    """3D-aware entity with perspective rendering"""

    def render_3d(self, screen: pygame.Surface):
        """Render entity with 3D perspective effects"""
        if not self.image or not self.perspective_enabled:
            # Fallback to standard rendering
            self.render(screen)
            return

        try:
            # Get perspective-adjusted values
            scale = self.get_depth_scale()
            screen_pos = self.get_screen_position()
            visual_size = self.get_visual_size()

            # Skip rendering if too small or too far
            if scale < 0.1 or visual_size[0] < 2 or visual_size[1] < 2:
                return

            # Create scaled image (with caching)
            scaled_image = self._get_scaled_image(scale)
            if scaled_image:
                # Apply depth-based effects
                final_image = self._apply_depth_effects(scaled_image, scale)

                # Calculate render position (center-adjusted)
                render_x = screen_pos[0] - visual_size[0] // 2
                render_y = screen_pos[1] - visual_size[1] // 2

                screen.blit(final_image, (render_x, render_y))

        except Exception as e:
            logger.error(f"Error in 3D rendering: {e}")
            self.render(screen)  # Fallback

    def _get_scaled_image(self, scale: float) -> pygame.Surface:
        """Get cached scaled image"""
        # Image caching implementation for performance
        cache_key = f"{id(self.image)}_{scale:.3f}"
        # Implementation with LRU cache or similar

    def _apply_depth_effects(self, image: pygame.Surface, scale: float) -> pygame.Surface:
        """Apply fog and depth-based visual effects"""
        if scale >= 0.8:
            return image  # Near objects unchanged

        # Apply fog effect for distant objects
        fog_intensity = int((1.0 - scale) * 100)
        fog_surface = pygame.Surface(image.get_size())
        fog_surface.fill((20, 30, 50))  # Deep space color
        fog_surface.set_alpha(fog_intensity)

        result = image.copy()
        result.blit(fog_surface, (0, 0), special_flags=pygame.BLEND_MULT)
        return result
```

### Phase 2: Game Integration (3-4 days)

#### 2.1 Enemy System Enhancement

**Modify**: `thunder_fighter/entities/enemies/enemy.py`

```python
class Enemy(Entity3D):
    """3D-aware enemy with depth-based spawning"""

    def __init__(self, game_time=0, game_level=1, all_sprites=None,
                 enemy_bullets_group=None, spawn_depth=None):
        # Calculate spawn depth based on level and randomization
        if spawn_depth is None:
            base_depth = 600 + (game_level * 50)  # Deeper for higher levels
            spawn_depth = base_depth + random.uniform(-100, 200)

        super().__init__(
            x=random.randrange(WIDTH - 60),
            y=random.randrange(-100, -50),
            width=32, height=32,
            z=spawn_depth
        )

        # 3D movement pattern
        self.z_velocity = -random.uniform(50, 150)  # Move toward player
        self.depth_phase = random.uniform(0, 6.28)  # For oscillation

    def update(self, dt: float):
        """Update with depth movement"""
        # Standard 2D movement
        super().update(dt)

        # Depth movement (toward player)
        self.set_depth(self.z + self.z_velocity * dt)

        # Optional: Add depth oscillation for visual interest
        depth_oscillation = math.sin(self.depth_phase) * 10
        self.depth_phase += dt * 2.0

        # Remove if too close or off-screen
        if self.z <= 0 or self.rect.y > HEIGHT + 50:
            self.kill()
```

#### 2.2 Collision System Adaptation

**Modify**: `thunder_fighter/systems/collision.py`

```python
class CollisionSystem:
    """Enhanced collision system with 3D depth awareness"""

    def check_bullet_enemy_collisions(self, enemies, bullets, all_sprites,
                                    score, last_score_checkpoint, score_threshold,
                                    items_group, player):
        """3D-aware collision detection"""
        hits = []

        for bullet in bullets:
            for enemy in enemies:
                # Check 2D collision first
                if bullet.rect.colliderect(enemy.rect):
                    # Add depth-based collision refinement
                    bullet_z = getattr(bullet, 'z', 0)
                    enemy_z = getattr(enemy, 'z', 0)
                    depth_diff = abs(bullet_z - enemy_z)

                    # Allow collision if depth difference is reasonable
                    max_collision_depth = 100  # Tunable parameter
                    if depth_diff <= max_collision_depth:
                        hits.append((bullet, enemy))

        # Process hits with depth-based scoring
        for bullet, enemy in hits:
            bullet.kill()
            enemy.kill()

            # Depth-based scoring bonus
            depth_bonus = max(0, int(enemy.z / 100))  # Further = more points
            base_score = 10 + getattr(enemy, "level", 0) * 2
            total_score = base_score + depth_bonus
            score.update(total_score)

            # Create explosion at depth-adjusted position
            explosion_pos = enemy.get_screen_position()
            explosion = create_explosion(explosion_pos, "md", depth=enemy.z)
            all_sprites.add(explosion)
```

#### 2.3 Spawning System Updates

**Modify**: `thunder_fighter/systems/spawning.py`

```python
class SpawningSystem:
    """3D-aware entity spawning"""

    def _update_enemy_spawning(self, dt: float, current_time: float, game_state: Dict[str, Any]):
        """Spawn enemies with depth variation"""
        if current_time - self.last_spawn_times["enemy"] >= self.spawn_rates["enemy"]:
            try:
                game_level = game_state.get("level", 1)
                enemy_level = min(game_level, 5)

                # Calculate spawn depth range based on game progression
                min_depth = 500 + (game_level * 30)
                max_depth = 800 + (game_level * 50)
                spawn_depth = random.uniform(min_depth, max_depth)

                # Create 3D enemy
                enemy = self.enemy_factory.create_enemy(
                    level=enemy_level,
                    x=random.randint(50, game_state.get("screen_width", 800) - 50),
                    y=-50,
                    spawn_depth=spawn_depth
                )

                # Add to groups
                enemies_group = game_state.get("enemies_group")
                all_sprites = game_state.get("all_sprites")

                if enemies_group and all_sprites:
                    enemies_group.add(enemy)
                    all_sprites.add(enemy)

                self.last_spawn_times["enemy"] = current_time
                logger.debug(f"3D Enemy spawned at depth {spawn_depth:.1f}")

            except Exception as e:
                logger.error(f"Error spawning 3D enemy: {e}")
```

### Phase 3: Performance Optimization (2-3 days)

#### 3.1 Image Scaling Cache System

**New File**: `thunder_fighter/graphics/image_cache.py`

```python
class ScalingCache:
    """LRU cache for scaled images to optimize performance"""

    def __init__(self, max_size: int = 200):
        self.cache = {}
        self.access_order = []
        self.max_size = max_size

    def get_scaled_image(self, original: pygame.Surface, scale: float) -> pygame.Surface:
        """Get cached scaled image or create new one"""
        # Quantize scale to reduce cache size
        quantized_scale = round(scale, 2)
        cache_key = (id(original), quantized_scale)

        if cache_key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(cache_key)
            self.access_order.append(cache_key)
            return self.cache[cache_key]

        # Create new scaled image
        if quantized_scale <= 0.1:
            return None  # Too small to render

        new_size = (
            max(1, int(original.get_width() * quantized_scale)),
            max(1, int(original.get_height() * quantized_scale))
        )

        scaled = pygame.transform.scale(original, new_size)

        # Add to cache with LRU management
        if len(self.cache) >= self.max_size:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]

        self.cache[cache_key] = scaled
        self.access_order.append(cache_key)

        return scaled
```

#### 3.2 Level of Detail (LOD) System

```python
class LODManager:
    """Manages level of detail based on depth and screen size"""

    @staticmethod
    def should_render(entity) -> bool:
        """Determine if entity should be rendered"""
        scale = entity.get_depth_scale()
        visual_size = entity.get_visual_size()

        # Skip very distant or very small entities
        return scale >= 0.05 and visual_size[0] >= 2 and visual_size[1] >= 2

    @staticmethod
    def get_update_frequency(entity) -> float:
        """Get update frequency multiplier based on depth"""
        scale = entity.get_depth_scale()
        if scale >= 0.8:
            return 1.0  # Full frequency for near objects
        elif scale >= 0.4:
            return 0.5  # Half frequency for medium distance
        else:
            return 0.25  # Quarter frequency for distant objects
```

### Phase 4: Visual Enhancements (2-3 days)

#### 4.1 Background Depth Layers

**Modify**: `thunder_fighter/graphics/background.py`

```python
class DynamicBackground:
    """Enhanced background with depth-aware star layers"""

    def __init__(self):
        self.star_layers = [
            {"stars": [], "depth": 900, "speed_multiplier": 0.3},  # Far stars
            {"stars": [], "depth": 700, "speed_multiplier": 0.6},  # Medium stars
            {"stars": [], "depth": 500, "speed_multiplier": 1.0},  # Near stars
        ]
        self._initialize_depth_layers()

    def _initialize_depth_layers(self):
        """Initialize stars at different depth layers"""
        for layer in self.star_layers:
            depth = layer["depth"]
            star_count = int(50 * (1000 - depth) / 500)  # More stars for nearer layers

            for _ in range(star_count):
                star = Star(depth=depth)
                layer["stars"].append(star)

    def update_with_depth(self, dt: float):
        """Update background with depth-aware movement"""
        for layer in self.star_layers:
            speed_mult = layer["speed_multiplier"]
            for star in layer["stars"]:
                star.update(dt * speed_mult)

    def render_with_depth(self, screen: pygame.Surface):
        """Render background layers back-to-front"""
        # Render from farthest to nearest
        sorted_layers = sorted(self.star_layers, key=lambda l: l["depth"], reverse=True)

        for layer in sorted_layers:
            depth = layer["depth"]
            alpha = int(255 * (1.0 - depth / 1000.0))  # Fade distant layers

            # Create temporary surface for alpha blending
            layer_surface = pygame.Surface((WIDTH, HEIGHT))
            layer_surface.set_alpha(alpha)

            for star in layer["stars"]:
                star.render_with_depth(layer_surface, depth)

            screen.blit(layer_surface, (0, 0))
```

#### 4.2 Particle Effects with Depth

**Modify**: `thunder_fighter/graphics/effects/explosion.py`

```python
class Explosion(Entity3D):
    """3D-aware explosion effect"""

    def __init__(self, position, size="md", depth=0):
        super().__init__(position[0], position[1], 64, 64, z=depth)
        self.size = size
        self.frame = 0
        self.animation_speed = 15
        self.lifetime = 1.0

        # Load explosion images
        self.images = self._load_explosion_images()
        self.image = self.images[0] if self.images else None

    def update(self, dt: float):
        """Update explosion animation with depth scaling"""
        self.lifetime -= dt

        if self.lifetime <= 0:
            self.kill()
            return

        # Animate frames
        self.frame += self.animation_speed * dt
        frame_index = int(self.frame) % len(self.images)
        self.image = self.images[frame_index]

        # Apply depth scaling to animation
        scale = self.get_depth_scale()
        if scale < 1.0:
            size = (int(self.image.get_width() * scale),
                   int(self.image.get_height() * scale))
            self.image = pygame.transform.scale(self.image, size)
```

### Phase 5: Game Balance Adjustments (1-2 days)

#### 5.1 Difficulty Scaling

```python
class DepthAwareDifficulty:
    """Manages difficulty scaling for 3D gameplay"""

    @staticmethod
    def calculate_hit_probability(player_depth: float, target_depth: float) -> float:
        """Calculate hit probability based on depth difference"""
        depth_diff = abs(player_depth - target_depth)
        base_probability = 1.0

        # Reduce hit probability for distant targets
        if depth_diff > 100:
            distance_penalty = min(0.3, depth_diff / 1000)
            base_probability -= distance_penalty

        return max(0.4, base_probability)  # Minimum 40% hit chance

    @staticmethod
    def calculate_depth_score_bonus(depth: float) -> int:
        """Calculate score bonus for hitting distant targets"""
        if depth > 600:
            return int((depth - 600) / 50)  # +1 point per 50 depth units
        return 0
```

## Technical Requirements

### Performance Targets
- **Frame Rate**: Maintain 60 FPS with 20+ entities on screen
- **Memory Usage**: <50MB additional memory for caching
- **Startup Time**: <1 second additional initialization

### Hardware Requirements
- **CPU**: No additional requirements beyond current game
- **Memory**: +32MB for image caching
- **Graphics**: Pygame software rendering (no hardware acceleration needed)

## Implementation Timeline

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| **Phase 1** | 2-3 days | Core 3D entity classes, depth rendering system |
| **Phase 2** | 3-4 days | Enemy/collision integration, spawning updates |
| **Phase 3** | 2-3 days | Performance optimization, caching systems |
| **Phase 4** | 2-3 days | Visual enhancements, background depth |
| **Phase 5** | 1-2 days | Game balance, difficulty tuning |

**Total Duration**: 10-15 days

## Risk Mitigation

### Performance Risks
- **Mitigation**: Aggressive caching, LOD system, configurable quality settings
- **Fallback**: Dynamic quality reduction for low-end hardware

### Gameplay Balance Risks
- **Mitigation**: Gradual difficulty introduction, configurable depth effects
- **Fallback**: Toggle between 2D and 3D modes in settings

### Code Integration Risks
- **Mitigation**: Backward compatibility maintained, gradual entity migration
- **Fallback**: Per-entity 3D enable/disable flags

## Testing Strategy

### Unit Tests
- Depth calculation accuracy
- Image scaling cache performance
- Collision detection correctness

### Integration Tests
- Enemy spawning with depth
- Player interaction with 3D entities
- Performance under load

### User Experience Tests
- Visual depth perception
- Gameplay difficulty curve
- Frame rate stability

## Configuration Options

### Player Settings
```python
PSEUDO_3D_CONFIG = {
    "enabled": True,
    "depth_intensity": 1.0,      # 0.5-2.0 range
    "fog_enabled": True,
    "perspective_strength": 1.0,  # 0.5-2.0 range
    "performance_mode": "auto",   # "high", "medium", "low", "auto"
}
```

### Developer Settings
```python
DEBUG_3D_CONFIG = {
    "show_depth_values": False,
    "render_depth_zones": False,
    "collision_depth_visualization": False,
    "performance_overlay": False,
}
```

## Conclusion

This pseudo-3D implementation design provides a comprehensive roadmap for transforming Thunder Fighter into a visually stunning 3D experience while preserving the core gameplay mechanics. The phased approach ensures controlled risk and allows for incremental testing and refinement.

The design leverages the existing architecture strengths while introducing minimal breaking changes, ensuring a smooth transition that maintains code quality and performance standards.