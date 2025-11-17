# Hyperbion Tripolar Network - API Guide

## Table of Contents

- [Python API](#python-api)
- [REST API](#rest-api)
- [Quadrupole API](#quadrupole-api)
- [Persistence API](#persistence-api)
- [Operator API](#operator-api)
- [Benchmarking API](#benchmarking-api)
- [Code Examples](#code-examples)

---

## Python API

### HyperbionNetwork

The main network class for standard tripolar networks.

#### Initialization

```python
from hyperbion import HyperbionNetwork

network = HyperbionNetwork(
    name="MyNetwork",           # Network name
    auto_cluster=True,          # Auto-detect clusters
    max_history_length=1000     # History buffer size
)
```

#### Cell Management

##### add_cell
```python
cell_id = network.add_cell(
    state=1,                    # Initial state: -1, 0, or +1
    bias=0.5,                   # Cell bias term
    plasticity_params=None      # Optional PlasticityParams
)
# Returns: int (cell ID)
```

##### remove_cell
```python
success = network.remove_cell(cell_id)
# Returns: bool
```

##### get_cell
```python
cell = network.get_cell(cell_id)
# Returns: GabrielCell or None
```

##### get_all_cells
```python
cells = network.get_all_cells()
# Returns: Dict[int, GabrielCell]
```

#### Connection Management

##### connect_cells
```python
network.connect_cells(
    source_id=0,
    target_id=1,
    weight=1.5                  # Connection weight
)
```

##### disconnect_cells
```python
network.disconnect_cells(source_id=0, target_id=1)
```

##### get_connections
```python
connections = network.get_connections(cell_id)
# Returns: Dict[int, float] - {target_id: weight}
```

##### get_all_connections
```python
all_connections = network.get_all_connections()
# Returns: List[Tuple[int, int, float]] - [(source, target, weight), ...]
```

#### Cluster Management

##### create_cluster
```python
cluster_id = network.create_cluster(cell_ids=[0, 1, 2])
# Returns: int (cluster ID)
```

##### detect_clusters
```python
clusters = network.detect_clusters()
# Returns: List[Set[int]] - list of cell ID sets
```

##### get_cluster_cells
```python
cells = network.get_cluster_cells(cluster_id)
# Returns: Set[int]
```

##### get_cell_cluster
```python
cluster_id = network.get_cell_cluster(cell_id)
# Returns: int or None
```

#### Simulation

##### step
```python
result = network.step(
    noise_level=0.1,            # Noise std dev
    apply_plasticity=True,      # Apply Hebbian learning
    auto_trigger_operators=True # Auto-trigger operators
)
# Returns: Dict with keys:
# - 'step': step number
# - 'active_cells': number of active cells
# - 'operators_triggered': list of triggered operators
# - 'metrics': performance metrics
```

##### run
```python
results = network.run(
    num_steps=100,
    noise_level=0.1,
    apply_plasticity=True,
    auto_trigger_operators=True,
    progress_callback=None      # Optional callback(step, result)
)
# Returns: List[Dict] - results for each step
```

#### Operators

##### apply_operator
```python
result = network.apply_operator(
    operator='DK',              # 'DK', 'SW', 'WT', 'Nullpunkt', 'MOR'
    targets=[0, 1, 2],          # Target cell IDs
    **params                    # Operator-specific params
)
# Returns: OperatorResult with:
# - success: bool
# - affected_cells: List[int]
# - metrics: Dict
# - message: str
```

**Operator-Specific Parameters**:

**DK (Doppelkick)**:
```python
network.apply_operator('DK', targets, delta=0.5)
```

**SW (Sweep)**:
```python
network.apply_operator('SW', targets, lambda_factor=0.9)
```

**WT (Wormhole)**:
```python
network.apply_operator('WT', targets,
    source_cluster=0,
    target_cluster=1,
    expiry_time=100
)
```

**Nullpunkt**:
```python
network.apply_operator('Nullpunkt', targets,
    mode='reset_weights'  # 'reset_weights', 'reset_state', 'delete_cell', 'delete_connection'
)
```

**MOR (Morphogenesis)**:
```python
network.apply_operator('MOR', targets,
    mode='divide',  # 'divide', 'fuse', 'spawn', 'grow'
    params={'inherit_connections': True}
)
```

##### get_operator_history
```python
history = network.get_operator_history()
# Returns: List[Dict] with operator applications
```

#### State & Metrics

##### get_state
```python
state = network.get_state()
# Returns: Dict with:
# - 'name': str
# - 'step_count': int
# - 'num_cells': int
# - 'num_connections': int
# - 'num_clusters': int
# - 'cells': List[Dict]
# - 'connections': List[Dict]
# - 'clusters': Dict[int, List[int]]
```

##### get_metrics
```python
metrics = network.get_metrics()
# Returns: Dict with:
# - 'information_capacity': float (bits)
# - 'avg_activity': float
# - 'state_distribution': Dict[int, int]
# - 'network_coherence': float
# - 'avg_degree': float
```

##### get_network_statistics
```python
stats = network.get_network_statistics()
# Returns: Dict with detailed statistics
```

#### Distance & Topology

##### get_topological_distance
```python
distance = network.get_topological_distance(cell_id1, cell_id2)
# Returns: int (shortest path length) or None
```

##### get_clustering_coefficient
```python
coeff = network.get_clustering_coefficient()
# Returns: float
```

---

### GabrielCell

Individual cell API.

#### Properties

```python
cell.id                         # int: Cell ID
cell.state                      # int: Current state (-1, 0, +1)
cell.bias                       # float: Bias term
cell.connections                # Dict[int, float]: Connections
cell.wormhole_connections       # Dict[int, Tuple[float, float]]
cell.state_history              # List[int]: State timeline
cell.activation_history         # List[float]: Activation values
```

#### Methods

##### update_state
```python
new_state = cell.update_state(
    inputs={0: 1, 1: -1},       # {cell_id: state}
    noise=0.0
)
# Returns: int (new state)
```

##### apply_plasticity
```python
cell.apply_plasticity(
    network,                    # HyperbionNetwork reference
    learning_rate=1.0
)
```

##### get_activation
```python
activation = cell.get_activation(inputs={0: 1, 1: -1})
# Returns: float
```

---

### PlasticityParams

Configuration for plasticity rules.

```python
from hyperbion.core.gabriel_cell import PlasticityParams

params = PlasticityParams(
    alpha=0.01,                 # Hebbian learning rate
    beta=0.001,                 # Weight decay
    gamma=0.005,                # Morphogenesis factor
    theta_pos=0.5,              # Positive threshold
    theta_neg=-0.5,             # Negative threshold
    w_max=5.0,                  # Max weight
    w_min=-5.0                  # Min weight
)
```

---

## Quadrupole API

### QuadrupoleNetwork

Enhanced network with quadrupole architecture.

#### Initialization

```python
from hyperbion.quadrupole import QuadrupoleNetwork

network = QuadrupoleNetwork(
    name="MyQuadrupole",
    phase_delta=0.05,           # Phase increment per step
    mirror_coupling=0.3,        # LD coupling strength
    signature_dim=10            # Signature vector dimension
)
```

#### Cell Management

##### add_cell
```python
cell_id = network.add_cell(
    cluster_id=0,               # Cluster: 0, 1, 2, 3
    initial_x=0.5,              # Internal state [0,1]
    tau_0=0.3,                  # Lower threshold
    tau_1=0.7,                  # Upper threshold
    bias=0.0,
    phase=0.0,                  # Local phase
    mirror_coupling=0.3
)
# Returns: int (cell ID)
```

#### Simulation

##### step
```python
result = network.step(
    noise_level=0.05,
    apply_learning=True
)
# Returns: Dict with:
# - 'step': int
# - 'phase': float (Θ(t))
# - 'active_quadrant': int (0-3)
# - 'mirror_value': float (H(t))
# - 'coherence': float
# - 'cluster_signatures': Dict[int, np.ndarray]
```

#### Phase System

##### get_phase
```python
phase = network.get_phase()
# Returns: float ∈ [0,1)
```

##### get_active_quadrant
```python
quadrant = network.get_active_quadrant()
# Returns: int ∈ {0, 1, 2, 3}
```

#### Mirror State

##### get_mirror_state
```python
mirror_value = network.get_mirror_state()
# Returns: float ∈ [0,1]
```

##### get_cluster_signature
```python
signature = network.get_cluster_signature(cluster_id)
# Returns: Dict with:
# - 'mean_x': float
# - 'state_distribution': Dict[str, int]
# - 'activity': float
# - 'vector': np.ndarray
```

#### Communication

##### get_communication_packets
```python
packets = network.get_communication_packets()
# Returns: Dict[int, np.ndarray] - {cluster_id: packet}
```

---

## REST API

The FastAPI server provides a complete REST interface.

### Starting the Server

```bash
# Method 1: Direct
python run_api.py

# Method 2: Uvicorn
uvicorn hyperbion.api.server:app --host 0.0.0.0 --port 8000

# Method 3: With auto-reload (development)
uvicorn hyperbion.api.server:app --reload
```

### API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Endpoints

#### Network Management

##### POST /network/create
```bash
curl -X POST http://localhost:8000/network/create \
  -H "Content-Type: application/json" \
  -d '{"name": "MyNetwork", "auto_cluster": true}'

# Response: {"network_id": "...", "name": "MyNetwork"}
```

##### POST /network/reset
```bash
curl -X POST http://localhost:8000/network/reset
```

##### GET /network/state
```bash
curl http://localhost:8000/network/state

# Response: Full network state
```

#### Cell Operations

##### POST /network/add_cell
```bash
curl -X POST http://localhost:8000/network/add_cell \
  -H "Content-Type: application/json" \
  -d '{"state": 1, "bias": 0.5}'

# Response: {"cell_id": 0}
```

##### POST /network/remove_cell/{cell_id}
```bash
curl -X POST http://localhost:8000/network/remove_cell/0
```

##### POST /network/connect
```bash
curl -X POST http://localhost:8000/network/connect \
  -H "Content-Type: application/json" \
  -d '{"source_id": 0, "target_id": 1, "weight": 1.5}'
```

##### POST /network/disconnect
```bash
curl -X POST http://localhost:8000/network/disconnect \
  -H "Content-Type: application/json" \
  -d '{"source_id": 0, "target_id": 1}'
```

#### Simulation

##### POST /network/step
```bash
curl -X POST http://localhost:8000/network/step \
  -H "Content-Type: application/json" \
  -d '{
    "noise_level": 0.1,
    "apply_plasticity": true,
    "auto_trigger_operators": true
  }'

# Response: Step result dictionary
```

##### POST /network/run
```bash
curl -X POST http://localhost:8000/network/run \
  -H "Content-Type: application/json" \
  -d '{
    "num_steps": 100,
    "noise_level": 0.1
  }'

# Response: Array of step results
```

#### Operators

##### POST /network/apply_operator
```bash
curl -X POST http://localhost:8000/network/apply_operator \
  -H "Content-Type: application/json" \
  -d '{
    "operator": "DK",
    "targets": [0, 1, 2],
    "params": {"delta": 0.5}
  }'

# Response: OperatorResult
```

##### GET /network/operator_history
```bash
curl http://localhost:8000/network/operator_history
```

#### Clusters

##### POST /network/create_cluster
```bash
curl -X POST http://localhost:8000/network/create_cluster \
  -H "Content-Type: application/json" \
  -d '{"cell_ids": [0, 1, 2]}'

# Response: {"cluster_id": 0}
```

##### GET /network/clusters
```bash
curl http://localhost:8000/network/clusters
```

#### Metrics

##### GET /network/metrics
```bash
curl http://localhost:8000/network/metrics
```

##### GET /network/statistics
```bash
curl http://localhost:8000/network/statistics
```

#### Export

##### POST /network/export
```bash
# GraphML
curl -X POST http://localhost:8000/network/export \
  -H "Content-Type: application/json" \
  -d '{"format": "graphml"}' \
  --output network.graphml

# JSON
curl -X POST http://localhost:8000/network/export \
  -H "Content-Type: application/json" \
  -d '{"format": "json"}' \
  --output network.json

# CSV (cells)
curl -X POST http://localhost:8000/network/export \
  -H "Content-Type: application/json" \
  -d '{"format": "csv", "export_type": "cells"}' \
  --output cells.csv
```

---

## Persistence API

### NetworkPersistence

State management and persistence.

#### Save State

```python
from hyperbion.persistence import NetworkPersistence

# JSON format
NetworkPersistence.save_state(
    network,
    filepath='network_state.json',
    format='json'
)

# Pickle format (binary)
NetworkPersistence.save_state(
    network,
    filepath='network_state.pkl',
    format='pickle'
)
```

#### Load State

```python
# JSON
network = NetworkPersistence.load_state(
    filepath='network_state.json',
    format='json'
)

# Pickle
network = NetworkPersistence.load_state(
    filepath='network_state.pkl',
    format='pickle'
)
```

#### Checkpoints

```python
# Create checkpoint
checkpoint_path = NetworkPersistence.create_checkpoint(
    network,
    checkpoint_dir='./checkpoints',
    name='experiment_1'
)

# Load checkpoint
network = NetworkPersistence.load_checkpoint(checkpoint_path)

# List checkpoints
checkpoints = NetworkPersistence.list_checkpoints('./checkpoints')
```

### Exporters

#### GraphMLExporter

```python
from hyperbion.persistence import GraphMLExporter

GraphMLExporter.export(
    network,
    filepath='network.graphml'
)
```

#### LaTeXExporter

```python
from hyperbion.persistence import LaTeXExporter

LaTeXExporter.export(
    network,
    filepath='network.tex',
    include_weights=True
)
```

#### CSVExporter

```python
from hyperbion.persistence import CSVExporter

# Export cells
CSVExporter.export_cells(network, 'cells.csv')

# Export connections
CSVExporter.export_connections(network, 'connections.csv')

# Export metrics
CSVExporter.export_metrics(network, 'metrics.csv')
```

---

## Operator API

### Custom Operators

Create custom operators by inheriting from `BaseOperator`:

```python
from hyperbion.operators.base import BaseOperator, OperatorResult

class MyOperator(BaseOperator):
    def __init__(self):
        super().__init__(name="MYOP")
        self.trigger_threshold = 0.8

    def should_trigger(self, network, targets):
        """Return True if operator should be applied."""
        if len(targets) < 3:
            return False
        # Custom trigger logic
        return self._check_condition(network, targets)

    def apply(self, network, targets, **params):
        """Apply operator to network."""
        affected_cells = []
        metrics = {}

        try:
            # Modify network
            for cell_id in targets:
                cell = network.get_cell(cell_id)
                # ... perform operations ...
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
                message=f"Error: {str(e)}"
            )

# Register operator
network.operator_registry['MYOP'] = MyOperator()

# Use operator
result = network.apply_operator('MYOP', targets=[0, 1, 2])
```

---

## Benchmarking API

### Running Benchmarks

```python
from hyperbion.benchmark import (
    BenchmarkRunner,
    PatternClassificationTask,
    MemoryCapacityTask,
    AssociationTask,
    NetworkComparator
)

# Create task
task = PatternClassificationTask(
    num_classes=4,
    pattern_size=16,
    noise_level=0.15
)

# Run benchmark
runner = BenchmarkRunner(task=task)
results = runner.run_benchmark(
    binary_network_size=80,
    tripolar_network_size=60,
    max_epochs=200
)

# Analyze results
comparator = NetworkComparator()
comparator.add_result(results)

# Generate reports
summary = comparator.generate_summary_report()
comparator.export_csv('results.csv')
comparator.export_json('results.json')
```

### Custom Tasks

```python
from hyperbion.benchmark.tasks import BaseTask

class MyTask(BaseTask):
    def generate_training_data(self, num_samples):
        """Generate training dataset."""
        return inputs, targets

    def generate_test_data(self, num_samples):
        """Generate test dataset."""
        return inputs, targets

    def evaluate(self, network, test_data):
        """Evaluate network performance."""
        inputs, targets = test_data
        # ... run evaluation ...
        return {
            'accuracy': accuracy,
            'metrics': metrics
        }
```

---

## Code Examples

### Example 1: Basic Network

```python
from hyperbion import HyperbionNetwork

# Create network
net = HyperbionNetwork(name="BasicExample")

# Add cells
cells = [net.add_cell(state=1) for _ in range(10)]

# Create connections
for i in range(len(cells) - 1):
    net.connect_cells(cells[i], cells[i+1], weight=1.0)

# Run simulation
for step in range(100):
    result = net.step(noise_level=0.1, apply_plasticity=True)
    if step % 10 == 0:
        print(f"Step {step}: {result['active_cells']} active cells")

# Get final state
state = net.get_state()
print(f"Final: {state['num_cells']} cells, {state['num_connections']} connections")
```

### Example 2: Operator Application

```python
from hyperbion import HyperbionNetwork

net = HyperbionNetwork()

# Create cluster
cluster = [net.add_cell(state=1) for _ in range(5)]
for i in range(len(cluster) - 1):
    net.connect_cells(cluster[i], cluster[i+1], 1.0)

# Apply Doppelkick
result = net.apply_operator('DK', cluster, delta=0.5)
print(f"DK: {result.success}, affected {len(result.affected_cells)}")

# Apply Morphogenesis
result = net.apply_operator('MOR', [cluster[0]], mode='divide')
print(f"MOR: created {result.metrics.get('created_cells', 0)} new cells")

# Get operator history
history = net.get_operator_history()
print(f"Applied {len(history)} operators")
```

### Example 3: Persistence

```python
from hyperbion import HyperbionNetwork
from hyperbion.persistence import NetworkPersistence, GraphMLExporter

# Create and run network
net = HyperbionNetwork()
# ... set up network ...
net.run(num_steps=100)

# Save state
NetworkPersistence.save_state(net, 'state.json', format='json')

# Create checkpoint
checkpoint = NetworkPersistence.create_checkpoint(
    net,
    checkpoint_dir='./checkpoints',
    name='run1'
)

# Export topology
GraphMLExporter.export(net, 'network.graphml')

# Load later
loaded_net = NetworkPersistence.load_state('state.json', format='json')
```

### Example 4: Quadrupole Network

```python
from hyperbion.quadrupole import QuadrupoleNetwork

# Create quadrupole network
net = QuadrupoleNetwork(
    name="QuadExample",
    phase_delta=0.05,
    mirror_coupling=0.3
)

# Add cells to each cluster
for cluster_id in range(4):
    for _ in range(20):
        net.add_cell(
            cluster_id=cluster_id,
            initial_x=0.5,
            tau_0=0.3,
            tau_1=0.7
        )

# Run simulation
for step in range(1000):
    result = net.step(noise_level=0.05, apply_learning=True)

    if step % 100 == 0:
        print(f"Step {step}:")
        print(f"  Phase: {result['phase']:.4f}")
        print(f"  Active: Q{result['active_quadrant']}")
        print(f"  Mirror: {result['mirror_value']:.4f}")
        print(f"  Coherence: {result['coherence']:.4f}")
```

---

## Error Handling

### Common Exceptions

```python
from hyperbion.core.exceptions import (
    CellNotFoundError,
    InvalidStateError,
    InvalidConnectionError,
    OperatorError
)

try:
    net.add_cell(state=5)  # Invalid state
except InvalidStateError as e:
    print(f"Invalid state: {e}")

try:
    net.remove_cell(999)  # Non-existent cell
except CellNotFoundError as e:
    print(f"Cell not found: {e}")

try:
    result = net.apply_operator('DK', [])  # Empty targets
except OperatorError as e:
    print(f"Operator error: {e}")
```

---

## Best Practices

1. **Always check operator results**:
   ```python
   result = net.apply_operator('DK', targets)
   if not result.success:
       print(f"Operator failed: {result.message}")
   ```

2. **Use context managers for state**:
   ```python
   with NetworkPersistence.checkpoint(net, 'checkpoint.pkl'):
       net.run(num_steps=100)
   # Auto-saved on exit
   ```

3. **Monitor metrics during simulation**:
   ```python
   for step in range(1000):
       result = net.step()
       if step % 100 == 0:
           metrics = net.get_metrics()
           if metrics['avg_activity'] < 0.1:
               print("Warning: Low activity")
   ```

4. **Handle history growth**:
   ```python
   net = HyperbionNetwork(max_history_length=1000)
   # Or clear periodically:
   if net.step_count % 1000 == 0:
       net.clear_history()
   ```

---

For architecture details, see [ARCHITECTURE.md](ARCHITECTURE.md).

For development guide, see [DEVELOPMENT.md](DEVELOPMENT.md).
