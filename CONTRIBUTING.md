# Contributing to Thunder Fighter

Thank you for your interest in contributing to Thunder Fighter! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please be respectful and constructive in all interactions.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your feature or fix
4. Make your changes
5. Push to your fork and submit a pull request

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- System information (OS, Python version, Pygame version)
- Screenshots or error messages if applicable

### Suggesting Features

Feature suggestions are welcome! Please provide:

- A clear and descriptive title
- Detailed description of the proposed feature
- Use cases and benefits
- Possible implementation approach (optional)

### Code Contributions

1. **Find an Issue**: Look for issues labeled `good first issue` or `help wanted`
2. **Claim an Issue**: Comment on the issue to let others know you're working on it
3. **Create a Branch**: Use a descriptive branch name (e.g., `feature/add-power-up` or `fix/collision-bug`)
4. **Write Code**: Follow our coding standards and architecture patterns
5. **Test**: Ensure all tests pass and add comprehensive tests for your changes
6. **Document**: Update documentation if needed
7. **Submit PR**: Create a pull request with a clear description

## Development Setup

### Prerequisites

- Python 3.12 or higher
- Git
- Virtual environment tool (venv, virtualenv, or uv)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/mike861/thunder_fighter.git
   cd thunder_fighter
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Run tests**
   ```bash
   ./venv/bin/python -m pytest tests/ -v
   ```

5. **Run the game**
   ```bash
   ./venv/bin/python main.py
   ```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with project-specific requirements:

- Use 4 spaces for indentation (no tabs)
- Maximum line length: 120 characters
- Use descriptive variable and function names
- Add type hints for all function parameters and return values
- Python 3.7+ compatibility (no walrus operator `:=`)
- All functions and classes must have docstrings (Google style)
- All comments, logs, and docstrings must be in English

### Code Formatting

We use Ruff for code formatting and linting:

```bash
# Format code
ruff format .

# Check linting
ruff check .
```

### Documentation

- Update relevant documentation files for significant changes
- Complex logic should have inline comments
- Follow existing documentation patterns and structure

### Testing

- Write tests for all new functionality
- Maintain or improve test coverage (target: >90% for critical systems)
- Tests should be in the appropriate directory under `tests/`
- Use pytest fixtures when appropriate
- Mock external dependencies (pygame surfaces, audio)
- Follow interface-focused testing over implementation details
- See [Testing Guide](docs/TESTING_GUIDE.md) for detailed patterns and best practices

## Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

### Examples

```
feat(player): add triple shot power-up

fix(collision): correct enemy collision detection bounds

docs: update README with new control scheme

refactor(ui): separate health bar into its own component
```

## Pull Request Process

1. **Update your branch**: Ensure your branch is up to date with the main branch
2. **Run tests**: All tests must pass
3. **Check code style**: Run Ruff and fix any issues
4. **Check type safety**: Run MyPy to ensure type safety
5. **Update documentation**: If applicable
6. **Create PR**: Use a clear, descriptive title
7. **Fill out template**: Complete the PR template
8. **Wait for CI**: All GitHub Actions checks must pass
9. **Wait for review**: Address any feedback from reviewers
10. **Merge**: Once approved, your PR will be merged

### Pre-PR Checklist

Before submitting your pull request, ensure:

- [ ] All tests pass locally: `./venv/bin/python -m pytest tests/ -v`
- [ ] Code is properly formatted: `ruff format .`
- [ ] No linting errors: `ruff check .`
- [ ] Type checking passes: `mypy thunder_fighter/`
- [ ] Documentation is updated if needed
- [ ] Commit messages follow conventional format
- [ ] Changes are covered by tests

### GitHub Actions CI Pipeline

Our CI pipeline runs automatically on every push and pull request with three main jobs:

- **Test Job**: Linting, type checking, and comprehensive test execution with coverage reporting
- **Security Job**: Security scanning and dependency vulnerability checks  
- **Build Job**: Package build verification and artifact generation

All CI checks must pass before your PR can be merged. If any check fails, review the error output and fix the issues locally before pushing updates.

### PR Title Format

Follow the same convention as commit messages:
- `feat: add boss health indicator`
- `fix: resolve memory leak in sprite rendering`

## Reporting Issues

### Before Submitting an Issue

1. Search existing issues (including closed ones)
2. Try to reproduce the issue with the latest version
3. Check the documentation for relevant information

### Issue Template

When creating an issue, please use the appropriate template and provide:

- Clear, descriptive title
- Detailed description
- Steps to reproduce (for bugs)
- System information
- Any relevant logs or screenshots

## Questions?

If you have questions about contributing, feel free to:

- Create an issue with the `question` label
- Check the project documentation for additional guidance
- Review similar pull requests for examples

Thank you for contributing to Thunder Fighter! 🚀 