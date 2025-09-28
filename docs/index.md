# swcviz

Jupyter-first 3D visualization of SWC neuronal morphologies using NetworkX and Plotly.

- Parse SWC into directed `SWCModel` and undirected `GeneralModel`
- Visualize skeletons (centroid) with `plot_centroid`
- Build volumetric frusta meshes with `FrustaSet` and `plot_frusta`

## Quick start

```python
from swcviz import parse_swc, GeneralModel, FrustaSet, plot_centroid, plot_frusta

swc = """
# CYCLE_BREAK reconnect 2 3
1 1 0 0 0 1 -1
2 3 2 0 0 0.5 1
3 3 2 0 0 0.5 1
4 3 3 0 0 0.4 2
""".strip()

gm = GeneralModel.from_swc_file(swc, strict=True, validate_reconnections=True)
fig1 = plot_centroid(gm, show_nodes=True)
fr = FrustaSet.from_general_model(gm, sides=20, end_caps=False)
fig2 = plot_frusta(fr)
```

See the API reference for details.
