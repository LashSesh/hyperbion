"""
Binary Network Implementation
==============================

Classical binary neural network for benchmark comparison.
Uses 2 states per node (0, 1) with similar architecture to Hyperbion.
"""

from typing import Dict, List, Optional, Set
import numpy as np
import time
from dataclasses import dataclass


@dataclass
class BinaryNetworkParams:
    """Parameters for binary network."""
    learning_rate: float = 0.01
    weight_decay: float = 0.001
    threshold: float = 0.5
    w_max: float = 5.0
    w_min: float = -5.0


class BinaryNode:
    """
    Binary node with 2 states (0, 1).

    Analogous to GabrielCell but with binary logic.
    """

    def __init__(
        self,
        node_id: int,
        initial_state: int = 0,
        bias: float = 0.0,
        params: Optional[BinaryNetworkParams] = None
    ):
        """Initialize binary node."""
        if initial_state not in {0, 1}:
            raise ValueError(f"State must be 0 or 1, got {initial_state}")

        self.id = node_id
        self.state = initial_state
        self.bias = bias
        self.params = params or BinaryNetworkParams()

        self.connections: Dict[int, float] = {}
        self.state_history: List[int] = [initial_state]
        self.age = 0

    def connect(self, target_id: int, weight: float) -> None:
        """Create connection to another node."""
        weight = np.clip(weight, self.params.w_min, self.params.w_max)
        self.connections[target_id] = weight

    def compute_activation(
        self,
        neighbor_states: Dict[int, int],
        noise_level: float = 0.0
    ) -> float:
        """Compute activation value."""
        activation = 0.0

        for target_id, weight in self.connections.items():
            if target_id in neighbor_states:
                activation += weight * neighbor_states[target_id]

        activation += self.bias

        if noise_level > 0:
            activation += np.random.normal(0, noise_level)

        return activation

    def binary_threshold(self, value: float) -> int:
        """Apply binary threshold function."""
        return 1 if value > self.params.threshold else 0

    def update_state(
        self,
        neighbor_states: Dict[int, int],
        noise_level: float = 0.0
    ) -> int:
        """Update node state."""
        activation = self.compute_activation(neighbor_states, noise_level)
        new_state = self.binary_threshold(activation)

        self.state = new_state
        self.state_history.append(new_state)
        self.age += 1

        return new_state

    def apply_learning(
        self,
        neighbor_states: Dict[int, int]
    ) -> Dict[int, float]:
        """Apply learning rule (Hebbian-style)."""
        weight_changes = {}

        for target_id, weight in list(self.connections.items()):
            if target_id not in neighbor_states:
                continue

            target_state = neighbor_states[target_id]

            # Hebbian learning for binary states
            delta_w = (
                self.params.learning_rate * self.state * target_state -
                self.params.weight_decay * weight
            )

            new_weight = np.clip(
                weight + delta_w,
                self.params.w_min,
                self.params.w_max
            )

            self.connections[target_id] = new_weight
            weight_changes[target_id] = delta_w

        return weight_changes


class BinaryNetwork:
    """
    Classical binary neural network.

    Reference implementation for benchmark comparison with Hyperbion.
    Uses 2 states per node: 0, 1
    Information capacity: I = log2(2) * N = N bits
    """

    def __init__(
        self,
        name: str = "BinaryNetwork",
        params: Optional[BinaryNetworkParams] = None
    ):
        """Initialize binary network."""
        self.name = name
        self.nodes: Dict[int, BinaryNode] = {}
        self.next_node_id = 0
        self.params = params or BinaryNetworkParams()

        self.step_count = 0
        self.creation_time = time.time()

        # Metrics
        self.convergence_time: Optional[int] = None
        self.training_epochs = 0

    def add_node(
        self,
        state: int = 0,
        bias: float = 0.0
    ) -> int:
        """Add a node to the network."""
        node_id = self.next_node_id

        node = BinaryNode(
            node_id=node_id,
            initial_state=state,
            bias=bias,
            params=self.params
        )

        self.nodes[node_id] = node
        self.next_node_id += 1

        return node_id

    def remove_node(self, node_id: int) -> bool:
        """Remove a node from the network."""
        if node_id not in self.nodes:
            return False

        # Remove connections to this node
        for node in self.nodes.values():
            if node_id in node.connections:
                del node.connections[node_id]

        del self.nodes[node_id]
        return True

    def connect_nodes(
        self,
        source_id: int,
        target_id: int,
        weight: float
    ) -> bool:
        """Create connection between nodes."""
        if source_id not in self.nodes or target_id not in self.nodes:
            return False

        self.nodes[source_id].connect(target_id, weight)
        return True

    def step(
        self,
        inputs: Optional[Dict[int, int]] = None,
        noise_level: float = 0.0,
        apply_learning: bool = True
    ) -> Dict[str, any]:
        """Execute one simulation step."""
        # Apply inputs
        if inputs:
            for node_id, state in inputs.items():
                if node_id in self.nodes:
                    self.nodes[node_id].state = state

        # Collect current states
        current_states = {nid: node.state for nid, node in self.nodes.items()}

        # Update all nodes
        new_states = {}
        for node_id, node in self.nodes.items():
            new_state = node.update_state(current_states, noise_level)
            new_states[node_id] = new_state

        # Apply learning
        if apply_learning:
            for node in self.nodes.values():
                node.apply_learning(current_states)

        self.step_count += 1

        return {
            'step': self.step_count,
            'new_states': new_states,
            'network_size': len(self.nodes)
        }

    def get_information_capacity(self) -> float:
        """
        Compute theoretical information capacity.

        For binary network: I = log2(2) * N = N bits
        """
        return len(self.nodes) * 1.0  # log2(2) = 1

    def get_total_connections(self) -> int:
        """Get total number of connections."""
        return sum(len(node.connections) for node in self.nodes.values())

    def check_convergence(self, window: int = 10) -> bool:
        """
        Check if network has converged.

        Convergence = no state changes in recent window.
        """
        if len(self.nodes) == 0:
            return True

        for node in self.nodes.values():
            if len(node.state_history) < window + 1:
                return False

            recent_states = node.state_history[-window:]
            if len(set(recent_states)) > 1:
                return False

        return True

    def get_state(self) -> Dict:
        """Get network state."""
        return {
            'name': self.name,
            'network_type': 'binary',
            'step_count': self.step_count,
            'network_size': len(self.nodes),
            'total_connections': self.get_total_connections(),
            'information_capacity': self.get_information_capacity(),
            'nodes': {
                nid: {
                    'state': node.state,
                    'bias': node.bias,
                    'connections': len(node.connections)
                }
                for nid, node in self.nodes.items()
            }
        }

    def __repr__(self) -> str:
        return (
            f"BinaryNetwork(name='{self.name}', "
            f"nodes={len(self.nodes)}, "
            f"steps={self.step_count})"
        )
