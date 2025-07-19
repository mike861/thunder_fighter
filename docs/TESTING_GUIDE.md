# Thunder Fighter Testing Guide

## Overview

This guide provides comprehensive information about testing in Thunder Fighter, including test structure, best practices, and guidance for adding new tests. The project maintains 390+ comprehensive tests ensuring code quality and functionality reliability.

## Table of Contents

1. [Test Architecture](#test-architecture)
2. [Test Categories](#test-categories)
3. [Running Tests](#running-tests)
4. [Writing New Tests](#writing-new-tests)
5. [Test Coverage Analysis](#test-coverage-analysis)
6. [Testing Best Practices](#testing-best-practices)
7. [Specialized Test Suites](#specialized-test-suites)
8. [Common Testing Patterns](#common-testing-patterns)
9. [Testing Gaps and Priorities](#testing-gaps-and-priorities)
10. [Performance and Benchmarking](#performance-and-benchmarking)

## Test Architecture

### Test Structure

Thunder Fighter uses a hierarchical test structure that separates concerns:

```
tests/
├── e2e/                     # End-to-End Tests (9 tests)
│   └── test_game_flow.py    # Complete game flow scenarios
├── integration/             # Integration Tests (9 tests)
│   └── test_event_flow.py   # System interaction tests
├── unit/                    # Unit Tests (70+ tests)
│   ├── entities/            # Entity factory tests
│   ├── test_pause_system.py # Pause functionality tests
│   └── test_*.py            # Individual component tests
├── sprites/                 # Game Object Tests (27 tests)
│   ├── test_player.py       # Player behavior tests
│   ├── test_enemy.py        # Enemy behavior tests
│   ├── test_boss.py         # Boss mechanics tests
│   └── test_items.py        # Item system tests
├── graphics/                # Visual Component Tests (80 tests)
│   ├── test_ui_components.py # UI component tests
│   ├── test_renderers.py    # Rendering system tests
│   └── test_background.py   # Background system tests
├── utils/                   # Utility Tests (43 tests)
│   ├── test_resource_manager.py
│   ├── test_config_manager.py
│   └── test_collisions.py
└── state/                   # State Management Tests (40 tests)
    ├── test_state_machine.py
    └── test_game_state.py
```

### Test Distribution

| Category | Test Count | Coverage Focus |
|----------|------------|----------------|
| Graphics | 80 (30.8%) | UI components, rendering |
| Utils | 43 (16.5%) | Resource management, configuration |
| State | 40 (15.4%) | State machines, game flow |
| Sprites | 27 (10.4%) | Game object behavior |
| Unit/Entities | 27 (10.4%) | Factory patterns, entity creation |
| E2E | 9 (3.5%) | Complete workflows |
| Integration | 9 (3.5%) | System interactions |

## Test Categories

### End-to-End Tests

**Purpose**: Validate complete game workflows and system integration.

**Key Test Areas**:
- Game initialization and component setup
- Level progression logic
- Boss defeat handling
- Item collection mechanics
- Player death scenarios
- Resource management integration

**Example Test Pattern**:
```python
def test_complete_game_flow():
    """Test complete game flow from start to boss defeat."""
    game = initialize_test_game()
    
    # Verify initialization
    assert game.is_initialized()
    
    # Simulate gameplay progression
    game.advance_to_level(2)
    assert game.current_level == 2
    
    # Test boss spawning and defeat
    boss = game.spawn_boss()
    game.defeat_boss(boss)
    
    # Verify state transitions
    assert game.current_level == 3
```

### Integration Tests

**Purpose**: Test interactions between different systems and components.

**Key Focus Areas**:
- Event system propagation
- Component interaction workflows
- Error handling across systems
- State synchronization between components

**Example Test Pattern**:
```python
def test_event_system_integration():
    """Test event propagation through multiple systems."""
    event_system = EventSystem()
    
    # Register multiple listeners
    collision_system = Mock()
    scoring_system = Mock()
    
    event_system.register(collision_system, EventType.ENEMY_DEFEATED)
    event_system.register(scoring_system, EventType.ENEMY_DEFEATED)
    
    # Dispatch event and verify propagation
    event = EnemyDefeatedEvent(enemy_id=123, points=100)
    event_system.dispatch(event)
    
    collision_system.handle.assert_called_once_with(event)
    scoring_system.handle.assert_called_once_with(event)
```

### Unit Tests

**Purpose**: Test individual components and functions in isolation.

**Key Areas**:
- Entity factories and creation logic
- Individual system components
- Utility functions and helper classes
- Configuration management

**Example Test Pattern**:
```python
def test_enemy_factory_creation():
    """Test enemy factory creates enemies with correct properties."""
    factory = EnemyFactory()
    
    enemy = factory.create_enemy(level=3, game_time=10)
    
    assert enemy.level == 3
    assert enemy.can_shoot == (enemy.level >= ENEMY_SHOOT_LEVEL)
    assert enemy.speed > 0
    assert hasattr(enemy, 'image')
    assert hasattr(enemy, 'rect')
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
./venv/bin/python -m pytest tests/ -v

# Run specific test categories
./venv/bin/python -m pytest tests/unit/ -v          # Unit tests
./venv/bin/python -m pytest tests/integration/ -v   # Integration tests
./venv/bin/python -m pytest tests/e2e/ -v          # End-to-end tests

# Run tests with coverage reporting
./venv/bin/python -m pytest tests/ --cov=thunder_fighter --cov-report=html
```

### Test Filtering and Selection

```bash
# Run tests matching a pattern
./venv/bin/python -m pytest tests/ -k "test_enemy" -v

# Run tests in a specific file
./venv/bin/python -m pytest tests/sprites/test_player.py -v

# Run tests with specific markers
./venv/bin/python -m pytest tests/ -m "slow" -v

# Run failed tests only
./venv/bin/python -m pytest tests/ --lf
```

### Test Configuration

Tests are configured via `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --strict-markers"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "e2e: marks tests as end-to-end tests"
]
filterwarnings = [
    # Ignore pygame's pkg_resources deprecation warning
    "ignore:pkg_resources is deprecated:UserWarning:pygame.pkgdata",
]
```

### Technical Testing Implementation

**SDL Headless Mode**: Tests run without display requirements using dummy drivers:
```bash
# Environment variables for headless testing
SDL_VIDEODRIVER=dummy
SDL_AUDIODRIVER=dummy
```

**Mock Dependencies**: Comprehensive mocking strategy for external dependencies:
- **Pygame surfaces and audio**: Mocked to prevent hardware dependencies
- **File I/O operations**: Mocked for deterministic test behavior
- **Time-dependent functions**: Controlled timing for consistent test results

**Interface-Focused Testing Philosophy**:
- Test public APIs rather than implementation details
- Use dependency injection for testable interfaces
- Focus on behavior verification over internal state checking

## Writing New Tests

### Test File Organization

**File Naming Convention**:
- Unit tests: `test_<component_name>.py`
- Integration tests: `test_<system>_integration.py`
- E2E tests: `test_<workflow>_flow.py`

**Class Naming Convention**:
- Test classes: `Test<ComponentName>`
- Test methods: `test_<specific_behavior>`

### Test Structure Template

```python
"""
Tests for <Component Name>.

Description of what this test module covers and any special considerations.
"""

from unittest.mock import MagicMock, patch
import pytest

from thunder_fighter.<module> import <Component>


class Test<ComponentName>:
    """Test the <Component> class."""

    def setup_method(self):
        """Set up test environment before each test method."""
        self.component = <Component>()
        # Initialize any required mocks or test data

    def test_initialization(self):
        """Test component initializes with correct default values."""
        # Test basic initialization
        assert self.component.is_initialized()
        
    def test_core_functionality(self):
        """Test the main functionality of the component."""
        # Test primary use cases
        result = self.component.main_method()
        assert result is not None
        
    def test_error_handling(self):
        """Test component handles errors gracefully."""
        # Test error conditions
        with pytest.raises(ValueError):
            self.component.invalid_operation()
            
    def test_edge_cases(self):
        """Test component behavior at boundaries."""
        # Test boundary conditions
        pass
```

### Mocking Guidelines

**Use Real Objects When Possible**:
```python
# Preferred: Use real lightweight objects
def test_with_real_objects():
    event_system = EventSystem()
    event = PlayerMovedEvent(x=100, y=200)
    # Test with actual objects
```

**Mock External Dependencies**:
```python
# Mock external systems (pygame, file I/O, network)
@patch('pygame.sprite.Sprite.__init__')
def test_sprite_creation(self, mock_sprite_init):
    mock_sprite_init.return_value = None
    sprite = EnemySprite()
    # Test sprite creation logic
```

**Mock Interface Boundaries**:
```python
# Mock at system boundaries
def test_resource_loading():
    with patch('thunder_fighter.utils.resource_manager.load_image') as mock_load:
        mock_load.return_value = Mock()
        # Test resource management logic
```

## Test Coverage Analysis

### Current Coverage Status

| Module | Current Coverage | Target Coverage |
|--------|------------------|-----------------|
| Core Game Logic | ~85% | 90% |
| UI Components | ~90% | 95% |
| Utility Classes | ~95% | 95% |
| Input System | ~40% | 85% |
| Event System | ~75% | 85% |
| **Overall** | ~75% | >85% |

### Coverage Commands

```bash
# Generate coverage report
./venv/bin/python -m pytest tests/ --cov=thunder_fighter

# Generate HTML coverage report
./venv/bin/python -m pytest tests/ --cov=thunder_fighter --cov-report=html

# View coverage in terminal with missing lines
./venv/bin/python -m pytest tests/ --cov=thunder_fighter --cov-report=term-missing

# Check coverage for specific module
./venv/bin/python -m pytest tests/ --cov=thunder_fighter.systems --cov-report=term
```

## Testing Best Practices

### Interface-Focused Testing

**Test Public APIs, Not Implementation**:
```python
# Good: Test public interface
def test_player_takes_damage():
    player = Player()
    initial_health = player.health
    
    player.take_damage(10)
    
    assert player.health == initial_health - 10

# Avoid: Testing private methods
def test_private_method():
    player = Player()
    # Don't test player._update_internal_state()
```

### Test Independence

**Each Test Should Be Isolated**:
```python
class TestPlayer:
    def setup_method(self):
        """Create fresh instance for each test."""
        self.player = Player()
        
    def test_shooting(self):
        """Test doesn't depend on other tests."""
        bullets = self.player.shoot()
        assert len(bullets) > 0
        
    def test_movement(self):
        """Independent test with own setup."""
        self.player.move(10, 0)
        assert self.player.rect.x == 10
```

### Clear Test Descriptions

**Use Descriptive Test Names**:
```python
# Good: Clear intent
def test_enemy_shoots_when_level_above_threshold():
    """Test enemy can shoot when level >= SHOOT_LEVEL."""
    
def test_player_loses_wingman_when_taking_damage():
    """Test wingman is destroyed before player health decreases."""

# Avoid: Vague names
def test_enemy_behavior():
def test_player_stuff():
```

### Test Data Management

**Use Realistic Test Data**:
```python
# Good: Use constants from the game
def test_boss_spawning():
    game_level = 2  # Bosses spawn from level 2
    spawn_interval = BOSS_SPAWN_INTERVAL
    
# Create test data that matches game reality
TEST_ENEMY_CONFIGS = {
    'level_0': {'can_shoot': False, 'speed': 2},
    'level_3': {'can_shoot': True, 'speed': 4},
}
```

## Specialized Test Suites

### Pause System Testing (16 tests)

**Key Test Areas**:
- **Pause-aware timing calculations**: Game time correctly excludes pause duration
- **State synchronization during pause/resume**: Consistent state across all game components
- **Multiple pause/resume cycles**: Handles repeated pause/resume operations correctly
- **Edge cases and error handling**: Rapid toggling, negative time prevention, malformed state recovery
- **Statistics tracking**: PauseStats dataclass provides complete pause session information
- **Dependency injection**: Clean interface with injectable timing dependencies for testability

**Example Test Pattern**:
```python
def test_pause_aware_timing_calculation():
    """Test game time correctly excludes pause duration."""
    pause_manager = PauseManager()
    start_time = time.time()
    
    # Simulate 10 seconds of gameplay
    with patch('time.time', return_value=start_time + 10):
        elapsed = pause_manager.calculate_game_time(start_time)
        assert elapsed == 10
    
    # Pause for 20 seconds
    pause_manager.pause()
    with patch('time.time', return_value=start_time + 30):
        elapsed = pause_manager.calculate_game_time(start_time)
        assert elapsed == 10  # No time added during pause
    
    # Resume and add 15 more seconds
    pause_manager.resume()
    with patch('time.time', return_value=start_time + 45):
        elapsed = pause_manager.calculate_game_time(start_time)
        assert elapsed == 25  # 10 + 15, excluding 20 seconds pause
```

### Input System Testing

**Key Test Areas**:
- Fallback mechanism for macOS screenshot interference
- Key binding and remapping
- Input state synchronization
- F1 reset functionality

**Example Test Pattern**:
```python
def test_input_fallback_mechanism():
    """Test input fallback when normal processing fails."""
    handler = InputHandler()
    
    # Mock a scenario where normal processing fails
    with patch.object(handler, '_process_normal', side_effect=Exception):
        # Simulate P key press
        pygame_event = create_mock_keydown_event(pygame.K_p)
        
        events = handler.process_event(pygame_event)
        
        # Verify fallback creates correct pause event
        assert len(events) == 1
        assert events[0].type == GameEventType.PAUSE_TOGGLE
```

### Localization Testing (39 tests)

**Key Test Areas**:
- **Loader abstraction pattern**: FileLanguageLoader, MemoryLanguageLoader, CachedLanguageLoader implementations
- **Font loading and rendering**: Chinese text rendering without "tofu blocks"
- **Language switching functionality**: Dynamic language switching during gameplay
- **Multi-language UI layout**: Interface components adapt to different text lengths and character sets
- **Dependency injection**: Testable language loading interfaces
- **Performance optimization**: Cached language loading with configurable caching strategies

**Example Test Pattern**:
```python
def test_chinese_font_rendering():
    """Test Chinese text renders without tofu blocks."""
    lang_manager = LanguageManager()
    lang_manager.set_language('zh')
    
    # Test font loading
    font = lang_manager.get_font('notification', 24)
    assert font is not None
    
    # Test text rendering
    chinese_text = "暂停游戏"
    surface = font.render(chinese_text, True, (255, 255, 255))
    
    # Verify surface is not empty (no tofu blocks)
    assert surface.get_width() > 0
    assert surface.get_height() > 0
```

### Boss Spawn Timing Testing (18 tests)

**Key Test Areas**:
- **Pause-aware boss intervals**: Boss generation correctly excludes pause periods
- **Timing calculation consistency**: Unified architecture eliminates timing inconsistencies
- **Level requirements**: Boss spawning only occurs at appropriate game levels (level 2+)
- **Edge case handling**: Zero game time, negative time prevention, rapid pause toggles
- **Integration with pause system**: Boss timing calculations use pause-aware game time

**Example Test Pattern**:
```python
def test_boss_spawn_timing_with_pause():
    """Test boss spawn timing excludes pause duration."""
    pause_manager = PauseManager()
    boss_system = BossSystem(pause_manager)
    
    game_start = 1000.0
    boss_interval = BOSS_SPAWN_INTERVAL  # e.g., 30 seconds
    
    # Simulate gameplay to boss spawn time
    current_time = game_start + boss_interval
    assert boss_system.should_spawn_boss(game_start, current_time) is True
    
    # Add pause time - boss should not spawn yet
    pause_manager.pause(current_time)
    paused_time = current_time + 10.0  # 10 second pause
    pause_manager.resume(paused_time)
    
    # Boss should not spawn until real game time reaches interval
    assert boss_system.should_spawn_boss(game_start, paused_time) is False
    
    # Boss should spawn after accounting for pause
    final_time = paused_time + 10.0  # Additional 10 seconds
    assert boss_system.should_spawn_boss(game_start, final_time) is True
```

### Enemy Entity Testing (8 tests)

**Key Test Areas**:
- **Interface-focused testing**: Testing public APIs over implementation details
- **Level-based behavior**: Enemy shooting capability based on level thresholds
- **Factory integration**: Enemy creation through factory pattern validation
- **Behavioral consistency**: Movement properties and interaction patterns
- **Performance characteristics**: Entity creation and update performance

**Example Test Pattern**:
```python
def test_enemy_level_based_behavior():
    """Test enemy behavior changes based on level."""
    factory = EnemyFactory()
    
    # Test low-level enemy (cannot shoot)
    low_level_enemy = factory.create_enemy(level=1)
    assert low_level_enemy.level == 1
    assert low_level_enemy.can_shoot is False
    assert low_level_enemy.shoot_delay is None
    
    # Test high-level enemy (can shoot)
    high_level_enemy = factory.create_enemy(level=5)
    assert high_level_enemy.level == 5
    assert high_level_enemy.can_shoot is True
    assert high_level_enemy.shoot_delay > 0
    assert high_level_enemy.shoot_delay < 3000  # Within reasonable range
```

## Common Testing Patterns

### Event System Testing

```python
def test_event_dispatch_and_handling():
    """Test event dispatching to multiple listeners."""
    event_system = EventSystem()
    listener1 = Mock()
    listener2 = Mock()
    
    event_system.register(listener1, EventType.ENEMY_DEFEATED)
    event_system.register(listener2, EventType.ENEMY_DEFEATED)
    
    event = EnemyDefeatedEvent(enemy_id=123, points=100)
    event_system.dispatch(event)
    
    listener1.handle.assert_called_once_with(event)
    listener2.handle.assert_called_once_with(event)
```

### Factory Pattern Testing

```python
def test_factory_creates_configured_entities():
    """Test factory creates entities with correct configuration."""
    factory = EnemyFactory()
    
    # Test different configurations
    configs = [
        {'level': 1, 'expected_shooting': False},
        {'level': 3, 'expected_shooting': True},
    ]
    
    for config in configs:
        enemy = factory.create_enemy(level=config['level'])
        assert enemy.can_shoot == config['expected_shooting']
```

### State Machine Testing

```python
def test_state_transitions():
    """Test state machine handles transitions correctly."""
    state_machine = StateMachine()
    
    # Test valid transition
    assert state_machine.transition_to(GameState.PLAYING)
    assert state_machine.current_state == GameState.PLAYING
    
    # Test invalid transition
    with pytest.raises(InvalidTransitionError):
        state_machine.transition_to(GameState.INVALID)
```

## Testing Gaps and Priorities

### High Priority Gaps (Add within 1 week)

1. **Input System Tests** (15-20 tests needed):
   ```python
   tests/unit/input/
   ├── test_input_handler.py      # Fallback mechanisms
   ├── test_input_manager.py      # Event coordination
   └── test_key_bindings.py       # Key mapping and F1 reset
   ```

2. **Pause System Enhancement** (5-8 tests needed):
   ```python
   tests/unit/test_pause_system.py
   - test_pause_aware_timing
   - test_repeated_pause_resume_cycles
   - test_pause_state_synchronization
   ```

3. **Localization Testing** (5-8 tests needed):
   ```python
   tests/unit/test_localization.py
   - test_chinese_font_rendering
   - test_language_switching
   - test_notification_font_sizes
   ```

### Medium Priority (2-3 weeks)

1. **Performance Testing**:
   ```python
   tests/performance/
   ├── test_rendering_performance.py
   ├── test_collision_performance.py
   └── test_memory_usage.py
   ```

2. **Edge Case Testing**:
   ```python
   tests/edge_cases/
   ├── test_extreme_entity_counts.py
   ├── test_rapid_input_sequences.py
   └── test_memory_limits.py
   ```

## Performance and Benchmarking

### Performance Test Framework

```python
import time
import pytest

class TestPerformance:
    @pytest.mark.slow
    def test_collision_detection_performance(self):
        """Test collision detection with many entities."""
        collision_system = CollisionSystem()
        
        # Create test scenario with many entities
        entities = [create_test_entity() for _ in range(1000)]
        
        start_time = time.time()
        collision_system.check_collisions(entities)
        elapsed_time = time.time() - start_time
        
        # Assert performance threshold
        assert elapsed_time < 0.016  # 60 FPS threshold
```

### Memory Usage Testing

```python
import psutil
import os

def test_memory_usage_stability():
    """Test memory usage doesn't grow excessively."""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Simulate game loop
    game = Game()
    for _ in range(1000):
        game.update()
    
    final_memory = process.memory_info().rss
    memory_growth = final_memory - initial_memory
    
    # Assert memory growth is reasonable
    assert memory_growth < 10 * 1024 * 1024  # Less than 10MB growth
```

## Conclusion

This testing guide provides the foundation for maintaining and expanding Thunder Fighter's comprehensive test suite. By following these patterns and practices, developers can:

- Add robust tests for new features
- Maintain high code coverage
- Ensure system reliability
- Catch regressions early
- Validate functionality across all game systems

## Related Documentation

For additional information related to testing and development:

- **[Technical Details](TECHNICAL_DETAILS.md)** - Technical implementation details and CI/CD testing setup
- **[Architecture Guide](ARCHITECTURE.md)** - System architecture and design patterns that support testability
- **[CI/CD Guide](CI_CD_GUIDE.md)** - Continuous integration pipeline and automated testing
- **[Contributing Guide](../CONTRIBUTING.md)** - Testing requirements for contributors
- **[Development Setup](../CLAUDE.md#testing)** - Quick testing commands and setup

---

*Last updated: January 2025*
*Test count: 390+ comprehensive tests*
*Overall coverage target: >85%*