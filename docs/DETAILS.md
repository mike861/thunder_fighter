# Project Details

This document contains more detailed information about the Thunder Fighter game mechanics and technical aspects.

## Internal Game Mechanics

### Player System
- **Wingmen**: The player can have a configurable number of wingmen (default max is 2), collected via the `WingmanItem`. Wingmen absorb one hit for the player, sacrificing themselves. The initial number, maximum count, and formation spacing are all configurable in `constants.py`.
- **Missiles**: Wingmen fire tracking missiles periodically. These missiles seek out the nearest enemies, prioritizing the Boss if one is active.

### Enemy System
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
- **Health Item**: Restores player health.
- **Bullet Speed Item**: Increases player bullet speed.
- **Bullet Path Item**: Increases the number of player shooting paths.
- **Player Speed Item**: Increases the player's movement speed.
- **Wingman Item**: Adds a wingman to fight alongside the player.
- **Item Generation**: Items are randomly generated as the game progresses and points are earned by defeating enemies.

### Boss System
- **Boss Levels**: Bosses range from level 1-10, with level determined by game progression (game_level // 3 + random(1,2)).
- **Boss Spawning**: A Boss spawns every 30 seconds starting from game level 2. No bosses appear during early levels (0-1).
- **Boss Health System**: 
  - Base health: 100 + (level-1) × 50 points
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
  - **Normal bullets**: Magenta color, standard speed (5 pixels/frame), 15 damage
  - **Aggressive bullets**: Orange-red color, faster speed (7 pixels/frame), 20 damage, 20% larger
  - **Final bullets**: Cyan color, fastest speed (9 pixels/frame), 25 damage, 50% larger, player tracking
- **Visual Effects**: 
  - Multi-layer damage flash effects (white, red, yellow)
  - Attack mode indicators on health bar
  - Glowing bullet effects with multiple layers
- **Boss Defeat Rewards**: Defeating a boss provides score bonuses (boss level × 500 points) and triggers immediate level progression.

### Level Progression System
- **Early Game (Levels 0-1)**: Players advance through score accumulation. This provides a friendly learning phase where players can familiarize themselves with game mechanics without boss pressure.
- **Mid-to-Late Game (Level 2+)**: Level progression is exclusively through boss defeats. Score accumulation no longer triggers level advancement, creating a skill-based progression system.
- **Dual Progression Mechanics**: 
  - Score-based progression: Available only for levels 0→1 and 1→2
  - Boss-defeat progression: Available from level 2 onwards, providing greater rewards and challenge
- **Clear Progression Path**: Players receive clear visual notifications when advancing levels, including enemies cleared count and bonus scores received.

### Visual Effects System
- **Explosions**: Occur when an entity (enemy, wingman) is destroyed, or when a missile hits a target.
- **Flash Effects**: Used for non-lethal damage. The entity itself flashes a specific color to indicate it was hit. This provides clearer feedback without cluttering the screen.
    - Player Hit: Flashes white.
    - Boss Hit (by Bullet): Flashes yellow.
    - Boss Hit (by Missile): Flashes red (in addition to the missile's explosion).

### Sound System
- **Background Music**: Loops during gameplay.
- **Explosion Sound**: Plays when enemies are destroyed.
- **Hit Sound**: Plays when the player takes damage.
- **Death Sound**: Plays when the player's ship is destroyed.
- **Item Pickup Sound**: Plays when an item is collected.
- **Boss Defeat Sound**: Plays when a Boss is successfully defeated.
- **Volume Control**: Sound effect and music volume can be adjusted.
- **System Stability**: The sound system includes a robust health check and auto-recovery mechanism. It periodically checks its status and automatically reinitializes if issues are detected (e.g., if background music stops unexpectedly). This ensures high reliability during long gameplay sessions.

### Logging System
- Standardized log output supporting different levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).
- Log level can be adjusted via the `THUNDER_FIGHTER_LOG_LEVEL` environment variable (See [How to Run](#how-to-run) in `README.md`).
- All game events are logged in English for easy debugging and monitoring.

## Sound Assets

The game uses the following sound and music files located in the `assets/` directory:

1. **Sounds (`sounds/`)**:
   - `player_hit.wav` - Player hit sound
   - `player_death.wav` - Player death sound
   - `enemy_explosion.wav` - Enemy explosion sound
   - `boss_death.wav` - Boss death sound
   - `item_pickup.wav` - Item pickup sound

2. **Music (`music/`)**:
   - `background_music.mp3` - Game background music

If these files are missing, the game will handle the missing sounds gracefully, logging a warning but not affecting gameplay.

## Development Status

- ✅ Core gameplay mechanics implemented
- ✅ Enemy system with varied behaviors
- ✅ Boss battles with unique patterns
- ✅ Item drop and collection system
- ✅ Sound system with enhanced stability and volume control
- ✅ Comprehensive test coverage (78 tests passing)
- ✅ Refined visual feedback system (explosions vs. damage flashes)
- ✅ Multi-language support (English, Chinese)
- ✅ Dynamic UI with notifications
- ✅ Configurable game parameters (wingmen, enemy counts, etc.)

## Technical Details

- Object-Oriented Programming used for game entity design.
- Pygame Sprite Groups manage game objects and collision detection.
- Custom rendering system creates game visual effects.
- Centralized `FlashEffectManager` for handling entity damage flashes.
- Standardized logging system tracks game events.
- Sound manager controls game audio playback, featuring a robust health-check and auto-recovery system.
- **Advanced Boss System Architecture**:
  - State-based attack pattern management with health-triggered transitions
  - Dynamic bullet generation with mode-specific properties and targeting
  - Multi-layer visual effects system with pre-computed flash sequences
  - Adaptive movement boundaries based on game progression
  - Comprehensive collision detection with mask-based precision
  - Real-time health bar rendering with mode indicators
- **Boss Bullet System**: 
  - Factory pattern for mode-specific bullet creation
  - Dynamic size and color adjustment based on attack mode
  - Player tracking algorithms for final mode bullets
  - Multi-layer glow effects for enhanced visual appeal
- Modular architecture allows for easy extension and maintenance.
- Test-driven development ensures code quality and reliability.
- Localization system for multi-language support. 