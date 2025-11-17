# Contributing to Hyperbion Tripolar Network

Thank you for your interest in contributing to the Hyperbion Tripolar Network project! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. We expect everyone to:

- Be respectful and considerate
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling, insulting, or derogatory remarks
- Public or private harassment
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Violations of the Code of Conduct may be reported to the project maintainers. All complaints will be reviewed and investigated, and will result in a response that is deemed necessary and appropriate to the circumstances.

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.10 or higher
- Git installed and configured
- A GitHub account
- Basic knowledge of neural networks and Python

### Setting Up Your Development Environment

1. **Fork the repository**
   ```bash
   # Fork via GitHub UI, then clone your fork
   git clone https://github.com/YOUR_USERNAME/tripolar-index.git
   cd tripolar-index
   ```

2. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/LashSesh/tripolar-index.git
   ```

3. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .

   # Install development dependencies
   pip install pytest pytest-cov black flake8 isort mypy
   ```

5. **Verify installation**
   ```bash
   pytest
   python examples/basic_simulation.py
   ```

---

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

#### 🐛 Bug Reports
Found a bug? Please create an issue with:
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Minimal code example

#### 💡 Feature Requests
Have an idea? Create an issue describing:
- The problem it solves
- Proposed solution
- Alternative approaches considered
- Willingness to implement

#### 📝 Documentation
Improve documentation by:
- Fixing typos or clarifications
- Adding examples
- Writing tutorials
- Translating documentation

#### 🔧 Code Contributions
Submit code for:
- Bug fixes
- New features
- Performance improvements
- Test coverage
- Refactoring

#### 🧪 Testing
Help by:
- Writing new tests
- Improving test coverage
- Creating benchmark tests
- Testing on different platforms

---

## Development Workflow

### 1. Create an Issue (Optional but Recommended)

For significant changes, create an issue first to discuss the approach:

```markdown
Title: Add [Feature Name]

## Description
Brief description of what you want to add/change

## Motivation
Why is this change needed?

## Proposed Implementation
High-level approach

## Alternatives Considered
Other approaches you've thought about

## Additional Context
Any other relevant information
```

### 2. Create a Branch

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-123
```

**Branch Naming Convention**:
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation updates
- `test/description` - Test improvements
- `refactor/description` - Code refactoring

### 3. Make Changes

- Write clean, readable code
- Follow coding standards (see below)
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 4. Test Your Changes

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=hyperbion --cov-report=html

# Run specific tests
pytest tests/test_network.py

# Check code style
black --check .
flake8 .
isort --check-only .

# Type checking (optional)
mypy src/hyperbion
```

### 5. Commit Changes

Follow conventional commit format:

```bash
git commit -m "type(scope): description

Longer explanation if needed

Fixes #123"
```

**Commit Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples**:
```bash
git commit -m "feat(operators): add CustomOperator for pattern matching"
git commit -m "fix(network): resolve cell deletion race condition"
git commit -m "docs(api): add examples for persistence API"
git commit -m "test(quadrupole): increase coverage for mirror state"
```

### 6. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create PR via GitHub UI
```

---

## Coding Standards

### Python Style

We follow **PEP 8** with these specifics:

#### Formatting

- **Formatter**: Black (line length: 100)
- **Import sorting**: isort with Black profile
- **Linting**: flake8

```bash
# Auto-format code
black .

# Sort imports
isort .

# Check linting
flake8 .
```

#### Naming Conventions

```python
# Classes: PascalCase
class GabrielCell:
    pass

# Functions/methods: snake_case
def calculate_activation():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_WEIGHT = 5.0

# Private: leading underscore
def _internal_helper():
    pass

# Protected: single underscore
self._protected_var = value

# Strongly private: double underscore
self.__private_var = value
```

#### Type Hints

Always add type hints for public APIs:

```python
from typing import Dict, List, Optional, Union

def add_cell(
    self,
    state: int,
    bias: float = 0.0,
    plasticity_params: Optional[PlasticityParams] = None
) -> int:
    """Add a cell to the network."""
    pass
```

#### Docstrings

Use Google-style docstrings:

```python
def apply_operator(
    self,
    operator: str,
    targets: List[int],
    **params
) -> OperatorResult:
    """
    Apply an operator to target cells.

    This method applies the specified operator to the target cells,
    potentially modifying network structure or dynamics.

    Args:
        operator: Operator name ('DK', 'SW', 'WT', 'Nullpunkt', 'MOR')
        targets: List of target cell IDs
        **params: Operator-specific parameters
            - delta (float): For DK operator
            - lambda_factor (float): For SW operator
            - mode (str): For Morphogenesis

    Returns:
        OperatorResult containing:
            - success (bool): Whether operation succeeded
            - affected_cells (List[int]): Modified cell IDs
            - metrics (Dict): Performance metrics
            - message (str): Status message

    Raises:
        ValueError: If operator name is invalid
        CellNotFoundError: If target cells don't exist
        OperatorError: If operator application fails

    Example:
        >>> network = HyperbionNetwork()
        >>> cells = [network.add_cell(state=1) for _ in range(5)]
        >>> result = network.apply_operator('DK', cells, delta=0.5)
        >>> print(result.success)
        True

    Note:
        Some operators may create or delete cells, changing the
        network structure. Always check the result for affected cells.

    See Also:
        - :class:`OperatorResult`: Result dataclass
        - :meth:`get_operator_history`: View operator history
    """
    pass
```

### Code Organization

#### File Structure

```python
"""
Module docstring describing the module's purpose.

This module implements [description].
"""

# Standard library imports
import time
from typing import Dict, List

# Third-party imports
import numpy as np
from fastapi import FastAPI

# Local imports
from hyperbion.core import GabrielCell
from hyperbion.operators import BaseOperator

# Constants
DEFAULT_THRESHOLD = 0.5
MAX_ITERATIONS = 1000

# Classes
class MyClass:
    """Class docstring."""
    pass

# Functions
def my_function():
    """Function docstring."""
    pass

# Main execution
if __name__ == "__main__":
    main()
```

#### Import Organization

Use isort with Black profile:

```python
# Standard library
import os
import sys
from typing import Any, Dict

# Third-party
import numpy as np
import pytest
from fastapi import FastAPI

# Local application
from hyperbion.core.network import HyperbionNetwork
from hyperbion.operators.base import BaseOperator
```

### Error Handling

```python
# Good: Specific exceptions
try:
    cell = network.get_cell(cell_id)
except CellNotFoundError as e:
    logger.error(f"Cell {cell_id} not found: {e}")
    raise

# Bad: Bare except
try:
    cell = network.get_cell(cell_id)
except:  # Don't do this!
    pass

# Good: Custom exceptions
class NetworkError(Exception):
    """Base exception for network errors."""
    pass

class CellNotFoundError(NetworkError):
    """Cell not found in network."""

    def __init__(self, cell_id: int):
        self.cell_id = cell_id
        super().__init__(f"Cell {cell_id} not found")
```

---

## Testing Guidelines

### Test Organization

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_network.py          # Network tests
├── test_operators.py        # Operator tests
├── test_quadrupole.py       # Quadrupole tests
└── integration/
    └── test_workflows.py    # Integration tests
```

### Writing Tests

#### Unit Tests

```python
import pytest
from hyperbion import HyperbionNetwork

def test_add_cell_basic():
    """Test basic cell addition."""
    network = HyperbionNetwork()
    cell_id = network.add_cell(state=1, bias=0.5)

    assert cell_id == 0
    assert len(network.cells) == 1
    assert network.cells[cell_id].state == 1
    assert network.cells[cell_id].bias == 0.5

def test_add_cell_invalid_state():
    """Test that invalid states raise ValueError."""
    network = HyperbionNetwork()

    with pytest.raises(ValueError, match="State must be -1, 0, or 1"):
        network.add_cell(state=5)

@pytest.mark.parametrize("state,expected", [
    (-1, -1),
    (0, 0),
    (1, 1),
])
def test_add_cell_states(state, expected):
    """Test all valid states."""
    network = HyperbionNetwork()
    cell_id = network.add_cell(state=state)
    assert network.cells[cell_id].state == expected
```

#### Fixtures

```python
# conftest.py
import pytest
from hyperbion import HyperbionNetwork

@pytest.fixture
def empty_network():
    """Provide an empty network."""
    return HyperbionNetwork(name="TestNetwork")

@pytest.fixture
def simple_network():
    """Provide a simple 10-cell network."""
    network = HyperbionNetwork()
    cells = [network.add_cell(state=1) for _ in range(10)]
    for i in range(len(cells) - 1):
        network.connect_cells(cells[i], cells[i+1], 1.0)
    return network

@pytest.fixture
def clustered_network():
    """Provide a network with defined clusters."""
    network = HyperbionNetwork()
    # Create two clusters
    cluster1 = [network.add_cell(state=1) for _ in range(5)]
    cluster2 = [network.add_cell(state=-1) for _ in range(5)]

    # Connect within clusters
    for i in range(4):
        network.connect_cells(cluster1[i], cluster1[i+1], 1.0)
        network.connect_cells(cluster2[i], cluster2[i+1], 1.0)

    # Connect between clusters (weakly)
    network.connect_cells(cluster1[4], cluster2[0], 0.1)

    return network, cluster1, cluster2
```

#### Integration Tests

```python
def test_full_simulation_workflow(simple_network):
    """Test complete simulation workflow."""
    network = simple_network

    # Run simulation
    results = network.run(num_steps=100, noise_level=0.1, apply_plasticity=True)

    assert len(results) == 100
    assert network.step_count == 100

    # Verify operators were triggered
    history = network.get_operator_history()
    assert len(history) > 0

    # Verify metrics
    metrics = network.get_metrics()
    assert 'information_capacity' in metrics
    assert metrics['information_capacity'] > 0
```

### Test Coverage Goals

- **Overall**: > 85%
- **Core modules**: > 90%
- **Operators**: > 85%
- **API**: > 80%

```bash
# Generate coverage report
pytest --cov=hyperbion --cov-report=html

# View report
open htmlcov/index.html
```

---

## Documentation

### Inline Documentation

- Add docstrings to all public classes, methods, and functions
- Use Google-style docstrings
- Include examples where helpful
- Document parameters, return values, and exceptions

### README Updates

If your change affects usage, update README.md:
- Installation instructions
- Quick start examples
- API changes
- New features

### API Documentation

For new APIs, add to `docs/API_GUIDE.md`:
- Method signatures
- Parameters and return values
- Usage examples
- Related methods

### Architecture Documentation

For architectural changes, update `docs/ARCHITECTURE.md`:
- New components
- Design patterns
- Data flow changes

---

## Pull Request Process

### Before Submitting

Checklist:
- [ ] Code follows style guidelines
- [ ] All tests pass (`pytest`)
- [ ] Code is formatted (`black .`)
- [ ] Imports are sorted (`isort .`)
- [ ] No linting errors (`flake8 .`)
- [ ] New code has tests
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### PR Template

When creating a PR, use this template:

```markdown
## Description
Brief description of the changes

Fixes #(issue number)

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
Describe the tests you added/ran:
- Test 1
- Test 2

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code where needed
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests
- [ ] All tests pass locally
- [ ] Any dependent changes have been merged

## Screenshots (if applicable)
Add screenshots to show before/after or new features

## Additional Notes
Any additional information for reviewers
```

### Review Process

1. **Automated Checks**: CI must pass
2. **Code Review**: At least one maintainer approval required
3. **Discussion**: Address reviewer feedback
4. **Updates**: Make requested changes
5. **Merge**: Maintainer merges when approved

### After Merge

- Delete your feature branch
- Close related issues
- Update any related documentation
- Celebrate! 🎉

---

## Community

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Questions, ideas, general discussion
- **Pull Requests**: Code contributions

### Getting Help

If you need help:
1. Check existing documentation
2. Search closed issues
3. Ask in GitHub Discussions
4. Create a new issue if needed

### Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Project README

---

## License

By contributing to Hyperbion Tripolar Network, you agree that your contributions will be licensed under the MIT License.

---

## Questions?

If you have questions about contributing, please:
1. Check this guide
2. Search existing issues
3. Ask in GitHub Discussions
4. Contact maintainers

Thank you for contributing to Hyperbion Tripolar Network!

---

**Last Updated**: 2025-11-17
**Version**: 1.0
