# Design - v0.1 Data Report

## Package Contract

The original implementation lives in `src/capital_reconcile/` because
the monthly memo directory is also named `capital_reconcile/`. The
factory contract expects the import package name
`capital_build_reconciler`. The v0.1 design keeps both names:

- `capital_reconcile` remains the implementation package.
- `capital_build_reconciler` is a facade package with stable module
  names for factory checks.
- `capital_build_reconciler.cli` delegates to the existing parser and
  command handlers.
- `capital_build_reconciler.model` exports typed report models and the
  normalized event model.
- `capital_build_reconciler.scoring` provides deterministic aggregate
  summaries for report artifacts and later scoring work.

## Report Artifact

`reports/2026-M06-ingest-summary.jsonl` is a small, inspectable data
report derived from `tests/fixtures/helicone_sample.json`. It records:

- month
- source fixture
- provider
- record count
- rate-limit hits
- regions
- token totals
- cost total

This artifact proves the repo can produce a reviewable data report even
before the memo writer lands.

## Boundary

The v0.1 report is descriptive. It does not assign pillar verdicts.
Verdicts remain in the future memo workflow, where the evidence policy
validators already exist.
