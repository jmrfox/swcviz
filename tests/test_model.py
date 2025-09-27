from pathlib import Path
import pytest

from swcviz import parse_swc, SWCParseResult, SWCRecord, SWCModel


def test_build_from_parse_result_basic():
    swc = """
# Simple SWC
1 1 0 0 0 1 -1
2 3 1 0 0 0.5 1
3 3 2 0 0 0.4 2
""".strip()
    result = parse_swc(swc)
    m = SWCModel.from_parse_result(result)

    assert set(m.nodes) == {1, 2, 3}
    # Edges parent -> child
    assert m.has_edge(1, 2)
    assert m.has_edge(2, 3)
    # Roots and queries
    assert m.roots() == [1]
    assert m.parent_of(2) == 1
    assert m.path_to_root(3) == [3, 2, 1]


def test_from_records_iterable():
    # Build records manually to exercise iterable path
    lines = [
        "1 1 0 0 0 1 -1",
        "2 3 1 0 0 0.5 1",
    ]
    result = parse_swc(lines)
    recs = list(result.records.values())
    m = SWCModel.from_records(recs)
    assert set(m.nodes) == {1, 2}
    assert m.has_edge(1, 2)
    assert m.roots() == [1]


def test_from_swc_path(tmp_path: Path):
    p = tmp_path / "tmp_model.swc"
    p.write_text(
        """
# header
1 1 0 0 0 1 -1
2 3 2 0 0 0.5 1
3 3 4 0 0 0.4 2
""".strip()
    )
    m = SWCModel.from_swc(p)
    assert set(m.nodes) == {1, 2, 3}
    assert m.roots() == [1]
    assert m.path_to_root(2) == [2, 1]


def test_optional_data_directory_models_if_present():
    # Optional scan mirroring test_io; skip if data/swc absent
    repo_root = Path(__file__).resolve().parents[1]
    data_dir = repo_root / "data" / "swc"
    if not data_dir.exists():
        pytest.skip("data/swc not present")
    files = list(data_dir.glob("*.swc"))
    if not files:
        pytest.skip("no .swc files found in data/swc")

    for swc_path in files:
        # Be lenient about reconnection validation for arbitrary examples
        m = SWCModel.from_swc(swc_path, strict=True, validate_reconnections=False)
        assert isinstance(m, SWCModel)
        assert m.number_of_nodes() > 0
        # Every non-root should have in-degree 1
        for n in m.nodes:
            indeg = m.in_degree(n)
            if n in set(m.roots()):
                assert indeg == 0
            else:
                assert indeg == 1
