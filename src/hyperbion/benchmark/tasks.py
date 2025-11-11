"""
Benchmark Tasks
===============

Standardized tasks for comparing network architectures.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any
import numpy as np


class BenchmarkTask(ABC):
    """Abstract base class for benchmark tasks."""

    def __init__(self, name: str, difficulty: str = "medium"):
        """
        Initialize benchmark task.

        Args:
            name: Task name
            difficulty: Task difficulty (easy, medium, hard)
        """
        self.name = name
        self.difficulty = difficulty

    @abstractmethod
    def generate_training_data(
        self,
        num_samples: int
    ) -> List[Tuple[Dict[int, int], Dict[int, int]]]:
        """
        Generate training data.

        Returns:
            List of (input_pattern, target_pattern) tuples
        """
        pass

    @abstractmethod
    def generate_test_data(
        self,
        num_samples: int
    ) -> List[Tuple[Dict[int, int], Dict[int, int]]]:
        """Generate test data."""
        pass

    @abstractmethod
    def evaluate_performance(
        self,
        predictions: List[Dict[int, int]],
        targets: List[Dict[int, int]]
    ) -> Dict[str, float]:
        """
        Evaluate network performance on task.

        Returns:
            Dictionary with performance metrics
        """
        pass

    def get_required_input_size(self) -> int:
        """Get minimum required input layer size."""
        return 10  # Default

    def get_required_output_size(self) -> int:
        """Get minimum required output layer size."""
        return 10  # Default


class PatternClassificationTask(BenchmarkTask):
    """
    Pattern classification task.

    Network must learn to classify input patterns into categories.
    """

    def __init__(
        self,
        name: str = "PatternClassification",
        num_classes: int = 4,
        pattern_size: int = 16,
        noise_level: float = 0.1
    ):
        """
        Initialize pattern classification task.

        Args:
            name: Task name
            num_classes: Number of pattern classes
            pattern_size: Size of each pattern
            noise_level: Noise level in patterns
        """
        super().__init__(name, difficulty="medium")
        self.num_classes = num_classes
        self.pattern_size = pattern_size
        self.noise_level = noise_level

        # Generate base patterns
        self.base_patterns = self._generate_base_patterns()

    def _generate_base_patterns(self) -> List[np.ndarray]:
        """Generate base patterns for each class."""
        patterns = []

        for i in range(self.num_classes):
            # Create distinct pattern for each class
            pattern = np.random.choice([0, 1], size=self.pattern_size)
            patterns.append(pattern)

        return patterns

    def _add_noise(self, pattern: np.ndarray) -> np.ndarray:
        """Add noise to a pattern."""
        noisy = pattern.copy()
        num_flips = int(self.pattern_size * self.noise_level)

        flip_indices = np.random.choice(
            self.pattern_size,
            size=num_flips,
            replace=False
        )

        noisy[flip_indices] = 1 - noisy[flip_indices]
        return noisy

    def _pattern_to_dict(self, pattern: np.ndarray, offset: int = 0) -> Dict[int, int]:
        """Convert numpy array to node state dictionary."""
        return {i + offset: int(val) for i, val in enumerate(pattern)}

    def _class_to_output(self, class_idx: int) -> Dict[int, int]:
        """Convert class index to output pattern."""
        # One-hot encoding starting from pattern_size
        output = {self.pattern_size + i: 0 for i in range(self.num_classes)}
        output[self.pattern_size + class_idx] = 1
        return output

    def generate_training_data(
        self,
        num_samples: int
    ) -> List[Tuple[Dict[int, int], Dict[int, int]]]:
        """Generate training samples."""
        data = []

        for _ in range(num_samples):
            # Random class
            class_idx = np.random.randint(0, self.num_classes)

            # Get base pattern and add noise
            base_pattern = self.base_patterns[class_idx]
            noisy_pattern = self._add_noise(base_pattern)

            # Convert to dictionaries
            input_dict = self._pattern_to_dict(noisy_pattern)
            output_dict = self._class_to_output(class_idx)

            data.append((input_dict, output_dict))

        return data

    def generate_test_data(
        self,
        num_samples: int
    ) -> List[Tuple[Dict[int, int], Dict[int, int]]]:
        """Generate test samples."""
        return self.generate_training_data(num_samples)

    def evaluate_performance(
        self,
        predictions: List[Dict[int, int]],
        targets: List[Dict[int, int]]
    ) -> Dict[str, float]:
        """Evaluate classification accuracy."""
        if len(predictions) != len(targets):
            raise ValueError("Predictions and targets must have same length")

        correct = 0
        total = len(predictions)

        for pred, target in zip(predictions, targets):
            # Extract class predictions (nodes pattern_size to pattern_size + num_classes)
            pred_class_nodes = {
                k - self.pattern_size: v
                for k, v in pred.items()
                if self.pattern_size <= k < self.pattern_size + self.num_classes
            }

            target_class_nodes = {
                k - self.pattern_size: v
                for k, v in target.items()
                if self.pattern_size <= k < self.pattern_size + self.num_classes
            }

            # Find predicted class (argmax)
            if pred_class_nodes and target_class_nodes:
                pred_class = max(pred_class_nodes.items(), key=lambda x: x[1])[0]
                target_class = max(target_class_nodes.items(), key=lambda x: x[1])[0]

                if pred_class == target_class:
                    correct += 1

        accuracy = correct / total if total > 0 else 0.0

        return {
            'accuracy': accuracy,
            'correct': correct,
            'total': total,
            'error_rate': 1.0 - accuracy
        }

    def get_required_input_size(self) -> int:
        """Get required input size."""
        return self.pattern_size

    def get_required_output_size(self) -> int:
        """Get required output size."""
        return self.num_classes


class MemoryCapacityTask(BenchmarkTask):
    """
    Memory capacity task.

    Tests how many distinct patterns can be stored and retrieved.
    """

    def __init__(
        self,
        name: str = "MemoryCapacity",
        pattern_size: int = 16,
        max_patterns: int = 20
    ):
        """
        Initialize memory capacity task.

        Args:
            name: Task name
            pattern_size: Size of each pattern
            max_patterns: Maximum number of patterns to store
        """
        super().__init__(name, difficulty="hard")
        self.pattern_size = pattern_size
        self.max_patterns = max_patterns

        # Generate unique patterns
        self.stored_patterns = self._generate_unique_patterns()

    def _generate_unique_patterns(self) -> List[np.ndarray]:
        """Generate unique random patterns."""
        patterns = []

        for _ in range(self.max_patterns):
            pattern = np.random.choice([0, 1], size=self.pattern_size)
            patterns.append(pattern)

        return patterns

    def _pattern_to_dict(self, pattern: np.ndarray) -> Dict[int, int]:
        """Convert pattern to dictionary."""
        return {i: int(val) for i, val in enumerate(pattern)}

    def generate_training_data(
        self,
        num_samples: int
    ) -> List[Tuple[Dict[int, int], Dict[int, int]]]:
        """
        Generate training data.

        For memory task, input and output are the same (autoencoder).
        """
        data = []

        for _ in range(num_samples):
            # Select random stored pattern
            pattern_idx = np.random.randint(0, len(self.stored_patterns))
            pattern = self.stored_patterns[pattern_idx]

            pattern_dict = self._pattern_to_dict(pattern)

            # Autoencoder: input = output
            data.append((pattern_dict, pattern_dict))

        return data

    def generate_test_data(
        self,
        num_samples: int
    ) -> List[Tuple[Dict[int, int], Dict[int, int]]]:
        """Generate test data (all stored patterns)."""
        data = []

        for pattern in self.stored_patterns[:num_samples]:
            pattern_dict = self._pattern_to_dict(pattern)
            data.append((pattern_dict, pattern_dict))

        return data

    def evaluate_performance(
        self,
        predictions: List[Dict[int, int]],
        targets: List[Dict[int, int]]
    ) -> Dict[str, float]:
        """Evaluate memory recall accuracy."""
        if len(predictions) != len(targets):
            raise ValueError("Predictions and targets must have same length")

        total_bits = 0
        correct_bits = 0

        for pred, target in zip(predictions, targets):
            for node_id in target.keys():
                if node_id in pred:
                    total_bits += 1
                    if pred[node_id] == target[node_id]:
                        correct_bits += 1

        bit_accuracy = correct_bits / total_bits if total_bits > 0 else 0.0

        # Pattern-level accuracy (all bits must match)
        perfect_patterns = sum(
            1 for pred, target in zip(predictions, targets)
            if all(pred.get(k) == v for k, v in target.items())
        )

        pattern_accuracy = perfect_patterns / len(predictions) if predictions else 0.0

        return {
            'bit_accuracy': bit_accuracy,
            'pattern_accuracy': pattern_accuracy,
            'correct_bits': correct_bits,
            'total_bits': total_bits,
            'perfect_patterns': perfect_patterns,
            'total_patterns': len(predictions)
        }

    def get_required_input_size(self) -> int:
        """Get required input/output size."""
        return self.pattern_size

    def get_required_output_size(self) -> int:
        """Get required input/output size."""
        return self.pattern_size


class AssociationTask(BenchmarkTask):
    """
    Association task.

    Network must learn associations between input and output patterns.
    """

    def __init__(
        self,
        name: str = "Association",
        input_size: int = 12,
        output_size: int = 12,
        num_associations: int = 8
    ):
        """Initialize association task."""
        super().__init__(name, difficulty="medium")
        self.input_size = input_size
        self.output_size = output_size
        self.num_associations = num_associations

        # Generate random associations
        self.associations = self._generate_associations()

    def _generate_associations(self) -> List[Tuple[np.ndarray, np.ndarray]]:
        """Generate random input-output associations."""
        associations = []

        for _ in range(self.num_associations):
            input_pattern = np.random.choice([0, 1], size=self.input_size)
            output_pattern = np.random.choice([0, 1], size=self.output_size)
            associations.append((input_pattern, output_pattern))

        return associations

    def generate_training_data(
        self,
        num_samples: int
    ) -> List[Tuple[Dict[int, int], Dict[int, int]]]:
        """Generate training data."""
        data = []

        for _ in range(num_samples):
            assoc_idx = np.random.randint(0, len(self.associations))
            input_pattern, output_pattern = self.associations[assoc_idx]

            input_dict = {i: int(val) for i, val in enumerate(input_pattern)}
            output_dict = {
                i + self.input_size: int(val)
                for i, val in enumerate(output_pattern)
            }

            data.append((input_dict, output_dict))

        return data

    def generate_test_data(
        self,
        num_samples: int
    ) -> List[Tuple[Dict[int, int], Dict[int, int]]]:
        """Generate test data."""
        return self.generate_training_data(num_samples)

    def evaluate_performance(
        self,
        predictions: List[Dict[int, int]],
        targets: List[Dict[int, int]]
    ) -> Dict[str, float]:
        """Evaluate association accuracy."""
        correct_bits = 0
        total_bits = 0

        for pred, target in zip(predictions, targets):
            for node_id in target.keys():
                if node_id in pred:
                    total_bits += 1
                    if pred[node_id] == target[node_id]:
                        correct_bits += 1

        accuracy = correct_bits / total_bits if total_bits > 0 else 0.0

        return {
            'accuracy': accuracy,
            'correct_bits': correct_bits,
            'total_bits': total_bits
        }

    def get_required_input_size(self) -> int:
        return self.input_size

    def get_required_output_size(self) -> int:
        return self.output_size
