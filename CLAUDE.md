# CLAUDE.md (Streamlined Version)

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**IMPORTANT**: When updating documentation, follow the **Documentation Update Guidelines** section below to ensure proper content placement and appropriate detail levels for each document type.

## Commands

### Running the Game
```bash
python main.py
# OR on macOS with virtual environment:
./venv/bin/python main.py
```

### Testing
```bash
# Run all tests (390+ comprehensive tests)
./venv/bin/python -m pytest tests/ -v

# Run specific test categories
./venv/bin/python -m pytest tests/integration/ -v    # Integration tests
./venv/bin/python -m pytest tests/unit/ -v          # Unit tests
./venv/bin/python -m pytest tests/e2e/ -v           # End-to-end tests

# Test coverage
./venv/bin/python -m pytest tests/ --cov=thunder_fighter --cov-report=html
```

For comprehensive testing documentation, see **[Testing Guide](docs/TESTING_GUIDE.md)**.

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

### Continuous Integration
```bash
# The project uses GitHub Actions for CI/CD with the following checks:
# - Code linting and formatting (Ruff)
# - Type checking (MyPy)
# - Test execution with coverage reporting
# - Build verification
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

### Project Philosophy
**Thunder Fighter prioritizes code quality and interface design over backward compatibility. We embrace refactoring legacy code to meet modern standards rather than working around technical debt.**

### Code Style
- Use Ruff for formatting and linting (line length: 120, Python 3.7+ compatible)
- Configuration follows modern `[tool.ruff.lint]` section in `pyproject.toml`
- No walrus operator (`:=`) - use compatible assignment syntax for Python 3.7
- Specific imports only - no star imports (`from module import *`)
- All functions/classes must have type annotations
- Follow Google Style docstrings
- Constants in UPPER_SNAKE_CASE in `constants.py`
- Proper exception handling with `except Exception:` (no bare `except:`)

### Type Safety Requirements
- **MyPy Configuration**: Project configured to suppress low-priority type errors while maintaining core type safety
- **Critical Type Errors Only**: Focus on errors that could cause runtime crashes or logical issues
- **Suppressed Error Categories** (via `pyproject.toml`):
  - `assignment` - None assignment compatibility issues
  - `no-any-return` - Any return type warnings
  - `arg-type` - Argument type compatibility warnings
  - `union-attr` - Union type attribute access warnings
  - `index` - Index type compatibility issues
  - `call-overload` - Overload call compatibility issues
  - `operator` - Operator type compatibility issues
  - `misc` - Miscellaneous type issues
  - `attr-defined` - Object attribute access warnings
  - `var-annotated` - Variable annotation requirements
  - `syntax` - Syntax issues in legacy code

### Type Annotation Best Practices
- **Optional Types**: Use `Optional[Type]` for parameters that can be None
- **Union Types**: Properly handle union types with None checks before attribute access
- **Event System**: Ensure `GameEventType` inherits from `EventType` for type hierarchy
- **GameEvent Construction**: Design clean interfaces for new code, refactor legacy compatibility patterns
- **Class Methods**: Always use keyword arguments for `source` parameter in event factory methods
- **Variable Annotations**: Add type annotations for dynamically created attributes to avoid `has-type` errors
- **Interface Design**: Prioritize type-safe, intuitive interfaces over maintaining legacy compatibility

### MyPy Error Resolution Guidelines
When fixing MyPy type errors, follow these principles:
- **Fix Root Causes**: Address the underlying type issues rather than suppressing errors
- **Optional Parameter Defaults**: Use `Optional[Type] = None` instead of `Type = None` for parameters
- **Assignment Type Safety**: 
  - Initialize variables with correct types (e.g., `0.0` for float variables, not `0`)
  - Use proper type conversions when assigning calculated values to variables
  - Add None checks before dictionary/object access: `if obj is not None: obj[key] = value`
- **Dict Value Type Safety**: 
  - Use `theme.get("key", default)` instead of `theme["key"]` for safer access
  - Apply type conversion with isinstance checks: `int(val) if isinstance(val, (int, float, str)) else default`
- **Variable Redefinition**: Avoid redefining variables with different types in the same scope
- **Import Requirements**: Always import required types (`Optional`, `Union`, etc.) when using them
- **Assertion-Based Type Narrowing**: Use assertions to help MyPy understand None checks in control flow
- **Type Ignore Usage**: Use `# type: ignore` sparingly and only when type conversion logic is complex but sound

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
- **Strategic Testing Approach**: Choose testing strategy based on component type
- Use dependency injection for testable interfaces
- Follow interface-focused testing over implementation details

### Testing Strategy Selection (CRITICAL)

**Before writing any test, determine the appropriate strategy:**

#### 70% - Lightweight Mock Strategy
**Use for**: Event systems, configuration, utilities, factory patterns, pure logic
```python
# ✅ Pattern: Mock external dependencies, use real business objects
def setup_method(self):
    self.event_system = EventSystem()  # Real object
    self.mock_listener = MagicMock()    # Mock external dependency
```

#### 20% - Heavy Mock Strategy  
**Use for**: Player combat, sprite groups, collision detection, pygame integrations
```python
# ✅ Pattern: Real pygame objects for integration testing
def setup_method(self):
    pygame.init()
    pygame.display.set_mode((1, 1))
    self.all_sprites = pygame.sprite.Group()  # Real Group
    self.screen = pygame.Surface((800, 600))   # Real Surface
```

#### 10% - Mixed Strategy
**Use for**: Performance testing, algorithms with performance requirements
```python
# ✅ Pattern: Separate algorithm and performance tests
def test_algorithm_logic(self):    # Lightweight for correctness
def test_performance_real(self):   # Heavy mock for performance
```

**Strategy Selection Matrix**:
- **Event System, Config, Utils** → Lightweight Mock
- **Player Combat, Sprite Groups** → Heavy Mock  
- **Collision System, Physics** → Mixed Strategy
- **UI Rendering** → Heavy Mock
- **Factory Patterns** → Lightweight Mock

For detailed testing guidelines, patterns, and best practices, see **[Testing Guide](docs/TESTING_GUIDE.md)**.

### Architecture Rules
- Components communicate through EventSystem
- Create entities through factory classes
- Use StateMachine for game state management
- Follow Single Responsibility Principle
- Pass dependencies through constructors
- Use dependency injection for better testability

### Core Interface Design Principles (CRITICAL)

**Primary Guidelines for All Interface Design Decisions:**

#### 1. **Interface Quality First Principle** 🎯
- **No Backward Compatibility Constraints**: Since this project has no inter-service communication, interface quality takes absolute priority over compatibility
- **Clean Interface Design**: Always design the most logical, intuitive, and maintainable interface possible
- **Technical Debt Reduction**: Actively eliminate poorly designed interfaces rather than working around them
- **Breaking Changes Encouraged**: Prefer clean, well-designed interfaces over maintaining compatibility with technical debt

#### 2. **Logic/Interface Separation Principle** 🎯
- **Pure Business Logic**: Business logic classes must not depend on graphics, UI, or I/O systems
- **Dependency Direction**: Graphics/UI adapters depend on business logic, never the reverse
- **Testable Logic**: All algorithms and business logic must be testable without external dependencies
- **Injectable Dependencies**: Use dependency injection for graphics, file I/O, and external system interactions

**Interface Design Decision Matrix:**
```
Option A: Clean interface (requires refactoring)  ✅ CHOOSE THIS
Option B: Maintain legacy compatibility           ❌ AVOID THIS
```

### Design Philosophy & Technical Debt Management
- **Interface-First Design**: Prioritize clean, well-designed interfaces for all new code
- **Technical Debt Cleanup**: Actively refactor and clean up existing code rather than maintaining backward compatibility
- **Legacy Code Approach**: When encountering legacy code, refactor it to meet current standards instead of working around it
- **Breaking Changes Acceptable**: Prefer clean, modern interfaces over maintaining compatibility with poorly designed legacy code
- **Proactive Refactoring**: Continuously improve code quality by eliminating technical debt
- **Modern Patterns**: Always use current best practices for new implementations, even if it requires updating related legacy code

### Performance Guidelines
- Use sprite groups for batch operations
- Implement object pooling for frequently created entities
- Profile performance-critical sections
- Use ResourceManager for asset caching

## Testing Quick Guide

The project has 390+ comprehensive tests organized by category:
- **Unit Tests (90+)**: Entity factories, individual components
- **Integration Tests (9)**: Event system flow, component interactions
- **End-to-End Tests (9)**: Complete game flow scenarios
- **Systems Tests**: Core systems architecture validation
- **Events Tests**: Event-driven architecture testing
- **Localization Tests**: Multi-language support testing

For detailed test structure, patterns, and comprehensive testing documentation, see **[Testing Guide](docs/TESTING_GUIDE.md)**.

## Documentation Structure

- **README.md** - Main project overview and quick start guide
- **[GAME_MECHANICS.md](docs/GAME_MECHANICS.md)** - Pure game mechanics guide (victory, boss, items systems)
- **[TECHNICAL_DETAILS.md](docs/TECHNICAL_DETAILS.md)** - Technical implementations and platform-specific optimizations
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture, design patterns, and detailed code organization
- **[TESTING_GUIDE.md](docs/TESTING_GUIDE.md)** - Comprehensive testing guide, patterns, and best practices
- **[CI_CD_GUIDE.md](docs/CI_CD_GUIDE.md)** - Comprehensive CI/CD pipeline documentation and best practices
- **[DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md)** - Development planning and implementation roadmap

## Documentation Update Guidelines (CRITICAL)

### Document Positioning Matrix

Each document has a specific purpose and content depth. **ALWAYS** respect these boundaries:

| Document | Purpose | Content Depth | Code Examples |
|----------|---------|---------------|---------------|
| **ARCHITECTURE.md** | High-level system overview | Conceptual only | Max 5 lines |
| **TECHNICAL_DETAILS.md** | Implementation strategies | Core algorithms | 10-15 lines + file references |
| **TESTING_GUIDE.md** | Test strategies & statistics | Test patterns | Full test examples |
| **Source Code** | Complete implementation | Full details | Complete classes |

### Content Depth Control

**Three-Layer Depth Model**:
1. **Concept Layer (ARCHITECTURE)**: Design patterns, component relationships, system interactions
2. **Technical Layer (TECHNICAL_DETAILS)**: Algorithm concepts, implementation references, performance data
3. **Implementation Layer (Source Code)**: Full code, detailed algorithms, complete tests

### Documentation Update Rules

**ALWAYS Include**:
- Clear section headings matching document purpose
- File path references for detailed implementations (e.g., `thunder_fighter/entities/projectiles/logic.py:15-45`)
- Appropriate depth of technical detail for the document type
- Cross-references to related documentation when needed

**NEVER Include**:
- Complete class implementations in ARCHITECTURE.md
- Duplicate detailed code across multiple documents
- Performance statistics in ARCHITECTURE.md (use TECHNICAL_DETAILS.md)
- Test statistics outside of TESTING_GUIDE.md
- Excessive adjectives like "Revolutionary" or "Game-changing"

### Pre-Update Checklist

Before updating any documentation, verify:
- [ ] Content matches the document's core purpose
- [ ] Code examples respect the line limit for that document type
- [ ] No duplication of content that belongs in another document
- [ ] Implementation details use file references instead of full code
- [ ] Technical depth is appropriate for the target audience

### Example Update Patterns

**Good ARCHITECTURE.md Update**:
```markdown
### Enhanced Entity System
The projectile system now implements logic/interface separation for improved testability.
See `entities/projectiles/logic.py` for implementation details.
```

**Good TECHNICAL_DETAILS.md Update**:
```python
# Core algorithm concept (10 lines max)
class BulletLogic:
    def update_position(self):
        # Pre-calculated vectors for performance
        self.x += self.speed_x
        self.y += self.speed_y
        
# Full implementation: thunder_fighter/entities/projectiles/logic.py:25-45
```

**Bad Documentation Update** (avoid):
```markdown
# 50+ lines of complete implementation in ARCHITECTURE.md ❌
# Duplicate code in multiple documents ❌
# Missing file path references ❌
```

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
- **All 390 tests passing** with zero regressions
- **Python 3.7 Compatibility**: Full compatibility maintained
- **Clean Architecture**: Eliminated all circular import risks
- **Modern Configuration**: All tools configured via `pyproject.toml`
- **Type Safety**: MyPy errors reduced from 107 to 0 through strategic configuration
- **Event System**: Fixed Enum inheritance issues and GameEvent construction compatibility
- **Technical Debt**: Actively cleaned up legacy code patterns and improved interface design
- **Refactoring Culture**: Established pattern of improving code quality over maintaining backward compatibility

---

*For comprehensive technical details, see the dedicated documentation files linked above. This streamlined guide focuses on essential development information for Claude Code.*