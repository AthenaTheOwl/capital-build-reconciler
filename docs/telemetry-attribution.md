# Rate-limit pressure is an observation; hardware attribution needs another test

Method update: October 18, 2026. Proposed experiments below are not reported as executed results.

The readable telemetry view now includes a 95% Wilson interval for each region and returns ABSTAIN for physical-supply attribution. One hit in two calls has an interval of about 9%–91%; ranking those two calls does not establish a persistent regional difference. The interval assumes independent calls. Repeated retries and request bursts need clustered analysis before using it inferentially.

Anthropic documents request/token limits, organization tiers, and spend limits. These mechanisms provide alternatives to a hardware-scarcity explanation. Preserve request identifiers, model, account tier, token volume, retry relationships and error details when available; do not invent them from normalized rows that omitted them. The current normalizer keeps only timestamp, provider, model, region, latency, rate-limit flag, cost and token counts; it drops request ids, status codes and retry links, so the interval cannot yet be clustered from this repo's own output.

For a discriminating experiment, hold account, model, offered load and retry policy fixed while comparing regions in alternating time blocks. Record latency, success rate, error category and cost per successful task. A region effect that disappears when the quota or offered load changes weakens the physical-capacity hypothesis. Even a persistent effect needs independent public evidence before mapping to a named capital pillar. No telemetry-only UPWEIGHT is justified by this implementation.

## References

- https://platform.claude.com/docs/en/api/rate-limits
- https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm
