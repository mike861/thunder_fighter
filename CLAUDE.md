# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Game
```bash
python main.py
# OR on macOS with virtual environment:
./venv/bin/python main.py
```

### Configuration Management
```bash
# View current settings
python -m thunder_fighter.utils.config_tool show

# Modify settings
python -m thunder_fighter.utils.config_tool set sound music_volume 0.8
python -m thunder_fighter.utils.config_tool set debug dev_mode true

# Reset to defaults
python -m thunder_fighter.utils.config_tool reset
```

### Testing
```bash
# Run all tests (354 comprehensive tests)
./venv/bin/python -m pytest tests/ -v

# Run specific test categories
./venv/bin/python -m pytest tests/integration/ -v    # Integration tests
./venv/bin/python -m pytest tests/unit/ -v          # Unit tests
./venv/bin/python -m pytest tests/e2e/ -v           # End-to-end tests

# Test coverage
./venv/bin/python -m pytest tests/ --cov=thunder_fighter --cov-report=html
```

### Code Quality
```bash
# Lint and format
ruff check .
ruff format .

# Type checking
mypy thunder_fighter/
```

### Development Dependencies
```bash
# Install development dependencies
pip install -e .[dev]
```

## Architecture

Thunder Fighter is a vertical scrolling space shooter built with Pygame using modern architecture patterns:

### Core Design Patterns

**Event-Driven Architecture**: Game components communicate through `EventSystem` rather than direct coupling. All game events are defined in `events/game_events.py`.

**Systems-Based Architecture**: Core game logic organized into dedicated systems in `systems/`:
- `CollisionSystem` - Unified collision detection and resolution for all entity interactions
- `ScoringSystem` - Centralized score management with level progression and achievement tracking
- `SpawningSystem` - Entity spawning coordination integrating all factory classes
- `PhysicsSystem` - Movement, boundaries, and collision detection for game physics

**Unified Input System**: Clean input architecture in `systems/input/`:
- `InputHandler` - Raw event processing with macOS screenshot interference handling
- `InputManager` - Event coordination and state management
- `InputFacade` - High-level input interface for game logic

**Factory Pattern**: Type-organized entity creation in `entities/`:
- `entities/enemies/` - `EnemyFactory` and `BossFactory` with difficulty scaling
- `entities/projectiles/` - `ProjectileFactory` for bullets and missiles
- `entities/items/` - `ItemFactory` for power-ups and collectibles
- `entities/player/` - Player and wingman entity management

**State Pattern**: Game states managed through `StateMachine` in `state/`:
- `GameState` - Base state class
- `PlayingState`, `PausedState`, `VictoryState`, `GameOverState`

**Single Responsibility**: Each system has clear boundaries:
- `systems/` - Core game systems (collision, scoring, spawning, physics, input)
- `entities/` - Type-organized game entities with base classes and factories
- `graphics/` - Rendering, UI components, visual effects
- `events/` - Event system and game event definitions
- `state/` - Game state management
- `localization/` - Multi-language support with loader abstraction
- `utils/` - Resource management, configuration, logging

### Key Systems

**Configuration System**: JSON-based configuration stored at `~/.thunder_fighter/config.json`. All gameplay parameters are configurable through `constants.py`.

**Resource Management**: Centralized asset loading with caching through `ResourceManager`. All game assets (images, sounds, fonts) are managed here.

**Pause System**: Dedicated `PauseManager` component provides testable pause functionality with pause-aware timing calculations, cooldown mechanisms, and comprehensive statistics tracking. Extracted from main game logic for better separation of concerns.

**Localization**: Multi-language support with dynamic switching and dependency injection. Language files in `localization/` directory. Features loader abstraction (`FileLanguageLoader`, `MemoryLanguageLoader`, `CachedLanguageLoader`) for enhanced testability. Optimized Chinese font rendering for macOS through `FontManager`.

**UI System**: Modular component-based UI in `graphics/ui/`:
- `HealthBarComponent` - Dynamic health displays
- `NotificationManager` - Game notifications (with clear/clear_all methods)
- `GameInfoDisplay` - Score and level information
- `BossStatusDisplay` - Boss health and combat modes (with reset method)
- `PlayerStatsDisplay` - Player statistics (with reset method)

**Background System**: Double-buffered dynamic backgrounds with smooth level transitions. Each level has unique visual themes.

**Game Features**: Victory system with final boss defeat, wingman companions (Level 3+), developer mode debugging, game over/restart functionality.

## Development Standards

### Code Style
- Use Ruff for formatting and linting (line length: 120)
- All functions/classes must have type annotations
- Follow Google Style docstrings
- Constants in UPPER_SNAKE_CASE in `constants.py`

### Language Requirements (MANDATORY)
- All code comments must be written in English
- All log messages must be written in English
- All git commit messages must be written in English
- All docstrings must be written in English
- This is a strict requirement - NO Chinese characters are allowed in comments, logs, or commit messages

### Testing Requirements
- Use pytest (not unittest) with configuration in pyproject.toml
- All test files in `tests/` directory with organized structure:
  - `tests/systems/` - Core systems architecture tests
  - `tests/events/` - Event system and communication tests
  - `tests/localization/` - Multi-language support tests
  - `tests/unit/` - Individual component unit tests
  - `tests/integration/` - Component interaction tests
  - `tests/e2e/` - End-to-end workflow tests
- Maintain test coverage above 90% for critical systems
- Mock external dependencies (pygame surfaces, sounds) 
- Use dependency injection for testable interfaces
- Follow interface-focused testing over implementation details

### Architecture Rules
- Components communicate through EventSystem
- Create entities through factory classes
- Use StateMachine for game state management
- Follow Single Responsibility Principle
- Pass dependencies through constructors
- Use dependency injection for better testability

### Performance Guidelines
- Use sprite groups for batch operations
- Implement object pooling for frequently created entities
- Profile performance-critical sections
- Use ResourceManager for asset caching

## File Structure

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
│   ├── en.json        # English translations
│   ├── zh.json        # Chinese translations
│   ├── loader.py      # Language loader interfaces
│   └── font_support.py # Font management for localization
├── utils/             # Utilities and configuration
│   └── pause_manager.py # Dedicated pause management
├── config.py          # Game configuration
├── constants.py       # Game constants
└── game.py           # Main game class
```

## Testing Architecture

The project has 357+ comprehensive tests organized by category:
- **Unit Tests (90+)**: Entity factories, individual components, pause system, localization, enemy entity tests
- **Integration Tests (9)**: Event system flow, component interactions
- **End-to-End Tests (9)**: Complete game flow scenarios
- **Systems Tests**: Core systems architecture validation and interface testing
- **Events Tests**: Event-driven architecture, listener management, event dispatch
- **Localization Tests**: Multi-language support, font management, language switching
- **Component Tests (246+)**: Sprites, graphics, utilities, state management, UI components

### Comprehensive Test Coverage
- **Systems Architecture Tests**: Complete testing framework for core game systems
  - **Collision System Tests**: Handler setup, interface validation, collision detection
  - **Scoring System Tests**: Score management, level progression, achievement tracking  
  - **Spawning System Tests**: Entity spawning coordination, factory integration
  - **Physics System Tests**: Movement, boundaries, physics simulation
- **Event System Tests**: Event-driven architecture validation, listener management, event dispatch
- **Localization System Tests**: Multi-language support, font management, language switching
- **PauseManager Tests (16)**: Comprehensive testing of pause functionality, timing calculations, and edge cases
- **Localization Tests (39)**: Complete coverage of loader abstraction, dependency injection, and language management
- **Boss Spawn Timing Tests (18)**: Specialized tests for boss generation interval calculations with pause handling
- **Enemy Entity Tests (8)**: Interface-focused testing of Enemy behavior and level progression
- **Factory Tests**: Comprehensive testing of all entity factories with proper import paths and mock validation
- **UI Component Tests**: Complete coverage of modular UI components with reset functionality

## Configuration

Game settings are managed through:
- **Modern Configuration**: Primary configuration in `pyproject.toml` for development tools (pytest, mypy, ruff)
- **Runtime Configuration**: Game settings via `config_tool.py`
- **Environment Variables**: THUNDER_FIGHTER_LOG_LEVEL for logging control
- **User Settings**: JSON configuration file at `~/.thunder_fighter/config.json`

Key configurable aspects:
- Sound and music volumes
- Difficulty settings  
- Display options (fullscreen, scaling)
- Debug mode and logging levels

## Recent Fixes & Important Notes

**Interface Testability Improvements**: Implemented Plan A improvements to enhance code testability:
- **PauseManager**: Extracted pause logic into dedicated `thunder_fighter/utils/pause_manager.py` with full dependency injection support
- **Localization System**: Enhanced with loader abstraction pattern featuring `FileLanguageLoader`, `MemoryLanguageLoader`, and `CachedLanguageLoader` for better testing
- **FontManager**: Integrated font management system in `thunder_fighter/localization/font_support.py` for proper language-specific font handling

**UI Component Reset Methods**: All UI components now have proper reset methods:
- `NotificationManager.clear_all()` - Clears all notifications (alias for clear())
- `PlayerStatsDisplay.reset()` - Resets player stats to initial values
- `BossStatusDisplay.reset()` - Resets boss status to initial values

**Virtual Environment**: Use `./venv/bin/python` for all commands on macOS to ensure correct Python environment.

**Game Restart**: The game properly handles restart functionality without crashes through UI manager's `reset_game_state()` method.

**macOS Screenshot Interference Fix**: The input system now includes hybrid processing with fallback mechanisms to handle macOS screenshot interference. When using `Shift+Cmd+5` with delayed capture, P (pause) and L (language) keys may trigger fallback processing but remain fully functional. The fix is implemented in `thunder_fighter/systems/input/handler.py` with `_process_single_event_with_fallback()` method. Use F1 key for manual input state reset if needed.

**Boss Spawn Timing Fix**: Fixed critical issue where boss generation intervals included pause time. Boss spawning now uses pause-aware timing calculations (`pause_manager.calculate_game_time()`) consistent with display time handling. The fix is implemented in `thunder_fighter/game.py:890-891` and includes comprehensive test coverage in `tests/unit/test_boss_spawn_timing.py` to prevent regression.

## Major Architecture Refactoring (Systems-Based Design)

**Complete Modular Refactoring**: Successfully implemented a comprehensive systems-based architecture refactoring that significantly improves code organization, maintainability, and testability.

### Refactoring Achievements

**Systems-Based Architecture Implementation**:
- **CollisionSystem**: Unified collision detection system in `thunder_fighter/systems/collision.py` with comprehensive compatibility functions
- **ScoringSystem**: Centralized score management in `thunder_fighter/systems/scoring.py` with Score alias for backward compatibility
- **SpawningSystem**: Entity spawning coordination in `thunder_fighter/systems/spawning.py` integrating all factory classes
- **PhysicsSystem**: Movement and physics management in `thunder_fighter/systems/physics.py`

**Enhanced Input System Refactoring**:
- **Layered Architecture**: Moved input system to `thunder_fighter/systems/input/` with handler→manager→facade pattern
- **InputHandler**: Raw event processing in `systems/input/handler.py` with macOS screenshot interference handling
- **InputManager**: Event coordination in `systems/input/manager.py`
- **InputFacade**: High-level interface in `systems/input/facade.py`

**Entity Organization by Type**:
- **Base Classes**: Created `thunder_fighter/entities/base.py` with GameObject, Entity, EntityFactory hierarchy
- **Type Organization**: Organized entities into `enemies/`, `projectiles/`, `items/`, `player/` subdirectories
- **Factory Integration**: Enhanced factory classes with type-specific organization and configuration presets

**Graphics Module Optimization**:
- **Effects System**: Organized visual effects in `thunder_fighter/graphics/effects/` with particle system
- **UI Components**: Maintained modular UI architecture in `thunder_fighter/graphics/ui/`

**Import Path Automation**:
- **Automated Migration**: Created `scripts/update_imports.py` to update 30+ files with new import mappings
- **Backward Compatibility**: Ensured all existing interfaces remain functional during transition

### Testing Improvements

**Comprehensive Test Refactoring**:
- **Factory Tests**: Fixed all entity factory tests with correct import paths (Enemy/Boss factories fully operational)
- **Collision System Tests**: Updated all collision detection tests for systems-based architecture (14 tests passing)
- **New Entity Tests**: Created `tests/unit/entities/test_enemy_entity.py` with 8 interface-focused tests
- **Test Migration**: Successfully migrated from implementation-detail tests to interface-focused testing

**Test Quality Improvements**:
- **354 Tests Passing**: All tests operational after refactoring with comprehensive coverage
- **Interface Testing**: New tests focus on behavior and public interfaces rather than implementation details
- **Backward Compatibility**: Maintained existing test functionality while improving architecture

### Runtime Fixes

**Flash Manager Fix**: Resolved critical runtime error `'Notification' object has no attribute 'update'` by implementing proper FlashEffectManager fallback in `thunder_fighter/graphics/effects/__init__.py`

**Game Functionality**: Verified complete game functionality post-refactoring:
- ✅ Game starts and runs without errors
- ✅ All systems integrate properly
- ✅ Score system functions correctly
- ✅ Input handling works as expected
- ✅ All architectural improvements are operational

### Code Quality Impact

**Maintainability**: Dramatically improved code organization with clear separation of concerns and modular design
**Testability**: Enhanced testability through dependency injection and interface-focused design
**Extensibility**: New systems-based architecture allows easy addition of new game features
**Performance**: Maintained performance while improving code structure

## Circular Import Elimination (Latest Update)

**Major Architectural Debt Cleanup**: Successfully eliminated all circular import risks and architectural debt through comprehensive refactoring.

### Problems Addressed

**Critical Issues Fixed**:
- **Duplicate Factory Files**: Removed 4 sets of duplicate factory files (boss_factory.py, enemy_factory.py, item_factory.py, projectile_factory.py) from entities/ top level
- **Dual Input Systems**: Eliminated conflicting input systems by removing thunder_fighter/input/ directory completely
- **Complex Import Hierarchies**: Simplified entities/__init__.py from 60 lines to 36 lines, removing 30+ unnecessary imports
- **Effects Module Circular Imports**: Resolved AchievementNotification position attribute error by restructuring graphics/effects

### Solutions Implemented

**Factory Organization**:
- **Unified Location**: All factories now located in type-specific subdirectories (entities/enemies/, entities/items/, entities/projectiles/)
- **Single Source of Truth**: Eliminated duplicate implementations with different import paths
- **Clean Dependencies**: Factory imports follow consistent ../ relative import patterns

**Input System Consolidation**:
- **Systems-Only Architecture**: Removed old thunder_fighter/input/ system completely
- **Unified Interface**: All input processing now uses systems/input/ with consistent API
- **No Naming Conflicts**: Eliminated duplicate class names (InputManager, InputHandler) across packages

**Effects Module Restructuring**:
- **Modular Design**: Split monolithic effects.py into focused modules:
  - `notifications.py` - Complete notification system with position attributes
  - `explosions.py` - Explosion and hit effect functions  
  - `flash_effects.py` - Flash effect management system
- **Eliminated Fallback Classes**: Removed incomplete fallback notification classes that caused AttributeError

### Impact and Verification

**Quantified Results**:
- **Files Removed**: 19 duplicate/obsolete files
- **Code Reduction**: 3,820 lines of duplicate code eliminated
- **Import Simplification**: 40% reduction in import complexity
- **Zero Regressions**: All 357 tests continue to pass
- **Runtime Verification**: Game starts and runs normally

**Risk Mitigation**:
- **Circular Import Prevention**: Systematic elimination of import patterns that could cause runtime errors
- **Architecture Clarity**: Clear module boundaries and responsibilities
- **Maintenance Reduction**: Single implementations eliminate synchronization overhead

**Future Proofing**:
- **Clean Architecture**: Consistent patterns reduce likelihood of future circular imports
- **Modular Design**: Clear separation of concerns makes dependencies explicit
- **Test Coverage**: Comprehensive tests prevent regression of import issues

## Latest Project Structure Optimization (Post-Refactoring)

**Comprehensive Structure Analysis and Cleanup**: Following the major architecture refactoring, conducted comprehensive analysis and optimization of the entire project structure including test code, demo code, and configuration files.

### Structure Analysis Achievements

**File and Directory Analysis**:
- **Complete Project Scan**: Analyzed all files including main code, tests, demos, and configuration
- **Naming Convention Validation**: Verified consistent naming patterns across all modules
- **Architecture Alignment**: Ensured test structure matches new systems-based architecture

**Problem Identification and Resolution**:
- **Duplicate File Elimination**: Removed additional 8+ duplicate files (stars.py, UI components, demo files)
- **Obsolete Code Cleanup**: Deleted demo file with Chinese comments violating language requirements
- **Cache File Cleanup**: Removed 115 __pycache__ directories with 848 .pyc files
- **Configuration Redundancy**: Eliminated outdated pytest.ini, unified configuration in pyproject.toml

### Testing Infrastructure Enhancement

**Test Architecture Completion**:
- **New Test Directories**: Created tests/systems/, tests/events/, tests/localization/
- **Framework Templates**: Established testing patterns for all core systems
- **Interface-Focused Testing**: Aligned tests with actual system interfaces and capabilities
- **Coverage Expansion**: Added testing support for systems architecture, event system, and localization

**Configuration Modernization**:
- **pyproject.toml Optimization**: Centralized all development tool configuration
- **Pytest Configuration**: Streamlined test execution configuration
- **.gitignore Standardization**: Updated to Python community best practices

### Code Quality Improvements

**Language Compliance**: 
- **English-Only Enforcement**: Removed all Chinese comments and violations
- **Documentation Standards**: Ensured all code adheres to mandatory English requirements

**Development Infrastructure**:
- **Modern Python Standards**: Adopted contemporary Python project structure
- **Configuration Unification**: Single source of truth for all development settings
- **Test Organization**: Clear separation of test types and responsibilities

**Maintenance Impact**:
- **Total Files Cleaned**: 20+ files removed (duplicates, obsolete demos, cache files)
- **Configuration Simplified**: Single configuration source in pyproject.toml
- **Test Coverage Enhanced**: Complete testing framework for all architectural components
- **Development Workflow**: Streamlined development and testing processes