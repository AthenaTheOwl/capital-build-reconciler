# Tasks - v0.1 Data Report

## PR 0002 follow-up patch

- [x] Add `PRODUCT_BRIEF.md`.
- [x] Add `SYSTEM_MAP.md`.
- [x] Add the `specs/0002-design/` ledger.
- [x] Add `src/capital_build_reconciler/cli.py`.
- [x] Add `src/capital_build_reconciler/model.py`.
- [x] Add `src/capital_build_reconciler/scoring.py`.
- [x] Add a JSONL report artifact under `reports/`.
- [x] Remove the root-level generated parquet artifact.

## Next feature queue input

- Add memo writer modules that turn a summary report into a draft
  `capital_reconcile/YYYY-Mnn.md`.
- Add validator tests for ABSTAIN and under-evidenced non-ABSTAIN
  verdicts.
- Add a real June 2026 memo only after private raw telemetry is present.
