# Thunder Fighter

A classic vertical scrolling space shooter game built with Pygame.

## Description

In Thunder Fighter, you pilot a fighter jet battling waves of enemies in space. Use the arrow keys or WASD to move and the spacebar to shoot. As the game progresses, enemies become stronger and more numerous, with powerful Bosses appearing periodically. Defeat enemies and Bosses to score points and collect power-ups.

## Features

- Dynamic level progression with increasing difficulty
- Multiple enemy types with different behaviors
- Epic boss battles with changing attack patterns
- Power-up system (health, speed, bullet enhancements)
- Particle effects and animations for explosions and impacts
- Dynamic UI with stacked notifications
- Multi-language support (currently English and Chinese)
- Responsive controls and collision detection
- Background music and sound effects with volume control
- Comprehensive logging system
- Fully tested codebase (43 tests passing)

For more detailed information on game mechanics, assets, and technical aspects, see [Project Details](docs/DETAILS.md).

## Screenshots

_(Add gameplay screenshots here if available)_ 
<!-- ![Gameplay Screenshot](screenshots/gameplay.png) -->

## Requirements

- Python 3.7+
- Pygame 2.0.0+
- Other dependencies listed in `requirements.txt`

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/thunder_fighter.git
    cd thunder_fighter
    ```
    (Replace `yourusername` with the actual repository path)

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows:
    # venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Play

1.  **Run the game:**
    ```bash
    python main.py
    ```

2.  **Adjust Log Level (Optional):**
    Set the `THUNDER_FIGHTER_LOG_LEVEL` environment variable (e.g., `DEBUG`, `INFO`, `WARNING`).
    ```bash
    # Windows
    # set THUNDER_FIGHTER_LOG_LEVEL=DEBUG
    # python main.py
    
    # Linux/macOS
    # THUNDER_FIGHTER_LOG_LEVEL=DEBUG python main.py
    ```

### Controls

-   **Movement:** Arrow Keys (↑↓←→) or WASD
-   **Shoot:** Spacebar
-   **Pause/Resume:** P
-   **Toggle Music:** M
-   **Toggle Sound Effects:** S
-   **Adjust Volume:** +/- (Plus/Minus keys)
-   **Switch Language:** L (Toggles between English and Chinese)
-   **Quit Game:** ESC
-   **(Dev Mode) Show Enemy Levels:** F3

## Testing

The project includes a comprehensive test suite covering game mechanics, collisions, and components. All 43 tests are currently passing.

-   **Run all tests:**
    ```bash
    pytest
    ```

-   **Run tests in a specific file:**
    ```bash
    pytest tests/sprites/test_boss.py
    ```

## Project Structure

```
thunder_fighter/
├── assets/         # Game assets (images, sounds, music)
├── docs/           # Detailed documentation
│   └── DETAILS.md
├── graphics/       # Rendering, effects, UI
├── localization/   # Language files (en.py, zh.py)
├── sprites/        # Game entities (player, enemies, boss, etc.)
├── tests/          # Unit tests
├── utils/          # Helper functions, managers (sound, score, etc.)
├── __init__.py
├── config.py       # Game configuration
├── constants.py    # Game constants
└── game.py         # Main game class
main.py             # Main entry point script
requirements.txt    # Python dependencies
README.md           # This file
README_CN.md        # Chinese README
.gitignore
LICENSE             # Project License
```

## Development

### Multi-language Support

The game supports multiple languages via `thunder_fighter/localization/`. 

1.  Language files (e.g., `en.py`, `zh.py`) store key-value pairs for text strings.
2.  The `LanguageManager` loads the appropriate language based on `config.py`.
3.  In-game text is retrieved using the `_()` function (e.g., `_("Game Over")`).
4.  Switch languages in-game using the 'L' key.

**To add a new language:**

1.  Create a new language file (e.g., `es.py` for Spanish) in `thunder_fighter/localization/` by copying `en.py`.
2.  Translate all the string values in the new file.
3.  Add the language code (e.g., `'es'`) to the `AVAILABLE_LANGUAGES` list in `thunder_fighter/config.py`.
4.  Update the `LanguageManager` if any special handling is needed (unlikely for simple additions).

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Acknowledgments

-   Pygame Community
-   Open-source game development resources
-   Contributors and testers 