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
   with verdicts set to TODO and evidence references pre-populated.
4. Operator hand-edits the draft. Verdicts and revert thresholds are
   the human's call, not the rubric's. The rubric provides evidence,
   not opinion.
5. `python -m capital_reconcile validate capital_reconcile/YYYY-Mnn.md`
   runs `validate_schemas` + `validate_pillars` + `voice_lint`.

## Why the rubric does not pick verdicts

A scorer that emits HOLD / UPWEIGHT / TRIM without human review
collapses to a noisy momentum signal. The point of a monthly cadence
plus a written memo is that the human stays in the loop on the
verdict. The rubric surfaces evidence; the human assigns weight.

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
      - data/normalized/2026-06.parquet#rate_limit_hits_n3
      - capital_reconcile/2026-M05.md#foundry-followup
    revert_threshold: "TRIM if rate-limit hits drop below 5/month for 2 mo"
  advanced-packaging:
    verdict: ABSTAIN
    evidence: []
    revert_threshold: "n/a — too thin"
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
