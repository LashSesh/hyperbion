"""
Morphogenesis (MOR) Operator
=============================

Growth, division, fusion, and structural evolution of the network.
"""

from typing import List, Dict, Any, Optional
import time
import numpy as np

from .base import Operator, OperatorResult


class MorphogenesisOperator(Operator):
    """
    Morphogenesis (MOR) Operator - Structural Evolution

    Purpose:
    --------
    - Creates new cells (division, emergence)
    - Fuses existing cells
    - Grows new connections
    - Enables structural plasticity

    Trigger Conditions:
    ------------------
    - Semantic stress (information bottleneck)
    - Capacity limits reached
    - Persistent activity patterns
    - Resource availability

    Effect:
    -------
    - Network expansion/contraction
    - Topological reorganization
    - Emergent structure formation

    Modes:
    ------
    - 'divide': Split cell into two
    - 'fuse': Merge two cells
    - 'spawn': Create new cell
    - 'grow_connections': Add new connections
    """

    def __init__(
        self,
        name: str = "MorphogenesisOperator",
        stress_threshold: float = 0.7,
        max_network_size: int = 1000,
        min_network_size: int = 10
    ):
        """
        Initialize Morphogenesis operator.

        Args:
            name: Operator name
            stress_threshold: Threshold for stress-induced growth
            max_network_size: Maximum allowed network size
            min_network_size: Minimum allowed network size
        """
        super().__init__(name)
        self.stress_threshold = stress_threshold
        self.max_network_size = max_network_size
        self.min_network_size = min_network_size

    def can_apply(
        self,
        network: 'HyperbionNetwork',
        targets: List[int],
        **kwargs
    ) -> bool:
        """
        Check if morphogenesis can be applied.

        Args:
            network: Network instance
            targets: Target cell IDs
            **kwargs: Must include 'mode' parameter

        Returns:
            True if can apply
        """
        mode = kwargs.get('mode', 'spawn')

        # Check network size constraints
        current_size = len(network.cells)

        if mode in ['divide', 'spawn', 'grow_connections']:
            if current_size >= self.max_network_size:
                return False

        if mode == 'fuse':
            if current_size <= self.min_network_size:
                return False
            if len(targets) < 2:
                return False

        # Check targets exist
        if mode != 'spawn':
            if not all(tid in network.cells for tid in targets):
                return False

        return True

    def _compute_stress(self, network: 'HyperbionNetwork', cell_id: int) -> float:
        """
        Compute semantic stress on a cell.

        Stress = (activation_variance + connection_density) / 2

        Args:
            network: Network instance
            cell_id: Cell ID

        Returns:
            Stress value [0, 1]
        """
        cell = network.cells[cell_id]

        # Activation variance
        if len(cell.activation_history) > 5:
            recent_activations = cell.activation_history[-10:]
            activation_var = float(np.var(recent_activations))
            activation_var = min(activation_var / 10.0, 1.0)  # Normalize
        else:
            activation_var = 0.0

        # Connection density
        max_connections = len(network.cells)
        connection_density = len(cell.connections) / max(max_connections, 1)

        # Combined stress
        stress = (activation_var + connection_density) / 2.0
        return stress

    def apply(
        self,
        network: 'HyperbionNetwork',
        targets: List[int],
        **kwargs
    ) -> OperatorResult:
        """
        Apply morphogenesis operator.

        Args:
            network: Network instance
            targets: Target cell IDs
            **kwargs: Must include 'mode' parameter

        Returns:
            OperatorResult
        """
        start_time = time.time()
        mode = kwargs.get('mode', 'spawn')

        if not self.can_apply(network, targets, **kwargs):
            return OperatorResult(
                operator_type="MOR",
                affected_cells=[],
                parameters={'mode': mode},
                timestamp=start_time,
                success=False,
                metrics={},
                message="Trigger conditions not met"
            )

        affected = []
        created_cells = []
        deleted_cells = []

        if mode == 'divide':
            # Divide a cell into two
            parent_id = targets[0]
            parent_cell = network.cells[parent_id]

            # Create daughter cell
            daughter_id = network.get_next_cell_id()
            daughter_cell = network.add_cell(
                state=parent_cell.state,
                bias=parent_cell.bias * 0.5,
                plasticity_params=parent_cell.params
            )

            # Split connections
            for target_id, weight in list(parent_cell.connections.items()):
                if np.random.random() > 0.5:
                    # Transfer to daughter
                    parent_cell.disconnect(target_id)
                    daughter_cell.connect(target_id, weight * 0.8)

            # Update parent bias
            parent_cell.bias *= 0.5
            parent_cell.division_count += 1

            # Record
            parent_cell.record_operator_application(
                'MOR',
                {'mode': mode, 'daughter_id': daughter_id}
            )

            affected = [parent_id, daughter_id]
            created_cells = [daughter_id]

        elif mode == 'fuse':
            # Fuse two cells into one
            if len(targets) < 2:
                return OperatorResult(
                    operator_type="MOR",
                    affected_cells=[],
                    parameters={'mode': mode},
                    timestamp=start_time,
                    success=False,
                    metrics={},
                    message="Need at least 2 cells to fuse"
                )

            cell1_id, cell2_id = targets[0], targets[1]
            cell1 = network.cells[cell1_id]
            cell2 = network.cells[cell2_id]

            # Merge connections into cell1
            for target_id, weight in cell2.connections.items():
                existing_weight = cell1.connections.get(target_id, 0.0)
                cell1.connect(target_id, (existing_weight + weight) / 2.0)

            # Average bias
            cell1.bias = (cell1.bias + cell2.bias) / 2.0
            cell1.fusion_count += 1

            # Remove cell2
            network.remove_cell(cell2_id)

            cell1.record_operator_application(
                'MOR',
                {'mode': mode, 'fused_with': cell2_id}
            )

            affected = [cell1_id]
            deleted_cells = [cell2_id]

        elif mode == 'spawn':
            # Create a new cell
            initial_state = kwargs.get('initial_state', 0)
            bias = kwargs.get('bias', 0.0)

            new_cell_id = network.add_cell(state=initial_state, bias=bias)

            # Optionally connect to existing cells
            if targets:
                new_cell = network.cells[new_cell_id]
                for target_id in targets:
                    if target_id in network.cells:
                        weight = np.random.uniform(-0.5, 0.5)
                        new_cell.connect(target_id, weight)

            affected = [new_cell_id]
            created_cells = [new_cell_id]

        elif mode == 'grow_connections':
            # Add new connections between cells
            connection_count = 0
            for source_id in targets:
                source_cell = network.cells[source_id]

                # Find potential targets
                potential_targets = [
                    cid for cid in network.cells.keys()
                    if cid != source_id and cid not in source_cell.connections
                ]

                # Add a few random connections
                num_new = min(kwargs.get('num_connections', 3), len(potential_targets))
                new_targets = np.random.choice(potential_targets, num_new, replace=False)

                for target_id in new_targets:
                    weight = np.random.uniform(-1.0, 1.0)
                    source_cell.connect(int(target_id), weight)
                    connection_count += 1

                source_cell.record_operator_application(
                    'MOR',
                    {'mode': mode, 'new_connections': connection_count}
                )

            affected = targets

        result = OperatorResult(
            operator_type="MOR",
            affected_cells=affected,
            parameters={'mode': mode},
            timestamp=start_time,
            success=True,
            metrics={
                'mode': mode,
                'created_cells': len(created_cells),
                'deleted_cells': len(deleted_cells),
                'new_cells': created_cells,
                'removed_cells': deleted_cells,
                'network_size': len(network.cells),
                'execution_time': time.time() - start_time
            },
            message=f"Applied morphogenesis ({mode}): {len(created_cells)} created, {len(deleted_cells)} deleted"
        )

        self.record_application(result)
        return result

    def get_trigger_condition(self, network: 'HyperbionNetwork') -> Dict[str, Any]:
        """
        Evaluate trigger conditions for morphogenesis.

        Args:
            network: Network instance

        Returns:
            Dictionary with trigger evaluation
        """
        triggers = []

        # Check for stressed cells (candidates for division)
        for cell_id, cell in network.cells.items():
            stress = self._compute_stress(network, cell_id)

            if stress > self.stress_threshold:
                triggers.append({
                    'cell_id': cell_id,
                    'reason': 'high_stress',
                    'stress': stress,
                    'mode': 'divide',
                    'should_trigger': True
                })

        # Check for fusion candidates (low activity neighbors)
        cell_ids = list(network.cells.keys())
        for i, cell1_id in enumerate(cell_ids):
            cell1 = network.cells[cell1_id]

            # Find connected neighbors with similar state
            for cell2_id in cell1.connections.keys():
                if cell2_id in network.cells:
                    cell2 = network.cells[cell2_id]

                    # Similar state and low activity
                    if (cell1.state == cell2.state and
                        len(cell1.state_history) > 5 and
                        len(cell2.state_history) > 5):

                        recent1 = cell1.state_history[-5:]
                        recent2 = cell2.state_history[-5:]

                        # Both stable
                        if len(set(recent1)) == 1 and len(set(recent2)) == 1:
                            triggers.append({
                                'cells': [cell1_id, cell2_id],
                                'reason': 'similar_stable_neighbors',
                                'mode': 'fuse',
                                'should_trigger': True
                            })

        return {
            'operator': 'MOR',
            'potential_morphogenesis': len(triggers),
            'triggers': triggers[:10]  # Limit to top 10
        }
