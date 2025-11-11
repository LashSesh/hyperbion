"""
Hyperbion Tripolar Neural Network
==================================

A self-organizing, structurally plastic neural network based on tripolar logic,
Gabriel cells, and dynamic operators.

Author: Sebastian Klemm
Version: Delta-Blueprint-1.0
"""

__version__ = "1.0.0"
__author__ = "Sebastian Klemm"

from .core.gabriel_cell import GabrielCell
from .core.network import HyperbionNetwork
from .operators.base import Operator
from .operators.doppelkick import DoppelkickOperator
from .operators.sweep import SweepOperator
from .operators.wormhole import WormholeOperator
from .operators.nullpunkt import NullpunktOperator
from .operators.morphogenesis import MorphogenesisOperator

__all__ = [
    "GabrielCell",
    "HyperbionNetwork",
    "Operator",
    "DoppelkickOperator",
    "SweepOperator",
    "WormholeOperator",
    "NullpunktOperator",
    "MorphogenesisOperator",
]
