"""SWC graph data model.

  SWCModel is a directed graph (forest) where nodes are SWC points and
  edges are directed from parent -> child according to the SWC format.

  Notes
  -----
  - Use `SWCModel` for topology and attribute management of parsed SWC.
  - Visualization should operate on a separate undirected `GeneralModel`
    that may perform reconnection merges; see project TODOs.
  """

from __future__ import annotations

from typing import Iterable, Mapping
import os
import networkx as nx

from .io import SWCRecord, SWCParseResult, parse_swc


class SWCModel(nx.DiGraph):
    """Directed SWC morphology graph.

    Nodes are keyed by SWC id `n` and store attributes:
    - t: int (structure type)
    - x, y, z: float (coordinates)
    - r: float (radius)
    - line: int (line number in source; informational)

    Edges are directed parent -> child.
    """

    def __init__(self) -> None:
        # Initialize as a plain DiGraph; we don't need multigraph features.
        super().__init__()

    # ----------------------------------------------------------------------------------------------
    # Construction helpers
    # ----------------------------------------------------------------------------------------------
    @classmethod
    def from_parse_result(cls, result: SWCParseResult) -> "SWCModel":
        """Build a model from a parsed SWC result."""
        return cls.from_records(result.records)

    @classmethod
    def from_records(
        cls, records: Mapping[int, SWCRecord] | Iterable[SWCRecord]
    ) -> "SWCModel":
        """Build a model from SWC records.

        Accepts either a mapping of id->record or any iterable of SWCRecord.
        """
        model = cls()

        # Materialize to a list once so we can iterate twice safely
        if isinstance(records, Mapping):
            rec_values = list(records.values())
        else:
            rec_values = list(records)

        # First pass: add all nodes with attributes
        for rec in rec_values:
            model.add_node(
                rec.n,
                t=rec.t,
                x=rec.x,
                y=rec.y,
                z=rec.z,
                r=rec.r,
                line=rec.line,
            )

        # Second pass: add edges parent -> child
        for rec in rec_values:
            if rec.parent != -1:
                model.add_edge(rec.parent, rec.n)

        return model

    @classmethod
    def from_swc(
        cls,
        source: str | os.PathLike[str] | Iterable[str],
        *,
        strict: bool = True,
        validate_reconnections: bool = True,
        float_tol: float = 1e-9,
    ) -> "SWCModel":
        """Parse an SWC source then build a model.

        The `source` is passed through to `parse_swc`, which supports a path,
        a file-like object, a string with the full contents, or an iterable of lines.
        """
        result = parse_swc(
            source,
            strict=strict,
            validate_reconnections=validate_reconnections,
            float_tol=float_tol,
        )
        return cls.from_parse_result(result)

    # ----------------------------------------------------------------------------------------------
    # Convenience queries
    # ----------------------------------------------------------------------------------------------
    def roots(self) -> list[int]:
        """Return nodes with in-degree 0 (forest roots)."""
        return [n for n, deg in self.in_degree() if deg == 0]

    def parent_of(self, n: int) -> int | None:
        """Return the parent id of node n, or None if n is a root.

        SWC trees should have at most one parent per node; if multiple are found
        this indicates invalid structure for SWC and an error is raised.
        """
        preds = list(self.predecessors(n))
        if not preds:
            return None
        if len(preds) > 1:
            raise ValueError(
                f"Node {n} has multiple parents in SWCModel; expected a tree/forest"
            )
        return preds[0]

    def path_to_root(self, n: int) -> list[int]:
        """Return the path from node n up to its root, inclusive.

        Example: For edges 1->2->3, `path_to_root(3)` returns `[3, 2, 1]`.
        """
        path: list[int] = [n]
        current = n
        while True:
            p = self.parent_of(current)
            if p is None:
                break
            path.append(p)
            current = p
        return path
