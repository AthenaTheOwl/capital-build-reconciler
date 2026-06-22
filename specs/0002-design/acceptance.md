# Acceptance - v0.1 Data Report

## Required files

- `PRODUCT_BRIEF.md`
- `SYSTEM_MAP.md`
- `specs/0002-design/requirements.md`
- `specs/0002-design/design.md`
- `specs/0002-design/tasks.md`
- `specs/0002-design/acceptance.md`
- `capital_build_reconciler/cli.py`
- `capital_build_reconciler/model.py`
- `capital_build_reconciler/scoring.py`
- `reports/2026-M06-ingest-summary.jsonl`

## Commands

```bash
python -m pytest
python scripts/voice_lint.py PRODUCT_BRIEF.md SYSTEM_MAP.md specs/0002-design capital_build_reconciler
python scripts/validate_schemas.py schemas/
python -m capital_build_reconciler ingest --provider anthropic --raw tests/fixtures --out reports/2026-M06.fixture.parquet
```

## Pass condition

- The commands above exit 0.
- `reports/2026-M06-ingest-summary.jsonl` is valid JSONL.
- No generated `out.parquet` remains at repo root.
