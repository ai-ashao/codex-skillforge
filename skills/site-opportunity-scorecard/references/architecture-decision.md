# Architecture Decision Rules

Scores are guardrails. Hard gates and evidence quality take priority.

## Default thresholds

### INDEPENDENT_SITE

Normally recommend only when all are true:

- opportunity score >= 75;
- separation risk <= 40;
- search opportunity subtotal >= 26 of 39;
- product differentiation subtotal >= 22 of 32;
- independent primary keyword raw score >= 3;
- homepage workflow difference raw score >= 3;
- no hard gate;
- overall confidence is medium or high.

A lower-confidence candidate may receive a provisional independent-site direction only after an existing-domain validation step.

### EXISTING_SITE_SECTION

Normally recommend when one or more are true:

- opportunity score >= 60 but separation risk is 41–70;
- keyword cluster and content system are substantial, but the audience/workflow is adjacent to the host;
- differentiation is moderate rather than strong;
- authority concentration is more valuable than a new brand;
- evidence is promising but not sufficient for a new domain.

A section should have its own hub, navigation, visual hierarchy, and distinct supporting pages.

### EXISTING_SITE_PAGE

Normally recommend when:

- opportunity score is 40–59;
- the query supports one useful tool or landing page but not a durable content system;
- users and workflow substantially overlap with the host;
- independent link or brand potential is limited;
- the feature is valuable primarily as part of a broader suite.

### OBSERVE_OR_REJECT

Normally recommend when:

- opportunity score < 40;
- a hard gate blocks the product entirely;
- the query is unstable, non-commercial, or unsupported by evidence;
- maintenance, compliance, or platform risk is unacceptable;
- the candidate is a duplicate shell with no real user value.

“Observe” is appropriate when the demand may emerge later. “Reject” is appropriate when structural problems are unlikely to change.

## Tie-breakers

When two architectures are plausible, prefer:

1. the architecture that concentrates authority and reduces duplicated operations;
2. an existing-site section before a new domain when confidence is low;
3. a dedicated page before a section when the long-tail system is weak;
4. a new domain only when the homepage, brand, content, and link systems are independently coherent.

## Re-evaluation triggers

Useful triggers include:

- dedicated page reaches a defined impression or click threshold;
- query breadth expands beyond the original cluster;
- direct or branded searches emerge;
- completion, return-use, or sharing behavior exceeds the host average;
- organic links repeatedly point to the feature;
- competitor weakness or platform changes create a new wedge;
- maintenance economics improve through code reuse or browser-side processing.
