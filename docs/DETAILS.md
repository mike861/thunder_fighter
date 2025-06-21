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
- **Boss Levels**: Bosses range from level 1-3, becoming more powerful at higher levels.
- **Boss Spawning**: A Boss spawns periodically.
- **Boss Attack**: Fires multiple bullets; the number and pattern change with level.

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
- ✅ Good test coverage (39 tests passing)
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
- Modular architecture allows for easy extension and maintenance.
- Test-driven development ensures code quality and reliability.
- Localization system for multi-language support. 