# swcviz — 3D Visualization of SWC Neuronal Morphologies

swcviz is a Python package for loading, analyzing, and visualizing neuronal morphologies stored in the SWC format. It is designed for interactive use in Jupyter notebooks and leverages Plotly for 3D visualization and NetworkX for graph-based topology.

Status: pre-alpha, actively evolving. Core parsing, models, geometry, and basic visualization are implemented.

Docs: [https://jmrfox.github.io/swcviz/](https://jmrfox.github.io/swcviz/)

Demo notebooks can be found in the `notebooks` directory.

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

## Design overview

- `SWCModel` (`networkx.DiGraph`)
  - Nodes keyed by SWC id `n`
  - Node attributes: `x`, `y`, `z`, `r`, `t` (type), and optional metadata
- `GeneralModel` (`networkx.Graph`)
  - Built from `SWCParseResult` with header-based reconnection merges
  - Node attributes preserved; provenance includes `merged_ids`, `lines`
- `Segment` dataclass and `FrustaSet` (batched frusta mesh)
- Visualization functions in `viz.py`: `plot_centroid`, `plot_frusta`

- Use in Jupyter:
  - Launch a notebook and import `swcviz`
  - Load or paste an SWC and use `GeneralModel`, `FrustaSet`, `plot_centroid`, `plot_frusta`

## Acknowledgements

- Community conventions around SWC and tools in the ecosystem
- NetworkX and Plotly for the backbone of graph analysis and 3D visualization
