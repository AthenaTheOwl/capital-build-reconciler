from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from capital_reconcile.ingest.helicone import NormalizedEvent


PILLAR_KEYS: tuple[str, ...] = (
    "foundry",
    "advanced-packaging",
    "hbm-memory",
    "networking",
    "power",
    "cooling",
)

Verdict = Literal["HOLD", "UPWEIGHT", "TRIM", "ABSTAIN"]


class IngestSummary(BaseModel):
    month: str = Field(pattern=r"^[0-9]{4}-[0-9]{2}$")
    artifact: Literal["ingest_summary"] = "ingest_summary"
    source: str
    provider: Literal["anthropic"]
    records: int = Field(ge=0)
    rate_limit_hits: int = Field(ge=0)
    regions: list[str]
    cost_usd: float = Field(ge=0)
    prompt_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)


class PillarReport(BaseModel):
    month: str = Field(pattern=r"^[0-9]{4}-[0-9]{2}$")
    pillar: str
    verdict: Verdict
    evidence: list[str]
    revert_threshold: str


__all__ = [
    "IngestSummary",
    "NormalizedEvent",
    "PILLAR_KEYS",
    "PillarReport",
    "Verdict",
]
