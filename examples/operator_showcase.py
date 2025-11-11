"""
Operator Showcase
=================

Demonstrates all five operators: DK, SW, WT, Nullpunkt, MOR
"""

import sys
sys.path.insert(0, '../src')

from hyperbion import HyperbionNetwork
import numpy as np


def showcase_doppelkick():
    """Demonstrate Doppelkick (DK) operator."""
    print("\n" + "=" * 60)
    print("Doppelkick (DK) Operator - Synchronous Amplification")
    print("=" * 60)

    network = HyperbionNetwork()

    # Create coherent cluster (all positive states)
    print("\nCreating coherent cluster...")
    cells = [network.add_cell(state=1) for _ in range(5)]

    # Connect cells
    for i in range(len(cells)):
        for j in range(len(cells)):
            if i != j:
                network.connect_cells(cells[i], cells[j], 0.5)

    print(f"Created {len(cells)} cells with uniform positive states")

    # Check initial weights
    initial_weights = []
    for cell_id in cells:
        cell = network.cells[cell_id]
        initial_weights.extend(cell.connections.values())

    avg_initial = np.mean(initial_weights)
    print(f"Average initial weight: {avg_initial:.3f}")

    # Apply DK
    print("\n⚡ Applying Doppelkick operator...")
    result = network.apply_operator('DK', cells)

    print(f"  Success: {result.success}")
    print(f"  Affected cells: {len(result.affected_cells)}")
    print(f"  Coherence change: {result.metrics['coherence_delta']:.3f}")

    # Check final weights
    final_weights = []
    for cell_id in cells:
        cell = network.cells[cell_id]
        final_weights.extend(cell.connections.values())

    avg_final = np.mean(final_weights)
    print(f"Average final weight: {avg_final:.3f}")
    print(f"Weight increase: {avg_final - avg_initial:.3f}")


def showcase_sweep():
    """Demonstrate Sweep (SW) operator."""
    print("\n" + "=" * 60)
    print("Sweep (SW) Operator - Weight Normalization")
    print("=" * 60)

    network = HyperbionNetwork()

    # Create cluster with high weights
    print("\nCreating cluster with high weights...")
    cells = [network.add_cell() for _ in range(4)]

    for i in range(len(cells)):
        for j in range(len(cells)):
            if i != j:
                network.connect_cells(cells[i], cells[j], 4.0)  # High weights

    # Check activity
    from hyperbion.operators.sweep import SweepOperator
    sw = SweepOperator()
    initial_activity = sw._compute_total_activity(network, cells)
    print(f"Initial total activity: {initial_activity:.2f}")

    # Apply SW
    print("\n🧹 Applying Sweep operator...")
    result = network.apply_operator('SW', cells)

    print(f"  Success: {result.success}")
    print(f"  Activity reduction: {result.metrics['activity_reduction']:.2f}")
    print(f"  Variance change: {result.metrics['initial_variance']:.2f} → "
          f"{result.metrics['final_variance']:.2f}")


def showcase_wormhole():
    """Demonstrate Wormhole (WT) operator."""
    print("\n" + "=" * 60)
    print("Wormhole (WT) Operator - Temporal Shortcuts")
    print("=" * 60)

    network = HyperbionNetwork()

    # Create two distant cells
    print("\nCreating distant cells...")
    c0 = network.add_cell(state=1)
    c1 = network.add_cell(state=1)

    print(f"Cell {c0} and Cell {c1} created")
    print(f"Initial topological distance: {network.get_topological_distance(c0, c1)}")

    # Apply WT
    print("\n🌀 Applying Wormhole operator...")
    result = network.apply_operator('WT', [c0, c1], duration=5.0, bidirectional=True)

    print(f"  Success: {result.success}")
    print(f"  Wormhole duration: 5.0 seconds")

    # Check wormhole
    cell0 = network.cells[c0]
    if c1 in cell0.wormhole_connections:
        print(f"  ✓ Wormhole connection established")
    else:
        print(f"  ✗ Wormhole not established")


def showcase_nullpunkt():
    """Demonstrate Nullpunkt operator."""
    print("\n" + "=" * 60)
    print("Nullpunkt Operator - Reset & Deletion")
    print("=" * 60)

    network = HyperbionNetwork()

    # Test reset_weights
    print("\nTest 1: Reset Weights")
    c0 = network.add_cell()
    c1 = network.add_cell()
    network.connect_cells(c0, c1, 2.0)
    print(f"  Initial connections: {len(network.cells[c0].connections)}")

    result = network.apply_operator('Nullpunkt', [c0], mode='reset_weights')
    print(f"  After reset: {len(network.cells[c0].connections)} connections")

    # Test reset_state
    print("\nTest 2: Reset State")
    c2 = network.add_cell(state=1)
    print(f"  Initial state: {network.cells[c2].state}")

    result = network.apply_operator('Nullpunkt', [c2], mode='reset_state')
    print(f"  After reset: {network.cells[c2].state}")

    # Test delete_cell
    print("\nTest 3: Delete Cell")
    c3 = network.add_cell()
    initial_size = len(network.cells)
    print(f"  Initial network size: {initial_size}")

    result = network.apply_operator('Nullpunkt', [c3], mode='delete_cell')
    print(f"  After deletion: {len(network.cells)} cells")


def showcase_morphogenesis():
    """Demonstrate Morphogenesis (MOR) operator."""
    print("\n" + "=" * 60)
    print("Morphogenesis (MOR) Operator - Growth & Evolution")
    print("=" * 60)

    network = HyperbionNetwork()

    # Test division
    print("\nTest 1: Cell Division")
    c0 = network.add_cell(state=1)
    initial_size = len(network.cells)
    print(f"  Initial network size: {initial_size}")

    result = network.apply_operator('MOR', [c0], mode='divide')
    print(f"  After division: {len(network.cells)} cells")
    print(f"  New cells: {result.metrics['new_cells']}")

    # Test fusion
    print("\nTest 2: Cell Fusion")
    c1 = network.add_cell()
    c2 = network.add_cell()
    initial_size = len(network.cells)
    print(f"  Initial network size: {initial_size}")

    result = network.apply_operator('MOR', [c1, c2], mode='fuse')
    print(f"  After fusion: {len(network.cells)} cells")
    print(f"  Removed cells: {result.metrics['removed_cells']}")

    # Test spawn
    print("\nTest 3: Cell Spawn")
    initial_size = len(network.cells)
    print(f"  Initial network size: {initial_size}")

    result = network.apply_operator('MOR', [], mode='spawn', initial_state=1)
    print(f"  After spawn: {len(network.cells)} cells")
    print(f"  New cells: {result.metrics['new_cells']}")


def main():
    """Main execution."""
    print("\n" + "=" * 60)
    print("HYPERBION OPERATOR SHOWCASE")
    print("=" * 60)

    showcase_doppelkick()
    showcase_sweep()
    showcase_wormhole()
    showcase_nullpunkt()
    showcase_morphogenesis()

    print("\n" + "=" * 60)
    print("All operators demonstrated successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
