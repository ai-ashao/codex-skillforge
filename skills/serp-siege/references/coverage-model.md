# Coverage Model

Coverage matrices turn observed product and SERP evidence into a shared product-and-page execution plan. They do not judge whether the project should exist.

## Feature Coverage Matrix

Required columns:

| Feature | Competitor A | Competitor B | Competitor C | Candidate | Priority | Evidence |
|---|---|---|---|---|---|---|

Use `YES`, `PARTIAL`, `NO`, or `MISSING` for competitor coverage. Use `EXISTING`, `PLANNED`, `OPTIONAL`, `REJECTED`, or `MISSING` for the candidate.

- `EXISTING` requires first-party or current live-public evidence about the candidate.
- `PLANNED` means the execution roadmap intentionally adds the feature; it must not stand in for an unknown current implementation state.
- `MISSING` means the candidate state has not been verified yet.

Interpretation:

- broad competitor adoption may indicate a baseline expectation, not differentiation;
- sparse adoption may be a gap or simply weak demand;
- a feature is attractive when it has demand evidence and reuses the candidate's core;
- cosmetic differences do not count as feature gaps.

## SERP Coverage Matrix

Required columns:

| Cluster | Primary Keyword | Intent | Evidence | SERP Strength | Gap | Reuse Potential | Proposed Page | Priority |
|---|---|---|---|---|---|---|---|---|

### SERP Strength

- `LOW`: several directly relevant results are weak, outdated, thin, broken, or poorly matched.
- `MEDIUM`: useful results exist, but product fit, depth, localization, or workflow remains inconsistent.
- `HIGH`: multiple strong, directly satisfying pages compete with credible authority and product fit.
- `VERY_HIGH`: the SERP is consistently dominated by strong products or brands with excellent intent fit and few visible weaknesses.

Use `MISSING` instead of guessing when current SERP evidence is unavailable.

### Gap

- `HIGH`: a concrete unmet workflow or quality gap appears repeatedly and can be delivered credibly.
- `MEDIUM`: a plausible gap exists but differentiation, demand, or execution evidence remains incomplete.
- `LOW`: current results already satisfy the task well, or the candidate advantage is cosmetic.
- `MISSING`: evidence is insufficient.

Gap is not keyword difficulty. Evaluate result quality, tool-intent fit, product experience, depth, authority dependence, freshness, localization, and workflow weakness.

### Reuse Potential

Use `HIGH`, `MEDIUM`, or `LOW` based on how much product logic, interface, validation, and content structure the cluster shares with the core tool. Do not use code reuse alone to justify a page.

## Evidence discipline

Every non-missing competitor and SERP claim must have a nearby source or observation. A matrix cell may summarize evidence, but its row must make the evidence type traceable.

The Keyword Cluster Map, SERP Coverage Map, SEO Page Map, and First Batch must use the same stable cluster names. Rejected exclusion-only candidates may appear only in the SEO Page Map, but every non-`REJECT` SEO row must be defined in the Keyword Cluster Map.
