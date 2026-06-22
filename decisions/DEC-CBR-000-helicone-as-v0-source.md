# DEC-CBR-000: Helicone-style JSON as the v0 source

Status: accepted

## Context

The reconciler needs one telemetry source before it can score monthly
pillar evidence. Helicone-style exports are JSON, easy to fixture, and
close to the fields named in R-CBR-005.

## Decision

Use Helicone-style JSON logs as the first supported ingest source.
Normalize each record into `schemas/normalized_event.schema.json` and
write the month as parquet.

## Consequences

The v0 CLI supports Anthropic records through the Helicone adapter.
Langfuse and Anthropic-native adapters stay out of scope until a real
question needs a field Helicone does not expose, or a second provider's
logs reach twice Anthropic's monthly volume.
