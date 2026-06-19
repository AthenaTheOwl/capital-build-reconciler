# AGENTS.md — capital-build-reconciler

Operating contract for AI agents (Claude, Codex, Cursor) working in
this repo. Conventions match the rest of the AthenaTheOwl portfolio so
an agent trained on `thesis-pillar-tracker` or `earnings-pillar-diff`
recognizes the shape.

## What this repo is

A monthly reconciliation pipeline. Personal LLM-inference telemetry on
one side, six named investing pillars on the other, one written page of
HOLD / UPWEIGHT / TRIM verdicts per month. The verdicts include
explicit revert thresholds and a per-pillar evidence trail.

This is a written-decision repo, not a dashboard. The monthly memo is
the artifact.

## Roles you may see in tasks

| Role | What they do |
|---|---|
| `telemetry-ingester` | Pulls Helicone/Langfuse-style logs into a typed monthly schema |
| `pillar-scorer` | Maps telemetry deltas onto the 6-pillar rubric |
| `memo-writer` | Produces the monthly capital_reconcile/<year>-Mnn.md |
| `revert-tracker` | Re-reads last 6 memos; flags pillars whose revert threshold tripped |

These roles exist in spec ledger; not all are implemented in v0.

## Voice constraints

- Plain assertion. The pillar verdicts are the load-bearing claim; the
  prose around them is scaffolding.
- No marketing words. No "leverage", "synergy", "seamless",
  "best-in-class".
- No antithetical-reversal structure. Each pillar verdict is a single
  flat claim plus the evidence behind it.
- Honest about uncertainty. If three months of telemetry is too thin
  to score a pillar, the memo says so and abstains.

## Gates (will land in spec 0002)

The intended local-gate chain:

```bash
python -m pytest
python scripts/voice_lint.py
python scripts/validate_schemas.py     # validates monthly-memo schema
python scripts/validate_pillars.py     # checks every verdict has evidence
```

The pillar-validator gate is the load-bearing one. A monthly memo
without an evidence reference per pillar verdict does not merge.

## Out of scope

- Real-time alerting. The cadence is monthly. Telemetry drift inside a
  month is noise.
- Public-narrative scraping. The point is that this repo's signal is
  *not* the news cycle. News fusion happens upstream in
  `earnings-pillar-diff`.
- Auto-trading or any execution layer. The repo writes memos; humans
  trade.
- Multi-account telemetry aggregation. Single operator's keys only in
  v0.
