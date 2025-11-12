"""
Doppelkick (DK) Operator
=========================

Synchronous amplification of tripolar clusters for coherence and resonance.
"""

from typing import List, Dict, Any
import time
import numpy as np

from .base import Operator, OperatorResult


class DoppelkickOperator(Operator):
    """
    Doppelkick (DK) Operator - Synchronous Cluster Amplification

    Purpose:
    --------
    - Synchronizes activity within a cluster
    - Amplifies coherent patterns
    - Creates resonance cascades

    Trigger Conditions:
    ------------------
    - High coherence signature in cluster
    - Input spike detected
    - Phase-locked activity pattern

    Effect:
    -------
    - w_ij += δ_DK for all i,j in cluster
    - Short-term activity cascade
    """

    def __init__(
        self,
        name: str = "DoppelkickOperator",
        amplification_factor: float = 0.5,
        coherence_threshold: float = 0.7
    ):
        """
        Initialize Doppelkick operator.

        Args:
            name: Operator name
            amplification_factor: Weight amplification (δ_DK)
            coherence_threshold: Minimum coherence to trigger
        """
        super().__init__(name)
        self.amplification_factor = amplification_factor
        self.coherence_threshold = coherence_threshold

    def can_apply(
        self,
        network: 'HyperbionNetwork',
        targets: List[int],
        **kwargs
    ) -> bool:
        """
        Check if DK can be applied.

        Requires:
        - All targets exist in network
        - Coherence above threshold
        - Cluster is active
        """
        # Check all targets exist
        if not all(tid in network.cells for tid in targets):
            return False

        # Need at least 2 cells for coherence
        if len(targets) < 2:
            return False

        # Check coherence
        coherence = self._compute_coherence(network, targets)
        return coherence >= self.coherence_threshold

    def _compute_coherence(
        self,
        network: 'HyperbionNetwork',
        targets: List[int]
    ) -> float:
        """
        Compute coherence signature of a cluster.

        Coherence = |Σ s_i| / N
        where s_i are tripolar states

        Args:
            network: Network instance
            targets: Target cell IDs

        Returns:
            Coherence value [0, 1]
        """
        if not targets:
            return 0.0

        states = [network.cells[tid].state for tid in targets]
        coherence = abs(sum(states)) / len(states)
        return coherence

    def apply(
        self,
        network: 'HyperbionNetwork',
        targets: List[int],
        **kwargs
    ) -> OperatorResult:
        """
        Apply Doppelkick to amplify cluster connections.

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
                operator_type="DK",
                affected_cells=[],
                parameters={'amplification_factor': self.amplification_factor},
                timestamp=start_time,
                success=False,
                metrics={},
                message="Trigger conditions not met"
            )

        # Amplify all connections within cluster
        amplified_count = 0
        initial_coherence = self._compute_coherence(network, targets)

        for source_id in targets:
            cell = network.cells[source_id]

            for target_id in targets:
                if target_id == source_id:
                    continue

                # Get current weight
                current_weight = cell.connections.get(target_id, 0.0)

                # Amplify
                new_weight = current_weight + self.amplification_factor

                # Apply with clipping
                cell.connect(target_id, new_weight)
                amplified_count += 1

            # Record operator application
            cell.record_operator_application(
                'DK',
                {'amplification_factor': self.amplification_factor}
            )

        # Compute final coherence
        final_coherence = self._compute_coherence(network, targets)

        result = OperatorResult(
            operator_type="DK",
            affected_cells=targets,
            parameters={'amplification_factor': self.amplification_factor},
            timestamp=start_time,
            success=True,
            metrics={
                'amplified_connections': amplified_count,
                'initial_coherence': initial_coherence,
                'final_coherence': final_coherence,
                'coherence_delta': final_coherence - initial_coherence,
                'execution_time': time.time() - start_time
            },
            message=f"Amplified {amplified_count} connections in cluster of {len(targets)} cells"
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
            coherence = self._compute_coherence(network, cluster['members'])

            if coherence >= self.coherence_threshold:
                triggers.append({
                    'cluster_id': cluster_id,
                    'coherence': coherence,
                    'members': cluster['members'],
                    'should_trigger': True
                })

        return {
            'operator': 'DK',
            'triggered_clusters': len(triggers),
            'triggers': triggers
        }
