"""
Unit tests for HyperbionNetwork
"""

import pytest
from hyperbion.core.network import HyperbionNetwork


class TestHyperbionNetwork:
    """Tests for Hyperbion Network functionality."""

    def test_initialization(self):
        """Test network initialization."""
        network = HyperbionNetwork(name="TestNetwork")

        assert network.name == "TestNetwork"
        assert len(network.cells) == 0
        assert network.step_count == 0

    def test_add_cell(self):
        """Test adding cells to network."""
        network = HyperbionNetwork()

        cell_id = network.add_cell(state=1, bias=0.5)

        assert cell_id == 0
        assert cell_id in network.cells
        assert network.cells[cell_id].state == 1

    def test_remove_cell(self):
        """Test removing cells from network."""
        network = HyperbionNetwork()

        cell_id = network.add_cell()
        assert network.remove_cell(cell_id) is True
        assert cell_id not in network.cells
        assert network.remove_cell(cell_id) is False  # Already removed

    def test_connect_cells(self):
        """Test connecting cells."""
        network = HyperbionNetwork()

        cell1_id = network.add_cell()
        cell2_id = network.add_cell()

        success = network.connect_cells(cell1_id, cell2_id, weight=1.5)

        assert success is True
        assert cell2_id in network.cells[cell1_id].connections

    def test_create_cluster(self):
        """Test cluster creation."""
        network = HyperbionNetwork()

        # Add cells
        cell_ids = [network.add_cell() for _ in range(5)]

        # Create cluster
        cluster_id = network.create_cluster(cell_ids)

        assert cluster_id in network.clusters
        assert network.clusters[cluster_id]['members'] == cell_ids

    def test_auto_detect_clusters(self):
        """Test automatic cluster detection."""
        network = HyperbionNetwork()

        # Create two separate clusters
        cluster1 = [network.add_cell() for _ in range(3)]
        cluster2 = [network.add_cell() for _ in range(3)]

        # Connect within clusters
        for i in range(len(cluster1) - 1):
            network.connect_cells(cluster1[i], cluster1[i + 1], 1.0)

        for i in range(len(cluster2) - 1):
            network.connect_cells(cluster2[i], cluster2[i + 1], 1.0)

        # Auto-detect
        detected = network.auto_detect_clusters(min_cluster_size=3)

        assert len(detected) == 2

    def test_topological_distance(self):
        """Test topological distance calculation."""
        network = HyperbionNetwork()

        # Create chain: 0 -> 1 -> 2
        c0 = network.add_cell()
        c1 = network.add_cell()
        c2 = network.add_cell()

        network.connect_cells(c0, c1, 1.0)
        network.connect_cells(c1, c2, 1.0)

        # Test distances
        assert network.get_topological_distance(c0, c1) == 1
        assert network.get_topological_distance(c0, c2) == 2
        assert network.get_topological_distance(c0, c0) == 0

    def test_network_step(self):
        """Test network simulation step."""
        network = HyperbionNetwork()

        # Add cells
        c0 = network.add_cell(state=1)
        c1 = network.add_cell(state=0)

        network.connect_cells(c0, c1, 2.0)

        # Execute step
        result = network.step()

        assert network.step_count == 1
        assert 'step' in result
        assert 'new_states' in result

    def test_apply_operator(self):
        """Test manual operator application."""
        network = HyperbionNetwork()

        # Create a cluster
        cells = [network.add_cell(state=1) for _ in range(3)]

        # Connect cells
        for i in range(len(cells) - 1):
            network.connect_cells(cells[i], cells[i + 1], 1.0)

        # Apply DK operator
        result = network.apply_operator('DK', cells)

        assert result.success is True
        assert result.operator_type == 'DK'

    def test_get_state(self):
        """Test getting network state."""
        network = HyperbionNetwork()

        network.add_cell()
        network.add_cell()

        state = network.get_state()

        assert 'name' in state
        assert 'cells' in state
        assert 'step_count' in state
        assert len(state['cells']) == 2
