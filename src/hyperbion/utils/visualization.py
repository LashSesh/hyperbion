"""
Visualization Utilities
=======================

Tools for visualizing network state and dynamics.
"""

from typing import Optional, Dict, Any
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from ..core.network import HyperbionNetwork


class NetworkVisualizer:
    """
    Visualization tools for Hyperbion networks.

    Provides methods for:
    - State distribution plots
    - Network topology visualization
    - Metrics over time
    - Operator activity timeline
    """

    @staticmethod
    def plot_state_distribution(
        network: HyperbionNetwork,
        save_path: Optional[str] = None
    ) -> None:
        """
        Plot distribution of cell states.

        Args:
            network: Network instance
            save_path: Optional path to save figure
        """
        if not network.cells:
            print("No cells to plot")
            return

        states = [cell.state for cell in network.cells.values()]

        plt.figure(figsize=(8, 6))

        # Count states
        counts = {-1: states.count(-1), 0: states.count(0), 1: states.count(1)}

        # Plot
        colors = {-1: 'red', 0: 'gray', 1: 'green'}
        labels = {-1: 'Negative (-1)', 0: 'Neutral (0)', 1: 'Positive (+1)'}

        bars = plt.bar(
            counts.keys(),
            counts.values(),
            color=[colors[k] for k in counts.keys()],
            alpha=0.7,
            edgecolor='black'
        )

        plt.xlabel('State')
        plt.ylabel('Count')
        plt.title(f'Cell State Distribution (N={len(network.cells)})')
        plt.xticks([-1, 0, 1], [labels[k] for k in [-1, 0, 1]])
        plt.grid(axis='y', alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved to {save_path}")
        else:
            plt.show()

        plt.close()

    @staticmethod
    def plot_metrics_timeline(
        network: HyperbionNetwork,
        metrics: Optional[list] = None,
        save_path: Optional[str] = None
    ) -> None:
        """
        Plot metrics over time.

        Args:
            network: Network instance
            metrics: List of metric names to plot (None = all)
            save_path: Optional path to save figure
        """
        if not network.metrics:
            print("No metrics to plot")
            return

        if metrics is None:
            metrics = list(network.metrics.keys())

        fig, axes = plt.subplots(
            len(metrics),
            1,
            figsize=(12, 3 * len(metrics)),
            squeeze=False
        )

        for idx, metric_name in enumerate(metrics):
            if metric_name not in network.metrics:
                continue

            values = network.metrics[metric_name]
            steps = list(range(len(values)))

            ax = axes[idx, 0]
            ax.plot(steps, values, linewidth=2)
            ax.set_xlabel('Step')
            ax.set_ylabel(metric_name.replace('_', ' ').title())
            ax.set_title(f'{metric_name.replace("_", " ").title()} over Time')
            ax.grid(alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved to {save_path}")
        else:
            plt.show()

        plt.close()

    @staticmethod
    def plot_operator_statistics(
        network: HyperbionNetwork,
        save_path: Optional[str] = None
    ) -> None:
        """
        Plot operator application statistics.

        Args:
            network: Network instance
            save_path: Optional path to save figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Application counts
        op_names = []
        op_counts = []
        op_success_rates = []

        for name, operator in network.operators.items():
            stats = operator.get_statistics()
            op_names.append(name)
            op_counts.append(stats['application_count'])
            op_success_rates.append(stats['success_rate'] * 100)

        # Plot 1: Application counts
        bars1 = ax1.bar(op_names, op_counts, alpha=0.7, edgecolor='black')
        ax1.set_xlabel('Operator')
        ax1.set_ylabel('Application Count')
        ax1.set_title('Operator Applications')
        ax1.grid(axis='y', alpha=0.3)

        # Color bars by count
        for i, bar in enumerate(bars1):
            if op_counts[i] > 0:
                bar.set_color('steelblue')
            else:
                bar.set_color('lightgray')

        # Plot 2: Success rates
        bars2 = ax2.bar(op_names, op_success_rates, alpha=0.7, edgecolor='black')
        ax2.set_xlabel('Operator')
        ax2.set_ylabel('Success Rate (%)')
        ax2.set_title('Operator Success Rates')
        ax2.set_ylim([0, 105])
        ax2.grid(axis='y', alpha=0.3)

        # Color bars by success rate
        for i, bar in enumerate(bars2):
            if op_success_rates[i] >= 80:
                bar.set_color('green')
            elif op_success_rates[i] >= 50:
                bar.set_color('orange')
            elif op_counts[i] > 0:
                bar.set_color('red')
            else:
                bar.set_color('lightgray')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved to {save_path}")
        else:
            plt.show()

        plt.close()

    @staticmethod
    def plot_network_evolution(
        network: HyperbionNetwork,
        save_path: Optional[str] = None
    ) -> None:
        """
        Plot network size and complexity evolution.

        Args:
            network: Network instance
            save_path: Optional path to save figure
        """
        if 'network_size' not in network.metrics:
            print("No evolution metrics to plot")
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        # Network size
        steps = list(range(len(network.metrics['network_size'])))
        ax1.plot(steps, network.metrics['network_size'], linewidth=2, color='steelblue')
        ax1.set_xlabel('Step')
        ax1.set_ylabel('Network Size')
        ax1.set_title('Network Size Evolution')
        ax1.grid(alpha=0.3)

        # Connection density
        if 'connection_density' in network.metrics:
            ax2.plot(
                steps,
                network.metrics['connection_density'],
                linewidth=2,
                color='darkgreen'
            )
            ax2.set_xlabel('Step')
            ax2.set_ylabel('Connection Density')
            ax2.set_title('Connection Density Evolution')
            ax2.set_ylim([0, 1])
            ax2.grid(alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved to {save_path}")
        else:
            plt.show()

        plt.close()
