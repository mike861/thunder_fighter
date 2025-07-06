# Changelog

All notable changes to Thunder Fighter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 🎨 **Double-Buffered Dynamic Background System**: Revolutionary visual enhancement
  - Professional-grade smooth level transitions with no visual artifacts
  - Unique visual themes for each level reflecting difficulty progression
  - Special effects including space storms and animated asteroid fields
  - Cubic bezier easing for ultra-smooth 3-second transitions
  - Alpha-based blending technology eliminating flash effects
- 🌐 **Enhanced Multi-Language Support**: Complete internationalization system
  - Chinese font optimization for macOS using TTF font files
  - Localized level indicators and Boss status displays
  - Multi-language level theme descriptions
  - Dynamic language switching with L key
  - Font size optimization for different character sets
- Comprehensive test suite with 255 tests
- Modular UI system with component-based architecture
- Event-driven architecture for decoupled components
- Factory pattern for entity creation
- Configuration management system with command-line tools
- Multi-language support (English and Chinese)
- Wingman system with tracking missiles
- Victory system with game completion statistics
- Developer mode with debug information
- Input management system with customizable key bindings

### Changed
- **Background System**: Complete rewrite with double buffering technology
- **Visual Polish**: Enhanced level indicators with glow effects and subtle overlays
- **Transition Experience**: Eliminated all visual artifacts and improved smoothness
- **Font System**: Completely redesigned for optimal Chinese character support
  - All UI components now use ResourceManager for font loading
  - TTF-only strategy on macOS for reliable Chinese rendering
  - Unified font management across all game components
- **UI Components**: Updated all components to support dynamic language switching
- Refactored UI system into separate components
- Improved state management system
- Enhanced sound system with automatic recovery
- Updated documentation structure

### Fixed
- **Background Transitions**: Completely eliminated flashing and visual artifacts during level changes
- **Chinese Font Display**: Resolved "tofu blocks" (□□□) issue on macOS
  - Fixed SysFont compatibility issues with Chinese characters
  - Implemented direct TTF font file loading for reliability
  - Optimized PingFang SC and STHeiti font usage
- **Time Display**: Fixed decimal time display for game durations under 1 minute
- **Language Switching**: Fixed L key functionality for proper language toggling
- **Localization**: Removed all hardcoded English text from level transitions and Boss displays
- Audio system stability improvements
- Memory leak in sprite rendering
- Collision detection accuracy
- Test compatibility with new background system

## [0.1.0] - 2024-01-01

### Added
- Initial release of Thunder Fighter
- Basic gameplay with 10 levels
- Player ship with movement and shooting
- Enemy waves and boss battles
- Power-up system
- Score tracking
- Background music and sound effects
- Pause functionality
- Game over and victory screens

[Unreleased]: https://github.com/mike861/thunder_fighter/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/mike861/thunder_fighter/releases/tag/v0.1.0 