"""
Quadrupole Tripolar Neural Network
===================================

Main network architecture combining:
- 4 resonant clusters in quadrupole arrangement
- Rotating phase space Θ(t)
- Holistic mirror state H(t) as LD coupling
- Quantum-hybrid communication layer

Network Dynamics:
1. Phase rotation determines active cluster
2. Active cluster transmits signature packet
3. Other clusters receive and process
4. After full cycle: compute H(t) from all signatures
5. H(t) couples to all LD cells
6. Holistic modulation of learning
"""

from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import time

from .tripolar_cell import TripolarGabrielCell, TripolarLogicState
from .phase_system import GlobalPhase, QuadrantSelector
from .mirror_state import HolisticMirrorState, ClusterSignature
from .communication import CommunicationLayer


class QuadrupoleNetwork:
    """
    Quadrupole Tripolar Neural Network.

    Architecture:
    - 4 clusters (G0, G1, G2, G3) in quadrupole arrangement
    - Global phase Θ(t) rotating through quadrants
    - Holistic mirror state H(t) computed after each cycle
    - Quantum-hybrid communication between clusters
    """

    def __init__(
        self,
        name: str = "QuadrupoleNetwork",
        phase_delta: float = 0.01,
        mirror_coupling: float = 0.3
    ):
        """
        Initialize quadrupole network.

        Args:
            name: Network identifier
            phase_delta: Phase increment per step
            mirror_coupling: Default coupling strength to mirror state
        """
        self.name = name

        # Clusters: {cluster_id: {cell_id: TripolarGabrielCell}}
        self.clusters: Dict[int, Dict[int, TripolarGabrielCell]] = {
            0: {},
            1: {},
            2: {},
            3: {}
        }

        # Global phase system
        self.phase = GlobalPhase(delta=phase_delta)
        self.quadrant_selector = QuadrantSelector(self.phase)

        # Holistic mirror state
        self.mirror_state = HolisticMirrorState()

        # Communication layer
        self.communication = CommunicationLayer()

        # Network state
        self.next_cell_id = 0
        self.step_count = 0
        self.cycle_count = 0

        # Metrics
        self.metrics: Dict[str, List[float]] = {
            'coherence': [],
            'mirror_value': [],
            'ld_fraction': [],
            'active_cluster': []
        }

        self.creation_time = time.time()

    def add_cell(
        self,
        cluster_id: int,
        initial_x: float = 0.5,
        tau_0: float = 0.3,
        tau_1: float = 0.7,
        bias: float = 0.0,
        phase: Optional[float] = None
    ) -> int:
        """
        Add a cell to a cluster.

        Args:
            cluster_id: Cluster to add cell to (0-3)
            initial_x: Initial internal state
            tau_0: Lower threshold
            tau_1: Upper threshold
            bias: Cell bias
            phase: Cell phase (random if None)

        Returns:
            Cell ID
        """
        if cluster_id not in {0, 1, 2, 3}:
            raise ValueError("cluster_id must be in {0, 1, 2, 3}")

        cell_id = self.next_cell_id

        if phase is None:
            # Random phase related to cluster
            phase = (cluster_id * 0.25 + np.random.rand() * 0.25) % 1.0

        cell = TripolarGabrielCell(
            cell_id=cell_id,
            cluster_id=cluster_id,
            initial_x=initial_x,
            tau_0=tau_0,
            tau_1=tau_1,
            bias=bias,
            phase=phase
        )

        self.clusters[cluster_id][cell_id] = cell
        self.next_cell_id += 1

        return cell_id

    def remove_cell(self, cell_id: int) -> bool:
        """
        Remove a cell from network.

        Args:
            cell_id: Cell to remove

        Returns:
            True if cell was removed
        """
        for cluster in self.clusters.values():
            if cell_id in cluster:
                # Remove connections to this cell
                for other_cluster in self.clusters.values():
                    for cell in other_cluster.values():
                        cell.disconnect(cell_id)

                del cluster[cell_id]
                return True
        return False

    def connect_cells(
        self,
        source_id: int,
        target_id: int,
        weight: float
    ) -> bool:
        """
        Connect two cells.

        Args:
            source_id: Source cell ID
            target_id: Target cell ID
            weight: Connection weight

        Returns:
            True if connection created
        """
        source_cell = self._get_cell(source_id)
        target_cell = self._get_cell(target_id)

        if source_cell is None or target_cell is None:
            return False

        source_cell.connect(target_id, weight)
        return True

    def _get_cell(self, cell_id: int) -> Optional[TripolarGabrielCell]:
        """Get cell by ID from any cluster."""
        for cluster in self.clusters.values():
            if cell_id in cluster:
                return cluster[cell_id]
        return None

    def _get_all_cells(self) -> List[TripolarGabrielCell]:
        """Get list of all cells."""
        cells = []
        for cluster in self.clusters.values():
            cells.extend(cluster.values())
        return cells

    def step(
        self,
        external_inputs: Optional[Dict[int, float]] = None,
        noise_level: float = 0.0,
        apply_learning: bool = True
    ) -> Dict[str, Any]:
        """
        Execute one network step.

        Procedure:
        1. Advance phase Θ(t)
        2. Determine active cluster
        3. Update all cell states
        4. Active cluster transmits signature
        5. Non-active clusters receive previous packets
        6. If cycle complete: compute H(t) and couple to LD cells
        7. Apply learning rules

        Args:
            external_inputs: {cell_id: input_value}
            noise_level: Noise level
            apply_learning: Whether to update weights

        Returns:
            Step results dictionary
        """
        step_start_time = time.time()

        # 1. Advance phase
        self.phase.step()
        active_quadrant = self.phase.get_active_quadrant()

        # 2. Collect current emissions for all cells
        all_emissions = {}
        for cluster in self.clusters.values():
            for cell_id, cell in cluster.items():
                all_emissions[cell_id] = cell.compute_emission()

        # 3. Update all cells
        mirror_value = self.mirror_state.get_mirror_value()

        for cluster_id, cluster in self.clusters.items():
            for cell_id, cell in cluster.items():
                # External input
                ext_input = external_inputs.get(cell_id, 0.0) if external_inputs else 0.0

                # Update state
                cell.update_state(
                    neighbor_states=all_emissions,
                    external_input=ext_input,
                    mirror_state=mirror_value,
                    noise_level=noise_level
                )

        # 4. Active cluster transmits
        active_cluster_cells = list(self.clusters[active_quadrant].values())
        if active_cluster_cells:
            signature = ClusterSignature(active_quadrant, active_cluster_cells)
            self.mirror_state.update_cluster_signature(
                active_quadrant,
                active_cluster_cells,
                self.step_count
            )
            self.communication.transmit_from_cluster(
                active_quadrant,
                signature,
                self.phase.theta
            )

        # 5. Non-active clusters receive (from previous quadrant)
        if active_quadrant > 0:
            prev_quadrant = active_quadrant - 1
        else:
            prev_quadrant = 3

        for cid in range(4):
            if cid != active_quadrant:
                self.communication.receive_at_cluster(
                    cid,
                    prev_quadrant,
                    self.phase.theta
                )

        # 6. Check for cycle completion
        if self.phase.has_completed_cycle():
            self._complete_cycle()

        # 7. Apply learning
        if apply_learning:
            self._apply_learning()

        # Update metrics
        self._collect_metrics()

        self.step_count += 1

        return {
            'step': self.step_count,
            'phase': self.phase.theta,
            'active_quadrant': active_quadrant,
            'cycle_count': self.cycle_count,
            'mirror_value': mirror_value,
            'coherence': self.mirror_state.get_coherence_metric(),
            'execution_time': time.time() - step_start_time
        }

    def _complete_cycle(self) -> None:
        """
        Complete one full cycle through all quadrants.

        1. Compute holistic mirror state H(t)
        2. Couple LD cells to H(t)
        3. Apply holistic learning modulation
        4. Clear communication buffers
        """
        # Compute mirror state
        if self.mirror_state.can_compute_mirror_state():
            mirror_value = self.mirror_state.compute_mirror_state()

            # The coupling to LD cells happens automatically in next update
            # via the mirror_state parameter

        # Reset for next cycle
        self.communication.clear_packets()
        self.cycle_count += 1

    def _apply_learning(self) -> None:
        """Apply tripolar Hebbian learning with holistic modulation."""
        # Collect logic states and internal states
        all_logic = {}
        all_x = {}

        for cluster in self.clusters.values():
            for cell_id, cell in cluster.items():
                all_logic[cell_id] = cell.logic_state
                all_x[cell_id] = cell.x

        # Base learning rate
        base_lr = 0.01

        # Get modulated learning rate from mirror state
        modulated_lr = self.mirror_state.get_mirror_modulation(base_lr)

        # Apply to each cell
        for cluster in self.clusters.values():
            for cell in cluster.values():
                cell.apply_hebbian_learning(
                    all_logic,
                    all_x,
                    learning_rate=modulated_lr
                )

    def _collect_metrics(self) -> None:
        """Collect network metrics."""
        # Coherence
        self.metrics['coherence'].append(
            self.mirror_state.get_coherence_metric()
        )

        # Mirror value
        mirror_val = self.mirror_state.get_mirror_value()
        self.metrics['mirror_value'].append(
            mirror_val if mirror_val is not None else 0.0
        )

        # LD fraction
        all_cells = self._get_all_cells()
        if all_cells:
            ld_count = sum(
                1 for c in all_cells
                if c.logic_state == TripolarLogicState.LD
            )
            self.metrics['ld_fraction'].append(ld_count / len(all_cells))
        else:
            self.metrics['ld_fraction'].append(0.0)

        # Active cluster
        self.metrics['active_cluster'].append(
            float(self.phase.get_active_quadrant())
        )

    def get_cluster_statistics(self) -> Dict[int, Dict[str, Any]]:
        """
        Get statistics for each cluster.

        Returns:
            {cluster_id: stats}
        """
        stats = {}

        for cluster_id, cluster in self.clusters.items():
            cells = list(cluster.values())

            if not cells:
                stats[cluster_id] = {
                    'size': 0,
                    'l0_count': 0,
                    'l1_count': 0,
                    'ld_count': 0,
                    'mean_x': 0.0
                }
                continue

            l0 = sum(1 for c in cells if c.logic_state == TripolarLogicState.L0)
            l1 = sum(1 for c in cells if c.logic_state == TripolarLogicState.L1)
            ld = sum(1 for c in cells if c.logic_state == TripolarLogicState.LD)

            mean_x = np.mean([c.x for c in cells])

            stats[cluster_id] = {
                'size': len(cells),
                'l0_count': l0,
                'l1_count': l1,
                'ld_count': ld,
                'mean_x': float(mean_x),
                'is_active': self.quadrant_selector.can_cluster_emit(cluster_id)
            }

        return stats

    def get_state(self) -> Dict[str, Any]:
        """Get complete network state."""
        return {
            'name': self.name,
            'step_count': self.step_count,
            'cycle_count': self.cycle_count,
            'phase': self.phase.to_dict(),
            'mirror_state': self.mirror_state.to_dict(),
            'communication': self.communication.get_communication_stats(),
            'cluster_stats': self.get_cluster_statistics(),
            'total_cells': sum(len(c) for c in self.clusters.values()),
            'metrics': {k: v[-100:] for k, v in self.metrics.items()}  # Last 100 steps
        }

    def __repr__(self) -> str:
        total_cells = sum(len(c) for c in self.clusters.values())
        return (
            f"QuadrupoleNetwork(name='{self.name}', "
            f"cells={total_cells}, steps={self.step_count}, "
            f"cycles={self.cycle_count}, "
            f"phase=Q{self.phase.get_active_quadrant()})"
        )
