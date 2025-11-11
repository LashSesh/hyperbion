"""
Unit tests for Quadrupole Tripolar Network components
"""

import pytest
import numpy as np

from hyperbion.quadrupole import (
    TripolarGabrielCell,
    TripolarLogicState,
    QuadrupoleNetwork,
    GlobalPhase,
    QuadrantSelector,
    HolisticMirrorState,
    ClusterSignature,
    CommunicationLayer
)


class TestTripolarGabrielCell:
    """Tests for Tripolar Gabriel Cell."""

    def test_initialization(self):
        """Test cell initialization."""
        cell = TripolarGabrielCell(
            cell_id=1,
            cluster_id=0,
            initial_x=0.5,
            tau_0=0.3,
            tau_1=0.7
        )

        assert cell.id == 1
        assert cell.cluster_id == 0
        assert cell.x == 0.5
        assert cell.tau_0 == 0.3
        assert cell.tau_1 == 0.7

    def test_logic_evaluation(self):
        """Test tripolar logic evaluation."""
        # L0 state
        cell_l0 = TripolarGabrielCell(1, 0, initial_x=0.2, tau_0=0.3, tau_1=0.7)
        assert cell_l0.logic_state == TripolarLogicState.L0

        # L1 state
        cell_l1 = TripolarGabrielCell(2, 0, initial_x=0.8, tau_0=0.3, tau_1=0.7)
        assert cell_l1.logic_state == TripolarLogicState.L1

        # LD state
        cell_ld = TripolarGabrielCell(3, 0, initial_x=0.5, tau_0=0.3, tau_1=0.7)
        assert cell_ld.logic_state == TripolarLogicState.LD

    def test_emission(self):
        """Test emission computation."""
        # L0: suppressed
        cell_l0 = TripolarGabrielCell(1, 0, initial_x=0.2, tau_0=0.3, tau_1=0.7)
        assert cell_l0.compute_emission() == 0.0

        # L1: forward
        cell_l1 = TripolarGabrielCell(2, 0, initial_x=0.8, tau_0=0.3, tau_1=0.7)
        assert cell_l1.compute_emission() == 0.8

        # LD: modulated
        cell_ld = TripolarGabrielCell(3, 0, initial_x=0.5, tau_0=0.3, tau_1=0.7)
        emission = cell_ld.compute_emission()
        assert 0.0 <= emission <= 1.0

    def test_state_update(self):
        """Test state update."""
        cell = TripolarGabrielCell(1, 0, initial_x=0.5)

        initial_x = cell.x
        neighbor_states = {}

        new_x = cell.update_state(neighbor_states, external_input=0.5)

        assert 0.0 <= new_x <= 1.0
        assert new_x != initial_x
        assert cell.age == 1

    def test_mirror_coupling(self):
        """Test LD coupling to mirror state."""
        cell = TripolarGabrielCell(1, 0, initial_x=0.5, tau_0=0.3, tau_1=0.7)
        assert cell.logic_state == TripolarLogicState.LD

        # Update with mirror state
        mirror_value = 0.7
        new_x = cell.update_state(
            neighbor_states={},
            mirror_state=mirror_value
        )

        # Should be influenced by mirror state
        assert new_x != 0.5

    def test_hebbian_learning(self):
        """Test tripolar Hebbian learning."""
        cell1 = TripolarGabrielCell(1, 0, initial_x=0.8)  # L1
        cell2 = TripolarGabrielCell(2, 0, initial_x=0.8)  # L1

        cell1.connect(2, 1.0)

        neighbor_logic = {2: TripolarLogicState.L1}
        neighbor_x = {2: 0.8}

        changes = cell1.apply_hebbian_learning(neighbor_logic, neighbor_x)

        assert 2 in changes
        # Both active -> strengthen
        assert changes[2] > 0

    def test_serialization(self):
        """Test to_dict and from_dict."""
        cell = TripolarGabrielCell(1, 0, initial_x=0.5)
        cell.connect(2, 1.5)

        data = cell.to_dict()
        cell2 = TripolarGabrielCell.from_dict(data)

        assert cell2.id == cell.id
        assert cell2.x == cell.x
        assert cell2.connections == cell.connections


class TestGlobalPhase:
    """Tests for GlobalPhase."""

    def test_initialization(self):
        """Test phase initialization."""
        phase = GlobalPhase(initial_phase=0.0, delta=0.1)

        assert phase.theta == 0.0
        assert phase.delta == 0.1
        assert phase.step_count == 0

    def test_phase_advancement(self):
        """Test phase stepping."""
        phase = GlobalPhase(initial_phase=0.0, delta=0.1)

        new_theta = phase.step()

        assert new_theta == 0.1
        assert phase.theta == 0.1
        assert phase.step_count == 1

    def test_phase_wrapping(self):
        """Test phase wraps at 1.0."""
        phase = GlobalPhase(initial_phase=0.95, delta=0.1)

        phase.step()

        assert 0.0 <= phase.theta < 1.0
        assert phase.theta == pytest.approx(0.05)

    def test_quadrant_detection(self):
        """Test quadrant detection."""
        phase = GlobalPhase(initial_phase=0.0)

        assert phase.get_active_quadrant() == 0

        phase.theta = 0.3
        assert phase.get_active_quadrant() == 1

        phase.theta = 0.6
        assert phase.get_active_quadrant() == 2

        phase.theta = 0.8
        assert phase.get_active_quadrant() == 3

    def test_cycle_detection(self):
        """Test cycle completion detection."""
        phase = GlobalPhase(initial_phase=0.0, delta=0.3)

        # Should not detect cycle initially
        assert not phase.has_completed_cycle()

        # Step through quadrants
        for _ in range(4):
            phase.step()

        # Should detect when entering Q0 from Q3
        assert phase.has_completed_cycle()


class TestQuadrantSelector:
    """Tests for QuadrantSelector."""

    def test_resonance_gates(self):
        """Test resonance gate computation."""
        phase = GlobalPhase(initial_phase=0.1)  # Q0
        selector = QuadrantSelector(phase)

        gates = selector.get_resonance_gates()

        assert gates[0] == True
        assert gates[1] == False
        assert gates[2] == False
        assert gates[3] == False

    def test_can_cluster_emit(self):
        """Test cluster emission check."""
        phase = GlobalPhase(initial_phase=0.4)  # Q1
        selector = QuadrantSelector(phase)

        assert not selector.can_cluster_emit(0)
        assert selector.can_cluster_emit(1)
        assert not selector.can_cluster_emit(2)
        assert not selector.can_cluster_emit(3)


class TestHolisticMirrorState:
    """Tests for HolisticMirrorState."""

    def test_cluster_signature(self):
        """Test cluster signature creation."""
        cells = [
            TripolarGabrielCell(1, 0, initial_x=0.2),  # L0
            TripolarGabrielCell(2, 0, initial_x=0.8),  # L1
            TripolarGabrielCell(3, 0, initial_x=0.5),  # LD
        ]

        signature = ClusterSignature(0, cells)

        assert signature.cluster_id == 0
        assert signature.l0_count == 1
        assert signature.l1_count == 1
        assert signature.ld_count == 1
        assert signature.total_cells == 3

    def test_mirror_state_computation(self):
        """Test mirror state computation."""
        mirror = HolisticMirrorState()

        # Create signatures for all 4 clusters
        for k in range(4):
            cells = [TripolarGabrielCell(i, k, initial_x=0.5) for i in range(5)]
            mirror.update_cluster_signature(k, cells, timestamp=0)

        # Should be able to compute
        assert mirror.can_compute_mirror_state()

        h_value = mirror.compute_mirror_state()

        assert 0.0 <= h_value <= 1.0
        assert mirror.computation_count == 1

    def test_coherence_metric(self):
        """Test coherence calculation."""
        mirror = HolisticMirrorState()

        # Create similar signatures (high coherence)
        for k in range(4):
            cells = [TripolarGabrielCell(i, k, initial_x=0.5) for i in range(5)]
            mirror.update_cluster_signature(k, cells, timestamp=0)

        coherence = mirror.get_coherence_metric()

        assert 0.0 <= coherence <= 1.0


class TestCommunicationLayer:
    """Tests for CommunicationLayer."""

    def test_packet_encoding_decoding(self):
        """Test packet encode/decode cycle."""
        comm = CommunicationLayer()

        # Create signature
        cells = [TripolarGabrielCell(i, 0, initial_x=0.5) for i in range(5)]
        signature = ClusterSignature(0, cells)

        # Encode
        packet = comm.encode_cluster_packet(signature, phase=0.1)

        assert packet is not None
        assert len(packet) == comm.operators.transport_dim

        # Decode
        decoded = comm.decode_cluster_packet(packet, phase=0.1)

        assert decoded is not None
        assert len(decoded) == comm.operators.signature_dim

    def test_transmission(self):
        """Test packet transmission."""
        comm = CommunicationLayer()

        cells = [TripolarGabrielCell(i, 0) for i in range(5)]
        signature = ClusterSignature(0, cells)

        # Transmit
        comm.transmit_from_cluster(0, signature, phase=0.1)

        assert comm.packets[0] is not None
        assert comm.transmission_count == 1

    def test_reception(self):
        """Test packet reception."""
        comm = CommunicationLayer()

        cells = [TripolarGabrielCell(i, 0) for i in range(5)]
        signature = ClusterSignature(0, cells)

        # Transmit from cluster 0
        comm.transmit_from_cluster(0, signature, phase=0.1)

        # Receive at cluster 1
        decoded = comm.receive_at_cluster(1, source_cluster=0, phase=0.1)

        assert decoded is not None


class TestQuadrupoleNetwork:
    """Tests for QuadrupoleNetwork."""

    def test_initialization(self):
        """Test network initialization."""
        network = QuadrupoleNetwork()

        assert network.name == "QuadrupoleNetwork"
        assert len(network.clusters) == 4
        assert network.step_count == 0
        assert network.cycle_count == 0

    def test_add_cell(self):
        """Test adding cells."""
        network = QuadrupoleNetwork()

        cell_id = network.add_cell(cluster_id=0)

        assert cell_id == 0
        assert 0 in network.clusters[0]

    def test_connect_cells(self):
        """Test connecting cells."""
        network = QuadrupoleNetwork()

        c1 = network.add_cell(cluster_id=0)
        c2 = network.add_cell(cluster_id=1)

        success = network.connect_cells(c1, c2, weight=1.5)

        assert success
        assert c2 in network.clusters[0][c1].connections

    def test_step_execution(self):
        """Test network step."""
        network = QuadrupoleNetwork()

        # Add cells
        for k in range(4):
            for _ in range(5):
                network.add_cell(cluster_id=k)

        # Execute step
        result = network.step()

        assert result['step'] == 1
        assert 0 <= result['active_quadrant'] <= 3
        assert 'phase' in result

    def test_cycle_completion(self):
        """Test cycle completion."""
        network = QuadrupoleNetwork(phase_delta=0.3)

        # Add cells
        for k in range(4):
            for _ in range(3):
                network.add_cell(cluster_id=k)

        # Run until cycle completes
        for _ in range(10):
            network.step()

        # Should have completed at least one cycle
        assert network.cycle_count > 0

    def test_cluster_statistics(self):
        """Test cluster statistics."""
        network = QuadrupoleNetwork()

        # Add cells
        for _ in range(5):
            network.add_cell(cluster_id=0)

        stats = network.get_cluster_statistics()

        assert 0 in stats
        assert stats[0]['size'] == 5

    def test_get_state(self):
        """Test state retrieval."""
        network = QuadrupoleNetwork()

        network.add_cell(cluster_id=0)
        network.add_cell(cluster_id=1)

        state = network.get_state()

        assert 'name' in state
        assert 'step_count' in state
        assert 'phase' in state
        assert 'mirror_state' in state
        assert 'cluster_stats' in state
