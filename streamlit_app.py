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
import sys
from pathlib import Path

import pyarrow.parquet as pq
import streamlit as st

REPO = Path(__file__).resolve().parent
REPORTS = REPO / "reports"
SRC = REPO / "src"
if SRC.is_dir() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# the real engine: the field-mapping normalizer + the per-region
# rate-limit-pressure ranker the CLI `ingest` and `show` verbs drive.
from capital_reconcile.ingest.helicone import normalize as _normalize  # noqa: E402
from capital_reconcile.show import region_rows as _region_rows  # noqa: E402

FIXTURE = REPO / "tests" / "fixtures" / "helicone_sample.json"


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

# ---------------------------------------------------------------------------
# interactive: reconcile your OWN logs (drives the real engine)
# ---------------------------------------------------------------------------
st.divider()
st.subheader("reconcile your own logs")
st.caption(
    "paste your own Helicone-style raw request logs (a JSON array). the app runs "
    "the real `capital_reconcile.ingest.helicone.normalize` (field-mapping + 429 "
    "detection) over each record, then the real `capital_reconcile.show.region_rows` "
    "ranker - the same engine the `ingest` and `show` CLI verbs drive. nothing is "
    "hardcoded; edit a record and the ranking recomputes."
)

_default_raw = (
    FIXTURE.read_text(encoding="utf-8")
    if FIXTURE.is_file()
    else json.dumps(
        [
            {
                "id": "req_demo",
                "created_at": "2026-06-01T00:00:00Z",
                "provider": "anthropic",
                "model": "claude-3-5-sonnet-20241022",
                "region": "us-east-1",
                "latency_ms": 500,
                "status_code": 200,
                "cost_usd": 0.01,
                "usage": {"prompt_tokens": 100, "completion_tokens": 20},
            }
        ],
        indent=2,
    )
)

raw_text = st.text_area(
    "raw Helicone-style logs (JSON array of request records)",
    value=_default_raw,
    height=320,
    help=(
        "the normalizer accepts many key spellings (created_at/createdAt, "
        "cost_usd/costUSD/heliconeCalculatedCost, usage.completion_tokens, ...). "
        "a record with status_code 429 (or rate_limit_hit:true) counts as a hit."
    ),
)

if st.button("run reconciler", type="primary"):
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        st.error(f"not valid JSON: {exc}")
        st.stop()

    if isinstance(parsed, dict):
        records = (
            parsed.get("data")
            or parsed.get("records")
            or parsed.get("results")
            or parsed.get("requests")
            or [parsed]
        )
    elif isinstance(parsed, list):
        records = parsed
    else:
        st.error("expected a JSON array of records (or an object wrapping one)")
        st.stop()

    normalized: list[dict] = []
    errors: list[str] = []
    for idx, rec in enumerate(records):
        if not isinstance(rec, dict):
            errors.append(f"record {idx}: not an object")
            continue
        try:
            normalized.append(_normalize(rec).model_dump(mode="json"))
        except Exception as exc:  # ValueError / pydantic ValidationError
            errors.append(f"record {idx}: {exc}")

    if errors:
        st.error(
            "the real normalizer rejected "
            f"{len(errors)} of {len(records)} record(s):"
        )
        for msg in errors:
            st.write(f"- {msg}")

    if not normalized:
        st.warning("no record normalized cleanly - nothing to rank.")
        st.stop()

    user_rows = _region_rows(normalized)

    n_hits = sum(r["rate_limit_hits"] for r in user_rows)
    m1, m2, m3 = st.columns(3)
    m1.metric("normalized events", len(normalized))
    m2.metric("regions", len(user_rows))
    m3.metric("rate-limit hits", n_hits)

    st.markdown("**normalized events** (real `normalize` output)")
    st.dataframe(normalized, use_container_width=True, hide_index=True)

    st.markdown("**per-region ranking** (real `region_rows`, by rl_pressure)")
    display_rows = [
        {**r, "models": ", ".join(m.split("-2024")[0] for m in r["models"])}
        for r in user_rows
    ]
    st.dataframe(display_rows, use_container_width=True, hide_index=True)

    if user_rows and user_rows[0]["rate_limit_hits"] > 0:
        top = user_rows[0]
        st.info(
            f"**headline:** {top['region']} carried {top['rate_limit_hits']} of "
            f"{n_hits} rate-limit hit(s) (rl_pressure {top['rl_pressure']:.0%}) - "
            "capacity signal: UPWEIGHT the foundry / packaging / HBM pillars."
        )
    else:
        st.info(
            "**headline:** no rate-limit hits across your logs - capacity reads "
            "HOLD; no pillar upweight signal."
        )
