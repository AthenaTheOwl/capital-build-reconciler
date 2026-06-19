# First PR (after scaffold)

The literal first PR after this v0 scaffold is PR 0002 in
`specs/0001-foundation/tasks.md`: schema, config, and ingester
skeleton.

## Scope

One PR, one reviewable diff. No memo writing yet. No scoring rubric
yet. Just the typed shape of inputs and outputs, plus a working
ingester for one provider.

## Files added

```
schemas/monthly_memo.schema.json
schemas/normalized_event.schema.json
config/pillars.yaml
src/capital_reconcile/__init__.py
src/capital_reconcile/__main__.py
src/capital_reconcile/cli.py
src/capital_reconcile/ingest/__init__.py
src/capital_reconcile/ingest/helicone.py
scripts/voice_lint.py
scripts/validate_schemas.py
scripts/validate_pillars.py
tests/test_ingest_helicone.py
tests/fixtures/helicone_sample.json
pyproject.toml
```

## Files changed

```
README.md         # add "How to run" with the new ingest command
AGENTS.md         # uncomment the gate block (now real)
```

## Why this scope

Telemetry without a typed shape rots. Get the schema and the ingester
landed first so every later PR has somewhere typed to write.

The voice_lint and validate_schemas scripts are copies of the
canonical templates from `trace-to-eval-harness` — same checks, same
banned-word list, same JSON-schema runner. Bringing them in early
means the README and the AGENTS.md text in this very repo already
pass the gates by the end of PR 0002.

## Verification

```bash
python -m pip install -e .[dev]
python -m pytest                  # one test passes: ingest_helicone
python scripts/voice_lint.py README.md AGENTS.md
python scripts/validate_schemas.py schemas/
python -m capital_reconcile ingest \
  --provider anthropic \
  --raw tests/fixtures \
  --out /tmp/out.parquet
```

The last command should exit 0 and write a one-row parquet whose
columns match `schemas/normalized_event.schema.json`.

## Out of scope (deferred to PR 0003)

- The scorer module.
- The memo writer.
- Langfuse adapter.
- Anthropic-native adapter.

## Decision record

PR 0002 lands one DEC record:
`decisions/DEC-CBR-000-helicone-as-v0-source.md`. It names why
Helicone-style exports were picked as the first adapter (open format,
JSON, schema-stable, cheap fixture) and what would have to be true to
add a second adapter.
