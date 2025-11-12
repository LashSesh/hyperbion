"""
Network Persistence
===================

State saving, loading, and replay functionality.
"""

import json
import pickle
from typing import Dict, Any, Optional, List
from pathlib import Path
import time

from ..core.network import HyperbionNetwork
from ..core.gabriel_cell import GabrielCell, PlasticityParams


class NetworkPersistence:
    """
    Handles saving and loading network state.

    Features:
    ---------
    - Save/load network state
    - Checkpoint management
    - History replay
    - Incremental snapshots
    """

    @staticmethod
    def save_state(
        network: HyperbionNetwork,
        filepath: str,
        format: str = 'json'
    ) -> bool:
        """
        Save network state to file.

        Args:
            network: Network instance
            filepath: Output file path
            format: 'json' or 'pickle'

        Returns:
            True if successful
        """
        state = network.to_dict()

        try:
            if format == 'json':
                with open(filepath, 'w') as f:
                    json.dump(state, f, indent=2, default=str)
            elif format == 'pickle':
                with open(filepath, 'wb') as f:
                    pickle.dump(state, f)
            else:
                raise ValueError(f"Unknown format: {format}")

            return True

        except Exception as e:
            print(f"Error saving state: {e}")
            return False

    @staticmethod
    def load_state(
        filepath: str,
        format: str = 'json'
    ) -> Optional[HyperbionNetwork]:
        """
        Load network state from file.

        Args:
            filepath: Input file path
            format: 'json' or 'pickle'

        Returns:
            HyperbionNetwork instance or None
        """
        try:
            if format == 'json':
                with open(filepath, 'r') as f:
                    state = json.load(f)
            elif format == 'pickle':
                with open(filepath, 'rb') as f:
                    state = pickle.load(f)
            else:
                raise ValueError(f"Unknown format: {format}")

            # Reconstruct network
            network = NetworkPersistence._reconstruct_network(state)
            return network

        except Exception as e:
            print(f"Error loading state: {e}")
            return None

    @staticmethod
    def _reconstruct_network(state: Dict[str, Any]) -> HyperbionNetwork:
        """
        Reconstruct network from state dictionary.

        Args:
            state: State dictionary

        Returns:
            HyperbionNetwork instance
        """
        # Create network
        network = HyperbionNetwork(name=state['name'])

        # Restore cells
        for cell_id, cell_data in state['cells'].items():
            cell = GabrielCell.from_dict(cell_data)
            network.cells[int(cell_id)] = cell

        # Update next_cell_id
        if network.cells:
            network.next_cell_id = max(network.cells.keys()) + 1

        # Restore clusters
        network.clusters = state.get('clusters', {})
        if network.clusters:
            network.next_cluster_id = max(int(k) for k in network.clusters.keys()) + 1

        # Restore step count
        network.step_count = state.get('step_count', 0)

        # Restore metrics
        network.metrics = state.get('metrics', {})

        return network

    @staticmethod
    def create_checkpoint(
        network: HyperbionNetwork,
        checkpoint_dir: str,
        name: Optional[str] = None
    ) -> str:
        """
        Create a checkpoint snapshot.

        Args:
            network: Network instance
            checkpoint_dir: Directory for checkpoints
            name: Optional checkpoint name

        Returns:
            Path to checkpoint file
        """
        Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)

        if name is None:
            name = f"checkpoint_step_{network.step_count}_{int(time.time())}"

        filepath = Path(checkpoint_dir) / f"{name}.json"

        NetworkPersistence.save_state(network, str(filepath), format='json')

        return str(filepath)

    @staticmethod
    def replay_history(
        network: HyperbionNetwork,
        event_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Replay network history with optional filtering.

        Args:
            network: Network instance
            event_filter: List of event types to include

        Returns:
            List of filtered events
        """
        if event_filter is None:
            return network.event_history

        return [
            event for event in network.event_history
            if event['type'] in event_filter
        ]

    @staticmethod
    def get_operator_timeline(network: HyperbionNetwork) -> List[Dict[str, Any]]:
        """
        Get timeline of operator applications.

        Args:
            network: Network instance

        Returns:
            List of operator events
        """
        timeline = []

        for result in network.operator_history:
            timeline.append({
                'operator': result.operator_type,
                'timestamp': result.timestamp,
                'affected_cells': result.affected_cells,
                'success': result.success,
                'metrics': result.metrics
            })

        return sorted(timeline, key=lambda x: x['timestamp'])

    @staticmethod
    def export_history(
        network: HyperbionNetwork,
        filepath: str,
        include_operator_history: bool = True,
        include_event_history: bool = True
    ) -> bool:
        """
        Export complete history to file.

        Args:
            network: Network instance
            filepath: Output file path
            include_operator_history: Include operator applications
            include_event_history: Include event log

        Returns:
            True if successful
        """
        history = {}

        if include_operator_history:
            history['operator_history'] = NetworkPersistence.get_operator_timeline(network)

        if include_event_history:
            history['event_history'] = network.event_history

        history['metrics'] = dict(network.metrics)
        history['step_count'] = network.step_count
        history['network_name'] = network.name

        try:
            with open(filepath, 'w') as f:
                json.dump(history, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error exporting history: {e}")
            return False
