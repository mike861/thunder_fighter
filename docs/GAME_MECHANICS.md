# Game Mechanics Guide

This document contains detailed information about Thunder Fighter's game mechanics, systems, and gameplay features.

## Related Documentation

- [Localization Guide](LOCALIZATION.md) - Comprehensive guide to the multi-language support and Chinese font optimization system
- [Architecture Guide](ARCHITECTURE.md) - Complete system architecture and technical design documentation
- [Development Roadmap](DEVELOPMENT_ROADMAP.md) - Planned improvements and implementation tasks
- [Development History](DEVELOPMENT_HISTORY.md) - Project evolution and major improvements timeline

## Internal Game Mechanics

### Game Victory System
- **Victory Condition**: Players achieve victory by defeating the final boss at the maximum game level (configurable via `MAX_GAME_LEVEL` constant)
- **Final Boss Battle**: The last boss provides enhanced challenge with double score bonus (boss level × 1000 points vs normal 500 points)
- **Victory Processing**: 
  - Automatic victory detection when final boss is defeated
  - Immediate game state transition to victory mode
  - Background music fadeout with victory sound effects
  - Prevention of further enemy/item spawning
- **Victory Statistics**: Comprehensive completion data including:
  - Final score with boss defeat bonus
  - Total survival time in minutes
  - Levels completed
  - Achievement notifications
- **Victory Interface**: 
  - Preserves game background for visual continuity
  - Semi-transparent overlay with elegant victory panel
  - Centered statistics display with green victory theme
  - Blinking exit prompt for user interaction
- **Duplicate Prevention**: Robust system prevents multiple victory processing and notification spam

### Player System
- **Wingmen**: The player can have a configurable number of wingmen (default max is 2), collected via the `WingmanItem` starting at game level 3. Wingmen absorb one hit for the player, sacrificing themselves. The initial number, maximum count, and formation spacing are all configurable in `constants.py`.
- **Missiles**: Wingmen fire tracking missiles periodically. These missiles seek out the nearest enemies, prioritizing the Boss if one is active.

### Enemy System
- **🛸 Enemy Visual Design**: Complete organic/alien biomechanical appearance system
  - **Size**: 45×45 pixels (distinct from player's 60×50)
  - **Shape**: Irregular organic hull with alien appendages instead of geometric wings
  - **Alien Features**: Bio-sensors ("eyes") replace cockpits, organic exhaust ports replace engines
  - **Front-Facing Orientation**: All enemies properly oriented with bio-thrusters pointing toward player
- **Enemy Themes by Level**: Progressive alien evolution across difficulty tiers
  - **Levels 1-3 (Insectoid)**: Dark crimson/red creatures with aggressive organic appearance
  - **Levels 4-6 (Toxic Alien)**: Toxic green entities with bio-luminescent glow effects
  - **Levels 7-9 (Energy Being)**: Purple void creatures with energy manifestations
  - **Levels 10+ (Nightmare Void)**: Dark energy beings with bright accent colors and maximum bio-luminescence
- **Enemy Levels**: Enemies range from level 0-10. Higher levels mean more health, speed, and attack power.
- **Enemy Spawning**: The number and level of enemies increase as the game progresses and the game level increases.
- **Enemy Shooting**: Enemies level 2 and above can shoot (configurable via the `ENEMY_SHOOT_LEVEL` constant). Firing rate and bullet speed increase with level.
  - Low-level enemies: Fire simple bullets that fall straight down.
  - Mid-level enemies: Fire faster bullets, possibly with more complex patterns.
  - High-level enemies: Fire faster and more damaging bullets.

### Bullet System
- **Player Bullets**: Up to 4 shooting paths based on collected items.
- **Enemy Bullets**: Different appearance, speed, and damage based on enemy level.
- **Boss Bullets**: Special large bullets with higher damage.

### Item System
- **Health Item**: Restores player health (10 points).
- **Bullet Speed Item**: Increases player bullet speed (up to maximum of 20).
- **Bullet Path Item**: Increases the number of player shooting paths (up to maximum of 4).
- **Player Speed Item**: Increases the player's movement speed (up to maximum of 15).
- **Wingman Item**: Adds a wingman to fight alongside the player (maximum 2 wingmen, available from level 3+).

#### Intelligent Item Distribution System
The game features an adaptive item distribution system that replaces simple random generation with context-aware algorithms:

**Base Item Probabilities**:
- Health Item: 20% (survival priority)
- Bullet Speed Item: 18% (attack enhancement)
- Bullet Path Item: 15% (firepower increase)
- Player Speed Item: 12% (mobility boost)
- Wingman Item: 10% (advanced support)

**Smart Weight Adjustments**:

*Health-Based Adaptation*:
- **Critical State** (≤30% health): Health item probability ×2.5
- **Injured State** (30-70% health): Health item probability ×1.5
- **Healthy State** (>70% health): Health item probability ×0.5

*Level-Based Item Gating*:
- **Levels 1-2**: Wingman items unavailable (0% probability)
- **Level 3+**: Full wingman availability

*Ability Cap Detection*:
- Items automatically disabled when player reaches maximum values
- Prevents useless item drops when abilities are fully upgraded

*Duplicate Prevention System*:
- Same item type within 15 seconds receives 80% probability reduction
- Maximum 2 consecutive identical items before automatic suppression
- Prevents item flooding while maintaining variety

**Intelligent Benefits**:
- **Contextual Relevance**: Items appear when most needed (health during combat, upgrades during progression)
- **Strategic Depth**: Players can anticipate item patterns based on their current state
- **Balance Maintenance**: Prevents both item drought and oversaturation scenarios
- **Difficulty Adaptation**: System responds to player performance and game progression

For advanced implementation details, see [Advanced Item System Strategy](../ADVANCED_ITEM_SYSTEM.md).

### Boss System
- **Boss Levels**: Bosses are dynamically generated based on game progression. Their level is calculated as `max(1, (game_level + 1) // 2)`. This means boss levels increase as the player advances through the game's 10 levels.
- **Boss Spawning**: A Boss spawns every 30 seconds starting from game level 2. No bosses appear during early levels (0-1).
- **Boss Health System**: 
  - Base health: `100 + (level-1) * 50` points
  - Health bar displayed above boss with level indicator
  - Visual health bar changes color based on attack mode
- **Boss Attack Modes**: Bosses have three distinct attack patterns that change based on health percentage:
  - **Normal Mode** (100%-50% health): Standard bullet patterns
    - Level 1: 3 bullets in straight line formation
    - Level 2: 4 bullets in fan pattern  
    - Level 3+: 5 bullets in wider fan pattern
  - **Aggressive Mode** (50%-25% health, Level 2+ only): Increased bullet count and faster firing
    - Shoot delay reduced by 30%
    - More bullets with wider spread patterns
    - Health bar shows yellow border warning
  - **Final Mode** (25%-0% health, Level 3+ only): Maximum intensity with player tracking
    - Shoot delay reduced by additional 20%
    - Maximum bullet count (up to 7 bullets for Level 3+)
    - Some bullets track player position
    - Health bar shows flashing red border
- **Boss Movement**: 
  - Entrance animation: Slides down from top of screen
  - Horizontal movement: Left-right pattern with dynamic boundaries
  - Movement speed increases with game level
  - Movement range adapts to game progression
- **Boss Bullets**: Special bullet system with mode-based characteristics:
  - **Normal bullets**: Magenta color, standard speed (5 pixels/frame), 10 damage
  - **Aggressive bullets**: Orange-red color, faster speed (6 pixels/frame), 15 damage, 20% larger
  - **Final bullets**: Cyan color, fastest speed (7 pixels/frame), 20 damage, 30% larger, player tracking
- **Visual Effects**: 
  - Multi-layer damage flash effects (white, red, yellow)
  - Attack mode indicators on health bar
  - Glowing bullet effects with multiple layers
- **Boss Defeat Rewards**: Defeating a boss provides score bonuses (boss level × 500 points for regular bosses, boss level × 1000 points for final boss) and triggers immediate level progression or game victory.

### Level Progression System
- **Early Game (Levels 0-1)**: Players advance through score accumulation. This provides a friendly learning phase where players can familiarize themselves with game mechanics without boss pressure.
- **Mid-to-Late Game (Level 2+)**: Level progression is exclusively through boss defeats. Score accumulation no longer triggers level advancement, creating a skill-based progression system.
- **Final Level Victory**: Reaching and defeating the boss at `MAX_GAME_LEVEL` triggers game completion instead of further progression.
- **Dual Progression Mechanics**: 
  - Score-based progression: Available only for levels 0→1 and 1→2
  - Boss-defeat progression: Available from level 2 onwards, providing greater rewards and challenge
  - Victory completion: Final boss defeat at maximum level triggers game completion
- **Clear Progression Path**: Players receive clear visual notifications when advancing levels, including enemies cleared count and bonus scores received.

### Visual Effects System
- **🎨 Dynamic Level Background System**: Revolutionary double-buffered rendering for seamless level transitions
  - **Level Themes**: Each level features unique visual identity reflecting difficulty progression:
    - Level 1 "Deep Space": Peaceful blue/black starfield (2 nebulae, 1 planet)
    - Level 2 "Nebula Field": Purple/blue clouds (4 nebulae, 2 planets)
    - Level 3 "Asteroid Belt": Brown/orange asteroid field with animated debris (3 nebulae, 3 planets)
    - Level 4 "Red Zone": Dangerous red space with particle storm effects (5 nebulae, 2 planets)
    - Level 5+ "Final Battle": Ominous dark red atmosphere with intense storms (6 nebulae, 1 planet)
  - **Double Buffering Technology**: Pre-renders level backgrounds into separate buffers for artifact-free transitions
  - **Smooth Transitions**: 3-second transitions using cubic bezier easing (t³(6t² - 15t + 10)) with alpha blending
  - **Special Effects**:
    - SpaceStorm: Animated red particles with sinusoidal movement for dangerous levels
    - AsteroidField: Procedurally generated rotating asteroids for level 3
    - Alpha Support: All effects support smooth fade-in/fade-out during transitions
  - **Hardware Optimization**: Uses pygame.BLEND_ALPHA_SDL2 for maximum performance
  - **Visual Polish**: Enhanced level indicator with glow effects and subtle overlays
- **Explosions**: Occur when an entity (enemy, wingman) is destroyed, or when a missile hits a target.
- **Flash Effects**: Used for non-lethal damage. The entity itself flashes a specific color to indicate it was hit. This provides clearer feedback without cluttering the screen.
    - Player Hit: Flashes white.
    - Boss Hit (by Bullet): Flashes yellow.
    - Boss Hit (by Missile): Flashes red (in addition to the missile's explosion).
- **Victory Effects**: Special visual treatment for game completion:
    - Background preservation for visual continuity
    - Semi-transparent overlay system
    - Elegant victory panel with border effects
    - Smooth transition from gameplay to victory state

### Sound System
- **Background Music**: Loops during gameplay with automatic fadeout during victory.
- **Explosion Sound**: Plays when enemies are destroyed.
- **Hit Sound**: Plays when the player takes damage.
- **Death Sound**: Plays when the player's ship is destroyed.
- **Item Pickup Sound**: Plays when an item is collected.
- **Boss Defeat Sound**: Plays when a Boss is successfully defeated.
- **Victory Sound**: Special audio feedback for game completion.
- **Volume Control**: Sound effect and music volume can be adjusted independently.
- **System Stability**: The sound system includes a robust health check and auto-recovery mechanism. It periodically checks its status and automatically reinitializes if issues are detected (e.g., if background music stops unexpectedly). This ensures high reliability during long gameplay sessions.
- **Audio Independence**: Fixed issue where toggling sound effects would incorrectly stop background music. Music and sound effects now operate independently as intended.

### Logging System
- Standardized log output supporting different levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).
- Log level can be adjusted via the `THUNDER_FIGHTER_LOG_LEVEL` environment variable (See [How to Run](#how-to-run) in `README.md`).
- All game events are logged in English for easy debugging and monitoring.
- **Victory Logging**: Comprehensive logging of victory conditions, final boss defeats, and completion statistics.

## Sound Assets

The game uses the following sound and music files located in the `assets/` directory:

1. **Sounds (`sounds/`)**:
   - `player_hit.wav` - Player hit sound
   - `player_death.wav` - Player death sound
   - `enemy_explosion.wav` - Enemy explosion sound
   - `boss_death.wav` - Boss death sound (also used for victory)
   - `item_pickup.wav` - Item pickup sound

2. **Music (`music/`)**:
   - `background_music.mp3` - Game background music

If these files are missing, the game will handle the missing sounds gracefully, logging a warning but not affecting gameplay.

## Implementation Status

### ✅ Completed Features
- **Core Gameplay**: Player movement, shooting, collision detection
- **Victory System**: Final boss battles and game completion
- **Enemy System**: Multi-level enemies with progressive difficulty
- **Boss Battles**: Three attack modes with health-based transitions
- **Item System**: Five types of power-ups with configurable effects
- **Sound System**: Background music, sound effects, and volume control
- **Visual Effects**: Explosions, damage flashes, and dynamic backgrounds
- **Multi-language Support**: English and Chinese with dynamic switching
- **Wingman System**: Companion fighters with tracking missiles
- **Level Progression**: Score-based and boss-defeat progression mechanics

### 🔧 System Reliability
- **Pause System**: Pause-aware timing calculations
- **Input Handling**: Cross-platform input with fallback mechanisms  
- **Font Rendering**: Optimized Chinese font support on macOS
- **Test Coverage**: 375+ comprehensive tests across all systems

## Related Documentation

- **[Architecture Guide](ARCHITECTURE.md)** - System architecture and design patterns
- **[Technical Details](TECHNICAL_DETAILS.md)** - Technical implementations and optimizations
- **[Development Roadmap](DEVELOPMENT_ROADMAP.md)** - Development roadmap and planned features
- **[Localization Guide](LOCALIZATION.md)** - Multi-language support guide
- **[Development History](DEVELOPMENT_HISTORY.md)** - Project evolution timeline

---

*For technical implementation details, platform-specific optimizations, and architectural improvements, see [Technical Details](TECHNICAL_DETAILS.md).* 