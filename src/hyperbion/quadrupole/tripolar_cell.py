"""
Tripolar Gabriel Cell
=====================

Enhanced Gabriel Cell with continuous internal state and tripolar logic.

Tripolar Logic Space: Σ = {L0, L1, LD}
- L0: Inactive pole
- L1: Active pole
- LD: Dynamic, oscillating mode coupled to holistic mirror state

Internal state: x_c(t) ∈ [0,1]
Logic evaluation with thresholds: 0 ≤ τ₀ < τ₁ ≤ 1
"""

from typing import Dict, Optional, List, Tuple, Any
from enum import Enum
import numpy as np
import time


class TripolarLogicState(Enum):
    """Tripolar logic states."""
    L0 = "L0"  # Inactive pole
    L1 = "L1"  # Active pole
    LD = "LD"  # Dynamic, oscillating (coupled to mirror state)


class TripolarGabrielCell:
    """
    Tripolar Gabriel Cell with continuous internal state.

    Mathematical Model:
    -------------------
    Internal state: x_c(t) ∈ [0,1]

    Logic evaluation:
        σ_c(t) = L0  if x_c(t) ≤ τ₀
        σ_c(t) = L1  if x_c(t) ≥ τ₁
        σ_c(t) = LD  if τ₀ < x_c(t) < τ₁

    State update:
        x_c(t+1) = f(x_c(t), Σ_j w_cj y_j(t), Input_c(t))

    LD coupling to mirror state H(t):
        x_c(t+1) = (1-α) x_c(t) + α Ψ_c(H(t))  when σ_c = LD
    """

    def __init__(
        self,
        cell_id: int,
        cluster_id: int,
        initial_x: float = 0.5,
        tau_0: float = 0.3,
        tau_1: float = 0.7,
        bias: float = 0.0,
        phase: float = 0.0,
        mirror_coupling: float = 0.3
    ):
        """
        Initialize Tripolar Gabriel Cell.

        Args:
            cell_id: Unique cell identifier
            cluster_id: Quadrupole cluster (0, 1, 2, 3)
            initial_x: Initial internal state [0,1]
            tau_0: Lower threshold for logic evaluation
            tau_1: Upper threshold for logic evaluation
            bias: Cell bias
            phase: Local phase/resonance component θ_c
            mirror_coupling: Coupling strength to mirror state (α)
        """
        if not 0 <= initial_x <= 1:
            raise ValueError("initial_x must be in [0,1]")
        if not 0 <= tau_0 < tau_1 <= 1:
            raise ValueError("Must have 0 ≤ τ₀ < τ₁ ≤ 1")
        if cluster_id not in {0, 1, 2, 3}:
            raise ValueError("cluster_id must be in {0, 1, 2, 3}")

        self.id = cell_id
        self.cluster_id = cluster_id

        # Internal continuous state
        self.x = initial_x

        # Thresholds
        self.tau_0 = tau_0
        self.tau_1 = tau_1

        # Bias and phase
        self.bias = bias
        self.phase = phase  # θ_c - local resonance

        # Mirror state coupling
        self.alpha = mirror_coupling

        # Connections
        self.connections: Dict[int, float] = {}  # {cell_id: weight}

        # History
        self.x_history: List[float] = [initial_x]
        self.logic_history: List[TripolarLogicState] = [self.evaluate_logic()]
        self.age = 0

        # Emission value
        self._emission = 0.0

    def evaluate_logic(self) -> TripolarLogicState:
        """
        Evaluate tripolar logic state from internal state.

        Returns:
            σ_c(t) ∈ {L0, L1, LD}
        """
        if self.x <= self.tau_0:
            return TripolarLogicState.L0
        elif self.x >= self.tau_1:
            return TripolarLogicState.L1
        else:
            return TripolarLogicState.LD

    @property
    def logic_state(self) -> TripolarLogicState:
        """Get current logic state."""
        return self.evaluate_logic()

    def compute_emission(self) -> float:
        """
        Compute emission value y_c(t) based on logic state.

        Emission function g(σ_c(t), x_c(t)):
        - L0: Suppressed (0)
        - L1: Deterministic forward (x_c)
        - LD: Modulated/resonant

        Returns:
            y_c(t) - emission value
        """
        logic = self.logic_state

        if logic == TripolarLogicState.L0:
            # Suppressed
            return 0.0
        elif logic == TripolarLogicState.L1:
            # Forward current state
            return self.x
        else:  # LD
            # Modulated by phase
            return self.x * (0.5 + 0.5 * np.sin(2 * np.pi * self.phase))

    def compute_input(self, neighbor_states: Dict[int, float]) -> float:
        """
        Compute weighted input from neighbors.

        Args:
            neighbor_states: {cell_id: emission_value}

        Returns:
            Σ_j w_cj y_j(t)
        """
        total = 0.0
        for cell_id, weight in self.connections.items():
            if cell_id in neighbor_states:
                total += weight * neighbor_states[cell_id]
        return total

    def update_state(
        self,
        neighbor_states: Dict[int, float],
        external_input: float = 0.0,
        mirror_state: Optional[float] = None,
        noise_level: float = 0.0
    ) -> float:
        """
        Update internal state x_c(t).

        Standard update:
            x_c(t+1) = f(x_c(t), Σ w_cj y_j(t), Input_c(t))

        LD coupling (when σ_c = LD and mirror_state provided):
            x_c(t+1) = (1-α) x_c(t) + α Ψ_c(H(t))

        Args:
            neighbor_states: {cell_id: emission} from neighbors
            external_input: External input signal
            mirror_state: Holistic mirror state H(t)
            noise_level: Noise standard deviation

        Returns:
            New internal state x_c(t+1)
        """
        # Compute weighted input
        weighted_input = self.compute_input(neighbor_states)

        # Standard activation
        activation = weighted_input + self.bias + external_input

        # Add noise
        if noise_level > 0:
            activation += np.random.normal(0, noise_level)

        # Sigmoid-like update function
        x_new = 1.0 / (1.0 + np.exp(-activation))

        # Apply LD coupling if in LD state and mirror state available
        if self.logic_state == TripolarLogicState.LD and mirror_state is not None:
            # Ψ_c(H(t)) - project mirror state to cell's space
            psi_c = self._project_mirror_state(mirror_state)
            x_new = (1 - self.alpha) * x_new + self.alpha * psi_c

        # Ensure bounds
        x_new = np.clip(x_new, 0.0, 1.0)

        self.x = x_new
        self.x_history.append(x_new)
        self.logic_history.append(self.evaluate_logic())
        self.age += 1

        # Update emission
        self._emission = self.compute_emission()

        return x_new

    def _project_mirror_state(self, mirror_state: float) -> float:
        """
        Project mirror state to cell's internal space.

        Ψ_c(H(t)) - cell-specific projection function

        Args:
            mirror_state: Global mirror state H(t)

        Returns:
            Projected value for this cell
        """
        # Phase-modulated projection
        # Each cell sees the mirror state through its local phase
        phase_factor = np.cos(2 * np.pi * (self.phase - mirror_state))
        return 0.5 * (1 + phase_factor)

    def connect(self, target_id: int, weight: float) -> None:
        """
        Create or update connection to another cell.

        Args:
            target_id: Target cell ID
            weight: Synaptic weight
        """
        self.connections[target_id] = weight

    def disconnect(self, target_id: int) -> bool:
        """
        Remove connection to another cell.

        Args:
            target_id: Target cell ID

        Returns:
            True if connection existed
        """
        if target_id in self.connections:
            del self.connections[target_id]
            return True
        return False

    def apply_hebbian_learning(
        self,
        neighbor_logic: Dict[int, TripolarLogicState],
        neighbor_x: Dict[int, float],
        learning_rate: float = 0.01
    ) -> Dict[int, float]:
        """
        Apply tripolar Hebbian learning rule.

        Δw_ci = η · f_Hebb(σ_i, σ_c)

        Rules:
        - Positive for correlated L1 activity
        - Negative for inconsistent patterns
        - LD-weighted when cells coupled to mirror

        Args:
            neighbor_logic: {cell_id: logic_state}
            neighbor_x: {cell_id: internal_state}
            learning_rate: η

        Returns:
            {cell_id: Δw}
        """
        weight_changes = {}
        my_logic = self.logic_state

        for cell_id, weight in list(self.connections.items()):
            if cell_id not in neighbor_logic:
                continue

            other_logic = neighbor_logic[cell_id]
            other_x = neighbor_x.get(cell_id, 0.5)

            # Hebbian term
            if my_logic == TripolarLogicState.L1 and other_logic == TripolarLogicState.L1:
                # Both active - strengthen
                delta = learning_rate * self.x * other_x
            elif my_logic == TripolarLogicState.L0 and other_logic == TripolarLogicState.L0:
                # Both inactive - no change
                delta = 0.0
            elif my_logic == TripolarLogicState.LD or other_logic == TripolarLogicState.LD:
                # LD involvement - modulated learning
                delta = learning_rate * 0.5 * (self.x - 0.5) * (other_x - 0.5)
            else:
                # Inconsistent - weaken
                delta = -learning_rate * 0.5

            # Weight decay (smaller than learning rate)
            delta -= learning_rate * 0.1 * weight

            # Apply
            new_weight = weight + delta
            self.connections[cell_id] = new_weight
            weight_changes[cell_id] = delta

        return weight_changes

    def to_dict(self) -> Dict[str, Any]:
        """Serialize cell to dictionary."""
        return {
            'id': self.id,
            'cluster_id': self.cluster_id,
            'x': self.x,
            'tau_0': self.tau_0,
            'tau_1': self.tau_1,
            'bias': self.bias,
            'phase': self.phase,
            'alpha': self.alpha,
            'logic_state': self.logic_state.value,
            'emission': self._emission,
            'connections': self.connections,
            'age': self.age
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TripolarGabrielCell':
        """Deserialize cell from dictionary."""
        cell = cls(
            cell_id=data['id'],
            cluster_id=data['cluster_id'],
            initial_x=data['x'],
            tau_0=data['tau_0'],
            tau_1=data['tau_1'],
            bias=data['bias'],
            phase=data['phase'],
            mirror_coupling=data['alpha']
        )
        cell.connections = data['connections']
        cell.age = data['age']
        return cell

    def __repr__(self) -> str:
        return (
            f"TripolarGabrielCell(id={self.id}, cluster={self.cluster_id}, "
            f"x={self.x:.3f}, logic={self.logic_state.value}, age={self.age})"
        )
