# Requirements - v0.1 Data Report

## Functional requirements

- **R-CBR-013** - The repo SHALL include a top-level product brief and
  system map for reviewer orientation.
- **R-CBR-014** - The repo SHALL expose importable
  `capital_build_reconciler.cli`, `capital_build_reconciler.model`, and
  `capital_build_reconciler.scoring` modules.
- **R-CBR-015** - The underscore-named package SHALL keep the existing
  `capital_reconcile` ingest behavior available through
  `python -m capital_build_reconciler ingest`.
- **R-CBR-016** - The repo SHALL include one checked-in report artifact
  under `reports/` in JSONL format.
- **R-CBR-017** - Report artifacts SHALL summarize normalized telemetry
  without requiring private raw export files.

## Gate requirements

- **R-CBR-018** - `python -m pytest` SHALL pass with the fixture ingest
  test.
- **R-CBR-019** - The schema and voice validators SHALL run against the
  files introduced by this spec.
- **R-CBR-020** - `STATUS.md` SHALL keep the exact H2 headings:
  `Current state`, `Known limits`, and `Next feature queue`.
