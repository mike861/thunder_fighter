# Thunder Fighter

A classic vertical scrolling space shooter game built with Pygame featuring modern architecture and comprehensive testing.

## Description

In Thunder Fighter, you pilot a fighter jet battling waves of enemies in space. Use the arrow keys or WASD to move and the spacebar to shoot. As the game progresses, enemies become stronger and more numerous, with powerful Bosses appearing periodically. Defeat enemies and Bosses to score points and collect power-ups. **Complete all levels by defeating the final boss to achieve victory!**

## Features

- **Complete Campaign**: Battle through multiple levels culminating in an epic final boss battle
- **Victory System**: Achieve game completion by defeating the final boss with comprehensive victory statistics
- **Wingman System**: Collect power-ups to gain up to two wingmen who provide extra firepower with tracking missiles and act as shields
- **Enhanced Victory Screen**: Beautiful victory interface that preserves game background with transparent overlay showing completion statistics
- **Robust Audio System**: Background music and sound effects with volume control, featuring automatic recovery from audio issues
- **Modular UI System**: Component-based UI architecture following single responsibility principle
- **Configuration Management**: JSON-based configuration with command-line tools
- **Event-Driven Architecture**: Comprehensive event system for decoupled game components
- **Factory Pattern**: Entity creation through configurable factories
- **Input Management System**: Decoupled input handling with customizable key bindings
- **Multi-language Support**: Currently English and Chinese with localization system
- **Developer Mode**: Debug information and configuration options
- **Dynamic Difficulty**: Configurable gameplay parameters
- **Extensively Tested**: Fully tested codebase with 249 comprehensive tests covering all game mechanics

For more detailed information on game mechanics, systems, and technical specifications, please see the [Project Details](./docs/DETAILS.md) document.

## Quick Start

### Requirements

- Python 3.7+
- Pygame 2.0.0+
- Other dependencies listed in `requirements.txt`

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mike861/thunder_fighter.git
   cd thunder_fighter
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   # venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the game:**
   ```bash
   python main.py
   ```

## Gameplay

### Controls

- **Movement**: Arrow Keys (↑↓←→) or WASD
- **Shoot**: Spacebar
- **Launch Missile**: X (when available)
- **Pause/Resume**: P
- **Toggle Music**: M
- **Toggle Sound Effects**: S
- **Adjust Volume**: +/- (Plus/Minus keys)
- **Switch Language**: L (Toggles between English and Chinese)
- **Quit Game**: ESC

### Game Objective

**Goal**: Progress through all 10 levels and defeat the final boss to achieve victory!

- **Early Levels (1-2)**: Advance by accumulating score points
- **Mid-to-Late Levels (3-10)**: Progress by defeating bosses at the end of each level
- **Final Victory**: Defeat the boss at Level 10 to complete the game
- **Victory Rewards**: Receive comprehensive statistics including final score, survival time, and completion achievements upon winning

### Wingman System

Starting from game level 3, a new power-up item may appear. Collecting this item grants you a "wingman" fighter that flanks your ship.

- **Firepower**: Each wingman automatically fires tracking missiles at nearby enemies, prioritizing the Boss when active
- **Shields**: Wingmen act as shields, absorbing enemy fire. They will be destroyed after taking a certain amount of damage
- **Limits**: You can have a maximum of two wingmen at a time
- **Configuration**: The initial number of wingmen, maximum number, and formation spacing are all configurable in `thunder_fighter/constants.py`

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

### Advanced Configuration

```bash
# Adjust Log Level (Optional)
# Set the THUNDER_FIGHTER_LOG_LEVEL environment variable
# Windows
set THUNDER_FIGHTER_LOG_LEVEL=DEBUG
python main.py

# Linux/macOS
THUNDER_FIGHTER_LOG_LEVEL=DEBUG python main.py
```

## Architecture

Thunder Fighter features a modern, modular architecture designed for maintainability and extensibility.

### Core Systems

- **Event-Driven Architecture**: Comprehensive event system enabling decoupled communication between game components
- **Factory Pattern**: Configurable entity creation system for enemies, bosses, items, and projectiles
- **Input Management**: Decoupled input handling with customizable key bindings and event callbacks
- **State Management**: Robust game state handling with transition management
- **Configuration System**: JSON-based configuration with runtime updates and command-line tools

### UI System

The UI system has been completely refactored into modular components:

- **HealthBarComponent**: Dynamic health bars with color-coded states
- **NotificationManager**: Game notifications and achievements system
- **GameInfoDisplay**: Score, level, and elapsed time display
- **PlayerStatsDisplay**: Player statistics and upgrades information
- **BossStatusDisplay**: Boss health and combat modes
- **ScreenOverlayManager**: Pause, victory, and game over screens
- **DevInfoDisplay**: Developer debug information (FPS, positions, etc.)

### Sound System

- **Instance-based management**: Each game instance has its own sound manager
- **Configurable volumes**: Separate music and sound effect controls
- **Health monitoring**: Automatic system recovery and music continuity
- **Format support**: MP3, WAV, OGG audio formats

## Testing

The project includes a comprehensive test suite with 249 tests covering all aspects of the game:

### Test Categories

- **Unit Tests (27 tests)**: Entity factories, individual components
- **Integration Tests (9 tests)**: Event system flow, component interactions
- **End-to-End Tests (9 tests)**: Complete game flow scenarios
- **Component Tests (204 tests)**: Sprites, graphics, utilities, state management

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/integration/ -v    # Integration tests
python -m pytest tests/unit/ -v          # Unit tests
python -m pytest tests/e2e/ -v           # End-to-end tests

# Run specific test files
python -m pytest tests/sprites/test_boss.py -v
python -m pytest tests/graphics/test_ui_components.py -v
```

### Test Coverage

All tests are currently passing, ensuring robust gameplay and stability across:
- Game mechanics and collision detection
- Victory and defeat conditions
- UI components and rendering
- Configuration management
- Event system and factory patterns
- Input handling and state transitions

## Project Structure

```
thunder_fighter/
├── docs/                       # Comprehensive documentation
│   ├── DETAILS.md             # Detailed game mechanics
│   ├── DETAILS_ZH.md          # Chinese documentation
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── STATE_MANAGEMENT_SYSTEM.md
│   ├── SEPARATION_OF_CONCERNS_SUMMARY.md
│   ├── UI_REFACTORING_SUMMARY.md
│   └── TEST_CASE_REVIEW.md
├── thunder_fighter/
│   ├── assets/                # Game assets (sounds, music)
│   ├── entities/              # Entity factories and creation logic
│   ├── events/                # Event system and game events
│   ├── graphics/              # Rendering, effects, UI components
│   │   ├── ui/               # Modular UI components
│   │   ├── ui_manager.py     # Main UI facade
│   │   ├── renderers.py      # Entity rendering functions
│   │   ├── background.py     # Dynamic background system
│   │   └── effects.py        # Visual effects
│   ├── input/                 # Input management and key bindings
│   ├── localization/          # Language files (en.json, zh.json)
│   ├── sprites/               # Game entities (player, enemies, boss, etc.)
│   ├── state/                 # Game state management
│   ├── utils/                 # Helper functions and managers
│   ├── config.py              # Game configuration
│   ├── constants.py           # Game constants
│   └── game.py                # Main game class
├── tests/                     # Comprehensive test suite (249 tests)
│   ├── e2e/                  # End-to-end tests
│   ├── integration/          # Integration tests
│   ├── unit/                 # Unit tests
│   ├── graphics/             # UI and rendering tests
│   ├── sprites/              # Entity tests
│   ├── state/                # State management tests
│   └── utils/                # Utility tests
├── main.py                    # Main entry point script
├── requirements.txt           # Python dependencies
├── pytest.ini                # Test configuration
├── README.md                  # This file
├── README_ZH.md              # Chinese README
└── LICENSE                   # Project License
```

## Known Issues

-   **Chinese Language Display**: On some systems (particularly macOS), switching to Chinese may display garbled text or "tofu" blocks (□□□) instead of the correct characters. This is a font rendering issue that is currently under investigation.

## Development

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

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass (`pytest tests/ -v`)
5. Submit a pull request

## Documentation

- [Detailed Game Mechanics](docs/DETAILS.md)
- [Configuration Management](docs/IMPLEMENTATION_SUMMARY.md)
- [State Management System](docs/STATE_MANAGEMENT_SYSTEM.md)
- [UI Refactoring Summary](docs/UI_REFACTORING_SUMMARY.md)
- [Separation of Concerns](docs/SEPARATION_OF_CONCERNS_SUMMARY.md)
- [Test Case Review](docs/TEST_CASE_REVIEW.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Screenshots

_(Add gameplay screenshots here if available)_
<!-- ![Gameplay Screenshot](screenshots/gameplay.png) -->