"""
Base Operator Class
===================

Abstract base class for all operators in the Hyperbion Tripolar Network.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time


@dataclass
class OperatorResult:
    """Result of an operator application."""
    operator_type: str
    affected_cells: List[int]
    parameters: Dict[str, Any]
    timestamp: float
    success: bool
    metrics: Dict[str, float]
    message: str = ""


class Operator(ABC):
    """
    Abstract base class for network operators.

    Operators modify the network topology, weights, or cell states
    in response to specific triggers or conditions.

    Operator Types:
    - DK (Doppelkick): Synchronous cluster amplification
    - SW (Sweep): Weight normalization
    - WT (Wormhole): Temporal shortcuts
    - Nullpunkt: Reset/deletion
    - MOR (Morphogenesis): Growth/fusion/division
    """

    def __init__(self, name: str):
        """
        Initialize operator.

        Args:
            name: Operator name/identifier
        """
        self.name = name
        self.application_count = 0
        self.last_application_time: Optional[float] = None
        self.history: List[OperatorResult] = []

    @abstractmethod
    def can_apply(self, network: 'HyperbionNetwork', targets: List[int], **kwargs) -> bool:
        """
        Check if operator can be applied to the target cells.

        Args:
            network: The network instance
            targets: List of target cell IDs
            **kwargs: Additional parameters

        Returns:
            True if operator can be applied
        """
        pass

    @abstractmethod
    def apply(
        self,
        network: 'HyperbionNetwork',
        targets: List[int],
        **kwargs
    ) -> OperatorResult:
        """
        Apply the operator to target cells.

        Args:
            network: The network instance
            targets: List of target cell IDs
            **kwargs: Additional parameters

        Returns:
            OperatorResult with application details
        """
        pass

    @abstractmethod
    def get_trigger_condition(self, network: 'HyperbionNetwork') -> Dict[str, Any]:
        """
        Evaluate the trigger condition for this operator.

        Args:
            network: The network instance

        Returns:
            Dictionary with trigger evaluation results
        """
        pass

    def record_application(self, result: OperatorResult) -> None:
        """
        Record operator application in history.

        Args:
            result: Result of the application
        """
        self.application_count += 1
        self.last_application_time = time.time()
        self.history.append(result)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get operator usage statistics.

        Returns:
            Dictionary with statistics
        """
        if not self.history:
            return {
                'application_count': 0,
                'success_rate': 0.0,
                'avg_affected_cells': 0.0
            }

        successful = sum(1 for r in self.history if r.success)
        total_affected = sum(len(r.affected_cells) for r in self.history)

        return {
            'application_count': self.application_count,
            'success_rate': successful / len(self.history),
            'avg_affected_cells': total_affected / len(self.history),
            'last_application': self.last_application_time
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', applications={self.application_count})"
