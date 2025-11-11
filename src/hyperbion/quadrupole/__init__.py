"""
Quadrupole Tripolar Neural Network
===================================

Evolution of the Hyperbion system with:
- Quadrupole architecture (4 resonant clusters)
- Rotating phase space Θ(t)
- Holistic mirror state H(t) as third oscillating mode LD
- Quantum-hybrid communication layer

Based on the Blueprint by Sebastian Klemm.
"""

from .tripolar_cell import TripolarGabrielCell, TripolarLogicState
from .quadrupole_network import QuadrupoleNetwork
from .phase_system import GlobalPhase, QuadrantSelector
from .mirror_state import HolisticMirrorState
from .communication import CommunicationLayer, SignatureOperators

__all__ = [
    "TripolarGabrielCell",
    "TripolarLogicState",
    "QuadrupoleNetwork",
    "GlobalPhase",
    "QuadrantSelector",
    "HolisticMirrorState",
    "CommunicationLayer",
    "SignatureOperators",
]
