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
  items exist for the pillar in the scoring window.
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
  threshold (e.g., "TRIM if foundry-capacity rate-limit hits drop
  below 5/month for two consecutive months").

## Voice requirements

- **R-CBR-009** — Memos SHALL pass `scripts/voice_lint.py`.
- **R-CBR-010** — Memos SHALL NOT use antithetical-reversal phrasing
  in pillar verdicts.

## Gate requirements

- **R-CBR-011** — `scripts/validate_pillars.py` SHALL reject any memo
  in which a non-ABSTAIN verdict carries fewer than two evidence
  references.
- **R-CBR-012** — `scripts/validate_schemas.py` SHALL validate every
  memo's YAML front-matter against the canonical schema before merge.
