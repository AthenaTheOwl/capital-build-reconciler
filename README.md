# capital-build-reconciler

You ask for tokens in us-east-1 and get a 429. The reconciler records the
observed rate-limit pressure and its sampling uncertainty. The reason for the
429 remains a separate question.

## What it does

The reconciler collapses a month of inference telemetry — calls, 429s, latency,
cost per region — into a ranked table with 95% Wilson intervals. Rate limits can
reflect account quotas, request bursts, or service policy; the logs alone cannot
identify a foundry, packaging, or memory constraint. Physical-supply attribution
therefore reads ABSTAIN until independently sourced evidence supports it.

The cadence is monthly. The decision is allocation across six named pillars
(foundry, packaging, memory, networking, power, cooling). The artifact is one
written page in `capital_reconcile/<year>-Mnn.md`. v0.0.2 ships the schema,
the pillar config, the validators, and a Helicone-style ingester for Anthropic
logs.

## Try it

Print the committed month's telemetry, ranked by rate-limit pressure. No args,
read-only, offline:

```bash
python -m capital_reconcile show
```

```
capital-build-reconciler - anthropic build telemetry, 2026-06 (2026-M06-ingest-summary)
3 call(s) across 2 region(s), ranked by rate-limit pressure (429s / calls)

region       calls  429s rl_pressure  95% interval avg_latency   cost_usd  models
---------------------------------------------------------------------------------
us-east-1        2     1       0.500        9%-91%       481ms $   0.0210  claude-3-5-sonnet
us-west-2        1     0       0.000        0%-79%       611ms $   0.0042  claude-3-5-haiku

headline: us-east-1 carried 1 of 1 rate-limit hit(s) this month (rl_pressure 50%). Observed service pressure; physical-supply attribution ABSTAIN pending independent evidence.
95% Wilson intervals assume independent calls; retries and bursts can widen uncertainty.
```

The interval assumes independent calls. Retries and correlated bursts can make
uncertainty larger. See [the attribution protocol](docs/telemetry-attribution.md).

## Live demo

A one-page Streamlit reader for the committed monthly telemetry: the per-region
table ranked by rate-limit pressure, three top-line metrics, a filter for
rate-limited regions, and the headline callout. It reads `reports/` directly —
no network, no secrets.

Run locally:

```bash
python -m uv run --with streamlit streamlit run streamlit_app.py
```

Deploy on Streamlit Community Cloud → New app → repo
`AthenaTheOwl/capital-build-reconciler`, branch `main`, main file
`streamlit_app.py`.

<!-- live-url: https://… (fill in after first deploy) -->

## Run the ingest path

Build the committed parquet from the fixture logs:

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

## How it connects

Sibling repos in the investing-decision spine, working the same six pillars from
different angles:

- [thesis-pillar-tracker](https://github.com/AthenaTheOwl/thesis-pillar-tracker)
  — holds the standing thesis each pillar is scored against.
- [earnings-pillar-diff](https://github.com/AthenaTheOwl/earnings-pillar-diff)
  — reads the same pillars off the public earnings calls, the slow channel this
  one runs ahead of.

This repo absorbs the older build-telemetry channel-check sketch.

## The six pillars

Named in `specs/0001-foundation/requirements.md`, moving to `config/pillars.yaml`
from PR 0002 forward:

1. Foundry capacity (TSMC N3 / N2 / A16)
2. Advanced packaging (CoWoS-S / CoWoS-L / SoIC)
3. HBM memory (HBM3E / HBM4)
4. Networking (NVLink / Infiniband / Ethernet at scale)
5. Power (grid interconnect, transformer lead times)
6. Cooling (liquid retrofit, immersion)

## Layout

```
src/capital_reconcile/    cli, show, ingest
capital_build_reconciler/ the ingest entry point
config/                   pillar config
reports/                  the committed month's telemetry
specs/0001-foundation/    schema + first monthly memo
schemas/  scripts/  tests/  decisions/  docs/
capital_reconcile/        written monthly memos land here
```

## License

MIT. See [LICENSE](LICENSE).

## Method update

[October method update: Rate-limit pressure is an observation; hardware attribution needs another test](docs/telemetry-attribution.md).
