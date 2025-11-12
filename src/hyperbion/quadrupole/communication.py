"""
Quantum-Hybrid Communication Layer
===================================

Operator-based communication between clusters with phase encoding.

Communication Operators:
- M: Masking/permutation operator
- V: Vector tunnel/embedding to transport space
- S: Spectral/phase-bound encoding operator

Packet construction:
p_k(t) = S_Θ(V(M(z_k(t))))

Decoding:
z̃_k(t) = M^(-1)(V^(-1)(S_Θ^(-1)(p_k(t))))
"""

from typing import Dict, List, Any, Optional
import numpy as np
from .mirror_state import ClusterSignature


class SignatureOperators:
    """
    Operators for transforming cluster signatures into packets.

    M: Masking/Permutation
    V: Vector embedding
    S: Spectral/phase encoding
    """

    def __init__(
        self,
        signature_dim: int = 8,
        transport_dim: int = 16
    ):
        """
        Initialize signature operators.

        Args:
            signature_dim: Dimension of cluster signature vector
            transport_dim: Dimension of transport space
        """
        self.signature_dim = signature_dim
        self.transport_dim = transport_dim

        # Generate random but fixed transformation matrices
        np.random.seed(42)  # For reproducibility

        # M: Masking/permutation matrix
        self.M = self._generate_permutation_matrix(signature_dim)

        # V: Embedding matrix (signature_dim → transport_dim)
        self.V = np.random.randn(transport_dim, signature_dim)
        self.V /= np.linalg.norm(self.V, axis=0, keepdims=True)

        # V_inv: Pseudo-inverse for decoding
        self.V_inv = np.linalg.pinv(self.V)

    def _generate_permutation_matrix(self, dim: int) -> np.ndarray:
        """Generate permutation matrix."""
        perm = np.random.permutation(dim)
        M = np.zeros((dim, dim))
        for i, j in enumerate(perm):
            M[i, j] = 1.0
        return M

    def apply_M(self, signature: np.ndarray) -> np.ndarray:
        """
        Apply masking/permutation operator M.

        Args:
            signature: Cluster signature vector

        Returns:
            Masked signature
        """
        return self.M @ signature

    def apply_M_inv(self, masked: np.ndarray) -> np.ndarray:
        """
        Apply inverse masking M^(-1).

        Args:
            masked: Masked signature

        Returns:
            Original signature
        """
        return self.M.T @ masked

    def apply_V(self, masked: np.ndarray) -> np.ndarray:
        """
        Apply vector embedding V.

        Args:
            masked: Masked signature

        Returns:
            Embedded vector in transport space
        """
        return self.V @ masked

    def apply_V_inv(self, embedded: np.ndarray) -> np.ndarray:
        """
        Apply inverse embedding V^(-1).

        Args:
            embedded: Embedded vector

        Returns:
            Reconstructed masked signature
        """
        return self.V_inv @ embedded

    def apply_S(
        self,
        embedded: np.ndarray,
        phase: float
    ) -> np.ndarray:
        """
        Apply spectral/phase encoding S_Θ.

        Modulates the embedded vector with global phase.

        Args:
            embedded: Embedded vector
            phase: Global phase Θ(t) ∈ [0,1)

        Returns:
            Phase-encoded packet
        """
        # Phase-dependent modulation
        phase_vector = np.array([
            np.sin(2 * np.pi * (phase + k / self.transport_dim))
            for k in range(self.transport_dim)
        ])

        # Element-wise modulation
        return embedded * (1.0 + 0.5 * phase_vector)

    def apply_S_inv(
        self,
        packet: np.ndarray,
        phase: float
    ) -> np.ndarray:
        """
        Apply inverse spectral encoding S_Θ^(-1).

        Args:
            packet: Phase-encoded packet
            phase: Global phase Θ(t)

        Returns:
            Decoded embedded vector
        """
        # Reverse phase modulation
        phase_vector = np.array([
            np.sin(2 * np.pi * (phase + k / self.transport_dim))
            for k in range(self.transport_dim)
        ])

        return packet / (1.0 + 0.5 * phase_vector + 1e-8)


class CommunicationLayer:
    """
    Quantum-hybrid communication layer for cluster interaction.

    Manages:
    - Packet encoding from cluster signatures
    - Phase-selective transmission
    - Packet decoding for receiving clusters
    - Rotating handoff between quadrants
    """

    def __init__(self):
        """Initialize communication layer."""
        self.operators = SignatureOperators()

        # Packet buffer for each cluster
        self.packets: Dict[int, Optional[np.ndarray]] = {
            0: None,
            1: None,
            2: None,
            3: None
        }

        # Decoded signatures buffer
        self.decoded_signatures: Dict[int, Optional[np.ndarray]] = {
            0: None,
            1: None,
            2: None,
            3: None
        }

        # Communication history
        self.transmission_count = 0
        self.packet_history: List[Dict[str, Any]] = []

    def encode_cluster_packet(
        self,
        cluster_signature: ClusterSignature,
        phase: float
    ) -> np.ndarray:
        """
        Encode cluster signature into communication packet.

        p_k(t) = S_Θ(V(M(z_k(t))))

        Args:
            cluster_signature: Cluster signature Sk(t)
            phase: Global phase Θ(t)

        Returns:
            Encoded packet p_k(t)
        """
        # Get signature vector
        z_k = cluster_signature.to_vector()

        # Apply operators in sequence: M → V → S
        masked = self.operators.apply_M(z_k)
        embedded = self.operators.apply_V(masked)
        packet = self.operators.apply_S(embedded, phase)

        return packet

    def decode_cluster_packet(
        self,
        packet: np.ndarray,
        phase: float
    ) -> np.ndarray:
        """
        Decode communication packet to signature.

        z̃_k(t) = M^(-1)(V^(-1)(S_Θ^(-1)(p_k(t))))

        Args:
            packet: Encoded packet p_k(t)
            phase: Global phase Θ(t)

        Returns:
            Decoded signature z̃_k(t)
        """
        # Apply inverse operators: S^(-1) → V^(-1) → M^(-1)
        embedded = self.operators.apply_S_inv(packet, phase)
        masked = self.operators.apply_V_inv(embedded)
        signature = self.operators.apply_M_inv(masked)

        return signature

    def transmit_from_cluster(
        self,
        cluster_id: int,
        cluster_signature: ClusterSignature,
        phase: float
    ) -> None:
        """
        Transmit packet from active cluster.

        Args:
            cluster_id: Transmitting cluster (0-3)
            cluster_signature: Cluster signature
            phase: Current global phase
        """
        # Encode packet
        packet = self.encode_cluster_packet(cluster_signature, phase)

        # Store in buffer
        self.packets[cluster_id] = packet

        # Record transmission
        self.transmission_count += 1
        self.packet_history.append({
            'cluster_id': cluster_id,
            'phase': phase,
            'timestamp': self.transmission_count,
            'packet_norm': float(np.linalg.norm(packet))
        })

    def receive_at_cluster(
        self,
        cluster_id: int,
        source_cluster: int,
        phase: float
    ) -> Optional[np.ndarray]:
        """
        Receive and decode packet at target cluster.

        Args:
            cluster_id: Receiving cluster
            source_cluster: Source cluster that sent packet
            phase: Current global phase

        Returns:
            Decoded signature or None if no packet available
        """
        # Get packet from source
        packet = self.packets.get(source_cluster)

        if packet is None:
            return None

        # Decode packet
        decoded = self.decode_cluster_packet(packet, phase)

        # Store decoded signature
        self.decoded_signatures[cluster_id] = decoded

        return decoded

    def get_all_available_packets(self) -> Dict[int, np.ndarray]:
        """
        Get all currently available packets.

        Returns:
            {cluster_id: packet} for available packets
        """
        return {
            k: v for k, v in self.packets.items()
            if v is not None
        }

    def rotate_packets(self) -> None:
        """
        Rotate packets for next quadrant.

        Called when phase transitions to new quadrant.
        """
        # Shift packets (optional - depends on architecture choice)
        # For now, keep all packets available
        pass

    def clear_packets(self) -> None:
        """Clear all packet buffers (e.g., after full cycle)."""
        self.packets = {k: None for k in range(4)}
        self.decoded_signatures = {k: None for k in range(4)}

    def get_communication_stats(self) -> Dict[str, Any]:
        """
        Get communication statistics.

        Returns:
            Statistics dictionary
        """
        available_packets = sum(1 for v in self.packets.values() if v is not None)

        return {
            'transmission_count': self.transmission_count,
            'available_packets': available_packets,
            'recent_transmissions': self.packet_history[-10:] if self.packet_history else []
        }

    def __repr__(self) -> str:
        available = sum(1 for v in self.packets.values() if v is not None)
        return (
            f"CommunicationLayer(transmissions={self.transmission_count}, "
            f"packets_available={available})"
        )
