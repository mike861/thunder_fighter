# Thunder Fighter Development Roadmap

## Overview

This document outlines planned improvements, missing implementations, and technical debt items identified through comprehensive code-documentation analysis. All items are prioritized and ready for development scheduling.

## 🔴 High Priority Items

### 1. **Missing Core Features**

#### Victory Sound System Enhancement
**Status**: Partially Implemented  
**Current State**: Only background music fadeout implemented  
**Required Implementation**:
- Add `victory_sound.wav` to assets/sounds/ directory
- Implement victory sound playback in `VictoryState.enter()` method
- Update sound manager to handle victory-specific audio effects

**Files to Modify**:
- `thunder_fighter/state/game_states.py` (lines 230-234)
- `thunder_fighter/utils/sound_manager.py`
- Add new asset: `assets/sounds/victory_sound.wav`

**Estimated Effort**: 2-4 hours

#### Dynamic Item Weight System
**Status**: Missing Implementation  
**Current State**: Simple `random.choice()` selection  
**Required Implementation**:
- Implement weight-based item selection in `ItemFactory.create_random_item()`
- Add configurable weight system that adjusts based on:
  - Player health percentage
  - Current game level
  - Time since last item of each type
  - Player progression needs

**Files to Modify**:
- `thunder_fighter/entities/items/item_factory.py` (line 69)
- `thunder_fighter/constants.py` (add ITEM_WEIGHTS configuration)

**Implementation Plan**:
```python
ITEM_WEIGHTS = {
    'HEALTH_ITEM': {'base': 15, 'health_modifier': 2.0},
    'BULLET_SPEED_ITEM': {'base': 12, 'level_modifier': 0.8},
    'BULLET_PATH_ITEM': {'base': 10, 'progression_modifier': 1.2},
    'PLAYER_SPEED_ITEM': {'base': 8, 'balance_modifier': 1.0},
    'WINGMAN_ITEM': {'base': 5, 'level_threshold': 3}
}
```

**Estimated Effort**: 4-6 hours

### 2. **Critical Configuration Improvements**

#### Extract Hardcoded Boss Combat Parameters
**Status**: Technical Debt  
**Current State**: Critical values hardcoded in boss.py  
**Required Changes**:

**Add to constants.py**:
```python
# Boss Attack System Configuration
BOSS_COMBAT = {
    'AGGRESSIVE_THRESHOLD': 0.5,           # Currently hardcoded at boss.py:131
    'FINAL_THRESHOLD': 0.25,               # Currently hardcoded at boss.py:139
    'AGGRESSIVE_DELAY_MULTIPLIER': 0.7,    # Currently hardcoded at boss.py:134
    'FINAL_DELAY_MULTIPLIER': 0.8,         # Currently hardcoded at boss.py:142
    'MIN_AGGRESSIVE_DELAY': 150,           # Currently hardcoded at boss.py:134
    'MIN_FINAL_DELAY': 100,                # Currently hardcoded at boss.py:142
    'DAMAGE_FLASH_FRAMES': 12,             # Currently hardcoded at boss.py:125
    'ENTRANCE_TARGET_Y': 50,               # Currently hardcoded at boss.py:156
    'ENTRANCE_SPEED': 2,                   # Currently hardcoded at boss.py:157
    'DIRECTION_CHANGE_INTERVAL': 100,      # Currently hardcoded at boss.py:161
    'MOVE_MARGIN': 10                      # Currently hardcoded at boss.py:74
}
```

**Files to Modify**:
- `thunder_fighter/constants.py`
- `thunder_fighter/entities/enemies/boss.py`

**Estimated Effort**: 3-4 hours

#### Extract Enemy System Parameters
**Status**: Technical Debt  
**Required Changes**:

**Add to constants.py**:
```python
# Enemy Spawn and Behavior Configuration
ENEMY_SYSTEM = {
    'SPAWN_INTERVAL': 2,                   # Currently hardcoded at game.py:794
    'MAX_SPEED_FACTOR': 3.0,               # Currently hardcoded at enemy.py:42
    'BASE_SPEED_FACTOR': 1.0,              # Currently hardcoded at enemy.py:42
    'SPEED_TIME_DIVISOR': 60.0,            # Currently hardcoded at enemy.py:42
    'LEVEL_SPEED_BONUS': 0.2,              # Currently hardcoded at enemy.py:43
    'MIN_BASE_SPEED': 1,                   # Currently hardcoded at enemy.py:45
    'MAX_BASE_SPEED': 3,                   # Currently hardcoded at enemy.py:45
    'ROTATION_SPEED_MIN': -8,              # Currently hardcoded at enemy.py:50
    'ROTATION_SPEED_MAX': 8,               # Currently hardcoded at enemy.py:50
    'BASE_SHOOT_DELAY': 800,               # Currently hardcoded at enemy.py:66
    'LEVEL_DELAY_REDUCTION': 50            # Currently hardcoded at enemy.py:67
}
```

**Files to Modify**:
- `thunder_fighter/constants.py`
- `thunder_fighter/sprites/enemy.py`
- `thunder_fighter/game.py`

**Estimated Effort**: 4-5 hours

## 🟡 Medium Priority Items

### 3. **Player System Enhancements**

#### Extract Player Animation Parameters
**Required Changes**:
```python
# Player Animation Configuration
PLAYER_ANIMATION = {
    'MISSILE_SHOOT_DELAY': 2000,           # Currently hardcoded at player.py:85
    'FLOAT_ANIMATION_SPEED': 1,            # Currently hardcoded at player.py:116
    'FLOAT_AMPLITUDE': 0.5,                # Currently hardcoded at player.py:117
    'THRUSTER_ANIMATION_FRAMES': 10,       # Currently hardcoded at player.py:139
    'FLASH_TOGGLE_INTERVAL': 100,          # Currently hardcoded at player.py:145
    'BULLET_OFFSET_SMALL': 5,              # Currently hardcoded at player.py:177
    'BULLET_OFFSET_LARGE': 8,              # Currently hardcoded at player.py:178
    'DEFAULT_DAMAGE': 10,                  # Currently hardcoded at player.py:267
    'INITIAL_Y_OFFSET': 10                 # Currently hardcoded at player.py:48
}
```

**Estimated Effort**: 2-3 hours

### 4. **Visual Effects System Improvements**

#### Extract Animation and Visual Parameters
**Required Changes**:
```python
# Visual Effects Configuration
VISUAL_EFFECTS = {
    'EXPLOSION_SIZE': 80,                  # Currently hardcoded at explosion.py:11
    'EXPLOSION_FRAME_RATE': 50,            # Currently hardcoded at explosion.py:17
    'EXPLOSION_TOTAL_FRAMES': 6,           # Currently hardcoded at explosion.py:24
    'EXPLOSION_FRAGMENT_COUNT': 8,         # Currently hardcoded at explosion.py:47
    'EXPLOSION_FRAGMENT_ANGLE_STEP': 45,   # Currently hardcoded at explosion.py:48
    'PARTICLE_COUNTS': {
        'EXPLOSION': 20,                   # Currently hardcoded at particles.py:70
        'TRAIL': 5,                        # Currently hardcoded at particles.py:87
        'SPARKS': 10,                      # Currently hardcoded at particles.py:109
        'HIT': 8                           # Various files
    }
}
```

**Estimated Effort**: 3-4 hours

### 5. **Background System Optimization**

#### Extract Background Parameters
**Required Changes**:
```python
# Background System Configuration
BACKGROUND_SYSTEM = {
    'STAR_COUNTS': {
        'LAYER1': 30,                      # Currently hardcoded at background.py:315
        'LAYER2': 20,                      # Currently hardcoded at background.py:316
        'LAYER3': 15                       # Currently hardcoded at background.py:317
    },
    'NEBULA_DEFAULT_COUNT': 3,             # Currently hardcoded at background.py:320
    'PLANET_DEFAULT_COUNT': 2,             # Currently hardcoded at background.py:323
    'STAR_SPEEDS': {
        'LAYER1_MIN': 0.5,                 # Currently hardcoded at background.py:19
        'LAYER2_MIN': 1.0,                 # Currently hardcoded at background.py:23
        'LAYER3_MIN': 2.0                  # Currently hardcoded at background.py:27
    }
}
```

**Estimated Effort**: 2-3 hours

## 🟢 Low Priority Items

### 6. **UI System Improvements**

#### Extract UI Parameters
```python
# UI System Configuration
UI_SYSTEM = {
    'HEALTH_BAR': {
        'BACKGROUND_COLOR': (60, 60, 60),  # Currently hardcoded at health_bar.py:37
        'LOW_THRESHOLD': 0.3,              # Currently hardcoded at health_bar.py:65
        'MEDIUM_THRESHOLD': 0.6,           # Currently hardcoded at health_bar.py:67
        'BORDER_WIDTH': 2                  # Currently hardcoded at health_bar.py:75
    },
    'PAUSE_COOLDOWN_MS': 200,              # Currently hardcoded at game.py:152
    'ITEM_SPAWN_INTERVAL': 30,             # Currently hardcoded at game.py:174
    'INPUT_VALIDATION_INTERVAL': 10.0      # Currently hardcoded at game.py:166
}
```

**Estimated Effort**: 2-3 hours

### 7. **Enemy Level Probability System**

#### Improve Enemy Level Distribution
**Current State**: Complex hardcoded probability arrays in enemy.py  
**Improvement**: Extract to configurable system

```python
# Enemy Level Probability Configuration
ENEMY_LEVEL_SYSTEM = {
    'BASE_PROBABILITIES': [0.35, 0.25, 0.15, 0.10, 0.05, 0.03, 0.02, 0.02, 0.02, 0.01, 0.01],
    'TIME_MODIFIERS': [0.05, 0.03, 0.01, 0.015, 0.01, 0.005, 0.003, 0.002, 0.001, 0.001, 0.001],
    'LEVEL_BOOST_PER_GAME_LEVEL': 0.02,    # Currently hardcoded at enemy.py:102
    'MIN_PROBABILITY': 0.001                # Currently hardcoded at enemy.py:122
}
```

**Estimated Effort**: 3-4 hours

## 📋 Implementation Timeline

### Phase 1: Core Features (Week 1)
- ✅ Victory Sound System Enhancement
- ✅ Dynamic Item Weight System
- ✅ Boss Combat Parameters Extraction

### Phase 2: System Parameters (Week 2)
- ✅ Enemy System Parameters
- ✅ Player Animation Parameters
- ✅ Visual Effects Parameters

### Phase 3: Optimization (Week 3)
- ✅ Background System Parameters
- ✅ UI System Parameters
- ✅ Enemy Level Probability System

## 🔧 Implementation Guidelines

### Code Standards
1. **Constants Organization**: Group related constants into dictionaries for better organization
2. **Backward Compatibility**: Ensure all changes maintain existing functionality
3. **Testing**: Add tests for any new configuration systems
4. **Documentation**: Update configuration documentation in TECHNICAL_DETAILS.md

### Configuration Philosophy
- **Centralization**: Move hardcoded values to constants.py
- **Grouping**: Organize related constants into logical sections
- **Flexibility**: Allow easy game balancing without code changes
- **Maintainability**: Clear naming and documentation for all parameters

### Validation Requirements
- All changes must pass existing test suite (375+ tests)
- New features require corresponding test coverage
- Performance impact must be minimal
- Configuration changes should not affect gameplay balance

## 📝 Notes

**Priority Rationale**:
- **High Priority**: Missing features that affect gameplay or technical debt that impacts maintainability
- **Medium Priority**: Parameter extraction that improves game balancing capabilities
- **Low Priority**: Nice-to-have improvements that enhance development experience

**Development Dependencies**:
- Items can be implemented independently
- Boss Combat Parameters should be completed before Enemy System Parameters
- Victory Sound System requires asset creation (victory_sound.wav)

**Future Considerations**:
- Consider implementing configuration file system for runtime parameter adjustment
- Evaluate adding difficulty presets using the extracted parameters
- Monitor performance impact of increased configuration complexity

---

*This roadmap represents a systematic approach to addressing technical debt and missing features identified through comprehensive code analysis. All items are ready for implementation and include detailed specifications.*