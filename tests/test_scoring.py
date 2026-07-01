from __future__ import annotations

from datetime import datetime, timezone

from capital_build_reconciler.scoring import summarize_events
from capital_reconcile.ingest.helicone import NormalizedEvent


def _event(*, region: str, rate_limit_hit: bool, cost_usd: float) -> NormalizedEvent:
    return NormalizedEvent(
        timestamp=datetime(2026, 6, 1, tzinfo=timezone.utc),
        provider="anthropic",
        model="claude-opus-4",
        region=region,
        latency_ms=120,
        rate_limit_hit=rate_limit_hit,
        cost_usd=cost_usd,
        prompt_tokens=10,
        output_tokens=20,
    )


def test_summarize_events_pins_current_output() -> None:
    # golden-master lock: any change to how summarize_events aggregates its
    # fields (records, rate_limit_hits, regions, tokens, cost) should fail here
    # asymmetric hit/miss split so inverting the rate_limit_hit predicate
    # changes the pinned count (2 hits vs 1 miss)
    events = [
        _event(region="us-east-1", rate_limit_hit=True, cost_usd=0.01),
        _event(region="us-east-1", rate_limit_hit=True, cost_usd=0.02),
        _event(region="us-west-2", rate_limit_hit=False, cost_usd=0.03),
    ]

    summary = summarize_events(events, month="2026-06", source="fixture")

    assert summary.month == "2026-06"
    assert summary.source == "fixture"
    assert summary.provider == "anthropic"
    assert summary.records == 3
    assert summary.rate_limit_hits == 2
    assert summary.regions == ["us-east-1", "us-west-2"]
    assert summary.cost_usd == 0.06
    assert summary.prompt_tokens == 30
    assert summary.output_tokens == 60
