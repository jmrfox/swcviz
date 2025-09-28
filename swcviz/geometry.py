"""Geometry utilities for segment/frustum mesh generation.

- Segment: oriented frustum defined by two points with radii
- frustum_mesh: build vertices/faces for a single frustum
- batch_frusta: combine multiple frusta into one mesh

Implementation is pure-Python (standard library math), returning lists
of vertices and triangular faces suitable for Plotly Mesh3d or other
renderers after light conversion.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple, Any
import math

# Types
Point3 = Tuple[float, float, float]
Vec3 = Tuple[float, float, float]
Face = Tuple[int, int, int]


# --------------------------------------------------------------------------------------
# Vector helpers (pure Python)
# --------------------------------------------------------------------------------------

def v_add(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def v_sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def v_mul(a: Vec3, s: float) -> Vec3:
    return (a[0] * s, a[1] * s, a[2] * s)


def v_dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def v_cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def v_norm(a: Vec3) -> float:
    return math.sqrt(v_dot(a, a))


def v_unit(a: Vec3, eps: float = 1e-12) -> Vec3:
    n = v_norm(a)
    if n < eps:
        return (0.0, 0.0, 0.0)
    return (a[0] / n, a[1] / n, a[2] / n)


# --------------------------------------------------------------------------------------
# Core structures
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Segment:
    """Oriented frustum segment between endpoints `a` and `b`.

    Attributes
    ----------
    a, b: Point3
        Endpoints in model/world coordinates.
    ra, rb: float
        Radii at `a` and `b`.
    """

    a: Point3
    b: Point3
    ra: float
    rb: float

    def vector(self) -> Vec3:
        return v_sub(self.b, self.a)

    def length(self) -> float:
        return v_norm(self.vector())

    def midpoint(self) -> Point3:
        return (self.a[0] * 0.5 + self.b[0] * 0.5, self.a[1] * 0.5 + self.b[1] * 0.5, self.a[2] * 0.5 + self.b[2] * 0.5)


# --------------------------------------------------------------------------------------
# Frames and rings
# --------------------------------------------------------------------------------------


def _orthonormal_frame(z_axis: Vec3) -> Tuple[Vec3, Vec3, Vec3]:
    """Return (U, V, W) forming a right-handed orthonormal basis with W along z_axis.

    Handles near-colinearity by choosing a stable temporary axis.
    """
    W = v_unit(z_axis)
    # Fallback if zero vector
    if W == (0.0, 0.0, 0.0):
        W = (0.0, 0.0, 1.0)

    # Pick a vector not parallel to W
    abs_w = tuple(abs(c) for c in W)
    tmp = (1.0, 0.0, 0.0) if abs_w[0] <= 0.9 else (0.0, 1.0, 0.0)
    U = v_cross(tmp, W)
    U = v_unit(U)
    # If still degenerate (happens when tmp ~ W), switch tmp
    if U == (0.0, 0.0, 0.0):
        tmp = (0.0, 1.0, 0.0)
        U = v_unit(v_cross(tmp, W))
    V = v_cross(W, U)
    return U, V, W


def _circle_ring(center: Point3, radius: float, U: Vec3, V: Vec3, sides: int) -> List[Point3]:
    pts: List[Point3] = []
    for k in range(sides):
        theta = 2.0 * math.pi * (k / sides)
        c = math.cos(theta)
        s = math.sin(theta)
        offset = v_add(v_mul(U, radius * c), v_mul(V, radius * s))
        pts.append(v_add(center, offset))
    return pts


# --------------------------------------------------------------------------------------
# Mesh generation
# --------------------------------------------------------------------------------------


def frustum_mesh(seg: Segment, *, sides: int = 16, end_caps: bool = False) -> Tuple[List[Point3], List[Face]]:
    """Generate a frustum mesh for a single `Segment`.

    Returns
    -------
    (vertices, faces):
        - vertices: List[Point3]
        - faces: List[Face], each = (i, j, k) indexing into `vertices`
    """
    # Local frame
    U, V, W = _orthonormal_frame(seg.vector())

    ring_a = _circle_ring(seg.a, seg.ra, U, V, sides)
    ring_b = _circle_ring(seg.b, seg.rb, U, V, sides)

    vertices: List[Point3] = []
    vertices.extend(ring_a)
    vertices.extend(ring_b)

    faces: List[Face] = []

    # Side faces (two triangles per quad)
    for i in range(sides):
        a0 = i
        a1 = (i + 1) % sides
        b0 = i + sides
        b1 = ((i + 1) % sides) + sides
        faces.append((a0, b0, b1))
        faces.append((a0, b1, a1))

    # Optional end caps
    if end_caps and seg.ra > 0.0:
        ca = len(vertices)
        vertices.append(seg.a)
        for i in range(sides):
            a0 = i
            a1 = (i + 1) % sides
            # Wind towards center for cap
            faces.append((ca, a1, a0))

    if end_caps and seg.rb > 0.0:
        cb = len(vertices)
        vertices.append(seg.b)
        for i in range(sides):
            b0 = i + sides
            b1 = ((i + 1) % sides) + sides
            faces.append((cb, b0, b1))

    return vertices, faces


def batch_frusta(segments: Iterable[Segment], *, sides: int = 16, end_caps: bool = False) -> Tuple[List[Point3], List[Face]]:
    """Batch multiple frusta into a single mesh.

    Returns a concatenated list of `vertices` and `faces` with the proper index offsets.
    """
    all_vertices: List[Point3] = []
    all_faces: List[Face] = []
    offset = 0

    for seg in segments:
        v, f = frustum_mesh(seg, sides=sides, end_caps=end_caps)
        all_vertices.extend(v)
        # Re-index faces
        all_faces.extend([(a + offset, b + offset, c + offset) for (a, b, c) in f])
        offset += len(v)

    return all_vertices, all_faces


# --------------------------------------------------------------------------------------
# Frusta set derived from a GeneralModel
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class FrustaSet:
    """A batched frusta mesh derived from a `GeneralModel`.

    Attributes
    ----------
    vertices: List[Point3]
        Concatenated vertices for all frusta.
    faces: List[Face]
        Triangular faces indexing into `vertices`.
    sides: int
        Circumferential resolution used per frustum.
    end_caps: bool
        Whether end caps were included during construction.
    segment_count: int
        Number of segments used (one per graph edge).
    edge_count: int
        Alias for `segment_count` for clarity.
    """

    vertices: List[Point3]
    faces: List[Face]
    sides: int
    end_caps: bool
    segment_count: int
    edge_count: int

    @classmethod
    def from_general_model(
        cls,
        gm: Any,
        *,
        sides: int = 16,
        end_caps: bool = False,
    ) -> "FrustaSet":
        """Build a `FrustaSet` by converting each undirected edge into a `Segment`.

        Expects nodes to have attributes `x, y, z, r`.
        """
        segments: List[Segment] = []
        for u, v in gm.edges:
            xu, yu, zu = gm.nodes[u]["x"], gm.nodes[u]["y"], gm.nodes[u]["z"]
            xv, yv, zv = gm.nodes[v]["x"], gm.nodes[v]["y"], gm.nodes[v]["z"]
            ru, rv = float(gm.nodes[u]["r"]), float(gm.nodes[v]["r"])
            segments.append(Segment(a=(xu, yu, zu), b=(xv, yv, zv), ra=ru, rb=rv))

        vertices, faces = batch_frusta(segments, sides=sides, end_caps=end_caps)
        return cls(
            vertices=vertices,
            faces=faces,
            sides=sides,
            end_caps=end_caps,
            segment_count=len(segments),
            edge_count=len(segments),
        )

    def to_mesh3d_arrays(self) -> Tuple[List[float], List[float], List[float], List[int], List[int], List[int]]:
        """Return Plotly Mesh3d arrays: x, y, z, i, j, k."""
        x = [p[0] for p in self.vertices]
        y = [p[1] for p in self.vertices]
        z = [p[2] for p in self.vertices]
        i = [f[0] for f in self.faces]
        j = [f[1] for f in self.faces]
        k = [f[2] for f in self.faces]
        return x, y, z, i, j, k

__all__ = [
    "Segment",
    "frustum_mesh",
    "batch_frusta",
    "FrustaSet",
]
