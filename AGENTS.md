# Repository Guidelines

## Project Structure & Module Organization
The gameplay package lives in `thunder_fighter/` (domains: `entities`, `systems`, `graphics`, `state`, `utils`) with `assets/` for art/audio and `config/` driving `config.py`. `main.py` launches the pygame loop. Tests mirror the package in `tests/` (unit, integration, e2e) and `docs/` holds design references, while planning notes stay in root `plan-*.txt` files.

## Build, Test & Development Commands
- `python -m venv venv && source venv/bin/activate`: prepare the expected virtual env.
- `pip install -r requirements.txt && pip install -r requirements-dev.txt`: install runtime + dev deps.
- `python main.py`: run the game with current assets.
- `python -m pytest tests -v`: run the full suite; add `-k` to focus modules.
- `ruff format . && ruff check .`: format + lint before pushing.
- `mypy thunder_fighter`: run strict typing across the package.

## Coding Style & Naming Conventions
Use 4 spaces, UTF-8 source, and keep lines ≤120 characters. Follow PEP 8 with explicit typing—annotate public functions and add Google-style docstrings. Prefer `snake_case` for modules, functions, fixtures, `UpperCamelCase` for classes, and descriptive asset filenames (e.g., `laser_blue.png`). Keep comments/log strings in English and park shared constants in `constants.py` or domain submodules.

## Testing Expectations
Pytest discovers `test_*.py`, classes `Test*`, and functions `test_*` per `pyproject.toml`. Keep fast logic in `tests/unit`, pygame-heavy cases in `tests/integration` or `tests/e2e`, and mirror package paths. Aim to preserve ≥90% coverage on critical systems (`systems/`, `state/`, `events/`). Before a PR, add regression coverage and run `python -m pytest --cov=thunder_fighter --cov-report=term-missing`.

## Commit & Pull Request Flow
Commits follow Conventional Commits (`feat(visual):`, `fix(events):`, `docs:`); scope subjects to the touched subsystem and keep bodies concise. Before a PR, rebase on `main`, rerun lint, type check, tests, and document user-facing changes. Link issues via `Fixes #id`, attach screenshots or GIFs for visual tweaks, and wait for GitHub Actions CI before requesting review.

## Configuration & Asset Notes
Configuration defaults live in `thunder_fighter/config.py` and `thunder_fighter/utils/config_manager.py`; once the tool runs, overrides persist at `~/.thunder_fighter/config.json`. Use `python -m thunder_fighter.utils.config_tool show|set|reset` to inspect or adjust settings. Shared assets (sprites, audio, localization JSON) reside under `thunder_fighter/assets` and `thunder_fighter/localization`; organize additions by feature and update preload manifests alongside them.
