# Thunder Fighter

A simple space shooter game made with Python and Pygame.

## Game Description

In the game, the player controls a fighter jet battling enemies in space. Use the arrow keys to control the plane's movement and the spacebar to fire bullets.
As game time progresses, enemies become stronger and more frequent, and a powerful Boss appears periodically. Defeating the Boss yields more points.

## Game Features

- Custom-drawn graphics and particle effects
- Difficulty system that increases with game time
- Multiple enemy types and shooting patterns
- Boss battles with unique attack patterns
- Various item drop system
- Enhanced bullet system
- Explosion effects and visual feedback
- Standardized logging system
- Complete sound effects and background music system
- Game pause functionality
- Fully tested codebase with 43 passing tests

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
- Log level can be adjusted via the `THUNDER_FIGHTER_LOG_LEVEL` environment variable.
- All game events are logged in English for easy debugging and monitoring.

## Controls

- Arrow Keys (↑↓←→) or WASD: Control ship movement
- Spacebar: Fire bullets
- P: Pause/Resume game
- F3: Show detailed enemy level distribution (Dev mode)
- M: Toggle background music on/off
- S: Toggle sound effects on/off
- +/-: Adjust volume
- ESC: Quit game

## Project Structure

The project uses a modular structure for easier maintenance and extension:

```
thunder_fighter/
├── __init__.py                 # Package initializer
├── constants.py                # Constant definitions
├── game.py                     # Main game logic
├── graphics/                   # Graphics rendering related
│   ├── __init__.py
│   ├── effects.py              # Effects system
│   └── renderers.py            # Rendering functions
├── sprites/                    # Game sprite classes
│   ├── __init__.py
│   ├── boss.py                 # Boss class
│   ├── bullets.py              # Bullet classes
│   ├── enemy.py                # Enemy class
│   ├── explosion.py            # Explosion effect class
│   ├── items.py                # Item classes (Health, Bullet Speed/Path, Player Speed)
│   └── player.py               # Player class
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── collisions.py           # Collision detection
│   ├── logger.py               # Logging system
│   ├── score.py                # Score system
│   ├── sound_manager.py        # Sound management
│   └── stars.py                # Background stars
└── assets/                     # Game assets
    ├── sounds/                 # Sound effect files
    └── music/                  # Background music
main.py                         # Main entry script
requirements.txt                # Dependency list
README_CN.md                    # Chinese README file
README.md                       # English README file
uml_class_diagram.md            # UML Class Diagram
.gitignore                      # Git ignore configuration
```

## Testing

The game includes a comprehensive test suite with 43 tests covering all major components:
- Player mechanics and interactions
- Enemy behaviors and level calculations
- Boss battle mechanics
- Item generation and effects
- Collision detection
- Game state management

Run the tests with:
```bash
pytest
```

## How to Run

Ensure you have Python and Pygame installed, then run:

```bash
python main.py
```

To adjust the log level, set the environment variable:

```bash
# Windows
set THUNDER_FIGHTER_LOG_LEVEL=DEBUG
python main.py

# Linux/macOS
THUNDER_FIGHTER_LOG_LEVEL=DEBUG python main.py
```

## Dependencies

- Python 3.6+
- Pygame 2.0+

## Sound Assets

The game uses the following sound and music files:

1. Place WAV or MP3 format sound effect files in the `thunder_fighter/assets/sounds/` directory:
   - `player_shoot.wav` - Player shooting sound
   - `player_hit.wav` - Player hit sound
   - `player_death.wav` - Player death sound
   - `enemy_explosion.wav` - Enemy explosion sound
   - `boss_death.wav` - Boss death sound
   - `item_pickup.wav` - Item pickup sound (Used for all item types currently)

2. Place MP3 format background music in the `thunder_fighter/assets/music/` directory:
   - `background_music.mp3` - Game background music

If these files are missing, the game will handle the missing sounds gracefully and will not affect normal gameplay.

## Development Status

- ✅ Core gameplay mechanics implemented
- ✅ Enemy system with varied behaviors
- ✅ Boss battles with unique patterns
- ✅ Item drop and collection system
- ✅ Sound system with volume control
- ✅ Complete test coverage
- ✅ Game polish and optimization

## Technical Details

- Object-Oriented Programming used for game entity design.
- Sprite Groups manage game objects and collision detection.
- Custom rendering system creates game visual effects.
- Standardized logging system tracks game events.
- Sound manager controls game audio playback.
- Modular architecture allows for easy extension and maintenance.
- Test-driven development ensures code quality and reliability.

## Developer

This game was created as a Python game development practice project. 