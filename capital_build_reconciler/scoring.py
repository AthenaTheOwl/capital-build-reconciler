from __future__ import annotations

from collections.abc import Iterable

from .model import IngestSummary, NormalizedEvent


def summarize_events(
    events: Iterable[NormalizedEvent],
    *,
    month: str,
    source: str,
) -> IngestSummary:
    rows = list(events)
    provider = rows[0].provider if rows else "anthropic"
    return IngestSummary(
        month=month,
        source=source,
        provider=provider,
        records=len(rows),
        rate_limit_hits=sum(1 for row in rows if row.rate_limit_hit),
        regions=sorted({row.region for row in rows}),
        cost_usd=round(sum(row.cost_usd for row in rows), 6),
        prompt_tokens=sum(row.prompt_tokens for row in rows),
        output_tokens=sum(row.output_tokens for row in rows),
    )


__all__ = ["summarize_events"]
