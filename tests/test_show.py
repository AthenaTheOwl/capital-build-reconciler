from __future__ import annotations

from pathlib import Path

from capital_reconcile.cli import main
from capital_reconcile.show import region_rows, render, show

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


def test_region_rows_ranks_by_rate_limit_pressure() -> None:
    events = [
        {"region": "us-east-1", "rate_limit_hit": True, "cost_usd": 0.0, "latency_ms": 120, "model": "m"},
        {"region": "us-east-1", "rate_limit_hit": False, "cost_usd": 0.02, "latency_ms": 840, "model": "m"},
        {"region": "us-west-2", "rate_limit_hit": False, "cost_usd": 0.004, "latency_ms": 600, "model": "m"},
    ]
    rows = region_rows(events)
    assert [r["region"] for r in rows] == ["us-east-1", "us-west-2"]
    east = rows[0]
    assert east["calls"] == 2
    assert east["rate_limit_hits"] == 1
    assert east["rl_pressure"] == 0.5
    assert east["avg_latency_ms"] == 480


def test_render_emits_headline_when_rate_limited() -> None:
    summary = {"month": "2026-06", "provider": "anthropic", "records": 2, "rate_limit_hits": 1}
    events = [
        {"region": "us-east-1", "rate_limit_hit": True, "cost_usd": 0.0, "latency_ms": 120, "model": "m"},
        {"region": "us-west-2", "rate_limit_hit": False, "cost_usd": 0.004, "latency_ms": 600, "model": "m"},
    ]
    out = render(summary, events, "2026-M06-ingest-summary")
    assert "rate-limit pressure" in out
    assert "headline:" in out
    assert "us-east-1" in out


def test_render_headline_when_no_rate_limits() -> None:
    summary = {"month": "2026-06", "provider": "anthropic", "records": 1, "rate_limit_hits": 0}
    events = [{"region": "us-west-2", "rate_limit_hit": False, "cost_usd": 0.004, "latency_ms": 600, "model": "m"}]
    out = render(summary, events, "stem")
    assert "no rate-limit hits" in out
    assert "HOLD" in out


def test_show_reads_committed_artifacts(capsys) -> None:
    rc = show(REPORTS)
    assert rc == 0
    out = capsys.readouterr().out
    assert "capital-build-reconciler" in out
    assert "us-east-1" in out
    assert "headline:" in out


def test_show_verb_via_cli_exits_zero(capsys) -> None:
    rc = main(["show"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "ranked by rate-limit pressure" in out


def test_show_missing_reports_returns_one(tmp_path: Path, capsys) -> None:
    rc = show(tmp_path)
    assert rc == 1
    assert "no ingest summary" in capsys.readouterr().out
