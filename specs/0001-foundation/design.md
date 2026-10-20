# Design — Foundation

## Shape

Three layers, each a thin Python module. No frameworks.

```
+--------------------------+
|  memo writer (markdown)  |
+--------------------------+
            |
+--------------------------+
|  pillar scorer (rubric)  |
+--------------------------+
            |
+--------------------------+
|   telemetry ingester     |
+--------------------------+
            |
   Helicone JSON exports
```

## Data flow

1. Operator drops a month of Helicone JSON exports into
   `data/raw/<provider>/YYYY-MM/`.
2. `python -m capital_reconcile ingest` normalizes records into
   `data/normalized/YYYY-MM.parquet` matching the typed event schema
   from R-CBR-005.
3. `python -m capital_reconcile score` reads
   `config/pillars.yaml` plus the normalized parquet plus the prior
   month's memo. It produces a draft `capital_reconcile/YYYY-Mnn.md`
   with verdicts set to TODO and telemetry flags (rate-limit pressure
   with its interval, latency, cost) pre-populated per pillar.
4. Operator hand-edits the draft and adds independent evidence refs,
   such as public earnings calls, for any pillar they want to call.
   Verdicts and revert thresholds are the human's call, not the
   rubric's. The rubric provides telemetry flags, not opinion, and a
   pillar with no independent evidence stays ABSTAIN (R-CBR-003).
5. `python -m capital_reconcile validate capital_reconcile/YYYY-Mnn.md`
   runs `validate_schemas` + `validate_pillars` + `voice_lint`.

## Why the rubric does not pick verdicts

A scorer that emits HOLD / UPWEIGHT / TRIM without human review
collapses to a noisy momentum signal. The point of a monthly cadence
plus a written memo is that the human stays in the loop on the
verdict. The rubric surfaces evidence; the human assigns weight.

Telemetry cannot pin a pillar either way. A 429 can reflect an account
quota, a request burst or service policy as easily as foundry,
packaging or memory supply. Rate-limit pressure therefore enters a memo
as a flag or a ranked interval, and a pillar verdict needs at least one
independent evidence ref (R-CBR-003, R-CBR-008, R-CBR-011). See
`docs/telemetry-attribution.md`.

This matches the operating discipline in `thesis-pillar-tracker` and
in the CDCP operating-model memo: typed artifacts and human-gated
promotion.

## Schema sketch

`schemas/monthly_memo.schema.json` will require:

```yaml
month: 2026-06
generated_at: 2026-07-02T10:00:00Z
pillars:
  foundry:
    verdict: HOLD
    evidence:
      - earnings-pillar-diff/2026-Q2/tsmc.md#n3-utilization
      - data/normalized/2026-06.parquet#rate_limit_pressure_us_east_1
    revert_threshold: "TRIM if two consecutive earnings calls report N3 utilization below 80%; rate-limit pressure is a flag only"
  advanced-packaging:
    verdict: ABSTAIN
    evidence:
      - data/normalized/2026-06.parquet#rate_limit_pressure_us_east_1
    revert_threshold: "n/a — telemetry flag only, no independent evidence"
  # ... four more
```

## What is deliberately NOT in v0

- LLM-judge scoring on memo prose.
- Multi-provider fusion in the ingester (just Helicone-style first).
- Trade-execution hooks.
- A web frontend. The artifact is markdown.

## Dependencies (planned for PR 0002)

- `pydantic` for typed events.
- `pyyaml` for front-matter parsing.
- `jsonschema` for memo validation.
- `pyarrow` for the normalized parquet store.

No LLM SDK in v0. The telemetry is the load-bearing input; LLM-assisted
draft writing comes later if it earns its keep.
