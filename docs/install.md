# Installation

This page describes how to install swcviz from GitHub and how to set up a development environment.

## Requirements

- Python >= 3.12 (per `pyproject.toml`)
- OS: Windows/macOS/Linux

## Install from GitHub (latest main)

```bash
pip install "git+https://github.com/jmrfox/swcviz.git"
```

## Development setup with uv

```bash
# Create and activate a virtual environment
uv venv

# Editable install with dev extras (linting, tests, docs)
uv pip install -e .[dev]

# Run tests
uv run pytest -q

# Serve documentation locally (MkDocs)
uv run mkdocs serve
```

## Jupyter usage

If you plan to use notebooks, ensure a kernel is available in your env. One option:

```bash
pip install ipykernel
python -m ipykernel install --user --name swcviz --display-name "Python (swcviz)"
```

Then in a notebook:

```python
from swcviz import parse_swc, GeneralModel, FrustaSet, plot_centroid, plot_frusta
```

## Uninstall

```bash
pip uninstall swcviz
```
