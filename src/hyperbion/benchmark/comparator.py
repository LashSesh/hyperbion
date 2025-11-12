"""
Network Comparator
==================

Comparison and visualization tools for benchmark results.
"""

from typing import Dict, List, Any
import json
import csv
from pathlib import Path


class NetworkComparator:
    """
    Compare and visualize results from multiple benchmarks.
    """

    def __init__(self):
        """Initialize comparator."""
        self.results: List[Dict[str, Any]] = []

    def add_result(self, result: Dict[str, Any]) -> None:
        """Add a benchmark result."""
        self.results.append(result)

    def export_to_json(self, filepath: str) -> None:
        """Export all results to JSON."""
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

    def export_to_csv(self, filepath: str) -> None:
        """Export comparison metrics to CSV."""
        if not self.results:
            return

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'Task',
                'Binary Size',
                'Hyperbion Size',
                'Binary Capacity',
                'Hyperbion Capacity',
                'Information Advantage (%)',
                'System Advantage (x)',
                'Binary Performance',
                'Hyperbion Performance',
                'Performance Improvement',
                'Binary Convergence (epochs)',
                'Hyperbion Convergence (epochs)',
                'Operator Applications'
            ])

            # Data
            for result in self.results:
                binary = result['binary']
                hyperbion = result['hyperbion']
                comp = result['comparison']

                writer.writerow([
                    result['task'],
                    binary['network_size'],
                    hyperbion['network_size'],
                    comp['information_capacity']['binary'],
                    comp['information_capacity']['tripolar'],
                    comp['information_capacity']['advantage_percentage'],
                    comp['system_efficiency']['system_advantage'],
                    binary['task_performance'],
                    hyperbion['task_performance'],
                    comp['task_performance']['improvement'],
                    binary['convergence_steps'],
                    hyperbion['convergence_steps'],
                    hyperbion.get('operator_applications', 0)
                ])

    def generate_summary_report(self) -> str:
        """Generate text summary report."""
        if not self.results:
            return "No benchmark results available."

        lines = []
        lines.append("=" * 80)
        lines.append("HYPERBION BENCHMARK SUMMARY REPORT")
        lines.append("=" * 80)
        lines.append("")

        for idx, result in enumerate(self.results, 1):
            lines.append(f"\n{idx}. {result['task']}")
            lines.append("-" * 80)

            binary = result['binary']
            hyperbion = result['hyperbion']
            comp = result['comparison']

            # Network sizes
            lines.append(f"\nNetwork Sizes:")
            lines.append(f"  Binary Network:    {binary['network_size']} nodes")
            lines.append(f"  Hyperbion Network: {hyperbion['network_size']} cells")

            # Information capacity
            lines.append(f"\nInformation Capacity:")
            lines.append(f"  Binary:    {comp['information_capacity']['binary']:.2f} bits")
            lines.append(f"  Hyperbion: {comp['information_capacity']['tripolar']:.2f} bits")
            lines.append(f"  Advantage: {comp['information_capacity']['advantage_percentage']:.1f}%")

            # System efficiency
            lines.append(f"\nSystem Efficiency:")
            lines.append(f"  System Advantage: {comp['system_efficiency']['system_advantage']:.2f}x")
            lines.append(f"  Size Ratio:       {comp['system_efficiency']['size_ratio']:.2f}x")
            lines.append(f"  Capacity Ratio:   {comp['system_efficiency']['capacity_ratio']:.2f}x")
            lines.append(f"  Operator Boost:   {comp['system_efficiency']['operator_boost']:.1%}")

            # Performance
            lines.append(f"\nTask Performance:")
            lines.append(f"  Binary:    {binary['task_performance']:.1%}")
            lines.append(f"  Hyperbion: {hyperbion['task_performance']:.1%}")
            lines.append(f"  Improvement: {comp['task_performance']['improvement']:.1%}")

            # Convergence
            lines.append(f"\nConvergence:")
            lines.append(f"  Binary:    {binary['convergence_steps']} epochs")
            lines.append(f"  Hyperbion: {hyperbion['convergence_steps']} epochs")
            lines.append(f"  Speedup:   {comp['convergence']['step_speedup']:.2f}x")

            # Resource efficiency
            lines.append(f"\nResource Efficiency:")
            lines.append(f"  Node Efficiency Ratio:       {comp['resource_efficiency']['node_efficiency_ratio']:.2f}x")
            lines.append(f"  Connection Efficiency Ratio: {comp['resource_efficiency']['connection_efficiency_ratio']:.2f}x")

        # Overall summary
        lines.append(f"\n{'='*80}")
        lines.append("OVERALL SUMMARY")
        lines.append(f"{'='*80}")

        avg_info_advantage = sum(
            r['comparison']['information_capacity']['advantage_percentage']
            for r in self.results
        ) / len(self.results)

        avg_system_advantage = sum(
            r['comparison']['system_efficiency']['system_advantage']
            for r in self.results
        ) / len(self.results)

        avg_perf_improvement = sum(
            r['comparison']['task_performance']['improvement']
            for r in self.results
        ) / len(self.results)

        lines.append(f"\nAverage Information Advantage: {avg_info_advantage:.1f}%")
        lines.append(f"Average System Advantage:      {avg_system_advantage:.2f}x")
        lines.append(f"Average Performance Improvement: {avg_perf_improvement:.1%}")

        # Success criteria
        lines.append(f"\n{'='*80}")
        lines.append("SUCCESS CRITERIA")
        lines.append(f"{'='*80}")

        criteria_met = []

        if avg_info_advantage >= 58.5:
            criteria_met.append(f"✓ Information advantage ≥ 58.5%: {avg_info_advantage:.1f}%")
        else:
            criteria_met.append(f"✗ Information advantage < 58.5%: {avg_info_advantage:.1f}%")

        if avg_system_advantage >= 2.0:
            criteria_met.append(f"✓ System advantage ≥ 2x: {avg_system_advantage:.2f}x")
        else:
            criteria_met.append(f"✗ System advantage < 2x: {avg_system_advantage:.2f}x")

        if avg_perf_improvement >= 0:
            criteria_met.append(f"✓ Performance improvement ≥ 0%: {avg_perf_improvement:.1%}")
        else:
            criteria_met.append(f"✗ Performance regression: {avg_perf_improvement:.1%}")

        lines.extend(criteria_met)
        lines.append("")

        return "\n".join(lines)
