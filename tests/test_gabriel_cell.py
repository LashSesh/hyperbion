"""
Unit tests for GabrielCell
"""

import pytest
from hyperbion.core.gabriel_cell import GabrielCell, PlasticityParams


class TestGabrielCell:
    """Tests for Gabriel Cell functionality."""

    def test_initialization(self):
        """Test cell initialization."""
        cell = GabrielCell(cell_id=1, initial_state=0, bias=0.5)

        assert cell.id == 1
        assert cell.state == 0
        assert cell.bias == 0.5
        assert len(cell.connections) == 0

    def test_invalid_initial_state(self):
        """Test that invalid states raise errors."""
        with pytest.raises(ValueError):
            GabrielCell(cell_id=1, initial_state=2)

    def test_tripolar_sign_function(self):
        """Test tripolar sign function."""
        cell = GabrielCell(cell_id=1)

        # Test positive threshold
        assert cell.tripolar_sign(1.0) == 1

        # Test negative threshold
        assert cell.tripolar_sign(-1.0) == -1

        # Test neutral zone
        assert cell.tripolar_sign(0.0) == 0
        assert cell.tripolar_sign(0.3) == 0

    def test_connect_cells(self):
        """Test creating connections."""
        cell = GabrielCell(cell_id=1)

        cell.connect(target_id=2, weight=1.5)
        cell.connect(target_id=3, weight=-0.5)

        assert len(cell.connections) == 2
        assert cell.connections[2] == 1.5
        assert cell.connections[3] == -0.5

    def test_disconnect_cells(self):
        """Test removing connections."""
        cell = GabrielCell(cell_id=1)

        cell.connect(target_id=2, weight=1.0)
        assert cell.disconnect(target_id=2) is True
        assert cell.disconnect(target_id=2) is False  # Already removed

    def test_state_update(self):
        """Test state update logic."""
        cell1 = GabrielCell(cell_id=1, initial_state=0)
        cell2 = GabrielCell(cell_id=2, initial_state=1)

        # Create connection
        cell1.connect(target_id=2, weight=2.0)

        # Update state
        neighbor_states = {2: cell2.state}
        new_state = cell1.update_state(neighbor_states)

        # With weight 2.0 and neighbor state 1, activation = 2.0
        # Should be positive
        assert new_state == 1

    def test_plasticity_hebbian(self):
        """Test Hebbian plasticity."""
        cell1 = GabrielCell(cell_id=1, initial_state=1)
        cell1.connect(target_id=2, weight=1.0)

        neighbor_states = {2: 1}  # Both cells active

        initial_weight = cell1.connections[2]
        cell1.apply_plasticity(neighbor_states)
        final_weight = cell1.connections[2]

        # Weight should increase (Hebbian learning)
        assert final_weight > initial_weight

    def test_wormhole_connections(self):
        """Test wormhole (temporary) connections."""
        cell = GabrielCell(cell_id=1)

        # Add wormhole
        cell.add_wormhole(target_id=5, weight=3.0, duration=1.0)

        assert 5 in cell.wormhole_connections

        # Get connection strength (includes wormhole)
        strength = cell.get_connection_strength(5)
        assert strength == 3.0

    def test_serialization(self):
        """Test cell serialization."""
        cell = GabrielCell(cell_id=1, initial_state=1, bias=0.5)
        cell.connect(target_id=2, weight=1.0)

        # Serialize
        data = cell.to_dict()

        # Deserialize
        cell2 = GabrielCell.from_dict(data)

        assert cell2.id == cell.id
        assert cell2.state == cell.state
        assert cell2.bias == cell.bias
        assert cell2.connections == cell.connections
