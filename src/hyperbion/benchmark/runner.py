"""
Benchmark Runner
================

Orchestrates benchmark execution and comparison.
"""

from typing import Dict, List, Any, Optional
import time
import numpy as np
from pathlib import Path

from .binary_network import BinaryNetwork
from ..core.network import HyperbionNetwork
from .tasks import BenchmarkTask
from .metrics import BenchmarkMetrics


class BenchmarkRunner:
    """
    Orchestrates benchmark execution for network comparison.

    Handles:
    - Network initialization
    - Training on tasks
    - Performance evaluation
    - Metrics collection
    """

    def __init__(
        self,
        task: BenchmarkTask,
        num_training_samples: int = 100,
        num_test_samples: int = 20,
        max_epochs: int = 100,
        convergence_threshold: float = 0.95
    ):
        """
        Initialize benchmark runner.

        Args:
            task: Benchmark task to execute
            num_training_samples: Number of training samples
            num_test_samples: Number of test samples
            max_epochs: Maximum training epochs
            convergence_threshold: Performance threshold for convergence
        """
        self.task = task
        self.num_training_samples = num_training_samples
        self.num_test_samples = num_test_samples
        self.max_epochs = max_epochs
        self.convergence_threshold = convergence_threshold

        self.results: Dict[str, Any] = {}

    def setup_binary_network(self, network_size: int) -> BinaryNetwork:
        """
        Setup binary network for task.

        Args:
            network_size: Number of nodes

        Returns:
            Initialized BinaryNetwork
        """
        network = BinaryNetwork(name="BinaryBenchmark")

        # Add nodes
        for i in range(network_size):
            network.add_node(state=0, bias=0.0)

        # Create random connections
        node_ids = list(network.nodes.keys())
        connection_prob = 0.3  # 30% connection probability

        for i in node_ids:
            for j in node_ids:
                if i != j and np.random.random() < connection_prob:
                    weight = np.random.uniform(-1.0, 1.0)
                    network.connect_nodes(i, j, weight)

        return network

    def setup_hyperbion_network(self, network_size: int) -> HyperbionNetwork:
        """
        Setup Hyperbion network for task.

        Args:
            network_size: Number of cells

        Returns:
            Initialized HyperbionNetwork
        """
        network = HyperbionNetwork(name="HyperbionBenchmark")

        # Add cells
        for i in range(network_size):
            state = np.random.choice([-1, 0, 1])
            network.add_cell(state=state, bias=0.0)

        # Create random connections
        cell_ids = list(network.cells.keys())
        connection_prob = 0.3

        for i in cell_ids:
            for j in cell_ids:
                if i != j and np.random.random() < connection_prob:
                    weight = np.random.uniform(-1.0, 1.0)
                    network.connect_cells(i, j, weight)

        return network

    def train_binary_network(
        self,
        network: BinaryNetwork,
        training_data: List[Any]
    ) -> Dict[str, Any]:
        """
        Train binary network on task.

        Args:
            network: BinaryNetwork instance
            training_data: Training samples

        Returns:
            Training metrics
        """
        start_time = time.time()
        convergence_epoch = None

        for epoch in range(self.max_epochs):
            epoch_correct = 0

            for input_pattern, target_pattern in training_data:
                # Set input
                for node_id, state in input_pattern.items():
                    if node_id in network.nodes:
                        network.nodes[node_id].state = state

                # Run network for a few steps
                for _ in range(10):
                    network.step(apply_learning=True)

                # Evaluate output
                output_nodes = set(target_pattern.keys())
                prediction = {
                    nid: network.nodes[nid].state
                    for nid in output_nodes
                    if nid in network.nodes
                }

                # Check if prediction matches target
                matches = sum(
                    1 for nid in output_nodes
                    if prediction.get(nid) == target_pattern.get(nid)
                )

                if matches >= len(output_nodes) * self.convergence_threshold:
                    epoch_correct += 1

            # Check convergence
            epoch_accuracy = epoch_correct / len(training_data)
            if epoch_accuracy >= self.convergence_threshold and convergence_epoch is None:
                convergence_epoch = epoch

        training_time = time.time() - start_time

        return {
            'training_time': training_time,
            'convergence_epoch': convergence_epoch or self.max_epochs,
            'final_network_size': len(network.nodes),
            'total_connections': network.get_total_connections()
        }

    def train_hyperbion_network(
        self,
        network: HyperbionNetwork,
        training_data: List[Any]
    ) -> Dict[str, Any]:
        """
        Train Hyperbion network on task.

        Args:
            network: HyperbionNetwork instance
            training_data: Training samples

        Returns:
            Training metrics
        """
        start_time = time.time()
        convergence_epoch = None
        operator_applications = 0

        for epoch in range(self.max_epochs):
            epoch_correct = 0

            for input_pattern, target_pattern in training_data:
                # Set input
                inputs = {}
                for cell_id, state in input_pattern.items():
                    if cell_id in network.cells:
                        # Map binary state to tripolar
                        inputs[cell_id] = state if state in [-1, 0, 1] else (1 if state > 0 else -1)

                # Run network
                initial_op_count = len(network.operator_history)

                for _ in range(10):
                    network.step(
                        inputs=inputs if _ == 0 else None,
                        apply_plasticity=True,
                        auto_trigger_operators=True
                    )

                operator_applications += len(network.operator_history) - initial_op_count

                # Evaluate output
                output_cells = set(target_pattern.keys())
                prediction = {}

                for cid in output_cells:
                    if cid in network.cells:
                        # Map tripolar back to binary for comparison
                        state = network.cells[cid].state
                        prediction[cid] = 1 if state > 0 else 0

                # Check if prediction matches target
                matches = sum(
                    1 for cid in output_cells
                    if prediction.get(cid) == target_pattern.get(cid)
                )

                if matches >= len(output_cells) * self.convergence_threshold:
                    epoch_correct += 1

            # Check convergence
            epoch_accuracy = epoch_correct / len(training_data)
            if epoch_accuracy >= self.convergence_threshold and convergence_epoch is None:
                convergence_epoch = epoch

        training_time = time.time() - start_time

        # Calculate operator boost
        operator_boost = operator_applications / max(len(training_data) * self.max_epochs, 1)

        return {
            'training_time': training_time,
            'convergence_epoch': convergence_epoch or self.max_epochs,
            'final_network_size': len(network.cells),
            'total_connections': sum(len(c.connections) for c in network.cells.values()),
            'operator_applications': operator_applications,
            'operator_boost': min(operator_boost, 1.0)  # Cap at 100%
        }

    def evaluate_network(
        self,
        network: Any,
        test_data: List[Any],
        is_hyperbion: bool = False
    ) -> Dict[str, float]:
        """
        Evaluate network on test data.

        Args:
            network: Network instance (binary or Hyperbion)
            test_data: Test samples
            is_hyperbion: Whether network is Hyperbion

        Returns:
            Performance metrics
        """
        predictions = []
        targets = []

        for input_pattern, target_pattern in test_data:
            # Set input and run network
            if is_hyperbion:
                inputs = {
                    cid: (state if state in [-1, 0, 1] else (1 if state > 0 else -1))
                    for cid, state in input_pattern.items()
                    if cid in network.cells
                }

                for _ in range(10):
                    network.step(
                        inputs=inputs if _ == 0 else None,
                        apply_plasticity=False,
                        auto_trigger_operators=False
                    )

                # Get output (map tripolar to binary)
                output_cells = set(target_pattern.keys())
                prediction = {
                    cid: (1 if network.cells[cid].state > 0 else 0)
                    for cid in output_cells
                    if cid in network.cells
                }

            else:  # Binary network
                for node_id, state in input_pattern.items():
                    if node_id in network.nodes:
                        network.nodes[node_id].state = state

                for _ in range(10):
                    network.step(apply_learning=False)

                # Get output
                output_nodes = set(target_pattern.keys())
                prediction = {
                    nid: network.nodes[nid].state
                    for nid in output_nodes
                    if nid in network.nodes
                }

            predictions.append(prediction)
            targets.append(target_pattern)

        # Evaluate using task-specific metrics
        performance = self.task.evaluate_performance(predictions, targets)

        return performance

    def run_benchmark(
        self,
        binary_network_size: int,
        tripolar_network_size: int
    ) -> Dict[str, Any]:
        """
        Run complete benchmark comparing both networks.

        Args:
            binary_network_size: Size of binary network
            tripolar_network_size: Size of Hyperbion network

        Returns:
            Complete benchmark results
        """
        print(f"\n{'='*60}")
        print(f"Running Benchmark: {self.task.name}")
        print(f"{'='*60}")

        # Generate data
        print(f"\nGenerating training data ({self.num_training_samples} samples)...")
        training_data = self.task.generate_training_data(self.num_training_samples)

        print(f"Generating test data ({self.num_test_samples} samples)...")
        test_data = self.task.generate_test_data(self.num_test_samples)

        # Binary network
        print(f"\n--- Binary Network (size={binary_network_size}) ---")
        binary_net = self.setup_binary_network(binary_network_size)
        print(f"Training...")

        binary_train_metrics = self.train_binary_network(binary_net, training_data)
        print(f"  Converged at epoch: {binary_train_metrics['convergence_epoch']}")
        print(f"  Training time: {binary_train_metrics['training_time']:.2f}s")

        print(f"Evaluating...")
        binary_perf = self.evaluate_network(binary_net, test_data, is_hyperbion=False)
        print(f"  Performance: {binary_perf}")

        # Hyperbion network
        print(f"\n--- Hyperbion Network (size={tripolar_network_size}) ---")
        hyperbion_net = self.setup_hyperbion_network(tripolar_network_size)
        print(f"Training...")

        hyperbion_train_metrics = self.train_hyperbion_network(hyperbion_net, training_data)
        print(f"  Converged at epoch: {hyperbion_train_metrics['convergence_epoch']}")
        print(f"  Training time: {hyperbion_train_metrics['training_time']:.2f}s")
        print(f"  Operator applications: {hyperbion_train_metrics['operator_applications']}")

        print(f"Evaluating...")
        hyperbion_perf = self.evaluate_network(hyperbion_net, test_data, is_hyperbion=True)
        print(f"  Performance: {hyperbion_perf}")

        # Aggregate results
        binary_results = {
            'network_size': binary_train_metrics['final_network_size'],
            'total_connections': binary_train_metrics['total_connections'],
            'convergence_steps': binary_train_metrics['convergence_epoch'],
            'training_time': binary_train_metrics['training_time'],
            'task_performance': binary_perf.get('accuracy', binary_perf.get('bit_accuracy', 0.0))
        }

        tripolar_results = {
            'network_size': hyperbion_train_metrics['final_network_size'],
            'total_connections': hyperbion_train_metrics['total_connections'],
            'convergence_steps': hyperbion_train_metrics['convergence_epoch'],
            'training_time': hyperbion_train_metrics['training_time'],
            'task_performance': hyperbion_perf.get('accuracy', hyperbion_perf.get('bit_accuracy', 0.0)),
            'operator_boost': hyperbion_train_metrics['operator_boost'],
            'operator_applications': hyperbion_train_metrics['operator_applications']
        }

        # Calculate comparison metrics
        comparison_metrics = BenchmarkMetrics.aggregate_metrics(
            binary_results,
            tripolar_results
        )

        # Store results
        self.results = {
            'task': self.task.name,
            'binary': binary_results,
            'hyperbion': tripolar_results,
            'comparison': comparison_metrics,
            'timestamp': time.time()
        }

        # Print summary
        self._print_summary()

        return self.results

    def _print_summary(self) -> None:
        """Print benchmark summary."""
        print(f"\n{'='*60}")
        print("BENCHMARK SUMMARY")
        print(f"{'='*60}")

        comp = self.results['comparison']

        print(f"\nInformation Capacity:")
        print(f"  Binary:    {comp['information_capacity']['binary']:.2f} bits")
        print(f"  Tripolar:  {comp['information_capacity']['tripolar']:.2f} bits")
        print(f"  Advantage: {comp['information_capacity']['advantage_percentage']:.1f}%")

        print(f"\nSystem Efficiency:")
        print(f"  System Advantage: {comp['system_efficiency']['system_advantage']:.2f}x")
        print(f"  Size Ratio:      {comp['system_efficiency']['size_ratio']:.2f}x")
        print(f"  Capacity Ratio:  {comp['system_efficiency']['capacity_ratio']:.2f}x")

        print(f"\nTask Performance:")
        print(f"  Binary:    {self.results['binary']['task_performance']:.1%}")
        print(f"  Hyperbion: {self.results['hyperbion']['task_performance']:.1%}")
        print(f"  Improvement: {comp['task_performance']['improvement']:.1%}")

        print(f"\nConvergence:")
        print(f"  Binary:    {self.results['binary']['convergence_steps']} epochs")
        print(f"  Hyperbion: {self.results['hyperbion']['convergence_steps']} epochs")

        print(f"\n{'='*60}\n")
