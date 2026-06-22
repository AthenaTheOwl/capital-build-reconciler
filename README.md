# Capital-Build Reconciler

A monthly memo pipeline that reconciles personal LLM-inference telemetry
(rate-limit hits, dollar-per-token drift, region latency, capacity
rejects) against the user's semis and AI-infra thesis pillars, emitting
HOLD / UPWEIGHT / TRIM verdicts per pillar with telemetry-grounded
rationale.

## What this is

Most investing-thesis tracking loops drift toward what the news cycle
amplifies. This repo treats personal build telemetry as a private
channel-check: when you cannot get tokens from Anthropic in us-east-1
for three consecutive Tuesdays, that is evidence about capacity that
the public narrative is two quarters behind on. The reconciler turns
that evidence into a typed monthly artifact.

The intended cadence is monthly. The intended decision is capital
allocation across 6 named pillars (foundry, packaging, memory,
networking, power, cooling). The intended artifact is
`capital_reconcile/<year>-Mnn.md`, one page, written.

This repo is a sibling to `thesis-pillar-tracker` and
`earnings-pillar-diff`. Together they form the investing-decision spine
for the portfolio.

## Status

v0.0.2 foundation. Specs in `specs/0001-foundation/` name the schema
and the first monthly memo. The repo now includes schemas, pillar
config, validators, and a Helicone-style ingester for Anthropic logs.

## How to run

Run the fixture ingest path:

```bash
python -m capital_build_reconciler ingest \
  --provider anthropic \
  --raw tests/fixtures \
  --out reports/2026-M06.fixture.parquet
```

The installed console entry delegates to the same parser:

```bash
capital-reconcile ingest \
  --provider anthropic \
  --raw tests/fixtures \
  --out reports/2026-M06.fixture.parquet
```

## Layout

```
capital-build-reconciler/
  README.md
  LICENSE
  AGENTS.md
  .gitignore
  specs/
    0001-foundation/
      requirements.md
      design.md
      tasks.md
      acceptance.md
  docs/
    first-pr.md
  reports/
    2026-M06-ingest-summary.jsonl
  capital_build_reconciler/
  config/
  src/
    capital_reconcile/
  capital_reconcile/     # written monthly memos land here
```

## Why this exists

Public thesis tracking is downstream of public earnings calls. Private
build telemetry is upstream of the next two quarters of capacity
reality. Most retail-grade thesis trackers cannot fuse the two because
they have neither the telemetry nor a written rubric. This repo is the
written rubric plus the telemetry pipeline plus the memo schema. It
absorbs the older Build-Telemetry Channel Check sketch.

## Pillars (v0)

The 6 pillars the reconciler scores against are named in
`specs/0001-foundation/requirements.md` and will live in
`config/pillars.yaml` from PR 0002 forward:

1. Foundry capacity (TSMC N3 / N2 / A16)
2. Advanced packaging (CoWoS-S / CoWoS-L / SoIC)
3. HBM memory (HBM3E / HBM4)
4. Networking (NVLink / Infiniband / Ethernet at scale)
5. Power (grid interconnect, transformer lead times)
6. Cooling (liquid retrofit, immersion)

## License

MIT. See [LICENSE](LICENSE).
