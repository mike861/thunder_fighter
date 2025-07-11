# Thunder Fighter

A classic vertical scrolling space shooter game built with Pygame featuring modern architecture and comprehensive testing.

![Thunder Fighter Screenshot](./docs/images/boss.png) 

## Description

In Thunder Fighter, you pilot a fighter jet battling waves of enemies in space. Use the arrow keys or WASD to move and the spacebar to shoot. As the game progresses, enemies become stronger and more numerous, with powerful Bosses appearing periodically. Defeat enemies and Bosses to score points and collect power-ups. **Complete all levels by defeating the final boss to achieve victory!**

## Features

- **Complete Campaign**: Battle through multiple levels culminating in an epic final boss battle
- **Victory System**: Achieve game completion by defeating the final boss with comprehensive victory statistics
- **🎨 Dynamic Level Backgrounds**: Each level features unique visual themes with ultra-smooth transitions
  - **Double Buffering Technology**: Eliminates visual artifacts and flashing during level changes
  - **Progressive Difficulty Visualization**: Background complexity and atmosphere evolve with game difficulty
  - **Special Effects**: Level-specific effects including space storms and asteroid fields
  - **Smooth Alpha Transitions**: Professional-grade 3-second transitions with cubic bezier easing
- **🛸 Distinct Ship Designs**: Clear visual differentiation between player and enemy forces
  - **Player Ships**: Modern blue fighter jets with geometric design (60×50 pixels)
  - **Enemy Ships**: Organic alien biomechanical entities with distinct appearance (45×45 pixels)
  - **Progressive Enemy Evolution**: 4 distinct alien themes across difficulty levels
  - **Front-Facing Combat**: All ships properly oriented for realistic space combat
- **Wingman System**: Collect power-ups to gain up to two wingmen who provide extra firepower with tracking missiles and act as shields
- **Enhanced Victory Screen**: Beautiful victory interface that preserves game background with transparent overlay showing completion statistics
- **Robust Audio System**: Background music and sound effects with volume control, featuring automatic recovery from audio issues
- **Modular UI System**: Component-based UI architecture following single responsibility principle
- **Configuration Management**: JSON-based configuration with command-line tools
- **Event-Driven Architecture**: Comprehensive event system for decoupled game components
- **Factory Pattern**: Entity creation through configurable factories
- **Input Management System**: Decoupled input handling with customizable key bindings
- **Enhanced Multi-language Support**: Complete internationalization with optimized Chinese font rendering
  - **Dynamic Language Switching**: Press L to toggle between English and Chinese
  - **Optimized Chinese Fonts**: TTF-based font system for reliable Chinese character display on macOS
  - **Localized UI Elements**: All game text including level transitions, Boss status, and notifications
  - **Font System**: ResourceManager-based font loading with automatic fallbacks
- **Developer Mode**: Debug information and configuration options
- **Dynamic Difficulty**: Configurable gameplay parameters
- **Extensively Tested**: Fully tested codebase with 354+ comprehensive tests covering all game mechanics and architectural improvements
- **Systems-Based Architecture**: Modular systems design with collision, scoring, spawning, and physics systems
- **Factory Pattern Entity Creation**: Type-organized entity factories (enemies/, projectiles/, items/, player/)
- **Enhanced Input System**: Unified input architecture with handler→manager→facade pattern
- **Clean Architecture**: Eliminated circular import risks and architectural debt through comprehensive refactoring

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

### Visual Experience

Thunder Fighter features a **dynamic background system** that enhances immersion:

- **Level 1 - Deep Space**: Peaceful blue/black starfield for your journey's beginning
- **Level 2 - Nebula Field**: Purple/blue nebula clouds as difficulty increases
- **Level 3 - Asteroid Belt**: Brown/orange asteroid field with animated debris
- **Level 4 - Red Zone**: Dangerous red space with particle storm effects
- **Level 5 - Final Battle**: Ominous dark red atmosphere for the ultimate challenge

Each transition between levels features **professional-grade smooth animations** with no visual artifacts or flashing, creating a cinematic experience that reflects the escalating intensity of your mission.

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
- **Systems-Based Design**: Modular architecture with dedicated systems for core game logic:
  - **CollisionSystem**: Unified collision detection and resolution for all entity interactions
  - **ScoringSystem**: Centralized score management with level progression and achievement tracking
  - **SpawningSystem**: Entity spawning coordination integrating all factory classes
  - **PhysicsSystem**: Movement, boundaries, and collision detection for game physics
- **Factory Pattern**: Type-organized entity creation with configurable presets:
  - **EnemyFactory**: Enemy creation with difficulty scaling and behavior patterns (enemies/)
  - **BossFactory**: Boss generation with level-appropriate challenges (enemies/)
  - **ItemFactory**: Power-up and collectible creation system (items/)
  - **ProjectileFactory**: Bullet and missile generation for all entities (projectiles/)
- **Unified Input System**: Clean input architecture (systems/input/) with:
  - **InputHandler**: Raw event processing with macOS screenshot interference handling
  - **InputManager**: Event coordination and state management
  - **InputFacade**: High-level input interface for game logic
- **State Management**: Robust game state handling with transition management
- **Configuration System**: JSON-based configuration with runtime updates and command-line tools
- **Pause Management**: Dedicated `PauseManager` component with pause-aware timing calculations and comprehensive statistics
- **Enhanced Localization**: Dependency injection-based localization system with loader abstraction for improved testability
- **Clean Architecture**: Eliminated circular imports and architectural debt through systematic refactoring

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

### Project Structure

The codebase follows a modular, systems-based architecture:

```
thunder_fighter/
├── systems/              # Core game systems
│   ├── input/           # Unified input management system
│   │   ├── handler.py   # Raw event processing
│   │   ├── manager.py   # Event coordination
│   │   ├── facade.py    # High-level interface
│   │   └── adapters/    # Platform adapters
│   ├── collision.py     # Unified collision detection
│   ├── scoring.py       # Score and level management
│   ├── spawning.py      # Entity spawning coordination
│   └── physics.py       # Movement and physics
├── entities/            # Type-organized entity system
│   ├── base.py         # Base entity classes
│   ├── enemies/        # Enemy entities and factories
│   │   ├── enemy_factory.py
│   │   └── boss_factory.py
│   ├── projectiles/    # Bullets and missiles
│   │   └── projectile_factory.py
│   ├── items/          # Power-ups and collectibles
│   │   └── item_factory.py
│   └── player/         # Player and wingman entities
├── graphics/           # Rendering and visual effects
│   ├── ui/            # Modular UI components
│   └── effects/       # Modular visual effects system
│       ├── notifications.py  # Notification system
│       ├── explosions.py     # Explosion effects
│       └── flash_effects.py  # Flash effects
├── events/            # Event system and definitions
├── state/             # Game state management
├── localization/      # Multi-language support
└── utils/             # Utilities and configuration
```

## Testing

The project includes a comprehensive test suite with 354+ tests covering all aspects of the game:

### Test Categories

- **Unit Tests (90+ tests)**: Entity factories, individual components, pause system, localization system, new enemy entity tests
- **Integration Tests (9 tests)**: Event system flow, component interactions
- **End-to-End Tests (9 tests)**: Complete game flow scenarios
- **Component Tests (246+ tests)**: Sprites, graphics, utilities, state management, collision systems

### Recently Added Test Coverage

- **Systems Architecture Tests**: Comprehensive testing framework for core game systems
  - **Collision System Tests**: Collision detection, handler setup, and interface validation
  - **Scoring System Tests**: Score management, level progression, and achievement tracking
  - **Spawning System Tests**: Entity spawning coordination and factory integration
  - **Physics System Tests**: Movement, boundaries, and physics simulation
- **Event System Tests**: Event-driven architecture validation, listener management, and event dispatch
- **Localization System Tests**: Multi-language support, font management, and language switching
- **PauseManager Tests (16 tests)**: Comprehensive testing of pause functionality, timing calculations, and edge cases
- **Localization Tests (39 tests)**: Complete coverage of loader abstraction, dependency injection, and language management  
- **Boss Spawn Timing Tests (18 tests)**: Specialized tests for boss generation interval calculations with pause handling

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/integration/ -v    # Integration tests
python -m pytest tests/unit/ -v          # Unit tests
python -m pytest tests/e2e/ -v           # End-to-end tests
python -m pytest tests/systems/ -v       # Systems architecture tests
python -m pytest tests/events/ -v        # Event system tests
python -m pytest tests/localization/ -v  # Localization tests

# Run specific test files
python -m pytest tests/sprites/test_boss.py -v
python -m pytest tests/graphics/test_ui_components.py -v
python -m pytest tests/systems/test_collision_system.py -v
```

### Test Coverage

All tests are currently passing, ensuring robust gameplay and stability across:
- **Core Systems**: Collision detection, scoring, spawning, and physics systems
- **Event Architecture**: Event-driven communication and listener management
- **Localization**: Multi-language support and font management
- **Game Mechanics**: Victory and defeat conditions, boss battles, level progression
- **UI Components**: Modular interface components and rendering
- **Configuration Management**: Settings persistence and runtime updates
- **Input Handling**: Clean input architecture and state transitions

## Project Structure

```
thunder_fighter/
├── docs/                       # Comprehensive documentation
│   ├── DETAILS.md             # Detailed game mechanics
│   ├── DETAILS_ZH.md          # Chinese documentation
│   ├── FONT_SYSTEM_AND_LOCALIZATION.md # Font system and multi-language support
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── STATE_MANAGEMENT_SYSTEM.md
│   ├── SEPARATION_OF_CONCERNS_SUMMARY.md
│   ├── UI_REFACTORING_SUMMARY.md
│   └── TEST_CASE_REVIEW.md
├── thunder_fighter/
│   ├── assets/                # Game assets (sounds, music)
│   ├── systems/               # Core game systems
│   │   ├── input/            # Unified input management system
│   │   ├── collision.py      # Collision detection system
│   │   ├── scoring.py        # Score and level management
│   │   ├── spawning.py       # Entity spawning coordination
│   │   └── physics.py        # Movement and physics
│   ├── entities/              # Type-organized entity system
│   │   ├── enemies/          # Enemy entities and factories
│   │   ├── projectiles/      # Bullets and missiles
│   │   ├── items/            # Power-ups and collectibles
│   │   └── player/           # Player and wingman entities
│   ├── events/                # Event system and game events
│   ├── graphics/              # Rendering, effects, UI components
│   │   ├── ui/               # Modular UI components
│   │   ├── effects/          # Modular visual effects system
│   │   ├── ui_manager.py     # Main UI facade
│   │   ├── renderers.py      # Entity rendering functions
│   │   └── background.py     # Dynamic background system
│   ├── localization/          # Enhanced localization system
│   │   ├── en.json           # English translations
│   │   ├── zh.json           # Chinese translations
│   │   ├── loader.py         # Language loader abstraction
│   │   └── font_support.py   # Font management system
│   ├── sprites/               # Game entities (player, enemies, boss, etc.)
│   ├── state/                 # Game state management
│   ├── utils/                 # Helper functions and managers
│   │   └── pause_manager.py  # Dedicated pause management
│   ├── config.py              # Game configuration
│   ├── constants.py           # Game constants
│   └── game.py                # Main game class
├── tests/                     # Comprehensive test suite (357+ tests)
│   ├── e2e/                  # End-to-end tests
│   ├── integration/          # Integration tests
│   ├── unit/                 # Unit tests
│   ├── systems/              # Systems architecture tests
│   ├── events/               # Event system tests
│   ├── localization/         # Localization tests
│   ├── graphics/             # UI and rendering tests
│   ├── sprites/              # Entity tests
│   ├── state/                # State management tests
│   └── utils/                # Utility tests
├── main.py                    # Main entry point script
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Modern Python project configuration
├── README.md                  # This file
├── README_ZH.md              # Chinese README
└── LICENSE                   # Project License
```

## Recent Improvements

- **🛸 Enemy Ship Redesign**: Complete visual overhaul of enemy ships for enhanced gameplay clarity
  - **Alien Biomechanical Design**: Replaced fighter jet appearance with organic alien entities
  - **Size Differentiation**: Enemy ships now 45×45 pixels vs player's 60×50 for clear distinction
  - **Thematic Evolution**: 4 distinct alien themes (Insectoid → Toxic → Energy → Void) across difficulty levels
  - **Front-Facing Orientation**: All ships properly oriented with thrusters pointing toward combat direction
- **Enhanced Chinese Font Support**: Resolved "tofu blocks" (□□□) issue on macOS through TTF-based font loading system
- **Complete Localization**: All UI elements now support dynamic language switching
- **Optimized Font System**: ResourceManager-based font loading with platform-specific optimizations
- **🍎 macOS Screenshot Interference Fix**: Resolved critical input issue affecting pause and language switching
  - **Hybrid Input Processing**: Intelligent fallback system ensures P and L keys remain functional
  - **Automatic Recovery**: Seamless operation even during macOS screenshot interference (`Shift+Cmd+5`)
  - **Manual Reset Option**: F1 key provides manual input state reset if needed
  - **Transparent Operation**: Users experience no functional difference during interference scenarios
- **⏸️ Enhanced Pause System**: Comprehensive improvements to pause/resume functionality
  - **Pause-Aware Timing**: Game time correctly excludes pause periods for accurate elapsed time calculation
  - **Robust State Management**: Enhanced pause/resume logic with cooldown and state synchronization
  - **Reliability Improvements**: Fixed pause failures after repeated pause/resume cycles
- **🔧 Interface Testability Improvements**: Enhanced code architecture for better testing
  - **PauseManager Component**: Extracted pause logic into dedicated, testable component with dependency injection
  - **Localization Abstraction**: Implemented loader pattern with `FileLanguageLoader`, `MemoryLanguageLoader`, and `CachedLanguageLoader`
  - **Enhanced Test Coverage**: Added 55 new comprehensive tests for pause and localization systems
  - **Dependency Injection**: Improved interfaces enable easier testing and better separation of concerns
- **🎯 Boss Spawn Timing Fix**: Critical fix for boss generation interval calculation
  - **Pause-Aware Boss Spawning**: Boss generation now correctly excludes pause time from spawn interval calculations
  - **Consistent Timing**: Boss spawning behavior now matches display time handling for unified pause-aware timing
  - **Comprehensive Testing**: Added 18 specialized test cases covering boss spawn timing with pause scenarios
  - **Regression Prevention**: Test suite ensures boss spawn timing remains accurate across future changes
- **🔄 Comprehensive Project Structure Optimization**: Major architectural debt cleanup and modernization
  - **Duplicate File Elimination**: Removed 4 sets of duplicate factory files + 7 duplicate UI component files + 1 obsolete demo file
  - **Unified Input System**: Consolidated from dual input systems to single systems/input/ architecture
  - **Factory Organization**: Standardized factory location in type-specific subdirectories (enemies/, items/, projectiles/)
  - **Import Simplification**: Reduced entities/__init__.py from 60 to 36 lines, removing 30+ unnecessary imports
  - **Effects Module Restructuring**: Split monolithic effects.py into modular components (notifications.py, explosions.py, flash_effects.py)
  - **Configuration Modernization**: Unified configuration management in pyproject.toml, removed redundant pytest.ini
  - **Testing Infrastructure Enhancement**: Added comprehensive test coverage for systems/, events/, and localization/ modules
  - **Code Quality Improvements**: Updated .gitignore to Python best practices, eliminated problematic ignore patterns
  - **Language Compliance**: Removed all violations of English-only code requirement
  - **Total Impact**: Eliminated 4000+ lines of duplicate/obsolete code while enhancing functionality and maintainability

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
- [Font System and Localization](docs/FONT_SYSTEM_AND_LOCALIZATION.md)
- [Configuration Management](docs/IMPLEMENTATION_SUMMARY.md)
- [State Management System](docs/STATE_MANAGEMENT_SYSTEM.md)
- [UI Refactoring Summary](docs/UI_REFACTORING_SUMMARY.md)
- [Separation of Concerns](docs/SEPARATION_OF_CONCERNS_SUMMARY.md)
- [Test Case Review](docs/TEST_CASE_REVIEW.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Screenshots