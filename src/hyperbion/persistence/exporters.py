"""
Export Utilities
================

Export network to various formats for visualization and analysis.
"""

import json
import csv
from typing import Dict, Any
import networkx as nx
from pathlib import Path

from ..core.network import HyperbionNetwork


class JSONExporter:
    """Export network to JSON format."""

    @staticmethod
    def export(network: HyperbionNetwork, filepath: str) -> bool:
        """
        Export network to JSON.

        Args:
            network: Network instance
            filepath: Output file path

        Returns:
            True if successful
        """
        try:
            state = network.to_dict()
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False


class GraphMLExporter:
    """Export network topology to GraphML format."""

    @staticmethod
    def export(network: HyperbionNetwork, filepath: str) -> bool:
        """
        Export network topology to GraphML.

        Args:
            network: Network instance
            filepath: Output file path

        Returns:
            True if successful
        """
        try:
            G = nx.DiGraph()

            # Add nodes
            for cell_id, cell in network.cells.items():
                G.add_node(
                    cell_id,
                    state=cell.state,
                    bias=cell.bias,
                    age=cell.age,
                    division_count=cell.division_count,
                    fusion_count=cell.fusion_count
                )

            # Add edges
            for cell_id, cell in network.cells.items():
                for target_id, weight in cell.connections.items():
                    if target_id in network.cells:
                        G.add_edge(cell_id, target_id, weight=weight)

            # Write to file
            nx.write_graphml(G, filepath)
            return True

        except Exception as e:
            print(f"Error exporting to GraphML: {e}")
            return False


class LaTeXExporter:
    """Export network visualization to LaTeX/TikZ."""

    @staticmethod
    def export(network: HyperbionNetwork, filepath: str, max_nodes: int = 50) -> bool:
        """
        Export network to LaTeX/TikZ diagram.

        Args:
            network: Network instance
            filepath: Output file path
            max_nodes: Maximum nodes to include

        Returns:
            True if successful
        """
        try:
            latex_content = LaTeXExporter._generate_tikz(network, max_nodes)

            with open(filepath, 'w') as f:
                f.write(latex_content)

            return True

        except Exception as e:
            print(f"Error exporting to LaTeX: {e}")
            return False

    @staticmethod
    def _generate_tikz(network: HyperbionNetwork, max_nodes: int) -> str:
        """Generate TikZ diagram code."""

        # Get subset of cells
        cell_ids = list(network.cells.keys())[:max_nodes]

        # Start LaTeX document
        latex = [
            r"\documentclass{article}",
            r"\usepackage{tikz}",
            r"\usetikzlibrary{arrows,positioning}",
            r"\begin{document}",
            r"\begin{tikzpicture}[",
            r"  node distance=2cm,",
            r"  cell/.style={circle, draw, minimum size=1cm},",
            r"  positive/.style={fill=green!30},",
            r"  negative/.style={fill=red!30},",
            r"  neutral/.style={fill=gray!20}",
            r"]",
            ""
        ]

        # Add nodes
        for i, cell_id in enumerate(cell_ids):
            cell = network.cells[cell_id]

            # Determine style based on state
            if cell.state == 1:
                style = "cell,positive"
            elif cell.state == -1:
                style = "cell,negative"
            else:
                style = "cell,neutral"

            # Position nodes in a grid
            x = (i % 7) * 2
            y = -(i // 7) * 2

            latex.append(
                f"  \\node[{style}] (n{cell_id}) at ({x},{y}) {{{cell_id}}};"
            )

        latex.append("")

        # Add edges
        for cell_id in cell_ids:
            cell = network.cells[cell_id]

            for target_id, weight in cell.connections.items():
                if target_id in cell_ids:
                    # Determine edge style based on weight
                    if weight > 0:
                        color = "green"
                        thickness = min(abs(weight), 3)
                    elif weight < 0:
                        color = "red"
                        thickness = min(abs(weight), 3)
                    else:
                        continue  # Skip zero weights

                    latex.append(
                        f"  \\draw[->,line width={thickness}pt,{color}!50] "
                        f"(n{cell_id}) -- (n{target_id});"
                    )

        # End document
        latex.extend([
            "",
            r"\end{tikzpicture}",
            "",
            r"\section*{Network Statistics}",
            f"Network: {network.name} \\\\",
            f"Cells: {len(network.cells)} \\\\",
            f"Steps: {network.step_count} \\\\",
            f"Clusters: {len(network.clusters)} \\\\",
            "",
            r"\end{document}"
        ])

        return "\n".join(latex)


class CSVExporter:
    """Export network data to CSV format."""

    @staticmethod
    def export_cells(network: HyperbionNetwork, filepath: str) -> bool:
        """
        Export cell data to CSV.

        Args:
            network: Network instance
            filepath: Output file path

        Returns:
            True if successful
        """
        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)

                # Header
                writer.writerow([
                    'cell_id', 'state', 'bias', 'age',
                    'connections', 'division_count', 'fusion_count'
                ])

                # Data
                for cell_id, cell in network.cells.items():
                    writer.writerow([
                        cell_id,
                        cell.state,
                        cell.bias,
                        cell.age,
                        len(cell.connections),
                        cell.division_count,
                        cell.fusion_count
                    ])

            return True

        except Exception as e:
            print(f"Error exporting cells to CSV: {e}")
            return False

    @staticmethod
    def export_connections(network: HyperbionNetwork, filepath: str) -> bool:
        """
        Export connections to CSV.

        Args:
            network: Network instance
            filepath: Output file path

        Returns:
            True if successful
        """
        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)

                # Header
                writer.writerow(['source', 'target', 'weight'])

                # Data
                for cell_id, cell in network.cells.items():
                    for target_id, weight in cell.connections.items():
                        writer.writerow([cell_id, target_id, weight])

            return True

        except Exception as e:
            print(f"Error exporting connections to CSV: {e}")
            return False

    @staticmethod
    def export_metrics(network: HyperbionNetwork, filepath: str) -> bool:
        """
        Export metrics to CSV.

        Args:
            network: Network instance
            filepath: Output file path

        Returns:
            True if successful
        """
        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)

                # Get all metric names
                metric_names = list(network.metrics.keys())

                if not metric_names:
                    return True

                # Header
                writer.writerow(['step'] + metric_names)

                # Data - iterate over steps
                max_len = max(len(values) for values in network.metrics.values())

                for step in range(max_len):
                    row = [step]
                    for metric_name in metric_names:
                        values = network.metrics[metric_name]
                        if step < len(values):
                            row.append(values[step])
                        else:
                            row.append('')
                    writer.writerow(row)

            return True

        except Exception as e:
            print(f"Error exporting metrics to CSV: {e}")
            return False
