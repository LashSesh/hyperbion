"""
Benchmark Metrics
=================

Metrics calculation and comparison for network benchmarks.
"""

from typing import Dict, Any
import numpy as np
import time


class BenchmarkMetrics:
    """
    Calculate and track benchmark metrics for network comparison.

    Metrics include:
    - Information capacity
    - Training convergence time
    - Network efficiency
    - Resource utilization
    """

    @staticmethod
    def calculate_information_capacity_binary(network_size: int) -> float:
        """
        Calculate information capacity for binary network.

        I_bin = log2(2) * N = N bits
        """
        return float(network_size)

    @staticmethod
    def calculate_information_capacity_tripolar(network_size: int) -> float:
        """
        Calculate information capacity for tripolar network.

        I_tri = log2(3) * N ≈ 1.585 * N bits
        """
        return network_size * np.log2(3)

    @staticmethod
    def calculate_information_advantage(
        binary_capacity: float,
        tripolar_capacity: float
    ) -> Dict[str, float]:
        """
        Calculate information advantage of tripolar over binary.

        Expected theoretical advantage: ~58.5%
        """
        advantage_per_node = (tripolar_capacity / binary_capacity) - 1.0
        advantage_percentage = advantage_per_node * 100.0

        return {
            'advantage_per_node': advantage_per_node,
            'advantage_percentage': advantage_percentage,
            'tripolar_capacity': tripolar_capacity,
            'binary_capacity': binary_capacity
        }

    @staticmethod
    def calculate_system_efficiency(
        binary_size: int,
        tripolar_size: int,
        binary_capacity: float,
        tripolar_capacity: float,
        operator_boost: float = 1.0
    ) -> Dict[str, float]:
        """
        Calculate effective system advantage.

        V = (S_bin / S_tri) * (I_tri / I_bin) * (1 + operator_boost)

        Args:
            binary_size: Number of nodes in binary network
            tripolar_size: Number of cells in tripolar network
            binary_capacity: Information capacity of binary network
            tripolar_capacity: Information capacity of tripolar network
            operator_boost: Boost from operators (emergent effects)

        Returns:
            Dictionary with efficiency metrics
        """
        size_ratio = binary_size / tripolar_size if tripolar_size > 0 else 0.0
        capacity_ratio = tripolar_capacity / binary_capacity if binary_capacity > 0 else 0.0

        system_advantage = size_ratio * capacity_ratio * (1.0 + operator_boost)

        return {
            'size_ratio': size_ratio,
            'capacity_ratio': capacity_ratio,
            'operator_boost': operator_boost,
            'system_advantage': system_advantage
        }

    @staticmethod
    def calculate_convergence_metrics(
        binary_steps: int,
        tripolar_steps: int,
        binary_time: float,
        tripolar_time: float
    ) -> Dict[str, float]:
        """Calculate convergence speed metrics."""
        step_ratio = binary_steps / tripolar_steps if tripolar_steps > 0 else 0.0
        time_ratio = binary_time / tripolar_time if tripolar_time > 0 else 0.0

        return {
            'binary_steps': binary_steps,
            'tripolar_steps': tripolar_steps,
            'binary_time': binary_time,
            'tripolar_time': tripolar_time,
            'step_speedup': step_ratio,
            'time_speedup': time_ratio
        }

    @staticmethod
    def calculate_resource_efficiency(
        binary_nodes: int,
        binary_connections: int,
        tripolar_cells: int,
        tripolar_connections: int,
        task_performance_binary: float,
        task_performance_tripolar: float
    ) -> Dict[str, float]:
        """Calculate resource efficiency."""
        # Performance per node
        perf_per_node_binary = (
            task_performance_binary / binary_nodes if binary_nodes > 0 else 0.0
        )
        perf_per_node_tripolar = (
            task_performance_tripolar / tripolar_cells if tripolar_cells > 0 else 0.0
        )

        # Performance per connection
        perf_per_conn_binary = (
            task_performance_binary / binary_connections if binary_connections > 0 else 0.0
        )
        perf_per_conn_tripolar = (
            task_performance_tripolar / tripolar_connections if tripolar_connections > 0 else 0.0
        )

        # Connection density
        max_conn_binary = binary_nodes * (binary_nodes - 1)
        max_conn_tripolar = tripolar_cells * (tripolar_cells - 1)

        density_binary = (
            binary_connections / max_conn_binary if max_conn_binary > 0 else 0.0
        )
        density_tripolar = (
            tripolar_connections / max_conn_tripolar if max_conn_tripolar > 0 else 0.0
        )

        return {
            'perf_per_node_binary': perf_per_node_binary,
            'perf_per_node_tripolar': perf_per_node_tripolar,
            'node_efficiency_ratio': (
                perf_per_node_tripolar / perf_per_node_binary
                if perf_per_node_binary > 0 else 0.0
            ),
            'perf_per_conn_binary': perf_per_conn_binary,
            'perf_per_conn_tripolar': perf_per_conn_tripolar,
            'connection_efficiency_ratio': (
                perf_per_conn_tripolar / perf_per_conn_binary
                if perf_per_conn_binary > 0 else 0.0
            ),
            'density_binary': density_binary,
            'density_tripolar': density_tripolar
        }

    @staticmethod
    def aggregate_metrics(
        binary_results: Dict[str, Any],
        tripolar_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Aggregate all metrics for comparison.

        Args:
            binary_results: Results from binary network benchmark
            tripolar_results: Results from tripolar network benchmark

        Returns:
            Complete metrics comparison
        """
        # Information capacity
        binary_capacity = BenchmarkMetrics.calculate_information_capacity_binary(
            binary_results['network_size']
        )
        tripolar_capacity = BenchmarkMetrics.calculate_information_capacity_tripolar(
            tripolar_results['network_size']
        )

        info_advantage = BenchmarkMetrics.calculate_information_advantage(
            binary_capacity,
            tripolar_capacity
        )

        # System efficiency
        operator_boost = tripolar_results.get('operator_boost', 0.0)
        system_efficiency = BenchmarkMetrics.calculate_system_efficiency(
            binary_results['network_size'],
            tripolar_results['network_size'],
            binary_capacity,
            tripolar_capacity,
            operator_boost
        )

        # Convergence
        convergence_metrics = BenchmarkMetrics.calculate_convergence_metrics(
            binary_results.get('convergence_steps', 0),
            tripolar_results.get('convergence_steps', 0),
            binary_results.get('training_time', 0.0),
            tripolar_results.get('training_time', 0.0)
        )

        # Resource efficiency
        resource_efficiency = BenchmarkMetrics.calculate_resource_efficiency(
            binary_results['network_size'],
            binary_results.get('total_connections', 0),
            tripolar_results['network_size'],
            tripolar_results.get('total_connections', 0),
            binary_results.get('task_performance', 0.0),
            tripolar_results.get('task_performance', 0.0)
        )

        return {
            'information_capacity': {
                'binary': binary_capacity,
                'tripolar': tripolar_capacity,
                **info_advantage
            },
            'system_efficiency': system_efficiency,
            'convergence': convergence_metrics,
            'resource_efficiency': resource_efficiency,
            'task_performance': {
                'binary': binary_results.get('task_performance', 0.0),
                'tripolar': tripolar_results.get('task_performance', 0.0),
                'improvement': (
                    tripolar_results.get('task_performance', 0.0) -
                    binary_results.get('task_performance', 0.0)
                )
            }
        }
