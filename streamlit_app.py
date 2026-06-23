"""capital-build-reconciler - live demo (Streamlit Community Cloud).

Reads the committed monthly telemetry under reports/ (the ingest summary
jsonl + the normalized parquet it summarizes) and shows which region is
under the most rate-limit pressure - a capacity signal for the AI-infra
capital pillars before it lands in public earnings. No network, no
secrets - runs entirely off the committed fixture artifacts.

Deploy: Streamlit Community Cloud -> New app -> repo
AthenaTheOwl/capital-build-reconciler, branch main, main file
streamlit_app.py.
"""
from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq
import streamlit as st

REPO = Path(__file__).resolve().parent
REPORTS = REPO / "reports"


def load_summary() -> tuple[dict, str] | tuple[None, None]:
    files = sorted(REPORTS.glob("*-ingest-summary.jsonl"))
    if not files:
        return None, None
    latest = files[-1]
    first = latest.read_text(encoding="utf-8").splitlines()[0]
    return json.loads(first), latest.stem


def load_events(summary: dict) -> list[dict]:
    month = summary.get("month", "")
    stamp = month.replace("-0", "-M0").replace("-1", "-M1") if month else ""
    candidate = REPORTS / f"{stamp}.fixture.parquet"
    if not candidate.is_file():
        parquets = sorted(REPORTS.glob("*.parquet"))
        if not parquets:
            return []
        candidate = parquets[-1]
    return pq.read_table(candidate).to_pylist()


def region_rows(events: list[dict]) -> list[dict]:
    by_region: dict[str, dict] = {}
    for ev in events:
        region = ev.get("region", "?")
        agg = by_region.setdefault(
            region,
            {"region": region, "calls": 0, "rate_limit_hits": 0, "cost_usd": 0.0, "lat": 0, "models": set()},
        )
        agg["calls"] += 1
        agg["rate_limit_hits"] += 1 if ev.get("rate_limit_hit") else 0
        agg["cost_usd"] += float(ev.get("cost_usd", 0.0))
        agg["lat"] += int(ev.get("latency_ms", 0))
        agg["models"].add(ev.get("model", "?"))
    rows = []
    for agg in by_region.values():
        calls = agg["calls"] or 1
        rows.append(
            {
                "region": agg["region"],
                "calls": agg["calls"],
                "429s": agg["rate_limit_hits"],
                "rl_pressure": round(agg["rate_limit_hits"] / calls, 3),
                "avg_latency_ms": round(agg["lat"] / calls),
                "cost_usd": round(agg["cost_usd"], 6),
                "models": ", ".join(sorted(m.split("-2024")[0] for m in agg["models"])),
            }
        )
    rows.sort(key=lambda r: (r["rl_pressure"], r["429s"]), reverse=True)
    return rows


st.set_page_config(page_title="capital-build-reconciler - build telemetry", layout="wide")
st.title("capital-build-reconciler")
st.caption(
    "personal LLM-inference telemetry as a private channel-check: which region is "
    "throwing rate limits, read as a capacity signal for the AI-infra capital pillars."
)

summary, stem = load_summary()
if summary is None:
    st.warning("no ingest summary found under reports/*-ingest-summary.jsonl")
    st.stop()

events = load_events(summary)
if not events:
    st.warning("no normalized parquet found under reports/*.parquet")
    st.stop()

rows = region_rows(events)

st.subheader(f"{summary.get('provider', '?')} build telemetry - {summary.get('month', '?')}")

c1, c2, c3 = st.columns(3)
c1.metric("calls", f"{summary.get('records', len(events)):,}")
c2.metric("rate-limit hits", f"{summary.get('rate_limit_hits', sum(r['429s'] for r in rows)):,}")
c3.metric("spend", f"${summary.get('cost_usd', sum(r['cost_usd'] for r in rows)):.4f}")

only_rl = st.checkbox("only regions with rate-limit hits", value=False)
shown = [r for r in rows if r["429s"] > 0] if only_rl else rows

st.dataframe(shown, use_container_width=True, hide_index=True)

if rows and rows[0]["429s"] > 0:
    top = rows[0]
    st.info(
        f"**headline:** {top['region']} carried {top['429s']} of "
        f"{summary.get('rate_limit_hits', sum(r['429s'] for r in rows))} rate-limit hit(s) this month "
        f"(rl_pressure {top['rl_pressure']:.0%}) - a capacity signal for the foundry / packaging / "
        f"HBM pillars before it shows up in public earnings."
    )
else:
    st.info(
        "**headline:** no rate-limit hits this month - capacity reads HOLD; "
        "no pillar upweight signal from telemetry."
    )

st.caption(
    "v0.0.2 ships one anthropic fixture month. the model + ingester live in "
    "`src/capital_reconcile/`; this page reads the committed reports/. "
    "repo: github.com/AthenaTheOwl/capital-build-reconciler"
)
