# Requirements — Foundation

Brand prefix: CBR (capital-build-reconciler).

## Functional requirements

- **R-CBR-001** — The repo SHALL define a typed monthly schema
  `schemas/monthly_memo.schema.json` covering: month, six pillar
  verdicts, per-pillar evidence-ref list, per-pillar revert threshold.
- **R-CBR-002** — The repo SHALL name six pillars in
  `config/pillars.yaml`: foundry, advanced-packaging, hbm-memory,
  networking, power, cooling.
- **R-CBR-003** — Each pillar verdict SHALL be one of HOLD, UPWEIGHT,
  TRIM, ABSTAIN. ABSTAIN is required when fewer than two evidence
  items exist for the pillar in the scoring window, or when none of
  them is independent evidence. Independent evidence is sourced outside
  this repo's own telemetry and prior memos (for example a public
  earnings call or supplier disclosure). Telemetry refs (rate-limit
  hits, latency, cost) may sit in a pillar's evidence list as flags but
  never by themselves support a non-ABSTAIN verdict.
- **R-CBR-004** — Telemetry ingest SHALL accept Helicone-style JSON
  log exports as the v0 source. Adapters for Langfuse and
  Anthropic-native logs are deferred to spec 0002.
- **R-CBR-005** — The ingester SHALL normalize each record into a
  typed event with fields: timestamp, provider, model, region,
  latency_ms, rate_limit_hit, cost_usd, prompt_tokens, output_tokens.

## Artifact requirements

- **R-CBR-006** — Monthly memos SHALL be written to
  `capital_reconcile/YYYY-Mnn.md` in append-only fashion (no
  rewriting prior months).
- **R-CBR-007** — Each memo SHALL embed a YAML front-matter block
  matching `schemas/monthly_memo.schema.json`. The CLI reads the
  YAML; the human reads the prose; both must agree.
- **R-CBR-008** — Each verdict SHALL carry an explicit revert
  threshold. Rate-limit pressure and other telemetry MAY raise a flag
  or a ranked interval inside a threshold (e.g., "flag for review if
  us-east-1 rate-limit pressure stays above 20% for two consecutive
  months"), but a threshold that moves a pillar verdict SHALL name
  independent evidence (e.g., "TRIM if two consecutive public earnings
  calls report N3 utilization below 80%"). Telemetry alone does not
  identify a foundry, packaging or memory constraint; without
  independent evidence the pillar reads ABSTAIN.

## Voice requirements

- **R-CBR-009** — Memos SHALL pass `scripts/voice_lint.py`.
- **R-CBR-010** — Memos SHALL NOT use antithetical-reversal phrasing
  in pillar verdicts.

## Gate requirements

- **R-CBR-011** — `scripts/validate_pillars.py` SHALL reject any memo
  in which a non-ABSTAIN verdict carries fewer than two evidence
  references, or carries no independent evidence reference (telemetry
  and prior-memo refs only).
- **R-CBR-012** — `scripts/validate_schemas.py` SHALL validate every
  memo's YAML front-matter against the canonical schema before merge.

## Traceability

| Requirement | Implementation | Tests |
|---|---|---|
| R-CBR-003 | `scripts/validate_pillars.py` (`is_independent_ref`, `validate`) | `tests/test_validate_pillars.py` |
| R-CBR-008 | `specs/0001-foundation/design.md` schema sketch; `src/capital_reconcile/show.py` and `streamlit_app.py` headlines (flag and interval only, attribution ABSTAIN) | `tests/test_validate_pillars.py::test_design_schema_sketch_passes_pillar_validator`, `tests/test_show.py`, `tests/test_telemetry_uncertainty.py` |
| R-CBR-011 | `scripts/validate_pillars.py` | `tests/test_validate_pillars.py` |
