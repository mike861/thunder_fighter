# CLAUDE.md (Streamlined Version)

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Game
```bash
python main.py
# OR on macOS with virtual environment:
./venv/bin/python main.py
```

### Testing
```bash
# Run all tests (375 comprehensive tests)
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
# Lint and format (Python 3.7+ compatible)
ruff check .
ruff format .

# Auto-fix safe issues
ruff check --fix .

# Type checking
mypy thunder_fighter/
```

### Development Dependencies
```bash
# Install development dependencies
pip install -e .[dev]
```

## Quick Architecture Reference

Thunder Fighter is a vertical scrolling space shooter built with Pygame using modern architecture patterns:

### Core Design Patterns
- **Event-Driven Architecture**: Game components communicate through `EventSystem` in `events/game_events.py`
- **Systems-Based Architecture**: Core game logic organized into dedicated systems in `systems/`
- **Factory Pattern**: Type-organized entity creation in `entities/`
- **State Pattern**: Game states managed through `StateMachine` in `state/`

### Key Systems Overview
- **CollisionSystem** - Unified collision detection and resolution
- **ScoringSystem** - Centralized score management with level progression
- **SpawningSystem** - Entity spawning coordination integrating all factory classes
- **PhysicsSystem** - Movement, boundaries, and collision detection
- **InputSystem** - Clean input architecture with macOS screenshot interference handling
- **PauseManager** - Dedicated pause management with pause-aware timing
- **Localization** - Multi-language support with dynamic switching

For detailed architecture information, see [Architecture Guide](docs/ARCHITECTURE.md) and [code organization](docs/ARCHITECTURE.md#code-organization).

## Development Standards

### Code Style
- Use Ruff for formatting and linting (line length: 120, Python 3.7+ compatible)
- Configuration follows modern `[tool.ruff.lint]` section in `pyproject.toml`
- No walrus operator (`:=`) - use compatible assignment syntax for Python 3.7
- Specific imports only - no star imports (`from module import *`)
- All functions/classes must have type annotations
- Follow Google Style docstrings
- Constants in UPPER_SNAKE_CASE in `constants.py`
- Proper exception handling with `except Exception:` (no bare `except:`)

### Language Requirements (MANDATORY)
- All code comments must be written in English
- All log messages must be written in English
- All git commit messages must be written in English
- All docstrings must be written in English
- This is a strict requirement - NO Chinese characters are allowed in comments, logs, or commit messages

### Testing Requirements
- Use pytest (not unittest) with configuration in pyproject.toml
- All test files in `tests/` directory with organized structure
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

## Testing Quick Guide

The project has 375 comprehensive tests organized by category:
- **Unit Tests (90+)**: Entity factories, individual components
- **Integration Tests (9)**: Event system flow, component interactions
- **End-to-End Tests (9)**: Complete game flow scenarios
- **Systems Tests**: Core systems architecture validation
- **Events Tests**: Event-driven architecture testing
- **Localization Tests**: Multi-language support testing

For detailed test structure, see test files in organized directories under `tests/`.

## Documentation Structure

- **README.md** - Main project overview and quick start guide
- **[GAME_MECHANICS.md](docs/GAME_MECHANICS.md)** - Pure game mechanics guide (victory, boss, items systems)
- **[TECHNICAL_DETAILS.md](docs/TECHNICAL_DETAILS.md)** - Technical implementations and platform-specific optimizations
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture, design patterns, and detailed code organization
- **[DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md)** - Development planning and implementation roadmap

## Important Notes

### Critical Fixes & Platform-Specific Issues

**Virtual Environment**: Use `./venv/bin/python` for all commands on macOS to ensure correct Python environment.

**macOS Screenshot Interference Fix**: The input system includes hybrid processing with fallback mechanisms to handle macOS screenshot interference. When using `Shift+Cmd+5` with delayed capture, P (pause) and L (language) keys may trigger fallback processing but remain fully functional. The fix is implemented in `thunder_fighter/systems/input/handler.py` with `_process_single_event_with_fallback()` method. Use F1 key for manual input state reset if needed.

**Boss Spawn Timing Fix**: Fixed critical issue where boss generation intervals included pause time. Boss spawning now uses pause-aware timing calculations (`pause_manager.calculate_game_time()`) consistent with display time handling. The fix is implemented in `thunder_fighter/game.py:890-891`.

### UI Component Methods
All UI components have proper reset methods:
- `NotificationManager.clear_all()` - Clears all notifications
- `PlayerStatsDisplay.reset()` - Resets player stats to initial values
- `BossStatusDisplay.reset()` - Resets boss status to initial values

### Game Restart
The game properly handles restart functionality without crashes through UI manager's `reset_game_state()` method.

### Code Quality Status
- **All 375 tests passing** with zero regressions
- **Python 3.7 Compatibility**: Full compatibility maintained
- **Clean Architecture**: Eliminated all circular import risks
- **Modern Configuration**: All tools configured via `pyproject.toml`

---

*For comprehensive technical details, see the dedicated documentation files linked above. This streamlined guide focuses on essential development information for Claude Code.*