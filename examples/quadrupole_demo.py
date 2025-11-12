#!/usr/bin/env python3
"""
Quadrupole Tripolar Network Demonstration
==========================================

Demonstrates the evolved architecture with:
- 4 resonant clusters in quadrupole arrangement
- Rotating phase space Θ(t)
- Holistic mirror state H(t) as LD coupling
- Quantum-hybrid communication layer
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from hyperbion.quadrupole import (
    QuadrupoleNetwork,
    TripolarLogicState
)
import numpy as np


def create_quadrupole_network(cells_per_cluster: int = 10) -> QuadrupoleNetwork:
    """
    Create a quadrupole network with balanced clusters.

    Args:
        cells_per_cluster: Number of cells in each cluster

    Returns:
        Initialized QuadrupoleNetwork
    """
    print("\n" + "=" * 60)
    print("Creating Quadrupole Tripolar Network")
    print("=" * 60)

    network = QuadrupoleNetwork(
        name="QuadrupoleDemo",
        phase_delta=0.05,  # Faster phase rotation for demo
        mirror_coupling=0.3
    )

    print(f"\nAdding {cells_per_cluster} cells to each of 4 clusters...")

    # Add cells to each cluster
    for cluster_id in range(4):
        print(f"\n  Cluster Q{cluster_id}:")

        for i in range(cells_per_cluster):
            # Varied thresholds for different LD behaviors
            tau_0 = 0.2 + np.random.rand() * 0.1
            tau_1 = 0.7 + np.random.rand() * 0.1

            # Initial state varies
            initial_x = np.random.rand()

            cell_id = network.add_cell(
                cluster_id=cluster_id,
                initial_x=initial_x,
                tau_0=tau_0,
                tau_1=tau_1,
                bias=np.random.uniform(-0.2, 0.2)
            )

            if i == 0:
                print(f"    Cell {cell_id}: x={initial_x:.3f}, "
                      f"τ₀={tau_0:.3f}, τ₁={tau_1:.3f}")

    # Create inter-cluster connections
    print(f"\nCreating inter-cluster connections...")

    all_cells = []
    for cluster in network.clusters.values():
        all_cells.extend(cluster.keys())

    # Random connections
    connection_count = 0
    for source_id in all_cells:
        # Connect to ~30% of other cells
        num_connections = int(len(all_cells) * 0.3)
        targets = np.random.choice(all_cells, size=num_connections, replace=False)

        for target_id in targets:
            if source_id != target_id:
                weight = np.random.uniform(-1.0, 1.0)
                network.connect_cells(source_id, int(target_id), weight)
                connection_count += 1

    print(f"  Created {connection_count} connections")

    # Show initial state
    print(f"\n✓ Network created: {network}")

    return network


def run_simulation(network: QuadrupoleNetwork, steps: int = 100):
    """
    Run network simulation.

    Args:
        network: QuadrupoleNetwork instance
        steps: Number of steps to simulate
    """
    print(f"\n{'=' * 60}")
    print(f"Running Simulation ({steps} steps)")
    print(f"{'=' * 60}")

    print(f"\nPhase rotation: Θ(0) = {network.phase.theta:.4f}")
    print(f"Initial active quadrant: Q{network.phase.get_active_quadrant()}")

    cycle_completed_at = []

    for step in range(steps):
        # Run step
        result = network.step(noise_level=0.05, apply_learning=True)

        # Track cycle completions
        if network.phase.has_completed_cycle():
            cycle_completed_at.append(step)

        # Print progress every 20 steps
        if step % 20 == 0:
            print(f"\n  Step {step}:")
            print(f"    Phase: Θ = {result['phase']:.4f} (Q{result['active_quadrant']})")
            print(f"    Cycles completed: {result['cycle_count']}")

            if result['mirror_value'] is not None:
                print(f"    Mirror state: H = {result['mirror_value']:.4f}")
                print(f"    Coherence: {result['coherence']:.4f}")

            # Show cluster statistics
            stats = network.get_cluster_statistics()
            for cid, cstats in stats.items():
                if cstats['size'] > 0:
                    print(f"    Q{cid}: L0={cstats['l0_count']}, "
                          f"L1={cstats['l1_count']}, "
                          f"LD={cstats['ld_count']}, "
                          f"x̄={cstats['mean_x']:.3f}"
                          + (" [ACTIVE]" if cstats['is_active'] else ""))

    print(f"\n✓ Simulation complete!")
    print(f"  Total cycles: {network.cycle_count}")
    print(f"  Cycles completed at steps: {cycle_completed_at}")


def analyze_results(network: QuadrupoleNetwork):
    """
    Analyze network behavior after simulation.

    Args:
        network: QuadrupoleNetwork instance
    """
    print(f"\n{'=' * 60}")
    print("Analysis Results")
    print(f"{'=' * 60}")

    state = network.get_state()

    # Phase statistics
    print(f"\nPhase System:")
    print(f"  Current phase: Θ = {state['phase']['theta']:.4f}")
    print(f"  Active quadrant: Q{state['phase']['active_quadrant']}")
    print(f"  Total cycles: {state['cycle_count']}")

    # Mirror state
    print(f"\nHolistic Mirror State:")
    if state['mirror_state']['mirror_value'] is not None:
        print(f"  H(t) = {state['mirror_state']['mirror_value']:.4f}")
        print(f"  Coherence = {state['mirror_state']['coherence']:.4f}")
        print(f"  Computations = {state['mirror_state']['computation_count']}")

        # Show cluster signatures
        print(f"\n  Cluster Signatures:")
        for cid, sig in state['mirror_state']['signatures'].items():
            if sig:
                print(f"    Q{cid}: L0={sig['L0']}, L1={sig['L1']}, "
                      f"LD={sig['LD']}, x̄={sig['mean_x']:.3f}")
    else:
        print(f"  Not yet computed (need full cycle)")

    # Communication
    print(f"\nCommunication Layer:")
    comm = state['communication']
    print(f"  Total transmissions: {comm['transmission_count']}")
    print(f"  Packets available: {comm['available_packets']}")

    # Cluster statistics
    print(f"\nCluster Statistics:")
    total_ld = 0
    total_cells = 0

    for cid, stats in state['cluster_stats'].items():
        print(f"  Q{cid}:")
        print(f"    Size: {stats['size']} cells")
        print(f"    Distribution: L0={stats['l0_count']}, "
              f"L1={stats['l1_count']}, LD={stats['ld_count']}")
        print(f"    Mean internal state: x̄ = {stats['mean_x']:.3f}")

        total_ld += stats['ld_count']
        total_cells += stats['size']

    # Global LD fraction
    if total_cells > 0:
        print(f"\n  Global LD fraction: {total_ld / total_cells:.1%}")
        print(f"  (Cells coupled to mirror state)")

    # Metrics trends
    if network.metrics['coherence']:
        print(f"\nMetrics (last 10 steps):")
        print(f"  Coherence: {network.metrics['coherence'][-10:]}")
        if network.metrics['mirror_value']:
            recent_mirror = [m for m in network.metrics['mirror_value'][-10:] if m > 0]
            if recent_mirror:
                print(f"  Mirror value: min={min(recent_mirror):.3f}, "
                      f"max={max(recent_mirror):.3f}, "
                      f"mean={np.mean(recent_mirror):.3f}")


def demonstrate_mirror_coupling():
    """
    Demonstrate how LD cells couple to mirror state.
    """
    print(f"\n{'=' * 60}")
    print("Mirror State Coupling Demonstration")
    print(f"{'=' * 60}")

    # Create small network
    network = QuadrupoleNetwork(phase_delta=0.1)

    # Add cells with specific thresholds to create LD states
    print(f"\nCreating cells tuned for LD state...")

    for cluster_id in range(4):
        for i in range(5):
            # Thresholds creating wide LD zone
            network.add_cell(
                cluster_id=cluster_id,
                initial_x=0.5,  # Start in LD
                tau_0=0.3,
                tau_1=0.7,
                bias=0.0
            )

    # Run until first mirror state computation
    print(f"\nRunning until first mirror state computation...")

    for step in range(100):
        result = network.step(noise_level=0.01, apply_learning=False)

        if result['mirror_value'] is not None and step > 20:
            print(f"\n  ✓ Mirror state computed at step {step}!")
            print(f"    H(t) = {result['mirror_value']:.4f}")
            print(f"    Coherence = {result['coherence']:.4f}")

            # Show LD cell states
            all_cells = []
            for cluster in network.clusters.values():
                all_cells.extend(cluster.values())

            ld_cells = [c for c in all_cells if c.logic_state == TripolarLogicState.LD]
            print(f"\n    Cells in LD state: {len(ld_cells)}/{len(all_cells)}")

            if ld_cells:
                x_values = [c.x for c in ld_cells]
                print(f"    LD internal states: x̄ = {np.mean(x_values):.3f} "
                      f"± {np.std(x_values):.3f}")
                print(f"    (These cells are now coupled to H(t))")

            break


def main():
    """Main demonstration."""
    print("\n" + "=" * 60)
    print("QUADRUPOLE TRIPOLAR NEURAL NETWORK")
    print("Evolved Architecture Demonstration")
    print("=" * 60)
    print("\nBased on Blueprint by Sebastian Klemm")
    print("=" * 60)

    # Create network
    network = create_quadrupole_network(cells_per_cluster=15)

    # Run simulation
    run_simulation(network, steps=80)

    # Analyze
    analyze_results(network)

    # Demonstrate mirror coupling
    demonstrate_mirror_coupling()

    print(f"\n{'=' * 60}")
    print("Demonstration Complete!")
    print(f"{'=' * 60}")

    print(f"\nKey Features Demonstrated:")
    print(f"  ✓ Quadrupole architecture (4 resonant clusters)")
    print(f"  ✓ Rotating phase space Θ(t)")
    print(f"  ✓ Tripolar logic (L0, L1, LD)")
    print(f"  ✓ Holistic mirror state H(t)")
    print(f"  ✓ LD coupling to mirror state")
    print(f"  ✓ Quantum-hybrid communication")
    print(f"  ✓ Phase-selective transmission")
    print(f"  ✓ Holistic learning modulation")

    print(f"\n")


if __name__ == "__main__":
    main()
