# swcviz — 3D Visualization of SWC Neuronal Morphologies

swcviz is a Python package for loading, analyzing, and visualizing neuronal morphologies stored in the SWC format. It is designed for interactive use in Jupyter notebooks and leverages Plotly for 3D visualization and NetworkX for graph-based topology.

Status: pre-alpha, actively evolving. Core parsing, models, geometry, and basic visualization are implemented.

## Features

- **SWC parser**: `parse_swc()` with robust error messages, header reconnection directives, iterable/file/string sources
- **Data models**:
  - `SWCModel` (`networkx.DiGraph`) for directed parent➔child topology with node attributes (`t, x, y, z, r`)
  - `GeneralModel` (`networkx.Graph`) for visualization; applies `# CYCLE_BREAK reconnect i j` merges (union-find)
  - Shared graph metrics via `_graph_attributes()` and `print_attributes()` helpers
- **Geometry**:
  - `Segment` dataclass and frustum meshing utilities (`frustum_mesh`, `batch_frusta`)
  - `FrustaSet.from_general_model()` to build a batched frusta mesh from a `GeneralModel`
- **Visualization**:
  - `plot_centroid(general_model, ...)` for skeleton plotting (`Scatter3d`)
  - `plot_frusta(frusta_set, ...)` for volumetric frusta rendering (`Mesh3d`)
- Roadmap: time-varying scalars and animations

## Why SWC?

The SWC format is a simple text-based convention widely used for representing neuronal morphologies as trees (or forests) of 3D points. Each point has a type, 3D coordinates, a radius, and a parent pointer. This structure is well-suited for graph analysis and 3D rendering.

An SWC file is a series of lines with either comments or 7 space-separated columns:

```text
# Example SWC header/comment lines start with '#'
# n T x y z r parent
1 1 0.0 0.0 0.0 5.0 -1
2 3 2.0 0.0 0.0 1.0 1
3 3 4.0 0.0 0.0 0.8 2
```

Columns:

- `n`: integer node id (unique within the file)
- `T`: structure type (commonly used codes below)
- `x y z`: coordinates (usually micrometers)
- `r`: radius
- `parent`: id of the parent node; `-1` indicates a root (no parent)

Typical type (T) codes in practice:

- 1: soma
- 3: dendrite
- 4: apical dendrite
- 5: fork point
- 6: end point
- 7: custom
- 0 and 8+ are seen as unspecified or reserved; conventions can vary by dataset

In this project we call the node-only graph (ignoring radii) the “centroid” or skeleton view. The volumetric view uses the radii and connectivity to generate piecewise truncated cones (frusta) connecting parent-child pairs.

Authoritative references:

- [SWC specification (NeuronLand)](http://www.neuronland.org/NLMorphologyConverter/MorphologyFormats/SWC/Spec.html)
- [INCF SWC page](https://www.incf.org/swc)
- [SWC+ extension (optional, future consideration)](https://neuroinformatics.nl/swcPlus/)

## Design overview

- `SWCModel` (`networkx.DiGraph`)
  - Nodes keyed by SWC id `n`
  - Node attributes: `x`, `y`, `z`, `r`, `t` (type), and optional metadata
  - Directed edges from parent ➔ child; supports multiple components (a forest)
- `GeneralModel` (`networkx.Graph`)
  - Built from `SWCParseResult` with header-based reconnection merges
  - Node attributes preserved; provenance includes `merged_ids`, `lines`
- `Segment` dataclass and `FrustaSet` (batched frusta mesh)
- Visualization functions in `viz.py`: `plot_centroid`, `plot_frusta`

## Quick start

```python
from swcviz import (
    parse_swc,
    GeneralModel,
    FrustaSet,
    plot_centroid,
    plot_frusta,
)

swc_text = """
# CYCLE_BREAK reconnect 2 3
1 1 0 0 0 1 -1
2 3 2 0 0 0.5 1
3 3 2 0 0 0.5 1
4 3 3 0 0 0.4 2
""".strip()

# Build visualization graph and inspect
gm = GeneralModel.from_swc_file(swc_text, strict=True, validate_reconnections=True)
gm.print_attributes()

# Centroid (skeleton) plot
fig_centroid = plot_centroid(gm, show_nodes=True)
fig_centroid.show()

# Volumetric frusta plot
fr = FrustaSet.from_general_model(gm, sides=20, end_caps=False)
fig_frusta = plot_frusta(fr, color="lightblue", opacity=0.85)
fig_frusta.show()
```

## Installation

- Install directly from GitHub (latest main):

```bash
pip install "git+https://github.com/jmrfox/swcviz.git"
```

- Or editable install for development:

```bash
uv pip install -e .
```

## Getting started (development)

This project uses the `uv` package manager for Python.

- Create a virtual environment:

```bash
uv venv
```

- Install in editable mode (recommended for development):

```bash
uv pip install -e .
```

- Run tests:

```bash
uv run pytest -q
```

- Use in Jupyter:
  - Launch a notebook and import `swcviz`
  - Load or paste an SWC and use `GeneralModel`, `FrustaSet`, `plot_centroid`, `plot_frusta`

## Documentation

- GitHub Pages (built via MkDocs): [https://jmrfox.github.io/swcviz/](https://jmrfox.github.io/swcviz/)
- Build locally:

```bash
uv run mkdocs serve
```

## Examples (coming soon)

- Basic loading and centroid plotting
- Volumetric rendering of a neuron

## Contributing

Contributions are welcome once the initial scaffold lands. Planned setup includes linting, formatting, and tests via CI.

## Acknowledgements

- Community conventions around SWC and tools in the ecosystem
- NetworkX and Plotly for the backbone of graph analysis and 3D visualization
