"""swcviz package scaffolding.

Public API is evolving; currently exposes SWC parsing utilities and models.
"""

from .io import SWCRecord, SWCParseResult, parse_swc
from .model import SWCModel, GeneralModel
from .geometry import Segment, frustum_mesh, batch_frusta, FrustaSet
from .viz import plot_centroid, plot_frusta

__all__ = [
    "SWCRecord",
    "SWCParseResult",
    "parse_swc",
    "SWCModel",
    "GeneralModel",
    "Segment",
    "frustum_mesh",
    "batch_frusta",
    "FrustaSet",
    "plot_centroid",
    "plot_frusta",
]
