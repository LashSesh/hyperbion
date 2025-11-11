"""
Global Phase System
===================

Rotating phase space Θ(t) that determines active quadrant and cluster.

Phase evolution: Θ(t+1) = (Θ(t) + Δ) mod 1
Quadrants: Q0=[0,0.25), Q1=[0.25,0.5), Q2=[0.5,0.75), Q3=[0.75,1)
"""

from typing import List, Dict, Any
import numpy as np


class GlobalPhase:
    """
    Global phase Θ(t) ∈ [0,1) with discrete dynamics.

    The phase rotates through four quadrants, determining which
    cluster is active on the main communication channel.
    """

    def __init__(
        self,
        initial_phase: float = 0.0,
        delta: float = 0.01
    ):
        """
        Initialize global phase.

        Args:
            initial_phase: Θ(0) ∈ [0,1)
            delta: Phase increment per step
        """
        if not 0 <= initial_phase < 1:
            raise ValueError("initial_phase must be in [0,1)")
        if not 0 < delta < 1:
            raise ValueError("delta must be in (0,1)")

        self.theta = initial_phase
        self.delta = delta
        self.step_count = 0

        # History
        self.history: List[float] = [initial_phase]
        self.quadrant_history: List[int] = [self.get_active_quadrant()]

    def step(self) -> float:
        """
        Advance phase by one step.

        Θ(t+1) = (Θ(t) + Δ) mod 1

        Returns:
            New phase value
        """
        self.theta = (self.theta + self.delta) % 1.0
        self.step_count += 1

        self.history.append(self.theta)
        self.quadrant_history.append(self.get_active_quadrant())

        return self.theta

    def get_active_quadrant(self) -> int:
        """
        Get current active quadrant.

        Q0 = [0, 0.25)
        Q1 = [0.25, 0.5)
        Q2 = [0.5, 0.75)
        Q3 = [0.75, 1)

        Returns:
            Quadrant index 0, 1, 2, or 3
        """
        if self.theta < 0.25:
            return 0
        elif self.theta < 0.5:
            return 1
        elif self.theta < 0.75:
            return 2
        else:
            return 3

    def is_quadrant_active(self, quadrant: int) -> bool:
        """
        Check if given quadrant is currently active.

        Args:
            quadrant: Quadrant index (0-3)

        Returns:
            True if quadrant is active
        """
        return self.get_active_quadrant() == quadrant

    def has_completed_cycle(self) -> bool:
        """
        Check if a complete cycle (all 4 quadrants) has been traversed.

        Returns:
            True if current position indicates cycle completion
        """
        if len(self.quadrant_history) < 4:
            return False

        # Check if we've just entered Q0 from Q3
        if (len(self.quadrant_history) >= 2 and
            self.quadrant_history[-2] == 3 and
            self.quadrant_history[-1] == 0):
            return True

        return False

    def get_phase_in_quadrant(self) -> float:
        """
        Get phase position within current quadrant [0,1).

        Returns:
            Normalized position in quadrant
        """
        quadrant = self.get_active_quadrant()
        quadrant_start = quadrant * 0.25
        return (self.theta - quadrant_start) / 0.25

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'theta': self.theta,
            'delta': self.delta,
            'step_count': self.step_count,
            'active_quadrant': self.get_active_quadrant()
        }

    def __repr__(self) -> str:
        return (
            f"GlobalPhase(θ={self.theta:.4f}, "
            f"quadrant=Q{self.get_active_quadrant()}, "
            f"step={self.step_count})"
        )


class QuadrantSelector:
    """
    Manages resonance gating based on global phase.

    For each cluster k, determines if it can emit on main channel:
    R_k(t) = 1 if Θ(t) ∈ Q_k, else 0
    """

    def __init__(self, phase_system: GlobalPhase):
        """
        Initialize quadrant selector.

        Args:
            phase_system: Global phase system
        """
        self.phase_system = phase_system

    def get_resonance_gates(self) -> Dict[int, bool]:
        """
        Get resonance gate status for all quadrants.

        Returns:
            {cluster_id: can_emit} for clusters 0-3
        """
        active = self.phase_system.get_active_quadrant()
        return {
            0: (active == 0),
            1: (active == 1),
            2: (active == 2),
            3: (active == 3)
        }

    def can_cluster_emit(self, cluster_id: int) -> bool:
        """
        Check if cluster can emit on main channel.

        Args:
            cluster_id: Cluster index (0-3)

        Returns:
            True if cluster is in active quadrant
        """
        return self.phase_system.get_active_quadrant() == cluster_id

    def get_next_active_cluster(self) -> int:
        """
        Predict which cluster will be active after next step.

        Returns:
            Next active cluster ID
        """
        # Simulate next phase
        next_theta = (self.phase_system.theta + self.phase_system.delta) % 1.0

        if next_theta < 0.25:
            return 0
        elif next_theta < 0.5:
            return 1
        elif next_theta < 0.75:
            return 2
        else:
            return 3

    def __repr__(self) -> str:
        gates = self.get_resonance_gates()
        active_clusters = [k for k, v in gates.items() if v]
        return f"QuadrantSelector(active={active_clusters})"
