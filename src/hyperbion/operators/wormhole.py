"""
Wormhole (WT) Operator
=======================

Creates temporal shortcuts between distant clusters for reduced latency.
"""

from typing import List, Dict, Any
import time

from .base import Operator, OperatorResult


class WormholeOperator(Operator):
    """
    Wormhole (WT) Operator - Temporal Shortcuts

    Purpose:
    --------
    - Creates temporary connections between distant cells/clusters
    - Reduces information propagation latency
    - Enables rapid cross-cluster communication

    Trigger Conditions:
    ------------------
    - Topological distance exceeds threshold
    - Latency spike detected
    - Cross-cluster synchronization needed

    Effect:
    -------
    - w_ik^(WT) ≠ 0 temporarily
    - Ephemeral connection with expiry time
    """

    def __init__(
        self,
        name: str = "WormholeOperator",
        connection_strength: float = 2.0,
        duration: float = 10.0,
        distance_threshold: int = 3
    ):
        """
        Initialize Wormhole operator.

        Args:
            name: Operator name
            connection_strength: Weight of wormhole connection
            duration: How long wormhole lasts (seconds)
            distance_threshold: Minimum topological distance to trigger
        """
        super().__init__(name)
        self.connection_strength = connection_strength
        self.duration = duration
        self.distance_threshold = distance_threshold

    def can_apply(
        self,
        network: 'HyperbionNetwork',
        targets: List[int],
        **kwargs
    ) -> bool:
        """
        Check if WT can be applied.

        Requires:
        - Exactly 2 targets (source and destination)
        - Both targets exist
        - Sufficient topological distance
        """
        if len(targets) != 2:
            return False

        if not all(tid in network.cells for tid in targets):
            return False

        # Check topological distance
        source_id, target_id = targets
        distance = network.get_topological_distance(source_id, target_id)

        return distance >= self.distance_threshold

    def apply(
        self,
        network: 'HyperbionNetwork',
        targets: List[int],
        **kwargs
    ) -> OperatorResult:
        """
        Apply Wormhole to create temporal shortcut.

        Args:
            network: Network instance
            targets: [source_id, target_id]
            **kwargs: Additional parameters (e.g., custom duration)

        Returns:
            OperatorResult
        """
        start_time = time.time()

        if not self.can_apply(network, targets, **kwargs):
            return OperatorResult(
                operator_type="WT",
                affected_cells=[],
                parameters={
                    'connection_strength': self.connection_strength,
                    'duration': self.duration
                },
                timestamp=start_time,
                success=False,
                metrics={},
                message="Trigger conditions not met"
            )

        source_id, target_id = targets
        duration = kwargs.get('duration', self.duration)
        strength = kwargs.get('strength', self.connection_strength)

        # Create wormhole
        source_cell = network.cells[source_id]
        source_cell.add_wormhole(target_id, strength, duration)

        # Record operator application
        source_cell.record_operator_application(
            'WT',
            {
                'target': target_id,
                'strength': strength,
                'duration': duration,
                'expiry': time.time() + duration
            }
        )

        # Optionally create bidirectional wormhole
        if kwargs.get('bidirectional', False):
            target_cell = network.cells[target_id]
            target_cell.add_wormhole(source_id, strength, duration)
            target_cell.record_operator_application(
                'WT',
                {
                    'target': source_id,
                    'strength': strength,
                    'duration': duration,
                    'expiry': time.time() + duration
                }
            )

        result = OperatorResult(
            operator_type="WT",
            affected_cells=targets,
            parameters={
                'connection_strength': strength,
                'duration': duration,
                'bidirectional': kwargs.get('bidirectional', False)
            },
            timestamp=start_time,
            success=True,
            metrics={
                'source': source_id,
                'target': target_id,
                'expiry_time': time.time() + duration,
                'execution_time': time.time() - start_time
            },
            message=f"Created wormhole from {source_id} to {target_id} for {duration}s"
        )

        self.record_application(result)
        return result

    def get_trigger_condition(self, network: 'HyperbionNetwork') -> Dict[str, Any]:
        """
        Evaluate trigger conditions for wormhole creation.

        Args:
            network: Network instance

        Returns:
            Dictionary with trigger evaluation
        """
        triggers = []

        # Look for distant but potentially related cells
        # This is a simplified heuristic - could be more sophisticated

        cell_ids = list(network.cells.keys())

        for i, source_id in enumerate(cell_ids):
            for target_id in cell_ids[i+1:]:
                distance = network.get_topological_distance(source_id, target_id)

                if distance >= self.distance_threshold:
                    # Check if there's activity correlation
                    source_state = network.cells[source_id].state
                    target_state = network.cells[target_id].state

                    # Simple correlation: same non-zero state
                    if source_state != 0 and source_state == target_state:
                        triggers.append({
                            'source': source_id,
                            'target': target_id,
                            'distance': distance,
                            'should_trigger': True
                        })

        return {
            'operator': 'WT',
            'potential_wormholes': len(triggers),
            'triggers': triggers[:10]  # Limit to top 10
        }
