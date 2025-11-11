"""
Gabriel Cell Implementation
============================

Core cell with tripolar state logic, dynamic plasticity, and operator support.
Implements the fundamental unit of the Hyperbion Tripolar Network.
"""

from typing import Dict, Optional, List, Tuple
import numpy as np
from dataclasses import dataclass, field
import time


@dataclass
class PlasticityParams:
    """Parameters for plasticity rules."""
    alpha: float = 0.01  # Hebbian learning rate
    beta: float = 0.001  # Weight decay
    gamma: float = 0.005  # Morphogenesis factor
    theta_pos: float = 0.5  # Positive activation threshold
    theta_neg: float = -0.5  # Negative activation threshold
    w_max: float = 5.0  # Maximum weight magnitude
    w_min: float = -5.0  # Minimum weight magnitude


class GabrielCell:
    """
    Gabriel Cell - Fundamental unit of the Hyperbion Tripolar Network.

    Characteristics:
    - Tripolar state: s ∈ {-1, 0, +1}
    - Weighted connections: w_ij ∈ [w_min, w_max]
    - Dynamic plasticity: Hebbian learning + morphogenesis
    - Operator support: DK, SW, WT, Nullpunkt, MOR

    Mathematical Model:
    -------------------
    State update:
        s_i^{t+1} = sign(Σ_j w_ij s_j^t + b_i + η_i^t)

    Plasticity:
        Δw_ij = α s_i s_j - β w_ij + γ f_morph(C_ij, t)

    Where:
        - sign(x) = +1 if x > θ_pos, -1 if x < θ_neg, 0 otherwise
        - η_i^t = noise term
        - f_morph = morphogenesis function
    """

    def __init__(
        self,
        cell_id: int,
        initial_state: int = 0,
        bias: float = 0.0,
        plasticity_params: Optional[PlasticityParams] = None
    ):
        """
        Initialize a Gabriel Cell.

        Args:
            cell_id: Unique identifier for the cell
            initial_state: Initial tripolar state (-1, 0, or +1)
            bias: Cell bias term
            plasticity_params: Parameters for plasticity rules
        """
        if initial_state not in {-1, 0, 1}:
            raise ValueError(f"Initial state must be -1, 0, or +1, got {initial_state}")

        self.id = cell_id
        self.state = initial_state
        self.bias = bias
        self.params = plasticity_params or PlasticityParams()

        # Connections: {cell_id: weight}
        self.connections: Dict[int, float] = {}

        # History tracking
        self.state_history: List[int] = [initial_state]
        self.activation_history: List[float] = [0.0]

        # Temporal state for operators
        self.wormhole_connections: Dict[int, Tuple[float, float]] = {}  # {cell_id: (weight, expiry_time)}
        self.last_update_time = time.time()

        # Morphogenesis tracking
        self.division_count = 0
        self.fusion_count = 0
        self.age = 0

        # Operator application tracking
        self.operator_applications: List[Dict] = []

    def connect(self, target_id: int, weight: float) -> None:
        """
        Create or update a connection to another cell.

        Args:
            target_id: ID of target cell
            weight: Connection weight (clipped to [w_min, w_max])
        """
        weight = np.clip(weight, self.params.w_min, self.params.w_max)
        self.connections[target_id] = weight

    def disconnect(self, target_id: int) -> bool:
        """
        Remove a connection to another cell.

        Args:
            target_id: ID of target cell

        Returns:
            True if connection existed and was removed
        """
        if target_id in self.connections:
            del self.connections[target_id]
            return True
        return False

    def add_wormhole(self, target_id: int, weight: float, duration: float) -> None:
        """
        Add a temporary wormhole connection (WT operator).

        Args:
            target_id: ID of target cell
            weight: Connection weight
            duration: How long the wormhole lasts (seconds)
        """
        expiry = time.time() + duration
        self.wormhole_connections[target_id] = (weight, expiry)

    def clean_wormholes(self) -> int:
        """
        Remove expired wormhole connections.

        Returns:
            Number of wormholes removed
        """
        current_time = time.time()
        expired = [
            target_id for target_id, (_, expiry) in self.wormhole_connections.items()
            if current_time > expiry
        ]

        for target_id in expired:
            del self.wormhole_connections[target_id]

        return len(expired)

    def compute_activation(
        self,
        neighbor_states: Dict[int, int],
        noise_level: float = 0.0
    ) -> float:
        """
        Compute the raw activation value before applying sign function.

        Args:
            neighbor_states: Dictionary of {cell_id: state} for connected cells
            noise_level: Standard deviation of Gaussian noise

        Returns:
            Raw activation value
        """
        # Clean expired wormholes first
        self.clean_wormholes()

        # Sum weighted inputs from permanent connections
        activation = 0.0
        for target_id, weight in self.connections.items():
            if target_id in neighbor_states:
                activation += weight * neighbor_states[target_id]

        # Add wormhole connections
        for target_id, (weight, _) in self.wormhole_connections.items():
            if target_id in neighbor_states:
                activation += weight * neighbor_states[target_id]

        # Add bias
        activation += self.bias

        # Add noise
        if noise_level > 0:
            activation += np.random.normal(0, noise_level)

        return activation

    def tripolar_sign(self, value: float) -> int:
        """
        Apply tripolar sign function with thresholds.

        Args:
            value: Input value

        Returns:
            Tripolar state: -1, 0, or +1
        """
        if value > self.params.theta_pos:
            return 1
        elif value < self.params.theta_neg:
            return -1
        else:
            return 0

    def update_state(
        self,
        neighbor_states: Dict[int, int],
        noise_level: float = 0.0
    ) -> int:
        """
        Update cell state based on inputs and tripolar logic.

        Args:
            neighbor_states: Dictionary of {cell_id: state} for connected cells
            noise_level: Noise level for stochastic dynamics

        Returns:
            New tripolar state
        """
        activation = self.compute_activation(neighbor_states, noise_level)
        new_state = self.tripolar_sign(activation)

        self.state = new_state
        self.state_history.append(new_state)
        self.activation_history.append(activation)
        self.age += 1
        self.last_update_time = time.time()

        return new_state

    def apply_plasticity(
        self,
        neighbor_states: Dict[int, int],
        morphogenesis_context: Optional[Dict] = None
    ) -> Dict[int, float]:
        """
        Apply plasticity rule to update connection weights.

        Implements: Δw_ij = α s_i s_j - β w_ij + γ f_morph(C_ij, t)

        Args:
            neighbor_states: Current states of connected cells
            morphogenesis_context: Additional context for morphogenesis

        Returns:
            Dictionary of weight changes {cell_id: delta_w}
        """
        weight_changes = {}

        for target_id, weight in list(self.connections.items()):
            if target_id not in neighbor_states:
                continue

            target_state = neighbor_states[target_id]

            # Hebbian term: α s_i s_j
            hebbian_term = self.params.alpha * self.state * target_state

            # Decay term: -β w_ij
            decay_term = -self.params.beta * weight

            # Morphogenesis term: γ f_morph(C_ij, t)
            morph_term = 0.0
            if morphogenesis_context:
                # Context-dependent morphogenesis
                cluster_activity = morphogenesis_context.get('cluster_activity', 0.0)
                stress_level = morphogenesis_context.get('stress', 0.0)
                morph_term = self.params.gamma * cluster_activity * stress_level

            # Total weight change
            delta_w = hebbian_term + decay_term + morph_term

            # Update weight with clipping
            new_weight = np.clip(
                weight + delta_w,
                self.params.w_min,
                self.params.w_max
            )

            self.connections[target_id] = new_weight
            weight_changes[target_id] = delta_w

        return weight_changes

    def get_connection_strength(self, target_id: int) -> float:
        """
        Get total connection strength to a target (including wormholes).

        Args:
            target_id: Target cell ID

        Returns:
            Total connection weight
        """
        strength = self.connections.get(target_id, 0.0)

        # Add wormhole if active
        if target_id in self.wormhole_connections:
            weight, expiry = self.wormhole_connections[target_id]
            if time.time() < expiry:
                strength += weight

        return strength

    def record_operator_application(
        self,
        operator_type: str,
        parameters: Dict
    ) -> None:
        """
        Record that an operator was applied to this cell.

        Args:
            operator_type: Type of operator (DK, SW, WT, etc.)
            parameters: Operator parameters
        """
        self.operator_applications.append({
            'type': operator_type,
            'time': time.time(),
            'age': self.age,
            'parameters': parameters
        })

    def to_dict(self) -> Dict:
        """
        Serialize cell to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'state': self.state,
            'bias': self.bias,
            'connections': self.connections,
            'wormhole_connections': {
                k: {'weight': v[0], 'expiry': v[1]}
                for k, v in self.wormhole_connections.items()
            },
            'age': self.age,
            'division_count': self.division_count,
            'fusion_count': self.fusion_count,
            'plasticity_params': {
                'alpha': self.params.alpha,
                'beta': self.params.beta,
                'gamma': self.params.gamma,
                'theta_pos': self.params.theta_pos,
                'theta_neg': self.params.theta_neg,
                'w_max': self.params.w_max,
                'w_min': self.params.w_min,
            }
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'GabrielCell':
        """
        Deserialize cell from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            GabrielCell instance
        """
        params = PlasticityParams(**data['plasticity_params'])
        cell = cls(
            cell_id=data['id'],
            initial_state=data['state'],
            bias=data['bias'],
            plasticity_params=params
        )

        cell.connections = data['connections']
        cell.age = data['age']
        cell.division_count = data['division_count']
        cell.fusion_count = data['fusion_count']

        # Restore wormhole connections
        for target_id, wh_data in data['wormhole_connections'].items():
            cell.wormhole_connections[int(target_id)] = (
                wh_data['weight'],
                wh_data['expiry']
            )

        return cell

    def __repr__(self) -> str:
        return (
            f"GabrielCell(id={self.id}, state={self.state}, "
            f"connections={len(self.connections)}, age={self.age})"
        )
