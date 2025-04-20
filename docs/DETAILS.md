# Project Details

This document contains more detailed information about the Thunder Fighter game mechanics and technical aspects.

## Internal Game Mechanics

### Enemy System
- **Enemy Levels**: Enemies range from level 0-10. Higher levels mean more health, speed, and attack power.
- **Enemy Spawning**: The number and level of enemies increase as game time progresses.
- **Enemy Shooting**: Enemies level 1 and above can shoot. Firing rate and bullet speed increase with level.
  - Low-level enemies (1-4): Fire simple red bullets that fall straight down.
  - Mid-level enemies (5-7): Fire orange bullets, possibly with horizontal movement.
  - High-level enemies (8-10): Fire blue or purple bullets, possibly with curved trajectories.

### Bullet System
- **Player Bullets**: Up to 4 shooting paths based on collected items.
- **Enemy Bullets**: Different appearance, speed, and damage based on enemy level.
- **Boss Bullets**: Special large bullets with higher damage.

### Item System
- **Health Item**: Restores player health.
- **Bullet Speed Item**: Increases player bullet speed.
- **Bullet Path Item**: Increases the number of player shooting paths.
- **Player Speed Item**: Increases the player's movement speed.
- **Item Generation**: Items are randomly generated as the game progresses and points are earned by defeating enemies.

### Boss System
- **Boss Levels**: Bosses range from level 1-3, becoming more powerful at higher levels.
- **Boss Spawning**: A Boss spawns periodically.
- **Boss Attack**: Fires multiple bullets; the number and pattern change with level.

### Sound System
- **Background Music**: Loops during gameplay.
- **Shooting Sound**: Plays when the player fires.
- **Explosion Sound**: Plays when enemies and Bosses are destroyed.
- **Hit Sound**: Plays when the player takes damage.
- **Death Sound**: Plays when the player's ship is destroyed.
- **Item Pickup Sound**: Plays when an item is collected.
- **Boss Defeat Sound**: Plays when a Boss is successfully defeated.
- **Volume Control**: Sound effect and music volume can be adjusted.

### Logging System
- Standardized log output supporting different levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).
- Log level can be adjusted via the `THUNDER_FIGHTER_LOG_LEVEL` environment variable (See [How to Run](#how-to-run) in README.md).
- All game events are logged in English for easy debugging and monitoring.

## Sound Assets

The game uses the following sound and music files located in the `thunder_fighter/assets/` directory:

1. **Sounds (`sounds/`)**: WAV or MP3 format
   - `player_shoot.wav` - Player shooting sound
   - `player_hit.wav` - Player hit sound
   - `player_death.wav` - Player death sound
   - `enemy_explosion.wav` - Enemy explosion sound
   - `boss_death.wav` - Boss death sound
   - `item_pickup.wav` - Item pickup sound (Used for all item types currently)

2. **Music (`music/`)**: MP3 format
   - `background_music.mp3` - Game background music

If these files are missing, the game will handle the missing sounds gracefully, logging a warning but not affecting gameplay.

## Development Status

- ✅ Core gameplay mechanics implemented
- ✅ Enemy system with varied behaviors
- ✅ Boss battles with unique patterns
- ✅ Item drop and collection system
- ✅ Sound system with volume control
- ✅ Complete test coverage (43 tests passing)
- ✅ Game polish and optimization
- ✅ Multi-language support (English, Chinese)
- ✅ Dynamic UI with notifications

## Technical Details

- Object-Oriented Programming used for game entity design.
- Pygame Sprite Groups manage game objects and collision detection.
- Custom rendering system creates game visual effects.
- Standardized logging system tracks game events.
- Sound manager controls game audio playback.
- Modular architecture allows for easy extension and maintenance.
- Test-driven development ensures code quality and reliability.
- Localization system for multi-language support. 