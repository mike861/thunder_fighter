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

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

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
4. **Write Code**: Follow our coding standards
5. **Test**: Ensure all tests pass and add new tests for your changes
6. **Document**: Update documentation if needed
7. **Submit PR**: Create a pull request with a clear description

## Development Setup

### Prerequisites

- Python 3.7 or higher
- Git
- Virtual environment tool (venv, virtualenv, or uv)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/thunder_fighter.git
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
   pytest tests/ -v
   ```

5. **Run the game**
   ```bash
   python main.py
   ```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with the following specifications:

- Use 4 spaces for indentation (no tabs)
- Maximum line length: 120 characters
- Use descriptive variable and function names
- Add type hints for all function parameters and return values

### Code Formatting

We use Ruff for code formatting and linting:

```bash
# Format code
ruff format .

# Check linting
ruff check .
```

### Documentation

- All functions and classes must have docstrings (Google style)
- Complex logic should have inline comments
- Update relevant documentation files for significant changes

### Testing

- Write tests for all new functionality
- Maintain or improve test coverage
- Tests should be in the appropriate directory under `tests/`
- Use pytest fixtures when appropriate

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
4. **Update documentation**: If applicable
5. **Create PR**: Use a clear, descriptive title
6. **Fill out template**: Complete the PR template
7. **Wait for review**: Address any feedback from reviewers
8. **Merge**: Once approved, your PR will be merged

### PR Title Format

Follow the same convention as commit messages:
- `feat: add boss health indicator`
- `fix: resolve memory leak in sprite rendering`

## Reporting Issues

### Before Submitting an Issue

1. Check the [FAQ](docs/FAQ.md) (if available)
2. Search existing issues (including closed ones)
3. Try to reproduce the issue with the latest version

### Issue Template

When creating an issue, please use the appropriate template and provide:

- Clear, descriptive title
- Detailed description
- Steps to reproduce (for bugs)
- System information
- Any relevant logs or screenshots

## Questions?

If you have questions about contributing, feel free to:

- Open a discussion in GitHub Discussions
- Ask in our community chat (if available)
- Create an issue with the `question` label

Thank you for contributing to Thunder Fighter! 🚀 