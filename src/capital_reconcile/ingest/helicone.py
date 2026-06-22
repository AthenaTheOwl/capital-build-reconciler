from __future__ import annotations

import json
from collections.abc import Iterator, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import pyarrow as pa
import pyarrow.parquet as pq
from pydantic import BaseModel, Field


FIELD_MAPPING: dict[str, tuple[str, ...]] = {
    "timestamp": ("timestamp", "created_at", "createdAt", "request.created_at", "request.createdAt"),
    "provider": ("provider", "request.provider", "properties.provider"),
    "model": ("model", "request.model", "request_body.model", "requestBody.model", "properties.model"),
    "region": ("region", "request.region", "properties.region", "user_properties.region", "userProperties.region"),
    "latency_ms": ("latency_ms", "latencyMs", "latency", "response_time_ms", "responseTimeMs"),
    "cost_usd": ("cost_usd", "costUSD", "cost", "heliconeCalculatedCost", "response.cost_usd"),
    "prompt_tokens": ("prompt_tokens", "promptTokens", "usage.prompt_tokens", "usage.promptTokens"),
    "output_tokens": (
        "output_tokens",
        "outputTokens",
        "completion_tokens",
        "completionTokens",
        "usage.output_tokens",
        "usage.outputTokens",
        "usage.completion_tokens",
        "usage.completionTokens",
    ),
}

STATUS_PATHS: tuple[str, ...] = (
    "status_code",
    "statusCode",
    "response_status",
    "responseStatus",
    "response.status_code",
    "response.statusCode",
)

PARQUET_SCHEMA = pa.schema(
    [
        pa.field("timestamp", pa.string()),
        pa.field("provider", pa.string()),
        pa.field("model", pa.string()),
        pa.field("region", pa.string()),
        pa.field("latency_ms", pa.int64()),
        pa.field("rate_limit_hit", pa.bool_()),
        pa.field("cost_usd", pa.float64()),
        pa.field("prompt_tokens", pa.int64()),
        pa.field("output_tokens", pa.int64()),
    ]
)


class NormalizedEvent(BaseModel):
    timestamp: datetime
    provider: Literal["anthropic"] = "anthropic"
    model: str = Field(min_length=1)
    region: str = Field(min_length=1)
    latency_ms: int = Field(ge=0)
    rate_limit_hit: bool
    cost_usd: float = Field(ge=0)
    prompt_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)

    def parquet_row(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


def _lookup(record: dict[str, Any], paths: Sequence[str]) -> Any:
    for path in paths:
        current: Any = record
        for part in path.split("."):
            if not isinstance(current, dict) or part not in current:
                current = None
                break
            current = current[part]
        if current is not None:
            return current
    return None


def _required(record: dict[str, Any], field: str) -> Any:
    value = _lookup(record, FIELD_MAPPING[field])
    if value is None:
        raise ValueError(f"missing Helicone field for {field}")
    return value


def _rate_limit_hit(record: dict[str, Any]) -> bool:
    explicit = _lookup(record, ("rate_limit_hit", "rateLimitHit", "is_rate_limit", "isRateLimit"))
    if explicit is not None:
        return bool(explicit)

    status = _lookup(record, STATUS_PATHS)
    if status is None:
        return False
    return int(status) == 429


def iter_records(raw_dir: Path) -> Iterator[dict[str, Any]]:
    for json_path in sorted(raw_dir.glob("*.json")):
        with json_path.open(encoding="utf-8") as handle:
            payload = json.load(handle)

        if isinstance(payload, list):
            records = payload
        elif isinstance(payload, dict):
            records = (
                payload.get("data")
                or payload.get("records")
                or payload.get("results")
                or payload.get("requests")
                or [payload]
            )
        else:
            raise ValueError(f"{json_path} does not contain a JSON object or array")

        for record in records:
            if not isinstance(record, dict):
                raise ValueError(f"{json_path} contains a non-object record")
            yield record


def normalize(record: dict[str, Any]) -> NormalizedEvent:
    provider = (_lookup(record, FIELD_MAPPING["provider"]) or "anthropic").lower()
    return NormalizedEvent(
        timestamp=_required(record, "timestamp"),
        provider=provider,
        model=str(_required(record, "model")),
        region=str(_required(record, "region")),
        latency_ms=int(_required(record, "latency_ms")),
        rate_limit_hit=_rate_limit_hit(record),
        cost_usd=float(_required(record, "cost_usd")),
        prompt_tokens=int(_required(record, "prompt_tokens")),
        output_tokens=int(_required(record, "output_tokens")),
    )


def write_parquet(events: Sequence[NormalizedEvent], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist([event.parquet_row() for event in events], schema=PARQUET_SCHEMA)
    pq.write_table(table, out_path)


def ingest(raw_dir: Path, out_path: Path) -> list[NormalizedEvent]:
    events = [normalize(record) for record in iter_records(raw_dir)]
    write_parquet(events, out_path)
    return events
