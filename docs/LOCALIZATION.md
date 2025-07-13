# Font System and Localization

This document describes the font system and localization implementation in Thunder Fighter, including the solutions for Chinese character display issues on macOS.

## Overview

Thunder Fighter features a comprehensive multi-language support system with optimized font rendering, particularly for Chinese characters on macOS. The system includes dynamic language switching, TTF-based font loading, and complete UI localization.

## Font System Architecture

### ResourceManager-Based Font Loading

All fonts in the game are loaded through the centralized `ResourceManager` class, which provides:

- **TTF Font File Priority**: Direct loading of TTF font files for reliable rendering
- **Font Caching**: Efficient font reuse across components
- **Platform Optimization**: macOS-specific optimizations for Chinese fonts
- **Fallback System**: Automatic fallbacks when preferred fonts are unavailable

### Key Components

#### 1. ResourceManager (`thunder_fighter/utils/resource_manager.py`)

**Core Methods:**
- `load_font(font_name, size, system_font=False)`: Main font loading interface
- `_get_optimized_system_font(font_name, size)`: macOS Chinese font optimization
- `_get_optimized_default_font(font_name, size)`: Default font with TTF priority

**macOS Chinese Font Strategy:**
```python
# Priority order for Chinese fonts on macOS
if platform.system() == 'Darwin':
    font_file_map = {
        'PingFang SC': '/System/Library/Fonts/PingFang.ttc',
        'Heiti SC': '/System/Library/Fonts/STHeiti Medium.ttc',
        'STHeiti': '/System/Library/Fonts/STHeiti Medium.ttc'
    }
```

#### 2. UI Components Font Integration

All UI components use ResourceManager for font loading:

- **GameInfoDisplay**: Game statistics (score, level, time)
- **PlayerStatsDisplay**: Player status information
- **BossStatusDisplay**: Boss health and mode indicators
- **NotificationManager**: Game notifications and achievements
- **ScreenOverlayManager**: Pause, victory, and game over screens

### Font Size Standards

| Component | Font Size | Usage |
|-----------|-----------|-------|
| Small | 24px | General UI text, status information |
| Medium | 36px | Important notifications, menu items |
| Large | 48px | Screen titles, major announcements |
| Boss Health | 20px | Boss status indicators |
| Level Indicator | 72px | Level transition displays |
| Level Description | 48px | Level theme descriptions |

## Localization System

### Language Files

**Location**: `thunder_fighter/localization/`
- `en.json`: English translations
- `zh.json`: Chinese translations

**Format**:
```json
{
    "KEY_NAME": "Translated text with {} placeholders",
    "SCORE": "Score: {}",
    "LEVEL_INDICATOR": "Level {}"
}
```

### Translation Function

**Usage**: `from thunder_fighter.localization import _`

```python
# Simple translation
text = _("GAME_TITLE")

# Translation with parameters
score_text = _("SCORE", player_score)
level_text = _("LEVEL_INDICATOR", current_level)
```

### Dynamic Language Switching

**Key Binding**: L key toggles between English and Chinese

**Implementation Flow**:
1. User presses L key
2. `InputHandler` detects language switch event
3. `Game` class processes the event
4. UI components refresh fonts and text
5. All displays update immediately

## Chinese Font Display Solution

### Problem Analysis

**Original Issue**: Chinese characters displayed as "tofu blocks" (□□□) on macOS

**Root Cause**: `pygame.font.SysFont()` incompatibility with Chinese character rendering on macOS

### Solution Implementation

#### 1. TTF-Only Strategy

**Before**:
```python
font = pygame.font.SysFont("PingFang SC", 24)  # Failed for Chinese
```

**After**:
```python
# Direct TTF file loading
font_path = "/System/Library/Fonts/PingFang.ttc"
font = pygame.font.Font(font_path, 24)  # Works reliably
```

#### 2. Component Updates

All UI components were updated to use `system_font=True`:

```python
# Before: Direct pygame font usage
self.font = pygame.font.Font(None, 24)

# After: ResourceManager with Chinese support
resource_manager = get_resource_manager()
self.font = resource_manager.load_font(None, 24, system_font=True)
```

#### 3. Font Refresh System

Components support dynamic font refresh during language changes:

```python
def refresh_font_for_language_change(self):
    """Refresh font when language changes"""
    resource_manager = get_resource_manager()
    self.font = resource_manager.load_font(None, 24, system_font=True)
```

## Localized UI Elements

### Game Information Display

**Keys Used**:
- `SCORE`: Score display format
- `LEVEL`: Level indicator format  
- `TIME`: Game time format

**Components**: `GameInfoDisplay`, `PlayerStatsDisplay`

### Level System

**Level Indicators**:
- English: "Level 1", "Level 2", etc.
- Chinese: "第1关", "第2关", etc.

**Level Themes**:
- `LEVEL_THEME_DEEP_SPACE`: "Deep Space" / "深空"
- `LEVEL_THEME_NEBULA_FIELD`: "Nebula Field" / "星云地带"
- `LEVEL_THEME_ASTEROID_BELT`: "Asteroid Belt" / "小行星带"
- `LEVEL_THEME_RED_ZONE`: "Red Zone" / "红色区域"
- `LEVEL_THEME_FINAL_BATTLE`: "Final Battle" / "最终之战"

### Boss System

**Boss Status Indicators**:
- `BOSS_LEVEL_NORMAL`: "BOSS Lv.{}" / "首领 Lv.{}"
- `BOSS_LEVEL_DANGER`: "BOSS Lv.{} [Danger]" / "首领 Lv.{} [危险]"
- `BOSS_LEVEL_EXTREME`: "BOSS Lv.{} [Extreme]" / "首领 Lv.{} [极限]"

### Notifications

**Achievement Notifications**:
- `LEVEL_UP`: "LEVEL UP! {} → {}" / "升级! {} → {}"
- `BOSS_DEFEATED`: "Boss Defeated! +{} score" / "BOSS被击败! +{}分"
- `STAGE_COMPLETE`: "Stage Complete!" / "关卡完成!"

## Technical Implementation Details

### Font Loading Flow

1. **Component Initialization**: Request font from ResourceManager
2. **Platform Detection**: Check if running on macOS
3. **Font File Resolution**: Map font names to TTF file paths
4. **TTF Loading**: Load font directly from file system
5. **Fallback Handling**: Use default fonts if specific fonts unavailable
6. **Caching**: Store loaded fonts for reuse

### Language Change Flow

1. **Event Trigger**: L key press generates language switch event
2. **Language Toggle**: Switch between 'en' and 'zh'
3. **UI Refresh**: All components refresh fonts and text
4. **Immediate Update**: Changes take effect in current frame

### Performance Optimizations

- **Font Caching**: Loaded fonts are cached to avoid repeated file access
- **Lazy Loading**: Fonts loaded only when needed
- **Resource Cleanup**: Proper cleanup when switching languages
- **Memory Management**: Efficient memory usage for font resources

## Platform Compatibility

### macOS
- **Primary Fonts**: PingFang SC, STHeiti Medium
- **Font Paths**: Direct TTF file access
- **Compatibility**: macOS 10.10+ (supports PingFang SC)

### Windows
- **Primary Fonts**: Microsoft YaHei, SimSun
- **Fallback**: System font resolution
- **Compatibility**: Windows 7+

### Linux
- **Primary Fonts**: WenQuanYi, DejaVu Sans
- **Fallback**: fontconfig resolution
- **Compatibility**: Most distributions

## Troubleshooting

### Common Issues

**Issue**: Chinese characters show as squares (□)
**Solution**: Ensure `system_font=True` when loading fonts

**Issue**: Font size appears inconsistent
**Solution**: Check font size constants in `constants.py`

**Issue**: Language switching not working
**Solution**: Verify L key binding in `key_bindings.py`

### Debug Information

Enable debug mode to see font loading information:

```bash
THUNDER_FIGHTER_LOG_LEVEL=DEBUG python main.py
```

**Log Output**:
```
INFO - ResourceManager initialized
DEBUG - Loading font: None, size: 24, system_font: True
DEBUG - Using TTF font: /System/Library/Fonts/PingFang.ttc
```

## Future Enhancements

### Planned Features

1. **Additional Languages**: Japanese, Korean support
2. **Font Configuration**: User-selectable fonts
3. **Text Scaling**: Adaptive text scaling for different screen sizes
4. **Font Fallback Chain**: More comprehensive fallback system

### Development Guidelines

1. **Always use ResourceManager**: Never use pygame fonts directly
2. **Test on Multiple Platforms**: Verify font rendering across systems
3. **Use Localization Keys**: No hardcoded display strings
4. **Document New Keys**: Add translations for both languages
5. **Font Size Consistency**: Follow established font size standards

## Conclusion

The font system and localization implementation in Thunder Fighter provides robust multi-language support with optimized Chinese character rendering. The TTF-based approach ensures reliable font display across platforms, while the modular architecture allows for easy extension and maintenance. 