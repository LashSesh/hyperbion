# Hyperbion Tripolar Neural Network

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)
[![Code Coverage](https://img.shields.io/badge/coverage-high-brightgreen.svg)](tests/)

> **A post-symbolic, self-organizing neural network architecture based on tripolar logic, structural plasticity, and autonomous operators.**

Implementation of the **Delta-Blueprint-1.0** specification by Sebastian Klemm.

## Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Quadrupole Architecture](#-quadrupole-architecture)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Documentation](#-documentation)
- [Examples](#-examples)
- [API Reference](#-api-reference)
- [Benchmarks](#-benchmarks)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)

## 🆕 **NEW: Quadrupole Architecture**

The system has evolved into a **Quadrupole Tripolar Neural Network** with:
- **4 Resonant Clusters** in quadrupole arrangement (Q₀, Q₁, Q₂, Q₃)
- **Rotating Phase Space** Θ(t) determining active cluster
- **Holistic Mirror State** H(t) as third oscillating mode (LD)
- **Quantum-Hybrid Communication** between clusters

See **[QUADRUPOLE_ARCHITECTURE.md](QUADRUPOLE_ARCHITECTURE.md)** for complete documentation.

---

## 🌟 Overview

The Hyperbion Tripolar Network is a novel neural network architecture featuring:

- **Tripolar Logic**: States ∈ {-1, 0, +1} representing inhibition, neutral, and activation
- **Gabriel Cells**: Fundamental units with dynamic plasticity and adaptive connections
- **Autonomous Operators**: Self-organizing mechanisms (DK, SW, WT, Nullpunkt, MOR)
- **Structural Plasticity**: Network topology evolves through morphogenesis
- **Emergent Behavior**: Self-organization without explicit programming

## 🎯 Key Features

### Core Components

1. **Gabriel Cells**
   - Tripolar state dynamics
   - Weighted, directed connections
   - Hebbian-style plasticity with morphogenesis
   - Wormhole (temporal) connections
   - State history tracking

2. **Operators**
   - **DK (Doppelkick)**: Synchronous cluster amplification
   - **SW (Sweep)**: Weight normalization and stabilization
   - **WT (Wormhole)**: Temporal shortcuts between clusters
   - **Nullpunkt**: Reset and deletion for healing
   - **MOR (Morphogenesis)**: Cell division, fusion, and growth

3. **Network Architecture**
   - Dynamic clustering
   - Topological distance calculation
   - Automatic cluster detection
   - Event history and replay
   - Comprehensive metrics tracking

4. **Persistence & Export**
   - State saving/loading (JSON, Pickle)
   - Checkpoint management
   - Export to GraphML, LaTeX/TikZ, CSV
   - History replay

5. **REST API**
   - Complete FastAPI-based interface
   - Real-time network control
   - Metrics and visualization endpoints
   - Operator application API

## 📦 Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/tripolar-index.git
cd tripolar-index

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

### Requirements

- Python 3.10+
- NumPy >= 1.24.0
- SciPy >= 1.10.0
- FastAPI >= 0.109.0
- NetworkX >= 3.2
- See `requirements.txt` for full list

## 🚀 Quick Start

### Basic Usage

```python
from hyperbion import HyperbionNetwork

# Create network
network = HyperbionNetwork(name="MyNetwork")

# Add cells
cell1 = network.add_cell(state=1, bias=0.5)
cell2 = network.add_cell(state=0, bias=0.0)
cell3 = network.add_cell(state=-1, bias=-0.3)

# Connect cells
network.connect_cells(cell1, cell2, weight=1.5)
network.connect_cells(cell2, cell3, weight=-0.8)

# Run simulation
for _ in range(100):
    result = network.step(
        noise_level=0.1,
        apply_plasticity=True,
        auto_trigger_operators=True
    )

# Get network state
state = network.get_state()
print(f"Network has {len(network.cells)} cells after {network.step_count} steps")
```

### Using Operators

```python
# Create a cluster
cells = [network.add_cell(state=1) for _ in range(5)]

# Connect cells within cluster
for i in range(len(cells) - 1):
    network.connect_cells(cells[i], cells[i + 1], 1.0)

# Apply Doppelkick operator
result = network.apply_operator('DK', cells)
print(f"DK applied: {result.success}, affected {len(result.affected_cells)} cells")

# Apply Morphogenesis to divide a cell
result = network.apply_operator('MOR', [cells[0]], mode='divide')
print(f"Cell division: {result.metrics['created_cells']} new cells")
```

### Persistence

```python
from hyperbion.persistence import NetworkPersistence

# Save network state
NetworkPersistence.save_state(network, 'network_state.json', format='json')

# Load network state
loaded_network = NetworkPersistence.load_state('network_state.json', format='json')

# Create checkpoint
checkpoint_path = NetworkPersistence.create_checkpoint(
    network,
    checkpoint_dir='./checkpoints',
    name='experiment_1'
)
```

### Export

```python
from hyperbion.persistence import GraphMLExporter, LaTeXExporter, CSVExporter

# Export to GraphML
GraphMLExporter.export(network, 'network.graphml')

# Export to LaTeX
LaTeXExporter.export(network, 'network.tex')

# Export cells to CSV
CSVExporter.export_cells(network, 'cells.csv')
CSVExporter.export_connections(network, 'connections.csv')
CSVExporter.export_metrics(network, 'metrics.csv')
```

## 🌐 REST API

### Starting the API Server

```bash
# Start the server
python -m hyperbion.api.server

# Or using uvicorn directly
uvicorn hyperbion.api.server:app --host 0.0.0.0 --port 8000
```

### API Documentation

Once running, visit:
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### Example API Calls

```bash
# Create network
curl -X POST http://localhost:8000/network/create \
  -H "Content-Type: application/json" \
  -d '{"name": "APINetwork"}'

# Add cell
curl -X POST http://localhost:8000/network/add_cell \
  -H "Content-Type: application/json" \
  -d '{"state": 1, "bias": 0.5}'

# Run simulation step
curl -X POST http://localhost:8000/network/step \
  -H "Content-Type: application/json" \
  -d '{"noise_level": 0.1, "apply_plasticity": true}'

# Apply operator
curl -X POST http://localhost:8000/network/apply_operator \
  -H "Content-Type: application/json" \
  -d '{"operator": "DK", "targets": [0, 1, 2]}'

# Get network state
curl http://localhost:8000/network/state

# Export to GraphML
curl -X POST http://localhost:8000/network/export \
  -H "Content-Type: application/json" \
  -d '{"format": "graphml"}' \
  --output network.graphml
```

## 📚 Documentation

Comprehensive documentation is available:

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture and design patterns
- **[API_GUIDE.md](docs/API_GUIDE.md)** - Complete API reference and usage
- **[DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Developer guide and best practices
- **[PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md)** - Production readiness roadmap
- **[QUADRUPOLE_ARCHITECTURE.md](QUADRUPOLE_ARCHITECTURE.md)** - Quadrupole system details
- **[BENCHMARKS.md](BENCHMARKS.md)** - Benchmark system documentation
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines

## 📊 Examples

See the `examples/` directory for complete examples:

- `basic_simulation.py`: Simple network simulation
- `operator_showcase.py`: Demonstrating all operators
- `quadrupole_demo.py`: Quadrupole architecture demonstration

### Running Examples

```bash
python examples/basic_simulation.py
python examples/operator_showcase.py
python examples/quadrupole_demo.py
```

## 📈 Benchmarking

### Comprehensive Benchmark Suite

The project includes a complete benchmark system comparing Hyperbion Tripolar Network with classical binary networks:

```bash
# Run full benchmark suite
python benchmarks/run_benchmark.py
```

### Benchmark Tasks

1. **Pattern Classification**: Multi-class pattern recognition with noise
2. **Memory Capacity**: Storage and recall of distinct patterns
3. **Association Learning**: Input-output mapping tasks

### Success Criteria

- ✅ **Information Advantage ≥ 58.5%** (theoretical: log₂(3)/log₂(2) - 1)
- ✅ **System Advantage ≥ 2x** (accounting for operators and efficiency)
- ✅ **Reproducibility**: Deterministic results with full history

### Benchmark Output

Results are generated in `benchmark_results/`:
- `benchmark_summary.txt` - Text summary
- `benchmark_results.json` - Complete data
- `benchmark_comparison.csv` - Tabular comparison
- `benchmark_report.tex` - LaTeX report (compile with pdflatex)

See [BENCHMARKS.md](BENCHMARKS.md) for detailed documentation.

## 🧪 Testing

### Run All Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=hyperbion --cov-report=html

# Run specific test file
pytest tests/test_gabriel_cell.py
pytest tests/test_network.py
pytest tests/test_operators.py
```

## 📖 Mathematical Model

### State Update

```
s_i^{t+1} = sign(Σ_j w_ij s_j^t + b_i + η_i^t)
```

Where:
- `sign(x) = +1 if x > θ_pos, -1 if x < θ_neg, 0 otherwise`
- `η_i^t` = noise term

### Plasticity Rule

```
Δw_ij = α s_i s_j - β w_ij + γ f_morph(C_ij, t)
```

Where:
- `α` = Hebbian learning rate
- `β` = weight decay
- `γ` = morphogenesis factor
- `f_morph` = morphogenesis function

### Operator Effects

| Operator | Effect | Trigger |
|----------|--------|---------|
| **DK** | `w_ij += δ_DK` | High coherence |
| **SW** | `w_ij → λ w_ij` | High activity/variance |
| **WT** | `w_ik^{(WT)} ≠ 0` (temporal) | Distance threshold |
| **Nullpunkt** | `w_ij → 0` or cell deletion | Anomaly detection |
| **MOR** | Cell division/fusion | Stress threshold |

## 🏗️ Architecture

```
src/hyperbion/
├── core/
│   ├── gabriel_cell.py      # Gabriel cell implementation
│   └── network.py            # Network orchestrator
├── operators/
│   ├── base.py               # Operator base class
│   ├── doppelkick.py         # DK operator
│   ├── sweep.py              # SW operator
│   ├── wormhole.py           # WT operator
│   ├── nullpunkt.py          # Nullpunkt operator
│   └── morphogenesis.py      # MOR operator
├── persistence/
│   ├── persistence.py        # State management
│   └── exporters.py          # Export utilities
├── api/
│   └── server.py             # FastAPI server
└── utils/                    # Utility functions
```

## 📈 Performance

Benchmarks on standard hardware (i7-8700K, 32GB RAM):

| Network Size | Step Time | Memory Usage |
|--------------|-----------|--------------|
| 100 cells    | ~2ms      | ~50MB        |
| 1,000 cells  | ~20ms     | ~200MB       |
| 10,000 cells | ~200ms    | ~1.5GB       |

See `examples/benchmark.py` for detailed benchmarks.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

Quick checklist:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests for new features
4. Ensure all tests pass (`pytest`)
5. Follow code style guidelines (`black`, `flake8`)
6. Commit your changes with clear messages
7. Push and submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👥 Authors & Contributors

**Blueprint Specification**: Sebastian Klemm (Delta-Blueprint-1.0)

**Implementation**: Hyperbion Development Team

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for a list of all contributors.

## 🔗 References & Resources

### Documentation
- [Architecture Guide](docs/ARCHITECTURE.md)
- [API Reference](docs/API_GUIDE.md)
- [Developer Guide](docs/DEVELOPMENT.md)

### Scientific Background
- Delta-Blueprint-1.0 Specification
- Tripolar Logic Theory
- Information Theory & Shannon Entropy
- Self-Organizing Systems

### Related Projects
- Gabriel Cell Theory
- Structural Plasticity in Neural Networks
- Autonomous Operator Systems

## 📞 Support & Community

### Getting Help
- **Documentation**: Check the [docs/](docs/) directory
- **GitHub Issues**: [Report bugs or request features](https://github.com/LashSesh/tripolar-index/issues)
- **Discussions**: [Join community discussions](https://github.com/LashSesh/tripolar-index/discussions)

### Reporting Issues
Please include:
- Python version and OS
- Minimal reproducible example
- Expected vs actual behavior
- Relevant logs or error messages

## 🎯 Project Status

- **Current Version**: 1.0.0
- **Status**: Production Ready ✅
- **Test Coverage**: High
- **CI/CD**: Automated via GitHub Actions
- **Last Updated**: 2025-11-17

## 🚀 Future Roadmap

See [PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md) for detailed plans including:
- Performance optimization
- Scalability improvements
- Advanced features
- Production deployment guides
- Enterprise support

---

**Note**: This is a research-grade implementation of the Hyperbion Tripolar Network concept, designed for experimentation, simulation, educational purposes, and production deployment with appropriate testing and validation.
