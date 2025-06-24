# Thunder Fighter

A classic vertical scrolling space shooter game built with Pygame.

## Description

In Thunder Fighter, you pilot a fighter jet battling waves of enemies in space. Use the arrow keys or WASD to move and the spacebar to shoot. As the game progresses, enemies become stronger and more numerous, with powerful Bosses appearing periodically. Defeat enemies and Bosses to score points and collect power-ups. **Complete all levels by defeating the final boss to achieve victory!**

## Features

- **Complete Campaign**: Battle through multiple levels culminating in an epic final boss battle
- **Victory System**: Achieve game completion by defeating the final boss with comprehensive victory statistics
- Dynamic level progression with increasing difficulty
- Multiple enemy types with different behaviors
- Epic boss battles with changing attack patterns
- Power-up system (health, speed, bullet enhancements)
- **Wingman System:** Collect power-ups to gain up to two wingmen who provide extra firepower with tracking missiles and act as shields.
- Particle effects and animations for explosions and impacts
- **Enhanced Victory Screen**: Beautiful victory interface that preserves game background with transparent overlay showing completion statistics
- Dynamic UI with stacked notifications
- Multi-language support (currently English and Chinese)
- Responsive controls and collision detection
- **Robust Audio System**: Background music and sound effects with volume control, featuring automatic recovery from audio issues
- Comprehensive logging system
- **Extensively Tested**: Fully tested codebase with 94 comprehensive tests covering all game mechanics
- **Localization**: All user-facing UI text is loaded via the localization module, with translations available in English and Chinese.
- **Modular UI System**: Component-based UI architecture following single responsibility principle
- **Configuration Management**: JSON-based configuration with command-line tools
- **Sound System**: Configurable audio with music and sound effects
- **Developer Mode**: Debug information and configuration options
- **Dynamic Difficulty**: Configurable gameplay parameters

For more detailed information on game mechanics, systems, and technical specifications, please see the [Project Details](./docs/DETAILS.md) document.

## Screenshots

_(Add gameplay screenshots here if available)_ 
<!-- ![Gameplay Screenshot](screenshots/gameplay.png) -->

## Requirements

- Python 3.7+
- Pygame 2.0.0+
- Other dependencies listed in `requirements.txt`

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/mike861/thunder_fighter.git
    cd thunder_fighter
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows:
    # venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Play

1.  **Run the game:**
    ```bash
    python main.py
    ```

2.  **Adjust Log Level (Optional):**
    Set the `THUNDER_FIGHTER_LOG_LEVEL` environment variable (e.g., `DEBUG`, `INFO`, `WARNING`).
    ```bash
    # Windows
    # set THUNDER_FIGHTER_LOG_LEVEL=DEBUG
    # python main.py
    
    # Linux/macOS
    # THUNDER_FIGHTER_LOG_LEVEL=DEBUG python main.py
    ```

## Configuration Management

Thunder Fighter includes a comprehensive configuration system that allows you to customize various aspects of the game.

### Configuration Tool

Use the built-in configuration tool to manage settings:

```bash
# Show current configuration
python -m thunder_fighter.utils.config_tool show

# Set music volume to 80%
python -m thunder_fighter.utils.config_tool set sound music_volume 0.8

# Enable developer mode
python -m thunder_fighter.utils.config_tool set debug dev_mode true

# Set difficulty to hard
python -m thunder_fighter.utils.config_tool set gameplay difficulty hard

# Reset all settings to defaults
python -m thunder_fighter.utils.config_tool reset
```

### Available Settings

| Section | Setting | Description | Default |
|---------|---------|-------------|---------|
| **Sound** | `music_volume` | Background music volume (0.0-1.0) | 0.5 |
| | `sound_volume` | Sound effects volume (0.0-1.0) | 0.7 |
| | `music_enabled` | Enable/disable music | true |
| | `sound_enabled` | Enable/disable sound effects | true |
| **Display** | `fullscreen` | Enable fullscreen mode | false |
| | `screen_scaling` | Screen scaling factor | 1.0 |
| **Gameplay** | `difficulty` | Game difficulty (easy/normal/hard) | normal |
| | `initial_lives` | Starting number of lives | 3 |
| **Debug** | `dev_mode` | Enable developer mode | false |
| | `log_level` | Logging level | INFO |

### Configuration File

Settings are automatically saved to `~/.thunder_fighter/config.json`. You can also edit this file directly if preferred.

### Controls

-   **Movement:** Arrow Keys (↑↓←→) or WASD
-   **Shoot:** Spacebar
-   **Pause/Resume:** P
-   **Toggle Music:** M
-   **Toggle Sound Effects:** S
-   **Adjust Volume:** +/- (Plus/Minus keys)
-   **Switch Language:** L (Toggles between English and Chinese)
-   **Quit Game:** ESC

### Game Objective

**Goal**: Progress through all 10 levels and defeat the final boss to achieve victory!

- **Early Levels (1-2)**: Advance by accumulating score points.
- **Mid-to-Late Levels (3-10)**: Progress by defeating bosses at the end of each level.
- **Final Victory**: Defeat the boss at Level 10 to complete the game.
- **Victory Rewards**: Receive comprehensive statistics including final score, survival time, and completion achievements upon winning.

### Wingman System

Starting from game level 3, a new power-up item may appear. Collecting this item grants you a "wingman" fighter that flanks your ship.

-   **Firepower**: Each wingman automatically fires tracking missiles at nearby enemies, prioritizing the Boss when active.
-   **Shields**: Wingmen act as shields, absorbing enemy fire. They will be destroyed after taking a certain amount of damage.
-   **Limits**: You can have a maximum of two wingmen at a time.
-   **Configuration**: The initial number of wingmen, maximum number, and formation spacing are all configurable in `thunder_fighter/constants.py`.

## Testing

The project includes a comprehensive test suite covering game mechanics, collisions, victory conditions, and all components. All 94 tests are currently passing, ensuring robust gameplay and stability.

-   **Run all tests:**
    ```bash
    pytest
    ```

-   **Run tests in a specific file:**
    ```bash
    pytest tests/sprites/test_boss.py
    ```

-   **Run victory system tests:**
    ```bash
    pytest tests/test_game_victory.py
    ```

## Project Structure

```
thunder_fighter/
├── docs/           # Detailed documentation
│   ├── DETAILS.md
│   └── DETAILS_ZH.md
├── thunder_fighter/
│   ├── assets/     # Game assets (sounds, music)
│   ├── graphics/   # Rendering, effects, UI
│   ├── localization/ # Language files (en.json, zh.json)
│   ├── sprites/    # Game entities (player, enemies, boss, etc.)
│   ├── utils/      # Helper functions and managers
│   ├── config.py   # Game configuration
│   ├── constants.py# Game constants
│   └── game.py     # Main game class
├── tests/          # Unit tests (94 comprehensive tests)
├── main.py         # Main entry point script
├── requirements.txt # Python dependencies
├── README.md       # This file
├── README_ZH.md    # Chinese README
└── LICENSE         # Project License
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py

# Configure settings
python -m thunder_fighter.utils.config_tool show
python -m thunder_fighter.utils.config_tool set sound music_volume 0.8
```

## Game Controls

- **Arrow Keys**: Move player
- **Space**: Shoot bullets
- **P**: Pause/Resume game
- **M**: Toggle music
- **S**: Toggle sound effects
- **+/-**: Adjust volume
- **L**: Switch language
- **ESC**: Exit game

## Architecture

### UI System (Recently Refactored)

The UI system has been completely refactored from a monolithic 700+ line class into modular components:

- **HealthBarComponent**: Draws health bars with dynamic colors
- **NotificationManager**: Manages game notifications and achievements
- **GameInfoDisplay**: Shows score, level, and elapsed time
- **PlayerStatsDisplay**: Displays player statistics and upgrades
- **BossStatusDisplay**: Shows boss health and combat modes
- **ScreenOverlayManager**: Handles pause, victory, and game over screens
- **DevInfoDisplay**: Developer debug information (FPS, positions, etc.)

### Configuration Management

- **JSON-based configuration**: Centralized settings management
- **Command-line tools**: Easy configuration without code changes
- **Runtime updates**: Change settings while game is running
- **Legacy compatibility**: Automatic migration from old config format

### Sound System

- **Instance-based management**: Each game instance has its own sound manager
- **Configurable volumes**: Separate music and sound effect controls
- **Health monitoring**: Automatic system recovery and music continuity
- **Format support**: MP3, WAV, OGG audio formats

## Development

### Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/graphics/ -v  # UI components
python -m pytest tests/sprites/ -v   # Game entities
python -m pytest tests/utils/ -v     # Utilities
```

### Configuration

```bash
# View current settings
python -m thunder_fighter.utils.config_tool show

# Modify settings
python -m thunder_fighter.utils.config_tool set sound music_volume 0.8
python -m thunder_fighter.utils.config_tool set debug dev_mode true

# Reset to defaults
python -m thunder_fighter.utils.config_tool reset
```

## Project Structure

```
thunder_fighter/
├── graphics/
│   ├── ui_components/          # Modular UI components
│   ├── ui_manager.py           # Main UI facade
│   └── ui_manager_refactored.py # Component coordinator
├── sprites/                    # Game entities
├── utils/                      # Utilities and managers
├── state/                      # Game state management
├── localization/              # Multi-language support
└── assets/                    # Game assets
```

## Recent Updates

### ✅ UI System Refactoring (Completed)
- Transformed monolithic UI into modular components
- Improved testability with 35 new UI tests
- Maintained full backwards compatibility
- Enhanced maintainability and extensibility

### ✅ Configuration Management System
- Implemented JSON-based configuration
- Added command-line configuration tools
- Integrated with all game systems
- Supports difficulty multipliers

### ✅ Sound System Improvements
- Instance-based sound management
- Health monitoring and auto-recovery
- Configurable volume controls
- Fixed notification duplicates

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass
5. Submit a pull request

## Documentation

- [UI Refactoring Summary](docs/UI_REFACTORING_SUMMARY.md)
- [Configuration Management](docs/IMPLEMENTATION_SUMMARY.md)
- [State Management System](docs/STATE_MANAGEMENT_SYSTEM.md)
- [Development Details](docs/DETAILS.md)