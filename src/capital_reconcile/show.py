"""Readable, ranked view of the committed monthly telemetry.

No args, read-only, offline. Reads the committed ingest summary
(``reports/*-ingest-summary.jsonl``) and the normalized parquet it
summarizes, then prints a per-region table ranked by rate-limit pressure
plus a one-line headline tying the telemetry to the capital thesis: a
region throwing 429s is a capacity signal the public narrative is behind on.
"""

from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq

# repo root is two parents up from src/capital_reconcile/show.py
_REPO_ROOT = Path(__file__).resolve().parents[2]
_REPORTS_DIR = _REPO_ROOT / "reports"


def latest_summary(reports_dir: Path) -> Path | None:
    files = sorted(reports_dir.glob("*-ingest-summary.jsonl"))
    return files[-1] if files else None


def _resolve_parquet(summary: dict, reports_dir: Path) -> Path | None:
    """Pick the parquet that goes with this summary.

    Prefer a sibling ``*.fixture.parquet`` for the same month; otherwise
    fall back to the most recent parquet under reports/.
    """
    month = summary.get("month", "")
    stamp = month.replace("-0", "-M0").replace("-1", "-M1") if month else ""
    for name in (f"{stamp}.fixture.parquet",):
        candidate = reports_dir / name
        if candidate.is_file():
            return candidate
    parquets = sorted(reports_dir.glob("*.parquet"))
    return parquets[-1] if parquets else None


def region_rows(events: list[dict]) -> list[dict]:
    """Collapse per-event telemetry into a per-region view."""
    by_region: dict[str, dict] = {}
    for ev in events:
        region = ev.get("region", "?")
        agg = by_region.setdefault(
            region,
            {
                "region": region,
                "calls": 0,
                "rate_limit_hits": 0,
                "cost_usd": 0.0,
                "latency_ms_total": 0,
                "models": set(),
            },
        )
        agg["calls"] += 1
        agg["rate_limit_hits"] += 1 if ev.get("rate_limit_hit") else 0
        agg["cost_usd"] += float(ev.get("cost_usd", 0.0))
        agg["latency_ms_total"] += int(ev.get("latency_ms", 0))
        agg["models"].add(ev.get("model", "?"))

    rows: list[dict] = []
    for agg in by_region.values():
        calls = agg["calls"] or 1
        rows.append(
            {
                "region": agg["region"],
                "calls": agg["calls"],
                "rate_limit_hits": agg["rate_limit_hits"],
                "rl_pressure": round(agg["rate_limit_hits"] / calls, 3),
                "avg_latency_ms": round(agg["latency_ms_total"] / calls),
                "cost_usd": round(agg["cost_usd"], 6),
                "models": sorted(agg["models"]),
            }
        )
    rows.sort(key=lambda r: (r["rl_pressure"], r["rate_limit_hits"]), reverse=True)
    return rows


def render(summary: dict, events: list[dict], stem: str) -> str:
    rows = region_rows(events)
    lines: list[str] = []
    month = summary.get("month", "?")
    provider = summary.get("provider", "?")
    lines.append(
        f"capital-build-reconciler - {provider} build telemetry, {month} ({stem})"
    )
    lines.append(
        f"{summary.get('records', len(events))} call(s) across "
        f"{len(rows)} region(s), ranked by rate-limit pressure (429s / calls)\n"
    )

    header = (
        f"{'region':<12} {'calls':>5} {'429s':>5} {'rl_pressure':>11} "
        f"{'avg_latency':>11} {'cost_usd':>10}  models"
    )
    lines.append(header)
    lines.append("-" * len(header))
    for r in rows:
        lines.append(
            f"{r['region'][:12]:<12} "
            f"{r['calls']:>5} "
            f"{r['rate_limit_hits']:>5} "
            f"{r['rl_pressure']:>11.3f} "
            f"{r['avg_latency_ms']:>9}ms "
            f"${r['cost_usd']:>9.4f}  "
            f"{', '.join(m.split('-2024')[0] for m in r['models'])}"
        )

    total_rl = summary.get("rate_limit_hits", sum(r["rate_limit_hits"] for r in rows))
    if rows and rows[0]["rate_limit_hits"] > 0:
        top = rows[0]
        lines.append(
            f"\nheadline: {top['region']} carried {top['rate_limit_hits']} of "
            f"{total_rl} rate-limit hit(s) this month "
            f"(rl_pressure {top['rl_pressure']:.0%}) - a capacity signal for the "
            f"foundry / packaging / HBM pillars before it shows up in public earnings."
        )
    else:
        lines.append(
            f"\nheadline: no rate-limit hits across {len(rows)} region(s) this month - "
            f"capacity reads HOLD; no pillar upweight signal from telemetry."
        )
    return "\n".join(lines)


def show(reports_dir: Path | None = None) -> int:
    reports_dir = reports_dir or _REPORTS_DIR
    summary_path = latest_summary(reports_dir)
    if summary_path is None:
        print(
            "show: no ingest summary found under reports/*-ingest-summary.jsonl - "
            "run `ingest` first"
        )
        return 1
    summary = json.loads(
        summary_path.read_text(encoding="utf-8").splitlines()[0]
    )
    parquet_path = _resolve_parquet(summary, reports_dir)
    if parquet_path is None or not parquet_path.is_file():
        print(f"show: no parquet found under {reports_dir} to read telemetry from")
        return 1
    events = pq.read_table(parquet_path).to_pylist()
    print(render(summary, events, summary_path.stem))
    return 0


__all__ = ["show", "render", "region_rows", "latest_summary"]
