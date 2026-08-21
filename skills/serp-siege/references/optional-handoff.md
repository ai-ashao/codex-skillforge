# Optional Upstream Handoff

SERP Siege does not require or invoke an opportunity-analysis skill. It assumes the user has already decided to pursue the direction.

When the user supplies an upstream opportunity or architecture result, treat it as execution context rather than a question to reopen.

## Accepted context

Use any supplied:

- chosen destination or architecture;
- primary job and seed keyword cluster;
- target country, language, audience, or device;
- product, maintenance, policy, legal, API, and platform constraints;
- user-supplied metrics or first-party observations;
- explicit exclusions or validation commitments.

Example:

```yaml
opportunity_context:
  source: site-opportunity-scorecard
  destination: independent_site
  primary_cluster: image-compression
  constraints:
    - browser-local
    - low maintenance
```

## Rules

- Do not rerun, rescore, or challenge the upstream opportunity decision.
- Do not require the upstream Skill to be installed.
- Do not copy opportunity score or separation-risk calculations into the SERP Siege report.
- Preserve the chosen destination when mapping URLs and navigation.
- Translate supplied constraints into feature scope, page scope, priority, prerequisites, and validation actions.
- If upstream context conflicts with a newer explicit user instruction, follow the newer instruction and state the changed assumption.
- If no upstream context is supplied, continue with bounded assumptions and destination-neutral URLs where necessary.
