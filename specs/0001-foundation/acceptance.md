# Acceptance — v0 Foundation

"v0 done" means the repo can ingest one month of Helicone-style
telemetry, emit a draft memo whose YAML front-matter validates against
the canonical schema, and produce a validator chain that catches a
missing-evidence pillar verdict.

## Commands a reviewer must be able to run

```bash
python -m pip install -e .[dev]
python -m capital_reconcile ingest \
  --provider anthropic \
  --raw data/raw/anthropic/2026-06 \
  --out data/normalized/2026-06.parquet

python -m capital_reconcile score \
  --month 2026-06 \
  --pillars config/pillars.yaml \
  --normalized data/normalized/2026-06.parquet \
  --out capital_reconcile/2026-M06.draft.md

python -m capital_reconcile validate \
  capital_reconcile/2026-M06.md
```

## Gates that must pass

- `python -m pytest` exits 0 with the fixture-based ingest test.
- `python scripts/voice_lint.py capital_reconcile/2026-M06.md` exits 0.
- `python scripts/validate_schemas.py capital_reconcile/2026-M06.md`
  exits 0.
- `python scripts/validate_pillars.py capital_reconcile/2026-M06.md`
  exits 0 — every non-ABSTAIN verdict has at least two evidence refs.

## Artifacts that must exist

- `capital_reconcile/2026-M06.md` — one real, hand-edited monthly memo
  for June 2026. This is the proof.
- `decisions/DEC-CBR-001-pillar-set.md` — one architectural decision
  record naming the six pillars and why they are the right cut.
- `data/normalized/2026-06.parquet` — one normalized month of
  telemetry, included or symlinked so the validator can reproduce.

## Out of scope for v0

- The pipeline does not need to run on a schedule. Manual invocation
  is enough.
- The pipeline does not need to ingest Langfuse or Anthropic-native
  logs. Helicone-style only.
- The pipeline does not need a web UI or any non-markdown surface.

## What "done" feels like

A reader picks up `capital_reconcile/2026-M06.md` and learns, in under
two minutes, six pillar verdicts and the telemetry behind each. They
can re-run the validator chain on the file and watch every gate pass.
That is enough.
