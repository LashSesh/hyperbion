"""
Hyperbion Network
=================

Main network orchestrator managing cells, clusters, and operators.
"""

from typing import Dict, List, Optional, Set, Tuple, Any
import numpy as np
import time
from collections import defaultdict, deque
import networkx as nx

from .gabriel_cell import GabrielCell, PlasticityParams
from ..operators.base import Operator, OperatorResult
from ..operators.doppelkick import DoppelkickOperator
from ..operators.sweep import SweepOperator
from ..operators.wormhole import WormholeOperator
from ..operators.nullpunkt import NullpunktOperator
from ..operators.morphogenesis import MorphogenesisOperator


class HyperbionNetwork:
    """
    Hyperbion Tripolar Neural Network

    A self-organizing, structurally plastic network with:
    - Gabriel cells with tripolar states
    - Dynamic clustering
    - Autonomous operators (DK, SW, WT, Nullpunkt, MOR)
    - Emergent behavior and morphogenesis

    Key Features:
    -------------
    - Structural plasticity
    - Operator-driven evolution
    - Cluster-based organization
    - History tracking and replay
    - Deterministic simulation
    """

    def __init__(
        self,
        name: str = "HyperbionNetwork",
        default_plasticity_params: Optional[PlasticityParams] = None
    ):
        """
        Initialize the network.

        Args:
            name: Network identifier
            default_plasticity_params: Default plasticity parameters for cells
        """
        self.name = name
        self.cells: Dict[int, GabrielCell] = {}
        self.clusters: Dict[int, Dict[str, Any]] = {}
        self.next_cell_id = 0
        self.next_cluster_id = 0

        self.default_plasticity_params = default_plasticity_params or PlasticityParams()

        # Operators
        self.operators: Dict[str, Operator] = {
            'DK': DoppelkickOperator(),
            'SW': SweepOperator(),
            'WT': WormholeOperator(),
            'Nullpunkt': NullpunktOperator(),
            'MOR': MorphogenesisOperator()
        }

        # History tracking
        self.step_count = 0
        self.event_history: List[Dict] = []
        self.operator_history: List[OperatorResult] = []

        # Metrics
        self.metrics: Dict[str, List[float]] = defaultdict(list)

        # Creation time
        self.creation_time = time.time()

    def add_cell(
        self,
        state: int = 0,
        bias: float = 0.0,
        plasticity_params: Optional[PlasticityParams] = None
    ) -> int:
        """
        Add a new cell to the network.

        Args:
            state: Initial state (-1, 0, or +1)
            bias: Cell bias
            plasticity_params: Custom plasticity parameters

        Returns:
            Cell ID
        """
        cell_id = self.next_cell_id
        params = plasticity_params or self.default_plasticity_params

        cell = GabrielCell(
            cell_id=cell_id,
            initial_state=state,
            bias=bias,
            plasticity_params=params
        )

        self.cells[cell_id] = cell
        self.next_cell_id += 1

        self._log_event('cell_added', {'cell_id': cell_id, 'state': state})

        return cell_id

    def remove_cell(self, cell_id: int) -> bool:
        """
        Remove a cell from the network.

        Args:
            cell_id: ID of cell to remove

        Returns:
            True if cell was removed
        """
        if cell_id not in self.cells:
            return False

        # Remove all connections to this cell
        for cell in self.cells.values():
            cell.disconnect(cell_id)

        # Remove from clusters
        for cluster in self.clusters.values():
            if cell_id in cluster['members']:
                cluster['members'].remove(cell_id)

        # Remove the cell
        del self.cells[cell_id]

        self._log_event('cell_removed', {'cell_id': cell_id})

        return True

    def connect_cells(self, source_id: int, target_id: int, weight: float) -> bool:
        """
        Create a connection between cells.

        Args:
            source_id: Source cell ID
            target_id: Target cell ID
            weight: Connection weight

        Returns:
            True if connection was created
        """
        if source_id not in self.cells or target_id not in self.cells:
            return False

        self.cells[source_id].connect(target_id, weight)

        self._log_event('connection_created', {
            'source': source_id,
            'target': target_id,
            'weight': weight
        })

        return True

    def create_cluster(self, cell_ids: List[int], metadata: Optional[Dict] = None) -> int:
        """
        Create a cluster from a set of cells.

        Args:
            cell_ids: List of cell IDs
            metadata: Optional cluster metadata

        Returns:
            Cluster ID
        """
        cluster_id = self.next_cluster_id

        self.clusters[cluster_id] = {
            'members': list(cell_ids),
            'active': True,
            'metadata': metadata or {},
            'created_at': time.time(),
            'step_created': self.step_count
        }

        self.next_cluster_id += 1

        self._log_event('cluster_created', {
            'cluster_id': cluster_id,
            'size': len(cell_ids)
        })

        return cluster_id

    def auto_detect_clusters(self, min_cluster_size: int = 3) -> List[int]:
        """
        Automatically detect clusters based on connectivity.

        Uses connected components analysis.

        Args:
            min_cluster_size: Minimum cluster size

        Returns:
            List of created cluster IDs
        """
        # Build graph
        G = nx.DiGraph()

        for cell_id in self.cells.keys():
            G.add_node(cell_id)

        for cell_id, cell in self.cells.items():
            for target_id in cell.connections.keys():
                if target_id in self.cells:
                    G.add_edge(cell_id, target_id)

        # Find connected components (undirected)
        G_undirected = G.to_undirected()
        components = list(nx.connected_components(G_undirected))

        # Create clusters
        cluster_ids = []
        for component in components:
            if len(component) >= min_cluster_size:
                cluster_id = self.create_cluster(
                    list(component),
                    {'detection_method': 'auto', 'step': self.step_count}
                )
                cluster_ids.append(cluster_id)

        return cluster_ids

    def get_topological_distance(self, source_id: int, target_id: int) -> int:
        """
        Compute topological distance between two cells.

        Args:
            source_id: Source cell ID
            target_id: Target cell ID

        Returns:
            Shortest path length, or -1 if no path exists
        """
        if source_id not in self.cells or target_id not in self.cells:
            return -1

        # BFS to find shortest path
        visited = {source_id}
        queue = deque([(source_id, 0)])

        while queue:
            current_id, distance = queue.popleft()

            if current_id == target_id:
                return distance

            current_cell = self.cells[current_id]
            for neighbor_id in current_cell.connections.keys():
                if neighbor_id not in visited and neighbor_id in self.cells:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, distance + 1))

        return -1  # No path found

    def get_next_cell_id(self) -> int:
        """Get the next available cell ID."""
        return self.next_cell_id

    def step(
        self,
        inputs: Optional[Dict[int, int]] = None,
        noise_level: float = 0.0,
        apply_plasticity: bool = True,
        auto_trigger_operators: bool = True
    ) -> Dict[str, Any]:
        """
        Execute one simulation step.

        Args:
            inputs: Optional external inputs {cell_id: state}
            noise_level: Noise level for stochastic dynamics
            apply_plasticity: Whether to apply plasticity rules
            auto_trigger_operators: Whether to auto-trigger operators

        Returns:
            Dictionary with step results
        """
        step_start = time.time()

        # Apply external inputs
        if inputs:
            for cell_id, state in inputs.items():
                if cell_id in self.cells:
                    self.cells[cell_id].state = state

        # Collect current states
        current_states = {cid: cell.state for cid, cell in self.cells.items()}

        # Update all cells
        new_states = {}
        for cell_id, cell in self.cells.items():
            new_state = cell.update_state(current_states, noise_level)
            new_states[cell_id] = new_state

        # Apply plasticity
        weight_changes = {}
        if apply_plasticity:
            for cell_id, cell in self.cells.items():
                changes = cell.apply_plasticity(current_states)
                if changes:
                    weight_changes[cell_id] = changes

        # Auto-trigger operators
        triggered_operators = []
        if auto_trigger_operators:
            triggered_operators = self._auto_trigger_operators()

        # Update step count
        self.step_count += 1

        # Collect metrics
        self._collect_metrics()

        # Log step
        step_result = {
            'step': self.step_count,
            'new_states': new_states,
            'weight_changes': len(weight_changes),
            'triggered_operators': [op['type'] for op in triggered_operators],
            'network_size': len(self.cells),
            'execution_time': time.time() - step_start
        }

        self._log_event('step_completed', step_result)

        return step_result

    def _auto_trigger_operators(self) -> List[Dict[str, Any]]:
        """
        Automatically trigger operators based on conditions.

        Returns:
            List of triggered operator results
        """
        triggered = []

        # Check each operator's trigger conditions
        for op_name, operator in self.operators.items():
            trigger_info = operator.get_trigger_condition(self)

            if trigger_info.get('triggers'):
                # Apply to first triggered target
                triggers = trigger_info['triggers']

                if op_name == 'DK' and triggers:
                    # Apply to most coherent cluster
                    best_trigger = max(
                        triggers,
                        key=lambda t: t.get('coherence', 0),
                        default=None
                    )
                    if best_trigger:
                        result = operator.apply(self, best_trigger['members'])
                        if result.success:
                            triggered.append({
                                'type': op_name,
                                'result': result
                            })
                            self.operator_history.append(result)

                elif op_name == 'SW' and triggers:
                    # Apply to most active cluster
                    best_trigger = max(
                        triggers,
                        key=lambda t: t.get('activity', 0),
                        default=None
                    )
                    if best_trigger:
                        result = operator.apply(self, best_trigger['members'])
                        if result.success:
                            triggered.append({
                                'type': op_name,
                                'result': result
                            })
                            self.operator_history.append(result)

        return triggered

    def apply_operator(
        self,
        operator_name: str,
        targets: List[int],
        **kwargs
    ) -> OperatorResult:
        """
        Manually apply an operator.

        Args:
            operator_name: Operator name (DK, SW, WT, Nullpunkt, MOR)
            targets: Target cell IDs
            **kwargs: Operator-specific parameters

        Returns:
            OperatorResult
        """
        if operator_name not in self.operators:
            raise ValueError(f"Unknown operator: {operator_name}")

        operator = self.operators[operator_name]
        result = operator.apply(self, targets, **kwargs)

        if result.success:
            self.operator_history.append(result)
            self._log_event('operator_applied', {
                'operator': operator_name,
                'targets': targets,
                'success': True
            })

        return result

    def _collect_metrics(self) -> None:
        """Collect network metrics for this step."""
        if not self.cells:
            return

        # State distribution
        states = [cell.state for cell in self.cells.values()]
        self.metrics['positive_count'].append(sum(1 for s in states if s == 1))
        self.metrics['negative_count'].append(sum(1 for s in states if s == -1))
        self.metrics['neutral_count'].append(sum(1 for s in states if s == 0))

        # Network size
        self.metrics['network_size'].append(len(self.cells))

        # Connection density
        total_connections = sum(len(cell.connections) for cell in self.cells.values())
        max_connections = len(self.cells) * (len(self.cells) - 1)
        density = total_connections / max(max_connections, 1)
        self.metrics['connection_density'].append(density)

        # Cluster count
        self.metrics['cluster_count'].append(len(self.clusters))

    def _log_event(self, event_type: str, data: Dict) -> None:
        """Log an event to history."""
        self.event_history.append({
            'type': event_type,
            'step': self.step_count,
            'timestamp': time.time(),
            'data': data
        })

    def get_state(self) -> Dict[str, Any]:
        """
        Get complete network state.

        Returns:
            Dictionary with full network state
        """
        return {
            'name': self.name,
            'step_count': self.step_count,
            'network_size': len(self.cells),
            'cells': {cid: cell.to_dict() for cid, cell in self.cells.items()},
            'clusters': self.clusters,
            'metrics': dict(self.metrics),
            'operator_stats': {
                name: op.get_statistics()
                for name, op in self.operators.items()
            }
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize network to dictionary."""
        return self.get_state()

    def __repr__(self) -> str:
        return (
            f"HyperbionNetwork(name='{self.name}', "
            f"cells={len(self.cells)}, "
            f"clusters={len(self.clusters)}, "
            f"steps={self.step_count})"
        )
