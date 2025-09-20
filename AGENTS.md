# Repository Guidelines

## Project Structure & Module Organization
- Source: `thunder_fighter/` (systems, entities, graphics, events, utils, localization, assets)
- Tests: `tests/` grouped by type (`unit/`, `integration/`, `systems/`, `e2e/`) and feature folders
- Docs: `docs/` (architecture, mechanics, testing, roadmap)
- Entry points: `main.py` (dev), `python -m thunder_fighter`, or installed CLI `thunder-fighter`
- Packaging: assets and localization are included via `pyproject.toml`

## Build, Test, and Development Commands
- Create env + dev deps: `python -m venv venv && source venv/bin/activate && pip install -e .[dev]`
  - Alternative: `pip install -r requirements.txt -r requirements-dev.txt`
- Run game (local): `python main.py` or `python -m thunder_fighter`
- Lint/format: `ruff format .` then `ruff check .`
- Type checking: `mypy thunder_fighter`
- Tests (all): `pytest -v`  | coverage: `pytest --cov=thunder_fighter -v`
- Targeted tests: `pytest tests/systems -v`, `pytest tests/unit -v`

## Coding Style & Naming Conventions
- Python 3.12+ for development (library compatible 3.8+). Indent 4 spaces; max line length 120
- Use type hints for public functions and datatypes; keep functions small and single‑purpose
- Follow event‑driven, systems‑based architecture; avoid global state and tight coupling
- Naming: modules/functions `snake_case`; classes `PascalCase`; constants `UPPER_SNAKE_CASE`; tests `test_*.py`

## Testing Guidelines
- Framework: pytest. Configured patterns: files `test_*.py`, classes `Test*`, functions `test_*`
- Place new tests under the closest matching folder (`tests/systems`, `tests/graphics`, etc.)
- Mock Pygame surfaces/audio in unit tests; prefer interface‑level assertions
- Keep or improve coverage (aim ≥90% for critical systems)

## Commit & Pull Request Guidelines
- Conventional Commits: `feat(scope): add X`, `fix(module): correct Y`, `test: add Z`
- PRs must: describe intent and approach, link issues (`Closes #123`), include tests, pass CI (Ruff, MyPy, pytest)
- Include screenshots/GIFs for gameplay or UI changes; update docs when user‑visible behavior changes

## Security & Configuration Tips
- Do not commit secrets or personal config. Runtime settings live in `~/.thunder_fighter/config.json`
- Add new assets under `thunder_fighter/assets/`; keep sizes reasonable and attribute sources in docs when needed

