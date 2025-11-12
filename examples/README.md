# Hyperbion Examples

This directory contains example scripts demonstrating various features of the Hyperbion Tripolar Network.

## Examples

### 1. Basic Simulation (`basic_simulation.py`)

A complete example showing:
- Network creation
- Adding cells and connections
- Running simulation steps
- Analyzing results
- Saving and exporting data

**Run:**
```bash
python basic_simulation.py
```

**Output:**
- Network state (JSON)
- Cell data (CSV)
- Connection data (CSV)
- Metrics over time (CSV)
- Event history (JSON)

### 2. Operator Showcase (`operator_showcase.py`)

Demonstrates all five operators:
- **DK (Doppelkick)**: Cluster synchronization
- **SW (Sweep)**: Weight normalization
- **WT (Wormhole)**: Temporal shortcuts
- **Nullpunkt**: Reset and deletion
- **MOR (Morphogenesis)**: Growth and evolution

**Run:**
```bash
python operator_showcase.py
```

## Running Examples

All examples can be run directly from this directory:

```bash
# Make sure you're in the examples directory
cd examples

# Run any example
python basic_simulation.py
python operator_showcase.py
```

## Output Files

Examples create an `outputs/` directory with results:
- `*.json` - Network states and history
- `*.csv` - Data tables for analysis
- `*.graphml` - Network topology for visualization

## Next Steps

After running examples:

1. Modify parameters in the scripts
2. Experiment with different network topologies
3. Try different operator combinations
4. Visualize results with your favorite tools

For more information, see the main README.md
