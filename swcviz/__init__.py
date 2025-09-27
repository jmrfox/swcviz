"""swcviz package scaffolding.

  Public API is evolving; currently exposes SWC parsing utilities.
  """

from .io import SWCRecord, SWCParseResult, parse_swc
from .model import SWCModel

__all__ = [
    "SWCRecord",
    "SWCParseResult",
    "parse_swc",
    "SWCModel",
]
