"""
Holistic Mirror State
=====================

The holistic mirror state H(t) is constructed from all four clusters
after a complete cycle (Q0 → Q1 → Q2 → Q3).

H(t) = Φ(S0(t), S1(t), S2(t), S3(t))

where Sk(t) is the state vector of cluster k.

The mirror state acts as a global meta-operator that:
1. Couples to all cells in LD state
2. Modulates learning processes
3. Provides global coherence
"""

from typing import Dict, List, Any, Optional
import numpy as np
from .tripolar_cell import TripolarLogicState


class ClusterSignature:
    """
    State vector Sk(t) capturing cluster configuration.

    Encodes:
    - Distribution of L0, L1, LD states
    - Average internal state x
    - Phase statistics
    - Activation patterns
    """

    def __init__(
        self,
        cluster_id: int,
        cells: List['TripolarGabrielCell']
    ):
        """
        Compute cluster signature from cells.

        Args:
            cluster_id: Cluster index
            cells: List of cells in this cluster
        """
        self.cluster_id = cluster_id
        self.timestamp = None  # Set when captured

        # Logic state distribution
        self.l0_count = sum(1 for c in cells if c.logic_state == TripolarLogicState.L0)
        self.l1_count = sum(1 for c in cells if c.logic_state == TripolarLogicState.L1)
        self.ld_count = sum(1 for c in cells if c.logic_state == TripolarLogicState.LD)
        self.total_cells = len(cells)

        # Internal state statistics
        x_values = [c.x for c in cells]
        self.mean_x = np.mean(x_values) if x_values else 0.5
        self.std_x = np.std(x_values) if x_values else 0.0

        # Phase statistics
        phases = [c.phase for c in cells]
        self.mean_phase = np.mean(phases) if phases else 0.0

        # Emission statistics
        emissions = [c.compute_emission() for c in cells]
        self.mean_emission = np.mean(emissions) if emissions else 0.0
        self.max_emission = np.max(emissions) if emissions else 0.0

    def to_vector(self) -> np.ndarray:
        """
        Convert signature to vector form.

        Returns:
            Feature vector representing cluster state
        """
        if self.total_cells == 0:
            return np.zeros(8)

        return np.array([
            self.l0_count / self.total_cells,
            self.l1_count / self.total_cells,
            self.ld_count / self.total_cells,
            self.mean_x,
            self.std_x,
            self.mean_phase,
            self.mean_emission,
            self.max_emission
        ])

    def __repr__(self) -> str:
        return (
            f"ClusterSignature(id={self.cluster_id}, "
            f"L0={self.l0_count}, L1={self.l1_count}, LD={self.ld_count}, "
            f"mean_x={self.mean_x:.3f})"
        )


class HolisticMirrorState:
    """
    Holistic mirror state H(t) as global meta-operator.

    Constructed from signatures of all four clusters:
    H(t) = Φ(S0, S1, S2, S3)

    The mirror state provides a global, coherent representation
    that couples back to all cells in LD state.
    """

    def __init__(self):
        """Initialize holistic mirror state."""
        self.signatures: Dict[int, Optional[ClusterSignature]] = {
            0: None,
            1: None,
            2: None,
            3: None
        }

        self.mirror_value: Optional[float] = None
        self.mirror_vector: Optional[np.ndarray] = None

        self.computation_count = 0
        self.history: List[float] = []

    def update_cluster_signature(
        self,
        cluster_id: int,
        cells: List['TripolarGabrielCell'],
        timestamp: int
    ) -> ClusterSignature:
        """
        Update signature for a cluster.

        Args:
            cluster_id: Cluster index (0-3)
            cells: Cells in this cluster
            timestamp: Current time step

        Returns:
            Computed cluster signature
        """
        signature = ClusterSignature(cluster_id, cells)
        signature.timestamp = timestamp
        self.signatures[cluster_id] = signature
        return signature

    def can_compute_mirror_state(self) -> bool:
        """
        Check if all cluster signatures are available.

        Returns:
            True if H(t) can be computed
        """
        return all(sig is not None for sig in self.signatures.values())

    def compute_mirror_state(self) -> float:
        """
        Compute holistic mirror state H(t) from all cluster signatures.

        Φ(S0, S1, S2, S3) - aggregation function

        Several approaches possible:
        1. Normalized linear combination
        2. Dominant eigenvector
        3. Spectral fingerprint
        4. Weighted consensus

        Current implementation: Weighted combination

        Returns:
            Scalar mirror state H(t) ∈ [0,1]
        """
        if not self.can_compute_mirror_state():
            raise ValueError("Cannot compute mirror state - missing signatures")

        # Collect all signature vectors
        vectors = [sig.to_vector() for sig in self.signatures.values()]
        combined = np.stack(vectors)  # Shape: (4, 8)

        # Aggregate: mean across clusters, then weighted mean of features
        cluster_means = combined.mean(axis=0)  # Shape: (8,)

        # Weight different components
        weights = np.array([
            0.1,  # L0 fraction
            0.1,  # L1 fraction
            0.3,  # LD fraction (important!)
            0.2,  # mean_x
            0.1,  # std_x
            0.1,  # mean_phase
            0.05, # mean_emission
            0.05  # max_emission
        ])

        # Compute weighted scalar
        self.mirror_value = float(np.dot(cluster_means, weights))
        self.mirror_vector = cluster_means

        self.computation_count += 1
        self.history.append(self.mirror_value)

        return self.mirror_value

    def get_mirror_value(self) -> Optional[float]:
        """
        Get current mirror state value.

        Returns:
            H(t) if computed, else None
        """
        return self.mirror_value

    def get_mirror_modulation(
        self,
        base_learning_rate: float
    ) -> float:
        """
        Get learning rate modulation from mirror state.

        Used for holistic modulation:
        w_ci(t+1) ← w_ci(t+1) + λ · G_ci(H(t))

        Args:
            base_learning_rate: Base λ

        Returns:
            Modulated learning rate
        """
        if self.mirror_value is None:
            return base_learning_rate

        # Modulate based on mirror state
        # High mirror state (global coherence) → enhance learning
        # Low mirror state → reduce learning
        modulation = 1.0 + (self.mirror_value - 0.5) * 0.5

        return base_learning_rate * modulation

    def get_coherence_metric(self) -> float:
        """
        Compute global coherence from cluster signatures.

        Returns:
            Coherence score [0,1]
        """
        if not self.can_compute_mirror_state():
            return 0.0

        # Measure similarity across clusters
        vectors = [sig.to_vector() for sig in self.signatures.values()]

        # Compute pairwise correlations
        correlations = []
        for i in range(4):
            for j in range(i+1, 4):
                corr = np.corrcoef(vectors[i], vectors[j])[0, 1]
                if not np.isnan(corr):
                    correlations.append(abs(corr))

        if correlations:
            return float(np.mean(correlations))
        return 0.0

    def reset_signatures(self) -> None:
        """Reset all cluster signatures for new cycle."""
        self.signatures = {
            0: None,
            1: None,
            2: None,
            3: None
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'mirror_value': self.mirror_value,
            'mirror_vector': self.mirror_vector.tolist() if self.mirror_vector is not None else None,
            'computation_count': self.computation_count,
            'coherence': self.get_coherence_metric(),
            'signatures': {
                k: {
                    'L0': v.l0_count,
                    'L1': v.l1_count,
                    'LD': v.ld_count,
                    'mean_x': v.mean_x
                } if v else None
                for k, v in self.signatures.items()
            }
        }

    def __repr__(self) -> str:
        return (
            f"HolisticMirrorState(H={self.mirror_value:.3f if self.mirror_value else 'None'}, "
            f"computations={self.computation_count}, "
            f"coherence={self.get_coherence_metric():.3f})"
        )
