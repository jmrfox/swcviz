"""Visualization helpers for swcviz.

- plot_centroid: skeleton plotting from GeneralModel using Scatter3d
- plot_frusta: volumetric frusta plotting from FrustaSet using Mesh3d
"""

from __future__ import annotations

from typing import Optional, Sequence

import plotly.graph_objects as go

from .geometry import FrustaSet


def plot_centroid(gm, *, marker_size: float = 2.0, line_width: float = 2.0, show_nodes: bool = True) -> go.Figure:
    """Plot centroid skeleton from a GeneralModel.

    Edges are drawn as line segments in 3D using Scatter3d.
    """
    xs = []
    ys = []
    zs = []

    # Build polyline segments with None separators for Plotly
    for u, v in gm.edges:
        xs.extend([gm.nodes[u]["x"], gm.nodes[v]["x"], None])
        ys.extend([gm.nodes[u]["y"], gm.nodes[v]["y"], None])
        zs.extend([gm.nodes[u]["z"], gm.nodes[v]["z"], None])

    edge_trace = go.Scatter3d(
        x=xs,
        y=ys,
        z=zs,
        mode="lines",
        line=dict(width=line_width, color="#1f77b4"),
        name="edges",
    )

    data = [edge_trace]

    if show_nodes:
        xn = [gm.nodes[n]["x"] for n in gm.nodes]
        yn = [gm.nodes[n]["y"] for n in gm.nodes]
        zn = [gm.nodes[n]["z"] for n in gm.nodes]
        node_trace = go.Scatter3d(
            x=xn,
            y=yn,
            z=zn,
            mode="markers",
            marker=dict(size=marker_size, color="#ff7f0e"),
            name="nodes",
        )
        data.append(node_trace)

    fig = go.Figure(data=data)
    fig.update_layout(scene_aspectmode="data", title="Centroid Skeleton")
    return fig


def plot_frusta(frusta: FrustaSet, *, color: str = "lightblue", opacity: float = 0.8, flatshading: bool = True) -> go.Figure:
    """Plot a FrustaSet as a Mesh3d figure."""
    x, y, z, i, j, k = frusta.to_mesh3d_arrays()
    mesh = go.Mesh3d(
        x=x,
        y=y,
        z=z,
        i=i,
        j=j,
        k=k,
        color=color,
        opacity=opacity,
        flatshading=flatshading,
    )
    fig = go.Figure(data=[mesh])
    fig.update_layout(scene_aspectmode="data", title="Frusta Mesh")
    return fig
