"""
Sweep (SW) Operator
===================

Normalization of weights in clusters to prevent overflow and maintain stability.
"""

from typing import List, Dict, Any
import time
import numpy as np

from .base import Operator, OperatorResult


class SweepOperator(Operator):
    """
    Sweep (SW) Operator - Weight Normalization

    Purpose:
    --------
    - Normalizes weight distributions in clusters
    - Prevents overflow/underflow
    - Maintains network stability

    Trigger Conditions:
    ------------------
    - Excessive total activity in cluster
    - Weight variance exceeds threshold
    - Saturation detected

    Effect:
    -------
    - w_ij → λ * w_ij (scaling)
    - Optional: soft normalization
    """

    def __init__(
        self,
        name: str = "SweepOperator",
        scaling_factor: float = 0.9,
        activity_threshold: float = 10.0,
        variance_threshold: float = 5.0
    ):
        """
        Initialize Sweep operator.

        Args:
            name: Operator name
            scaling_factor: Weight scaling factor (λ)
            activity_threshold: Trigger on excess activity
            variance_threshold: Trigger on high variance
        """
        super().__init__(name)
        self.scaling_factor = scaling_factor
        self.activity_threshold = activity_threshold
        self.variance_threshold = variance_threshold

    def can_apply(
        self,
        network: 'HyperbionNetwork',
        targets: List[int],
        **kwargs
    ) -> bool:
        """
        Check if SW can be applied.

        Requires:
        - All targets exist
        - Activity or variance exceeds threshold
        """
        if not all(tid in network.cells for tid in targets):
            return False

        if len(targets) < 2:
            return False

        # Check activity level
        total_activity = self._compute_total_activity(network, targets)
        if total_activity > self.activity_threshold:
            return True

        # Check weight variance
        variance = self._compute_weight_variance(network, targets)
        if variance > self.variance_threshold:
            return True

        return False

    def _compute_total_activity(
        self,
        network: 'HyperbionNetwork',
        targets: List[int]
    ) -> float:
        """
        Compute total activity in cluster.

        Activity = Σ |Σ w_ij|

        Args:
            network: Network instance
            targets: Target cell IDs

        Returns:
            Total activity
        """
        total = 0.0
        for tid in targets:
            cell = network.cells[tid]
            total += sum(abs(w) for w in cell.connections.values())
        return total

    def _compute_weight_variance(
        self,
        network: 'HyperbionNetwork',
        targets: List[int]
    ) -> float:
        """
        Compute variance of weights in cluster.

        Args:
            network: Network instance
            targets: Target cell IDs

        Returns:
            Weight variance
        """
        weights = []
        for tid in targets:
            cell = network.cells[tid]
            weights.extend(cell.connections.values())

        if not weights:
            return 0.0

        return float(np.var(weights))

    def apply(
        self,
        network: 'HyperbionNetwork',
        targets: List[int],
        **kwargs
    ) -> OperatorResult:
        """
        Apply Sweep to normalize cluster weights.

        Args:
            network: Network instance
            targets: Target cell IDs
            **kwargs: Additional parameters

        Returns:
            OperatorResult
        """
        start_time = time.time()

        if not self.can_apply(network, targets, **kwargs):
            return OperatorResult(
                operator_type="SW",
                affected_cells=[],
                parameters={'scaling_factor': self.scaling_factor},
                timestamp=start_time,
                success=False,
                metrics={},
                message="Trigger conditions not met"
            )

        # Compute initial metrics
        initial_activity = self._compute_total_activity(network, targets)
        initial_variance = self._compute_weight_variance(network, targets)

        # Scale all weights in cluster
        scaled_count = 0
        for source_id in targets:
            cell = network.cells[source_id]

            # Scale each connection
            for target_id, weight in list(cell.connections.items()):
                new_weight = weight * self.scaling_factor
                cell.connect(target_id, new_weight)
                scaled_count += 1

            # Record operator application
            cell.record_operator_application(
                'SW',
                {'scaling_factor': self.scaling_factor}
            )

        # Compute final metrics
        final_activity = self._compute_total_activity(network, targets)
        final_variance = self._compute_weight_variance(network, targets)

        result = OperatorResult(
            operator_type="SW",
            affected_cells=targets,
            parameters={'scaling_factor': self.scaling_factor},
            timestamp=start_time,
            success=True,
            metrics={
                'scaled_connections': scaled_count,
                'initial_activity': initial_activity,
                'final_activity': final_activity,
                'activity_reduction': initial_activity - final_activity,
                'initial_variance': initial_variance,
                'final_variance': final_variance,
                'execution_time': time.time() - start_time
            },
            message=f"Normalized {scaled_count} connections in cluster of {len(targets)} cells"
        )

        self.record_application(result)
        return result

    def get_trigger_condition(self, network: 'HyperbionNetwork') -> Dict[str, Any]:
        """
        Evaluate trigger conditions across all clusters.

        Args:
            network: Network instance

        Returns:
            Dictionary with trigger evaluation
        """
        triggers = []

        for cluster_id, cluster in network.clusters.items():
            members = cluster['members']
            activity = self._compute_total_activity(network, members)
            variance = self._compute_weight_variance(network, members)

            should_trigger = (
                activity > self.activity_threshold or
                variance > self.variance_threshold
            )

            if should_trigger:
                triggers.append({
                    'cluster_id': cluster_id,
                    'activity': activity,
                    'variance': variance,
                    'members': members,
                    'should_trigger': True
                })

        return {
            'operator': 'SW',
            'triggered_clusters': len(triggers),
            'triggers': triggers
        }
