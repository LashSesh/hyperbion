"""
Basic Simulation Example
=========================

Demonstrates basic network creation, simulation, and analysis.
"""

import sys
sys.path.insert(0, '../src')

from hyperbion import HyperbionNetwork
from hyperbion.persistence import NetworkPersistence, CSVExporter
import numpy as np


def create_simple_network():
    """Create a simple network for demonstration."""
    print("=" * 60)
    print("Hyperbion Tripolar Network - Basic Simulation")
    print("=" * 60)

    # Create network
    network = HyperbionNetwork(name="BasicSimulation")
    print(f"\n✓ Created network: {network.name}")

    # Add cells with different initial states
    print("\n📍 Adding cells...")
    cells = []
    for i in range(10):
        state = np.random.choice([-1, 0, 1])
        bias = np.random.uniform(-0.5, 0.5)
        cell_id = network.add_cell(state=state, bias=bias)
        cells.append(cell_id)
        print(f"  Cell {cell_id}: state={state:+d}, bias={bias:.2f}")

    # Create connections
    print("\n🔗 Creating connections...")
    connection_count = 0
    for i in range(len(cells)):
        for j in range(len(cells)):
            if i != j and np.random.random() > 0.6:  # 40% connection probability
                weight = np.random.uniform(-2.0, 2.0)
                network.connect_cells(cells[i], cells[j], weight)
                connection_count += 1

    print(f"  Created {connection_count} connections")

    # Auto-detect clusters
    print("\n🔍 Detecting clusters...")
    cluster_ids = network.auto_detect_clusters(min_cluster_size=2)
    print(f"  Found {len(cluster_ids)} clusters")

    return network, cells


def run_simulation(network, steps=50):
    """Run the simulation."""
    print(f"\n🚀 Running simulation for {steps} steps...")

    for step in range(steps):
        result = network.step(
            noise_level=0.05,
            apply_plasticity=True,
            auto_trigger_operators=True
        )

        if step % 10 == 0:
            print(f"  Step {step}: {len(network.cells)} cells, "
                  f"{len(result['triggered_operators'])} operators triggered")

    print(f"\n✓ Simulation completed: {network.step_count} total steps")


def analyze_results(network):
    """Analyze simulation results."""
    print("\n📊 Analysis Results:")
    print("=" * 60)

    # Network statistics
    print(f"\nNetwork Statistics:")
    print(f"  Total cells: {len(network.cells)}")
    print(f"  Total steps: {network.step_count}")
    print(f"  Clusters: {len(network.clusters)}")

    # State distribution
    states = [cell.state for cell in network.cells.values()]
    print(f"\nState Distribution:")
    print(f"  Positive (+1): {states.count(1)}")
    print(f"  Neutral (0):   {states.count(0)}")
    print(f"  Negative (-1): {states.count(-1)}")

    # Connection statistics
    total_connections = sum(len(cell.connections) for cell in network.cells.values())
    avg_connections = total_connections / len(network.cells) if network.cells else 0
    print(f"\nConnection Statistics:")
    print(f"  Total connections: {total_connections}")
    print(f"  Average per cell:  {avg_connections:.2f}")

    # Operator statistics
    print(f"\nOperator Applications:")
    for op_name, op in network.operators.items():
        stats = op.get_statistics()
        print(f"  {op_name:12s}: {stats['application_count']} times "
              f"(success rate: {stats['success_rate']:.1%})")

    # Metrics
    if network.metrics:
        print(f"\nMetrics Collected:")
        for metric_name, values in network.metrics.items():
            if values:
                print(f"  {metric_name:20s}: {len(values)} data points")


def save_results(network):
    """Save simulation results."""
    print("\n💾 Saving results...")

    # Save network state
    NetworkPersistence.save_state(network, 'outputs/basic_simulation_state.json')
    print("  ✓ Saved network state")

    # Export metrics
    CSVExporter.export_cells(network, 'outputs/basic_simulation_cells.csv')
    CSVExporter.export_connections(network, 'outputs/basic_simulation_connections.csv')
    CSVExporter.export_metrics(network, 'outputs/basic_simulation_metrics.csv')
    print("  ✓ Exported CSV files")

    # Export history
    NetworkPersistence.export_history(network, 'outputs/basic_simulation_history.json')
    print("  ✓ Exported history")


def main():
    """Main execution."""
    # Create outputs directory
    import os
    os.makedirs('outputs', exist_ok=True)

    # Run simulation
    network, cells = create_simple_network()
    run_simulation(network, steps=50)
    analyze_results(network)
    save_results(network)

    print("\n" + "=" * 60)
    print("Simulation Complete!")
    print("=" * 60)
    print("\nOutput files in ./outputs/:")
    print("  - basic_simulation_state.json")
    print("  - basic_simulation_cells.csv")
    print("  - basic_simulation_connections.csv")
    print("  - basic_simulation_metrics.csv")
    print("  - basic_simulation_history.json")


if __name__ == "__main__":
    main()
