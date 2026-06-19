# Tasks — Foundation

Ordered for the first three PRs after the v0 scaffold.

## PR 0002 — schema, config, ingester skeleton

- [ ] Write `schemas/monthly_memo.schema.json` matching R-CBR-001.
- [ ] Write `schemas/normalized_event.schema.json` matching R-CBR-005.
- [ ] Add `config/pillars.yaml` with the six named pillars (R-CBR-002).
- [ ] Stub `src/capital_reconcile/__init__.py` and CLI entry point.
- [ ] Implement `src/capital_reconcile/ingest/helicone.py` for v0.
- [ ] Add `scripts/voice_lint.py` (copy template from
      `trace-to-eval-harness`).
- [ ] Add `scripts/validate_schemas.py` and
      `scripts/validate_pillars.py`.
- [ ] Add `pyproject.toml` with the dependencies listed in design.md.

## PR 0003 — scorer and memo-writer skeleton

- [ ] Implement `src/capital_reconcile/score/rubric.py` that maps
      normalized events onto per-pillar evidence references.
- [ ] Implement `src/capital_reconcile/memo/writer.py` that emits a
      draft `capital_reconcile/YYYY-Mnn.md` with TODO verdicts.
- [ ] Write `tests/test_ingest_helicone.py` against a fixture export.
- [ ] Write `tests/test_validate_pillars.py` covering the
      under-evidence ABSTAIN rule.
- [ ] Document the operator workflow in `docs/operator-workflow.md`.

## PR 0004 — first real monthly memo

- [ ] Backfill last 30 days of Helicone exports into
      `data/raw/anthropic/`.
- [ ] Run the full ingest → score → draft pipeline for 2026-M06.
- [ ] Hand-edit verdicts and revert thresholds.
- [ ] Land `capital_reconcile/2026-M06.md`.
- [ ] Add a `decisions/DEC-CBR-001-pillar-set.md` recording why these
      six pillars and not others.
