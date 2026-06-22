# System Map

## Flow

```text
Helicone-style JSON exports
        |
        v
capital_reconcile.ingest.helicone
        |
        v
normalized event parquet
        |
        v
report JSONL and future memo scorer
        |
        v
human-reviewed monthly memo
```

## Components

- `schemas/normalized_event.schema.json` defines the event contract.
- `schemas/monthly_memo.schema.json` defines the memo front-matter
  contract.
- `config/pillars.yaml` defines the six durable pillar keys.
- `src/capital_reconcile/` contains the working ingest CLI and adapter.
- `capital_build_reconciler/` exposes the factory contract module
  names and delegates ingest to the working implementation.
- `scripts/validate_schemas.py` checks JSON Schema files and memo front
  matter.
- `scripts/validate_pillars.py` enforces evidence count policy.
- `scripts/voice_lint.py` enforces memo voice constraints.
- `reports/2026-M06-ingest-summary.jsonl` is the checked-in v0.1 report
  artifact.

## Ownership Boundaries

- The ingester owns telemetry normalization only.
- Scoring helpers own aggregate summaries and evidence candidates.
- The memo writer remains future work; final verdicts stay human-owned.
