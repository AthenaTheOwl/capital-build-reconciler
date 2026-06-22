# Capital Build Reconciler Status

## Current state

- PR 0002 schema, config, and Helicone-style ingest surface is implemented.
- The package exposes `python -m capital_reconcile ingest` and the `capital-reconcile` console entry.
- Fixture-driven parquet ingest tests and schema/voice validators are checked in.
- Product brief, system map, and `specs/0002-design/` are checked in.
- `capital_build_reconciler` exposes the factory-facing `cli`, `model`, and `scoring` modules.
- `reports/2026-M06-ingest-summary.jsonl` is the checked-in v0.1 report artifact.

## Known limits

- `score` and `validate` CLI subcommands are reserved stubs.
- No checked-in monthly memo exists yet.
- Only Anthropic records in Helicone-style JSON are supported.
- The report artifact uses fixture data, not private operator telemetry.

## Next feature queue

- Implement scorer evidence extraction against `config/pillars.yaml`.
- Add the memo writer for `capital_reconcile/YYYY-Mnn.md` drafts.
- Add validator tests for under-evidenced verdicts and ABSTAIN handling.
- Replace the fixture report with a private-telemetry monthly report when raw data is available.

- Resolve factory defect: missing PRODUCT_BRIEF.md,SYSTEM_MAP.md
- Resolve factory defect: missing reports/*.jsonl
- Resolve factory defect: PRODUCT_BRIEF.md is required for active repos
- Resolve factory defect: SYSTEM_MAP.md is required for active repos
- Resolve factory defect: expected file 'PRODUCT_BRIEF.md' is missing
- Resolve factory defect: expected file 'SYSTEM_MAP.md' is missing
- Resolve factory defect: expected file 'specs/0002-design/requirements.md' is missing
- Resolve factory defect: expected file 'specs/0002-design/design.md' is missing
- Resolve factory defect: expected file 'specs/0002-design/tasks.md' is missing
- Resolve factory defect: expected file 'specs/0002-design/acceptance.md' is missing
- Resolve factory defect: expected file 'capital_build_reconciler/cli.py' is missing
- Resolve factory defect: expected glob 'reports/*.jsonl' matched no files
- Resolve factory defect: module 'cli' declares source 'capital_build_reconciler/cli.py', but it is missing
- Resolve factory defect: module 'model' declares source 'capital_build_reconciler/model.py', but it is missing
- Resolve factory defect: module 'report' declares source 'capital_build_reconciler/scoring.py', but it is missing
- Resolve factory defect: claude_code review requested patch; inspect defect log
