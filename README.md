# Thunder Fighter

[![CI](https://github.com/mike861/thunder_fighter/workflows/CI/badge.svg)](https://github.com/mike861/thunder_fighter/actions)
[![codecov](https://codecov.io/gh/mike861/thunder_fighter/branch/main/graph/badge.svg)](https://codecov.io/gh/mike861/thunder_fighter)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A classic vertical scrolling space shooter game built with Pygame featuring modern architecture and comprehensive testing.

![Thunder Fighter Screenshot](./docs/images/boss.png) 

## Description

In Thunder Fighter, you pilot a fighter jet battling waves of enemies in space. Use the arrow keys or WASD to move and the spacebar to shoot. As the game progresses, enemies become stronger and more numerous, with powerful Bosses appearing periodically. Defeat enemies and Bosses to score points and collect power-ups. **Complete all levels by defeating the final boss to achieve victory!**

## Features

### Gameplay
- **Complete Campaign**: Battle through 10 levels culminating in an epic final boss battle
- **🎨 Dynamic Level Backgrounds**: Each level features unique visual themes with ultra-smooth transitions
- **🛸 Distinct Ship Designs**: Clear visual differentiation between player (geometric jets) and enemy forces (organic aliens)
- **Wingman System**: Collect power-ups to gain up to two wingmen for extra firepower and protection
- **Boss Battles**: Progressive difficulty with multiple attack patterns and health-based combat modes
- **Victory System**: Complete victory screen with comprehensive statistics and achievements

### Technical
- **Modern Architecture**: Event-driven, systems-based design with clean separation of concerns
- **Multi-language Support**: Dynamic switching between English and Chinese (Press L)
- **Comprehensive Testing**: 390+ tests ensuring stability and reliability
- **Configuration System**: JSON-based settings with command-line tools
- **Cross-platform**: Works on Windows, macOS, and Linux with platform-specific optimizations

## 📚 Documentation

- **[Game Mechanics Guide](docs/GAME_MECHANICS.md)** - Detailed game systems and mechanics
- **[Architecture Guide](docs/ARCHITECTURE.md)** - System architecture and design patterns
- **[Technical Details](docs/TECHNICAL_DETAILS.md)** - Technical implementations and optimizations
- **[Testing Guide](docs/TESTING_GUIDE.md)** - Comprehensive testing guide and best practices
- **[Development Roadmap](docs/DEVELOPMENT_ROADMAP.md)** - Development roadmap and planned features
- **[Localization Guide](docs/LOCALIZATION.md)** - Multi-language support guide

## Quick Start

### Requirements

- Python 3.12+
- Pygame 2.6.0+
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

### Visual Experience

Thunder Fighter features a **dynamic background system** with unique themes for each level:

- **Level 1 - Deep Space**: Peaceful blue/black starfield
- **Level 2 - Nebula Field**: Purple/blue nebula clouds  
- **Level 3 - Asteroid Belt**: Brown/orange asteroid field with animated debris
- **Level 4 - Red Zone**: Dangerous red space with particle storm effects
- **Level 5+ - Final Battle**: Ominous dark red atmosphere

Each level transition features smooth 3-second animations with no visual artifacts.

### Wingman System

Starting from game level 3, a new power-up item may appear. Collecting this item grants you a "wingman" fighter that flanks your ship.

- **Firepower**: Each wingman automatically fires tracking missiles at nearby enemies, prioritizing the Boss when active
- **Shields**: Wingmen act as shields, absorbing enemy fire. They will be destroyed after taking a certain amount of damage
- **Limits**: You can have a maximum of two wingmen at a time
- **Configuration**: The initial number of wingmen, maximum number, and formation spacing are all configurable in `thunder_fighter/constants.py`

## Configuration

Thunder Fighter uses a JSON-based configuration system:

```bash
# View and modify settings
python -m thunder_fighter.utils.config_tool show
python -m thunder_fighter.utils.config_tool set sound music_volume 0.8
python -m thunder_fighter.utils.config_tool reset
```

Settings are saved to `~/.thunder_fighter/config.json`. For detailed configuration options, see [Technical Details](docs/TECHNICAL_DETAILS.md#configuration-options-reference).

## Architecture Overview

Thunder Fighter uses modern software engineering patterns:
- **Event-driven architecture** for decoupled components
- **Systems-based design** (collision, scoring, spawning, physics)
- **Factory pattern** for entity creation
- **State management** for game flow
- **Modular UI components** with single responsibility

See [Architecture Guide](docs/ARCHITECTURE.md) for detailed technical documentation and [code organization](docs/ARCHITECTURE.md#code-organization).

## Testing

The project includes 390+ comprehensive tests covering all aspects of the game:

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/integration/ -v    # Integration tests
python -m pytest tests/unit/ -v          # Unit tests
python -m pytest tests/e2e/ -v           # End-to-end tests
python -m pytest tests/systems/ -v       # Systems architecture tests
```

### Test Coverage
- **Core Systems**: Collision detection, scoring, spawning, physics
- **Game Mechanics**: Victory conditions, boss battles, level progression
- **Localization**: Multi-language support and font management
- **UI Components**: Modular interface components and rendering
- **Input Handling**: Clean input architecture and state transitions

For detailed testing documentation, patterns, and best practices, see **[Testing Guide](docs/TESTING_GUIDE.md)**.

## Project Structure

```
thunder_fighter/
├── docs/                     # Documentation
│   ├── GAME_MECHANICS.md    # Game mechanics guide
│   ├── ARCHITECTURE.md      # System architecture
│   ├── TECHNICAL_DETAILS.md # Technical implementations
│   └── ...
├── thunder_fighter/         # Main game package
│   ├── systems/            # Core game systems
│   ├── entities/           # Type-organized entities
│   ├── graphics/           # Rendering and UI
│   ├── localization/       # Multi-language support
│   └── ...
├── tests/                  # Comprehensive test suite (375+ tests)
├── main.py                 # Game entry point
└── requirements.txt        # Dependencies
```

## What's New

- 🛸 **Enhanced Ship Designs**: Redesigned enemy ships with alien biomechanical appearance
- 🎨 **Dynamic Level Backgrounds**: Smooth transitions with unique visual themes
- 🌏 **Full Chinese Support**: Optimized fonts and complete localization
- 🔧 **Architecture Improvements**: Major code cleanup and systems-based design
- 📊 **Enhanced Testing**: 390+ comprehensive tests with specialized coverage
- 🍎 **macOS Optimizations**: Fixed input interference and font rendering issues

See [Technical Details](docs/TECHNICAL_DETAILS.md) for complete technical information and [Development History](docs/DEVELOPMENT_HISTORY.md) for detailed changelog.

## Development

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass (`pytest tests/ -v`)
5. Submit a pull request


## License

This project is licensed under the GPL License - see the [LICENSE](LICENSE) file for details.

## Screenshots