# Thunder Fighter Architecture Guide

## Overview

Thunder Fighter uses a modern, modular architecture designed for maintainability, testability, and extensibility. The system is built around event-driven communication, systems-based design, and clear separation of concerns.

## Core Design Principles

### Event-Driven Architecture
Game components communicate through `EventSystem` rather than direct coupling. All game events are defined in `events/game_events.py`.

### Systems-Based Architecture
Core game logic is organized into dedicated systems in `systems/`:
- `CollisionSystem` - Unified collision detection and resolution for all entity interactions
- `ScoringSystem` - Centralized score management with level progression and achievement tracking
- `SpawningSystem` - Entity spawning coordination integrating all factory classes
- `PhysicsSystem` - Movement, boundaries, and collision detection for game physics

### Factory Pattern
Type-organized entity creation in `entities/`:
- `entities/enemies/` - `EnemyFactory` and `BossFactory` with difficulty scaling
- `entities/projectiles/` - `ProjectileFactory` for bullets and missiles
- `entities/items/` - `ItemFactory` for power-ups and collectibles
- `entities/player/` - Player and wingman entity management

### Single Responsibility
Each system has clear boundaries and focused responsibilities.

## System Architecture

### Input System Architecture

**Unified Input System**: Clean input architecture in `systems/input/`:
- `InputHandler` - Raw event processing with macOS screenshot interference handling
- `InputManager` - Event coordination and state management
- `InputFacade` - High-level input interface for game logic

The layered architecture provides:
- **Raw Event Processing**: Platform-specific event handling with fallback mechanisms
- **State Management**: Input state coordination and validation
- **Game Interface**: High-level input interface for game logic

### State Management System

**State Pattern**: Game states managed through `StateMachine` in `state/`:

#### Core Components
1. **GameState** - Data structure holding all game state information
2. **GameStateManager** - Centralized manager for state data and transitions
3. **StateMachine** - Generic state machine framework
4. **State** - Abstract base class for individual game states
5. **Concrete States** - Specific implementations for each game mode
6. **StateFactory** - Factory for creating state instances

#### State Types
- **MenuState** - Main menu (ready for future implementation)
- **PlayingState** - Active gameplay with enemy/boss/item spawning
- **PausedState** - Game paused with adjusted music volume
- **GameOverState** - Game over screen with restart/exit handling
- **VictoryState** - Victory screen with completion statistics
- **LevelTransitionState** - Level transition animations with 3-second timer

#### Key Features
- **Centralized State Management**: All game state in one place
- **Type-Safe State Transitions**: Clear, validated transitions
- **Event-Driven Architecture**: State change listeners and callbacks
- **Separation of Concerns**: Each state handles its own logic

### Background System Architecture

**Double-Buffered Dynamic Backgrounds**: Revolutionary visual enhancement system

#### Technical Implementation
- **Double Buffering Technology**: Pre-rendering with alpha blending
- **Ultra-Smooth Transitions**: Cubic bezier curve easing with 3-second duration
- **Level-Based Themes**: Unique visual themes reflecting difficulty progression
- **Enhanced Special Effects**: Space storms and asteroid fields with alpha support

#### Visual Themes
- **Level 1 - Deep Space**: Blue/black color scheme, peaceful atmosphere
- **Level 2 - Nebula Field**: Purple/blue colors with increased nebula density
- **Level 3 - Asteroid Belt**: Brown/orange tones with animated asteroid field
- **Level 4 - Red Zone**: Red/orange colors with space storm particles
- **Level 5 - Final Battle**: Dark red/black with intense storm effects

#### Performance Optimizations
- **Buffer Reuse**: Surfaces only recreated on screen size change
- **Hardware Acceleration**: Uses `pygame.BLEND_ALPHA_SDL2`
- **Efficient Alpha Handling**: Minimal state changes

## Component Systems

### UI System Architecture

**Modular Component-Based UI** in `graphics/ui/`:
- `HealthBarComponent` - Dynamic health displays with color-coded states
- `NotificationManager` - Game notifications and achievements system
- `GameInfoDisplay` - Score, level, and elapsed time display
- `PlayerStatsDisplay` - Player statistics and upgrades information (with reset method)
- `BossStatusDisplay` - Boss health and combat modes (with reset method)
- `ScreenOverlayManager` - Pause, victory, and game over screens
- `DevInfoDisplay` - Developer debug information (FPS, positions, etc.)

### Configuration System

**JSON-Based Configuration**: Stored at `~/.thunder_fighter/config.json`
- Runtime configuration updates through `config_tool.py`
- All gameplay parameters configurable through `constants.py`
- Environment variable support (`THUNDER_FIGHTER_LOG_LEVEL`)

### Resource Management

**Centralized Asset Loading**: `ResourceManager` provides:
- Asset caching and optimization
- Font management with platform-specific optimizations
- Sound and music management with health monitoring
- Image loading with format support (PNG, JPG, etc.)

### Pause Management

**Dedicated PauseManager Component**: Extracted pause logic in `utils/pause_manager.py`
- Pause-aware timing calculations and cooldown mechanisms
- Comprehensive statistics tracking
- Dependency injection support for enhanced testability

## Entity Architecture

### Base Entity System

**Hierarchical Entity Structure** in `entities/base.py`:
- `GameObject` - Base class for all game objects
- `Entity` - Enhanced game entity with lifecycle management
- `EntityFactory` - Base factory class for entity creation

### Type-Organized Entity System

**Factory Pattern Implementation**:
- **enemies/** - Enemy entities and factories with difficulty scaling
- **projectiles/** - Bullets and missiles with tracking capabilities
- **items/** - Power-ups and collectibles with configurable effects
- **player/** - Player and wingman entities with formation management

## Graphics and Effects

### Visual Effects System

**Modular Effects Architecture** in `graphics/effects/`:
- `notifications.py` - Complete notification system with position attributes
- `explosions.py` - Explosion and hit effect functions
- `flash_effects.py` - Flash effect management system

### Rendering System

**Optimized Rendering Pipeline**:
- Sprite groups for batch operations
- Object pooling for frequently created entities
- Performance profiling for critical sections

## Testing Architecture

### Comprehensive Test Coverage

**375 Tests** organized by category:
- **Unit Tests (90+)**: Entity factories, components, pause system, localization
- **Integration Tests (9)**: Event system flow, component interactions
- **End-to-End Tests (9)**: Complete game flow scenarios
- **Systems Tests**: Core systems architecture validation
- **Events Tests**: Event-driven architecture testing
- **Localization Tests**: Multi-language support testing

### Testing Principles
- **Interface-Focused Testing**: Tests focus on behavior and public interfaces
- **Dependency Injection**: Enhanced interfaces for easier testing
- **Mock External Dependencies**: Pygame surfaces, sounds mocked appropriately
- **Comprehensive Coverage**: 90%+ coverage for critical systems

## Performance Considerations

### Optimization Strategies
- **Sprite Groups**: Batch operations for entity management
- **Object Pooling**: Reuse frequently created entities
- **Resource Caching**: Asset loading optimization
- **Event-Driven Updates**: Only processes relevant changes

### Memory Management
- **Lazy Initialization**: Resources loaded when needed
- **Buffer Reuse**: Efficient surface management
- **Cleanup Protocols**: Proper resource disposal

## Future Architecture Enhancements

### Planned Improvements
1. **State Persistence**: Save/load game states
2. **Nested States**: Sub-states within main states
3. **Dynamic Lighting**: Background interaction with gameplay events
4. **Enhanced Particle Systems**: Advanced environmental effects
5. **Component Entity System**: Full ECS architecture migration

### Extension Points
- Custom state validation rules
- State-specific configuration
- Dynamic entity creation
- Analytics and monitoring integration

## Conclusion

Thunder Fighter's architecture successfully balances performance, maintainability, and extensibility. The systems-based design with event-driven communication provides a solid foundation for current gameplay while enabling future enhancements and features.