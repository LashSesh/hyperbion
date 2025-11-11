"""
Nullpunkt Operator
==================

Reset or deletion of cells, connections, or clusters for healing and reorganization.
"""

from typing import List, Dict, Any
import time

from .base import Operator, OperatorResult


class NullpunktOperator(Operator):
    """
    Nullpunkt Operator - Reset/Deletion

    Purpose:
    --------
    - Resets problematic cells or connections
    - Deletes dysfunctional components
    - Enables healing and reorganization

    Trigger Conditions:
    ------------------
    - Anomaly detection (stuck states, oscillations)
    - Error accumulation
    - Policy-driven reset events

    Effect:
    -------
    - w_ij → 0 (connection reset)
    - s_i → 0 (state reset)
    - Cell/cluster deletion

    Modes:
    ------
    - 'reset_weights': Reset all weights to zero
    - 'reset_state': Reset cell state to neutral
    - 'delete_cell': Remove cell from network
    - 'delete_connections': Remove specific connections
    """

    def __init__(
        self,
        name: str = "NullpunktOperator",
        anomaly_threshold: float = 0.8,
        oscillation_window: int = 10
    ):
        """
        Initialize Nullpunkt operator.

        Args:
            name: Operator name
            anomaly_threshold: Threshold for anomaly detection
            oscillation_window: Window size for oscillation detection
        """
        super().__init__(name)
        self.anomaly_threshold = anomaly_threshold
        self.oscillation_window = oscillation_window

    def can_apply(
        self,
        network: 'HyperbionNetwork',
        targets: List[int],
        **kwargs
    ) -> bool:
        """
        Check if Nullpunkt can be applied.

        Args:
            network: Network instance
            targets: Target cell IDs
            **kwargs: Must include 'mode' parameter

        Returns:
            True if can apply
        """
        if not all(tid in network.cells for tid in targets):
            return False

        mode = kwargs.get('mode', 'reset_weights')

        # Always allow explicit reset/delete
        if mode in ['reset_weights', 'reset_state', 'delete_cell', 'delete_connections']:
            return True

        return False

    def _detect_oscillation(self, cell: 'GabrielCell') -> bool:
        """
        Detect if cell is oscillating.

        Args:
            cell: Gabriel cell

        Returns:
            True if oscillating
        """
        if len(cell.state_history) < self.oscillation_window:
            return False

        recent_states = cell.state_history[-self.oscillation_window:]

        # Check for rapid state changes
        changes = sum(
            1 for i in range(1, len(recent_states))
            if recent_states[i] != recent_states[i-1]
        )

        # Oscillating if > 50% of steps had state changes
        return changes > self.oscillation_window * 0.5

    def apply(
        self,
        network: 'HyperbionNetwork',
        targets: List[int],
        **kwargs
    ) -> OperatorResult:
        """
        Apply Nullpunkt operator.

        Args:
            network: Network instance
            targets: Target cell IDs
            **kwargs: Must include 'mode' parameter

        Returns:
            OperatorResult
        """
        start_time = time.time()
        mode = kwargs.get('mode', 'reset_weights')

        if not self.can_apply(network, targets, **kwargs):
            return OperatorResult(
                operator_type="Nullpunkt",
                affected_cells=[],
                parameters={'mode': mode},
                timestamp=start_time,
                success=False,
                metrics={},
                message="Trigger conditions not met"
            )

        affected = []
        action_count = 0

        if mode == 'reset_weights':
            # Reset all weights to zero
            for cell_id in targets:
                cell = network.cells[cell_id]
                initial_connections = len(cell.connections)
                cell.connections.clear()
                action_count += initial_connections
                affected.append(cell_id)

                cell.record_operator_application(
                    'Nullpunkt',
                    {'mode': mode, 'reset_connections': initial_connections}
                )

        elif mode == 'reset_state':
            # Reset state to neutral
            for cell_id in targets:
                cell = network.cells[cell_id]
                old_state = cell.state
                cell.state = 0
                action_count += 1
                affected.append(cell_id)

                cell.record_operator_application(
                    'Nullpunkt',
                    {'mode': mode, 'old_state': old_state}
                )

        elif mode == 'delete_cell':
            # Delete cells from network
            for cell_id in targets:
                if cell_id in network.cells:
                    network.remove_cell(cell_id)
                    action_count += 1
                    affected.append(cell_id)

        elif mode == 'delete_connections':
            # Delete specific connections
            connection_targets = kwargs.get('connection_targets', [])
            for cell_id in targets:
                cell = network.cells[cell_id]
                for target_id in connection_targets:
                    if cell.disconnect(target_id):
                        action_count += 1
                affected.append(cell_id)

                cell.record_operator_application(
                    'Nullpunkt',
                    {'mode': mode, 'deleted_connections': action_count}
                )

        result = OperatorResult(
            operator_type="Nullpunkt",
            affected_cells=affected,
            parameters={'mode': mode},
            timestamp=start_time,
            success=True,
            metrics={
                'action_count': action_count,
                'mode': mode,
                'execution_time': time.time() - start_time
            },
            message=f"Applied Nullpunkt ({mode}) to {len(affected)} cells"
        )

        self.record_application(result)
        return result

    def get_trigger_condition(self, network: 'HyperbionNetwork') -> Dict[str, Any]:
        """
        Evaluate trigger conditions for Nullpunkt.

        Args:
            network: Network instance

        Returns:
            Dictionary with trigger evaluation
        """
        triggers = []

        for cell_id, cell in network.cells.items():
            # Check for oscillation
            if self._detect_oscillation(cell):
                triggers.append({
                    'cell_id': cell_id,
                    'reason': 'oscillation',
                    'mode': 'reset_state',
                    'should_trigger': True
                })

            # Check for stuck state (same state for long time)
            if len(cell.state_history) > 20:
                recent = cell.state_history[-20:]
                if len(set(recent)) == 1 and recent[0] != 0:
                    triggers.append({
                        'cell_id': cell_id,
                        'reason': 'stuck_state',
                        'mode': 'reset_state',
                        'should_trigger': True
                    })

        return {
            'operator': 'Nullpunkt',
            'triggered_cells': len(triggers),
            'triggers': triggers
        }
