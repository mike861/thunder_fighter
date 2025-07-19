# CI/CD Guide for Thunder Fighter

## Overview

Thunder Fighter uses GitHub Actions for Continuous Integration and Continuous Deployment (CI/CD). This guide explains the pipeline structure, requirements, and best practices for maintaining and contributing to the project.

## Pipeline Structure

The CI/CD pipeline consists of three main jobs that run automatically on every push and pull request:

### 1. Test Job

**Environment**: macOS-latest with Python 3.12, 3.13
**Purpose**: Comprehensive code quality validation and testing

**Steps**:
1. **Checkout**: Repository checkout using `actions/checkout@v4`
2. **Python Setup**: Environment setup with `actions/setup-python@v5`
3. **Dependency Installation**: Install project and development dependencies
4. **Linting**: Code style verification with Ruff
5. **Type Checking**: Static type analysis with MyPy
6. **Testing**: Execute full test suite with coverage reporting
7. **Coverage Upload**: Upload coverage reports to Codecov

**Key Features**:
- Fail-fast disabled for comprehensive testing
- SDL dummy drivers for headless GUI testing
- Coverage reporting with XML and terminal output
- Support for multiple Python versions

### 2. Security Job

**Environment**: ubuntu-latest with Python 3.10
**Purpose**: Security vulnerability scanning and dependency analysis

**Steps**:
1. **Checkout**: Repository checkout
2. **Python Setup**: Environment setup
3. **Security Tools**: Install Bandit and Safety scanners
4. **Vulnerability Scanning**: 
   - Code security analysis with Bandit
   - Dependency vulnerability check with Safety
5. **Report Generation**: Generate security reports in JSON format

**Security Tools**:
- **Bandit**: Static security analysis for Python code
- **Safety**: Known security vulnerabilities in dependencies

### 3. Build Job

**Environment**: macOS-latest with Python 3.10
**Purpose**: Package build verification and artifact generation

**Dependencies**: Requires successful completion of Test Job

**Steps**:
1. **Checkout**: Repository checkout
2. **Python Setup**: Environment setup
3. **Build Tools**: Install Python build tools
4. **Package Build**: Create distribution packages
5. **Artifact Upload**: Upload build artifacts using `actions/upload-artifact@v4`

## GitHub Actions Versions

The project maintains the latest stable versions of all GitHub Actions:

| Action | Version | Purpose |
|--------|---------|---------|
| `actions/checkout` | v4 | Repository checkout |
| `actions/setup-python` | v5 | Python environment setup |
| `actions/upload-artifact` | v4 | Build artifact handling |
| `codecov/codecov-action` | v4 | Coverage reporting |

## CI Configuration

### Trigger Conditions

```yaml
on:
  push:
    branches: [ main, dev-* ]
  pull_request:
    branches: [ main ]
```

- **Push**: Triggers on main branch and development branches (dev-*)
- **Pull Request**: Triggers on PRs targeting main branch

### Environment Variables

```yaml
env:
  SDL_VIDEODRIVER: dummy
  SDL_AUDIODRIVER: dummy
```

- **SDL Configuration**: Enables headless mode for GUI testing
- **Audio/Video**: Dummy drivers prevent audio/video initialization errors

### Matrix Strategy

```yaml
strategy:
  fail-fast: false
  matrix:
    os: [macos-latest]
    python-version: ['3.12', '3.13']
```

- **Operating System**: Currently focused on macOS for development
- **Python Versions**: Support for Python 3.12 and 3.13
- **Fail-fast**: Disabled to run all combinations even if one fails

## Quality Gates

### Code Quality Requirements

1. **Linting**: All code must pass Ruff linting checks
2. **Formatting**: Code must be properly formatted with Ruff
3. **Type Safety**: Zero MyPy errors tolerance
4. **Test Coverage**: All tests must pass (390+ tests)

### Security Requirements

1. **No High-Risk Vulnerabilities**: Bandit security scan must pass
2. **Dependency Safety**: All dependencies must be free of known vulnerabilities
3. **Automated Scanning**: Continuous security monitoring

### Build Requirements

1. **Package Build**: Distribution packages must build successfully
2. **Artifact Generation**: Build artifacts must be properly generated
3. **Cross-platform Compatibility**: Builds must work across supported platforms

## Best Practices for Contributors

### Before Submitting PRs

1. **Local Testing**: Run the complete test suite locally
   ```bash
   pytest tests/ -v
   ```

2. **Code Quality**: Ensure code meets quality standards
   ```bash
   ruff format .
   ruff check .
   mypy thunder_fighter/
   ```

3. **Coverage**: Verify test coverage for new features
   ```bash
   pytest tests/ --cov=thunder_fighter --cov-report=term
   ```

### CI Troubleshooting

#### Common Issues

1. **Test Failures**: Check test output for specific failures
2. **Linting Errors**: Run `ruff check .` locally to identify issues
3. **Type Errors**: Run `mypy thunder_fighter/` to check type safety
4. **Security Warnings**: Review Bandit output for security issues

#### Resolution Steps

1. **Fix Locally**: Address issues in your development environment
2. **Test Again**: Verify fixes work locally before pushing
3. **Push Updates**: Commit and push fixes to trigger CI re-run
4. **Monitor CI**: Watch GitHub Actions for successful completion

## Maintenance and Updates

### Action Updates

GitHub Actions are regularly updated to maintain security and performance:

1. **Version Monitoring**: Track new releases of used actions
2. **Security Updates**: Apply security patches promptly
3. **Performance Improvements**: Upgrade to newer versions for better performance
4. **Deprecation Handling**: Replace deprecated actions before they're removed

### Pipeline Evolution

The CI/CD pipeline evolves with project needs:

1. **New Tools**: Integration of new development tools
2. **Platform Support**: Addition of new operating systems
3. **Python Versions**: Support for new Python releases
4. **Performance Optimization**: Continuous improvement of pipeline speed

## Monitoring and Reporting

### Coverage Reporting

- **Codecov Integration**: Automatic coverage reporting
- **Coverage Thresholds**: Maintain high coverage standards
- **Trend Analysis**: Monitor coverage trends over time

### Security Monitoring

- **Automated Scanning**: Regular security vulnerability checks
- **Dependency Updates**: Monitor for security updates in dependencies
- **Report Analysis**: Review security scan results

### Performance Metrics

- **Build Time**: Monitor CI pipeline execution time
- **Test Execution**: Track test suite performance
- **Resource Usage**: Optimize resource consumption

## Support and Documentation

### Resources

- **GitHub Actions Documentation**: [GitHub Actions Docs](https://docs.github.com/en/actions)
- **Workflow File**: `.github/workflows/ci.yml`
- **Requirements**: `requirements.txt` and `requirements-dev.txt`

### Getting Help

- **GitHub Issues**: Report CI/CD issues
- **Discussions**: Community support for CI/CD questions
- **Documentation**: Refer to project documentation

---

This guide ensures consistent, reliable, and secure CI/CD practices for Thunder Fighter development.