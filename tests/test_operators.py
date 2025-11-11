"""
Unit tests for Operators
"""

import pytest
from hyperbion.core.network import HyperbionNetwork
from hyperbion.operators.doppelkick import DoppelkickOperator
from hyperbion.operators.sweep import SweepOperator
from hyperbion.operators.wormhole import WormholeOperator
from hyperbion.operators.nullpunkt import NullpunktOperator
from hyperbion.operators.morphogenesis import MorphogenesisOperator


class TestDoppelkickOperator:
    """Tests for DK operator."""

    def test_doppelkick_application(self):
        """Test DK operator application."""
        network = HyperbionNetwork()

        # Create coherent cluster
        cells = [network.add_cell(state=1) for _ in range(3)]

        # Connect cells
        for i in range(len(cells)):
            for j in range(len(cells)):
                if i != j:
                    network.connect_cells(cells[i], cells[j], 0.5)

        # Apply DK
        dk = DoppelkickOperator()
        result = dk.apply(network, cells)

        assert result.success is True
        assert len(result.affected_cells) == 3


class TestSweepOperator:
    """Tests for SW operator."""

    def test_sweep_normalization(self):
        """Test SW operator normalization."""
        network = HyperbionNetwork()

        # Create cells with high weights
        cells = [network.add_cell() for _ in range(3)]

        for i in range(len(cells)):
            for j in range(len(cells)):
                if i != j:
                    network.connect_cells(cells[i], cells[j], 5.0)

        # Apply SW
        sw = SweepOperator()
        result = sw.apply(network, cells)

        assert result.success is True

        # Check weights were reduced
        for cell_id in cells:
            cell = network.cells[cell_id]
            for weight in cell.connections.values():
                assert abs(weight) < 5.0


class TestWormholeOperator:
    """Tests for WT operator."""

    def test_wormhole_creation(self):
        """Test WT operator creating shortcuts."""
        network = HyperbionNetwork()

        # Create distant cells with connection between them
        c0 = network.add_cell()
        c1 = network.add_cell()
        c2 = network.add_cell()

        # Create a path c0 -> c1 -> c2 (distance = 2)
        network.connect_cells(c0, c1, 1.0)
        network.connect_cells(c1, c2, 1.0)

        # Apply WT to create shortcut from c0 to c2
        wt = WormholeOperator(distance_threshold=2)
        result = wt.apply(network, [c0, c2])

        assert result.success is True
        assert c2 in network.cells[c0].wormhole_connections


class TestNullpunktOperator:
    """Tests for Nullpunkt operator."""

    def test_reset_weights(self):
        """Test Nullpunkt resetting weights."""
        network = HyperbionNetwork()

        c0 = network.add_cell()
        c1 = network.add_cell()

        network.connect_cells(c0, c1, 2.0)

        # Apply Nullpunkt
        nullpunkt = NullpunktOperator()
        result = nullpunkt.apply(network, [c0], mode='reset_weights')

        assert result.success is True
        assert len(network.cells[c0].connections) == 0

    def test_reset_state(self):
        """Test Nullpunkt resetting state."""
        network = HyperbionNetwork()

        c0 = network.add_cell(state=1)

        # Apply Nullpunkt
        nullpunkt = NullpunktOperator()
        result = nullpunkt.apply(network, [c0], mode='reset_state')

        assert result.success is True
        assert network.cells[c0].state == 0

    def test_delete_cell(self):
        """Test Nullpunkt deleting cells."""
        network = HyperbionNetwork()

        c0 = network.add_cell()

        # Apply Nullpunkt
        nullpunkt = NullpunktOperator()
        result = nullpunkt.apply(network, [c0], mode='delete_cell')

        assert result.success is True
        assert c0 not in network.cells


class TestMorphogenesisOperator:
    """Tests for MOR operator."""

    def test_cell_division(self):
        """Test MOR cell division."""
        network = HyperbionNetwork()

        c0 = network.add_cell(state=1)
        initial_size = len(network.cells)

        # Apply MOR
        mor = MorphogenesisOperator()
        result = mor.apply(network, [c0], mode='divide')

        assert result.success is True
        assert len(network.cells) == initial_size + 1

    def test_cell_fusion(self):
        """Test MOR cell fusion."""
        network = HyperbionNetwork()

        # Create enough cells to exceed min_network_size (default 10)
        cells = [network.add_cell() for _ in range(12)]
        c0, c1 = cells[0], cells[1]

        initial_size = len(network.cells)

        # Apply MOR with reduced min_network_size for test
        mor = MorphogenesisOperator(min_network_size=5)
        result = mor.apply(network, [c0, c1], mode='fuse')

        assert result.success is True
        assert len(network.cells) == initial_size - 1

    def test_cell_spawn(self):
        """Test MOR spawning new cells."""
        network = HyperbionNetwork()

        initial_size = len(network.cells)

        # Apply MOR
        mor = MorphogenesisOperator()
        result = mor.apply(network, [], mode='spawn', initial_state=1)

        assert result.success is True
        assert len(network.cells) == initial_size + 1


class TestOperatorIntegration:
    """Integration tests for operator chains."""

    def test_operator_chain(self):
        """Test applying multiple operators in sequence."""
        network = HyperbionNetwork()

        # Create network
        cells = [network.add_cell(state=1) for _ in range(5)]

        for i in range(len(cells) - 1):
            network.connect_cells(cells[i], cells[i + 1], 1.0)

        # Apply operator chain
        network.apply_operator('DK', cells)
        network.apply_operator('SW', cells)

        assert len(network.operator_history) == 2

    def test_auto_trigger(self):
        """Test automatic operator triggering."""
        network = HyperbionNetwork()

        # Create coherent cluster
        cells = [network.add_cell(state=1) for _ in range(5)]

        for i in range(len(cells)):
            for j in range(len(cells)):
                if i != j:
                    network.connect_cells(cells[i], cells[j], 1.0)

        # Create cluster
        network.create_cluster(cells)

        # Run with auto-trigger
        network.step(auto_trigger_operators=True)

        # Check if any operators were triggered
        # (May or may not trigger depending on conditions)
        assert network.step_count == 1
