import pytest

from capital_reconcile.show import interval_label, pressure_interval, render


def test_sparse_pressure_retains_uncertainty_and_does_not_assert_hardware_cause():
    low, high = pressure_interval(1, 2)
    assert low == pytest.approx(0.0945312, abs=1e-6)
    assert high == pytest.approx(0.9054688, abs=1e-6)
    events = [{"region": "r", "rate_limit_hit": True}, {"region": "r", "rate_limit_hit": False}]
    output = render({}, events, "synthetic")
    row = next(line for line in output.splitlines() if line.startswith("r "))
    assert "9%-91%" in row
    assert (
        "Observed service pressure; physical-supply attribution ABSTAIN "
        "pending independent evidence." in output
    )
    for phrase in ("foundry", "hbm", "capacity signal", "upweight", "public earnings"):
        assert phrase not in output.lower()
    assert "95% Wilson" in output


def test_zero_hits_does_not_prove_zero_pressure():
    low, high = pressure_interval(0, 10)
    assert low == pytest.approx(0, abs=1e-12)
    assert 0.27 < high < 0.28
    assert pressure_interval(0, 0) == (0, 1)
    with pytest.raises(ValueError):
        pressure_interval(3, 2)


@pytest.mark.parametrize("hits,calls", [(0, float("nan")), (0.5, 2), (False, 2)])
def test_pressure_interval_requires_integer_counts(hits, calls):
    with pytest.raises(ValueError, match="integer"):
        pressure_interval(hits, calls)


def test_interval_label_rounds_to_percent_range():
    assert interval_label(pressure_interval(1, 2)) == "9%-91%"
    assert interval_label((0.0, 0.7934)) == "0%-79%"


def test_streamlit_app_uses_shared_interval_label():
    import ast
    from pathlib import Path

    app = Path(__file__).resolve().parents[1] / "streamlit_app.py"
    tree = ast.parse(app.read_text())
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module == "capital_reconcile.show"
        for alias in node.names
    }
    assert "interval_label" in imported
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "interval_label"
    ]
    assert len(calls) >= 2  # synthetic-sample table and uploaded-telemetry table
