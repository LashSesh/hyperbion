# Hyperbion Tripolar Network - Development Guide

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Style](#code-style)
- [Debugging](#debugging)
- [Performance Profiling](#performance-profiling)
- [Adding Features](#adding-features)
- [Release Process](#release-process)

---

## Development Setup

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Git
- Virtual environment tool (venv, conda, or virtualenv)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/LashSesh/tripolar-index.git
cd tripolar-index

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black flake8 isort mypy
```

### IDE Configuration

#### VS Code

Recommended `settings.json`:
```json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "editor.formatOnSave": true,
    "python.sortImports.args": [
        "--profile",
        "black"
    ]
}
```

Recommended extensions:
- Python (Microsoft)
- Pylance
- Python Test Explorer
- GitLens

#### PyCharm

1. Set interpreter to virtual environment
2. Enable pytest as test runner
3. Configure Black as formatter
4. Enable flake8 inspections

---

## Project Structure

```
tripolar-index/
├── src/hyperbion/              # Main package
│   ├── __init__.py
│   ├── core/                   # Core components
│   │   ├── gabriel_cell.py     # Cell implementation
│   │   └── network.py          # Network orchestrator
│   ├── operators/              # Operator implementations
│   │   ├── base.py
│   │   ├── doppelkick.py
│   │   ├── sweep.py
│   │   ├── wormhole.py
│   │   ├── nullpunkt.py
│   │   └── morphogenesis.py
│   ├── quadrupole/             # Quadrupole architecture
│   │   ├── tripolar_cell.py
│   │   ├── phase_system.py
│   │   ├── mirror_state.py
│   │   ├── communication.py
│   │   └── quadrupole_network.py
│   ├── persistence/            # State management
│   │   ├── persistence.py
│   │   └── exporters.py
│   ├── api/                    # REST API
│   │   └── server.py
│   ├── benchmark/              # Benchmark system
│   │   ├── binary_network.py
│   │   ├── tasks.py
│   │   ├── runner.py
│   │   ├── metrics.py
│   │   ├── comparator.py
│   │   └── report.py
│   └── utils/                  # Utilities
│       └── visualization.py
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_network.py
│   ├── test_operators.py
│   └── test_quadrupole.py
├── examples/                   # Example scripts
│   ├── basic_simulation.py
│   ├── operator_showcase.py
│   └── quadrupole_demo.py
├── benchmarks/                 # Benchmark scripts
│   └── run_benchmark.py
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md
│   ├── API_GUIDE.md
│   └── DEVELOPMENT.md
├── .github/                    # GitHub configuration
│   └── workflows/
│       └── ci.yml
├── setup.py                    # Package setup
├── requirements.txt            # Dependencies
├── README.md                   # Main documentation
└── LICENSE                     # MIT License
```

### Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| `core/` | Fundamental network and cell logic |
| `operators/` | Network modification operators |
| `quadrupole/` | Advanced quadrupole architecture |
| `persistence/` | State save/load, export |
| `api/` | REST API server |
| `benchmark/` | Performance benchmarking |
| `utils/` | Helper functions, visualization |

---

## Development Workflow

### 1. Feature Development

```bash
# Create feature branch
git checkout -b feature/my-new-feature

# Make changes
# ... edit files ...

# Run tests
pytest

# Check code style
black .
flake8 .
isort .

# Commit changes
git add .
git commit -m "Add my new feature"

# Push to remote
git push origin feature/my-new-feature

# Create pull request on GitHub
```

### 2. Bug Fixes

```bash
# Create bugfix branch
git checkout -b bugfix/issue-123

# Fix the bug
# ... edit files ...

# Add test for the bug
# ... create test_bugfix.py ...

# Verify fix
pytest tests/test_bugfix.py

# Commit
git commit -m "Fix issue #123: description"

# Push and create PR
git push origin bugfix/issue-123
```

### 3. Code Review Checklist

Before submitting a PR:

- [ ] All tests pass (`pytest`)
- [ ] Code is formatted (`black .`)
- [ ] No linting errors (`flake8 .`)
- [ ] Imports sorted (`isort .`)
- [ ] New features have tests
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)
- [ ] No debug print statements
- [ ] Type hints added (where applicable)

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=hyperbion --cov-report=html

# Run specific test file
pytest tests/test_network.py

# Run specific test function
pytest tests/test_network.py::test_add_cell

# Run with verbose output
pytest -v

# Run and stop at first failure
pytest -x

# Run tests matching pattern
pytest -k "test_operator"
```

### Writing Tests

#### Unit Tests

```python
# tests/test_my_feature.py
import pytest
from hyperbion import HyperbionNetwork

def test_my_feature():
    """Test description."""
    # Arrange
    network = HyperbionNetwork()
    cell_id = network.add_cell(state=1)

    # Act
    result = network.my_new_method(cell_id)

    # Assert
    assert result is not None
    assert result['success'] == True

def test_my_feature_error_handling():
    """Test error conditions."""
    network = HyperbionNetwork()

    with pytest.raises(ValueError):
        network.my_new_method(-1)  # Invalid cell ID
```

#### Integration Tests

```python
def test_operator_chain():
    """Test multiple operators working together."""
    network = HyperbionNetwork()

    # Create cluster
    cells = [network.add_cell(state=1) for _ in range(5)]
    for i in range(len(cells) - 1):
        network.connect_cells(cells[i], cells[i+1], 1.0)

    # Apply operators in sequence
    result1 = network.apply_operator('DK', cells)
    assert result1.success

    result2 = network.apply_operator('SW', cells)
    assert result2.success

    result3 = network.apply_operator('MOR', [cells[0]], mode='divide')
    assert result3.success

    # Verify network state
    assert len(network.cells) > len(cells)
```

#### Fixtures

```python
# tests/conftest.py
import pytest
from hyperbion import HyperbionNetwork

@pytest.fixture
def empty_network():
    """Provide an empty network."""
    return HyperbionNetwork(name="TestNetwork")

@pytest.fixture
def simple_network():
    """Provide a network with basic structure."""
    net = HyperbionNetwork()
    cells = [net.add_cell(state=1) for _ in range(10)]
    for i in range(len(cells) - 1):
        net.connect_cells(cells[i], cells[i+1], 1.0)
    return net

# Use in tests
def test_with_fixture(simple_network):
    assert simple_network.num_cells() == 10
```

### Test Coverage Goals

- **Core components**: > 90%
- **Operators**: > 85%
- **API**: > 80%
- **Overall**: > 85%

---

## Code Style

### Python Style Guide

We follow PEP 8 with these specific guidelines:

#### Formatting

```python
# Use Black for auto-formatting
black src/ tests/

# Line length: 100 characters
# Indentation: 4 spaces
# String quotes: Double quotes preferred
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

# Private members: leading underscore
def _internal_method():
    pass
```

#### Type Hints

```python
from typing import Dict, List, Optional, Tuple

def add_cell(
    self,
    state: int,
    bias: float = 0.0
) -> int:
    """Add a cell to the network."""
    pass

def get_connections(self, cell_id: int) -> Dict[int, float]:
    """Get cell connections."""
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

    Args:
        operator: Operator name ('DK', 'SW', 'WT', 'Nullpunkt', 'MOR')
        targets: List of target cell IDs
        **params: Operator-specific parameters

    Returns:
        OperatorResult containing success status and metrics

    Raises:
        ValueError: If operator name is invalid
        CellNotFoundError: If target cells don't exist

    Example:
        >>> result = network.apply_operator('DK', [0, 1, 2], delta=0.5)
        >>> print(result.success)
        True
    """
    pass
```

### Import Organization

Use isort with Black profile:

```python
# Standard library
import time
from typing import Dict, List

# Third-party
import numpy as np
from fastapi import FastAPI

# Local
from hyperbion.core import GabrielCell
from hyperbion.operators import BaseOperator
```

### Linting

```bash
# Run flake8
flake8 src/ tests/

# Common rules:
# E501: Line too long (handled by Black)
# W503: Line break before binary operator (Black style)
# F401: Imported but unused

# Configure in setup.cfg or .flake8:
[flake8]
max-line-length = 100
extend-ignore = E203, W503
exclude = .git,__pycache__,venv
```

---

## Debugging

### Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Use in code
def step(self):
    logger.debug(f"Starting step {self.step_count}")
    # ... code ...
    logger.info(f"Completed step {self.step_count}")
```

### Debugging Tools

#### pdb (Python Debugger)

```python
import pdb

def problematic_function():
    x = calculate_something()
    pdb.set_trace()  # Breakpoint
    y = process(x)
    return y
```

#### VS Code Debugger

`launch.json` configuration:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        },
        {
            "name": "Python: Run Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["-v"],
            "console": "integratedTerminal"
        }
    ]
}
```

#### Debugging Network State

```python
def debug_network(network):
    """Print detailed network state."""
    print(f"=== Network Debug ===")
    print(f"Cells: {len(network.cells)}")
    print(f"Connections: {sum(len(c.connections) for c in network.cells.values())}")
    print(f"Step: {network.step_count}")

    print("\nCell States:")
    for cell_id, cell in network.cells.items():
        print(f"  Cell {cell_id}: state={cell.state}, bias={cell.bias}")

    print("\nOperator History:")
    for event in network.get_operator_history()[-5:]:
        print(f"  {event['operator']} on {event['targets']}")
```

---

## Performance Profiling

### Timing

```python
import time

def profile_step():
    """Profile network step performance."""
    network = create_large_network()  # 1000 cells

    start = time.time()
    network.step()
    elapsed = time.time() - start

    print(f"Step time: {elapsed*1000:.2f}ms")
```

### cProfile

```python
import cProfile
import pstats

def profile_simulation():
    """Profile full simulation."""
    profiler = cProfile.Profile()
    profiler.enable()

    # Run simulation
    network = HyperbionNetwork()
    # ... setup ...
    network.run(num_steps=100)

    profiler.disable()

    # Print stats
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions
```

### Memory Profiling

```python
from memory_profiler import profile

@profile
def memory_intensive_operation():
    """Profile memory usage."""
    network = HyperbionNetwork()
    for _ in range(10000):
        network.add_cell(state=1)
    return network
```

### Benchmarking

```python
import timeit

def benchmark_operators():
    """Benchmark operator performance."""
    setup = """
from hyperbion import HyperbionNetwork
network = HyperbionNetwork()
cells = [network.add_cell(state=1) for _ in range(100)]
for i in range(99):
    network.connect_cells(cells[i], cells[i+1], 1.0)
"""

    operators = ['DK', 'SW', 'WT', 'Nullpunkt', 'MOR']

    for op in operators:
        code = f"network.apply_operator('{op}', cells[:10])"
        time = timeit.timeit(code, setup=setup, number=100)
        print(f"{op}: {time/100*1000:.2f}ms per call")
```

---

## Adding Features

### 1. New Operator

```python
# src/hyperbion/operators/my_operator.py
from hyperbion.operators.base import BaseOperator, OperatorResult

class MyOperator(BaseOperator):
    """
    My custom operator.

    Purpose: [Describe what it does]
    Trigger: [When it should activate]
    Effect: [What it modifies]
    """

    def __init__(self):
        super().__init__(name="MYOP")
        self.threshold = 0.5

    def should_trigger(self, network, targets):
        """Check if operator should trigger."""
        # Implement trigger logic
        return len(targets) >= 3

    def apply(self, network, targets, **params):
        """Apply operator effect."""
        affected_cells = []
        metrics = {}

        try:
            for cell_id in targets:
                cell = network.get_cell(cell_id)
                # Implement modification
                affected_cells.append(cell_id)

            return OperatorResult(
                success=True,
                affected_cells=affected_cells,
                metrics=metrics,
                message=f"Applied to {len(affected_cells)} cells"
            )
        except Exception as e:
            return OperatorResult(
                success=False,
                affected_cells=[],
                metrics={},
                message=str(e)
            )

# Register in network.__init__ or operator registry
```

### 2. New Export Format

```python
# src/hyperbion/persistence/exporters.py
class MyFormatExporter:
    """Export to my custom format."""

    @staticmethod
    def export(network, filepath):
        """Export network to custom format."""
        data = {
            'cells': [],
            'connections': []
        }

        for cell_id, cell in network.cells.items():
            data['cells'].append({
                'id': cell_id,
                'state': cell.state,
                'bias': cell.bias
            })

        for source_id, source_cell in network.cells.items():
            for target_id, weight in source_cell.connections.items():
                data['connections'].append({
                    'source': source_id,
                    'target': target_id,
                    'weight': weight
                })

        # Write to file
        with open(filepath, 'w') as f:
            custom_write(f, data)
```

### 3. New Metric

```python
# Add to HyperbionNetwork
def get_spectral_radius(self):
    """Calculate spectral radius of weight matrix."""
    import numpy as np

    # Build adjacency matrix
    n = len(self.cells)
    W = np.zeros((n, n))

    cell_to_idx = {cell_id: i for i, cell_id in enumerate(self.cells.keys())}

    for source_id, source_cell in self.cells.items():
        i = cell_to_idx[source_id]
        for target_id, weight in source_cell.connections.items():
            j = cell_to_idx[target_id]
            W[i, j] = weight

    # Compute eigenvalues
    eigenvalues = np.linalg.eigvals(W)
    spectral_radius = np.max(np.abs(eigenvalues))

    return spectral_radius
```

---

## Release Process

### Version Numbering

We use Semantic Versioning (SemVer):

```
MAJOR.MINOR.PATCH

1.0.0 → Initial release
1.1.0 → New features (backward compatible)
1.1.1 → Bug fixes
2.0.0 → Breaking changes
```

### Release Checklist

1. **Update version**
   ```python
   # setup.py
   version="1.1.0"
   ```

2. **Update CHANGELOG.md**
   ```markdown
   ## [1.1.0] - 2025-11-17
   ### Added
   - New operator: MyOperator
   - Export to new format

   ### Changed
   - Improved performance of step()

   ### Fixed
   - Bug in cluster detection
   ```

3. **Run full test suite**
   ```bash
   pytest --cov=hyperbion --cov-report=html
   ```

4. **Build package**
   ```bash
   python setup.py sdist bdist_wheel
   ```

5. **Tag release**
   ```bash
   git tag -a v1.1.0 -m "Release 1.1.0"
   git push origin v1.1.0
   ```

6. **Create GitHub release**
   - Go to GitHub releases
   - Create new release from tag
   - Add release notes
   - Upload distribution files

### Continuous Integration

Our CI pipeline (`.github/workflows/ci.yml`) automatically:
- Runs tests on Python 3.10, 3.11, 3.12
- Checks code style
- Measures coverage
- Runs benchmarks
- Builds documentation

---

## Best Practices

### 1. Code Quality

- Write self-documenting code
- Add docstrings to all public APIs
- Use type hints
- Keep functions small and focused
- Follow SOLID principles

### 2. Testing

- Write tests before fixing bugs (TDD)
- Aim for high coverage
- Test edge cases
- Use fixtures to reduce duplication
- Mock external dependencies

### 3. Performance

- Profile before optimizing
- Use appropriate data structures
- Avoid premature optimization
- Document performance characteristics
- Add benchmarks for critical paths

### 4. Documentation

- Keep README.md up to date
- Document all public APIs
- Add examples for complex features
- Update architecture docs when needed
- Write clear commit messages

### 5. Git Workflow

- Use feature branches
- Write descriptive commit messages
- Keep commits atomic
- Rebase before merging (optional)
- Delete merged branches

---

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Solution: Install in development mode
pip install -e .
```

#### Test Failures
```bash
# Run specific test with verbose output
pytest tests/test_network.py::test_add_cell -v

# Check for stale .pyc files
find . -name "*.pyc" -delete
```

#### Slow Tests
```bash
# Profile test execution
pytest --durations=10

# Run only fast tests
pytest -m "not slow"
```

---

## Resources

### Documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [API_GUIDE.md](API_GUIDE.md) - API reference
- [PRODUCTION_ROADMAP.md](../PRODUCTION_ROADMAP.md) - Production plan

### External Resources
- [PEP 8](https://pep8.org/) - Python style guide
- [pytest docs](https://docs.pytest.org/) - Testing framework
- [Black](https://black.readthedocs.io/) - Code formatter
- [FastAPI](https://fastapi.tiangolo.com/) - API framework

### Community
- GitHub Issues
- GitHub Discussions
- Contributing Guide

---

## Getting Help

If you encounter issues:

1. Check existing documentation
2. Search GitHub issues
3. Ask in GitHub discussions
4. Create a new issue with:
   - Python version
   - OS
   - Minimal reproducible example
   - Expected vs actual behavior

Happy coding!
