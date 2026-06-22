# Product Brief

Capital Build Reconciler is a monthly data-report repo for one operator
tracking AI-infra capital exposure against private build telemetry.

## User

- A portfolio operator with Helicone-style LLM usage exports.
- A reviewer who needs a short artifact, not a dashboard.
- A later factory agent that needs typed files and command contracts.

## Problem

- Public earnings data arrives after capacity stress has already shown
  up in build telemetry.
- Raw telemetry is too low-level for a capital decision.
- A monthly verdict needs explicit evidence refs and a revert threshold
  per pillar.

## v0.1 outcome

- Normalize Helicone-style Anthropic records into a typed parquet file.
- Keep the six pillar keys in `config/pillars.yaml`.
- Validate memo front matter and per-pillar evidence policy locally.
- Check in one report artifact under `reports/` so reviewers can inspect
  the data shape without rerunning ingest.

## Non-goals

- No trade execution.
- No live alerting.
- No public-news scraping.
- No multi-account telemetry aggregation.
